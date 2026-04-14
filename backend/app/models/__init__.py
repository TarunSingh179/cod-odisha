"""COD-Odisha Model Package"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import torch
import torch.nn as nn
import torchvision.models as models
from app.modules import CCSIM, SGFL, BoundaryAwareDecoder
import torch.nn.functional as F


class CODModel(nn.Module):
    """
    Complete Camouflaged Object Detection Model
    Architecture: Backbone -> CCSIM -> SGFL -> Decoder
    """
    
    def __init__(self, backbone='resnet50', pretrained=True, ccsim_out=128, sgfl_out=64):
        super().__init__()
        self.backbone_name = backbone
        self.pretrained = pretrained
        
        # Load backbone
        if backbone == 'resnet50':
            weights = models.ResNet50_Weights.DEFAULT if pretrained else None
            resnet = models.resnet50(weights=weights)
            self.layer1 = nn.Sequential(resnet.conv1, resnet.bn1, resnet.relu, resnet.maxpool)
            self.layer2 = resnet.layer1
            self.layer3 = resnet.layer2
            self.layer4 = resnet.layer3
            self.layer5 = resnet.layer4
            
            # Feature channels at each stage
            feature_channels = [64, 256, 512, 1024, 2048]
        
        elif backbone == 'resnet18':
            weights = models.ResNet18_Weights.DEFAULT if pretrained else None
            resnet = models.resnet18(weights=weights)
            self.layer1 = nn.Sequential(resnet.conv1, resnet.bn1, resnet.relu, resnet.maxpool)
            self.layer2 = resnet.layer1
            self.layer3 = resnet.layer2
            self.layer4 = resnet.layer3
            self.layer5 = resnet.layer4
            
            feature_channels = [64, 64, 128, 256, 512]
        
        else:
            raise ValueError(f"Unsupported backbone: {backbone}")
        
        self.feature_channels = feature_channels
        
        # CCSIM: Cross-Scale Channel Similarity & Interaction
        self.ccsim = CCSIM(
            in_channels=feature_channels[1:],  # C2, C3, C4, C5
            out_channels=ccsim_out
        )
        
        # SGFL: Semantic Guided Feature Learning
        self.sgfl = SGFL(
            in_channels=ccsim_out,
            out_channels=sgfl_out
        )
        
        # Decoder
        self.decoder = BoundaryAwareDecoder(in_channels=sgfl_out)
        
        # Loss weights
        self.loss_weights = {
            'bce': 1.0,
            'iou': 1.0,
            'boundary': 0.5,
            'semantic': 0.3
        }
    
    def forward(self, x, target_mask=None, target_boundary=None):
        """
        Forward pass of COD model.
        
        Args:
            x: Input image tensor (B, 3, H, W)
            target_mask: Target mask for training (B, 1, H, W)
            target_boundary: Target boundary for training (B, 1, H, W)
        
        Returns:
            Dictionary with predictions and losses
        """
        orig_size = x.shape[-2:]
        
        # Backbone feature extraction
        c1 = self.layer1(x)  # 1/4
        c2 = self.layer2(c1)  # 1/4
        c3 = self.layer3(c2)  # 1/8
        c4 = self.layer4(c3)  # 1/16
        c5 = self.layer5(c4)  # 1/32
        
        # CCSIM: Multi-scale feature fusion
        fused_features = self.ccsim([c2, c3, c4, c5])
        
        # SGFL: Semantic guided feature learning
        enhanced_features = self.sgfl(fused_features)
        
        # Decoder: Generate predictions
        decoder_out = self.decoder(enhanced_features, target_size=orig_size)
        
        output = {
            'mask': decoder_out['mask'],
            'boundary': decoder_out['boundary'],
            'confidence': decoder_out['confidence']
        }
        
        # Compute losses during training
        if target_mask is not None:
            losses = self.compute_losses(
                output['mask'],
                target_mask,
                target_boundary
            )
            output['losses'] = losses
        
        return output
    
    def compute_losses(self, pred_mask, target_mask, target_boundary=None):
        """Compute training losses."""
        losses = {}
        
        # BCE Loss
        bce_loss = F.binary_cross_entropy(pred_mask, target_mask)
        losses['bce'] = bce_loss
        
        # IoU Loss
        intersection = (pred_mask * target_mask).sum()
        union = (pred_mask + target_mask - pred_mask * target_mask).sum()
        iou_loss = 1 - (intersection + 1e-8) / (union + 1e-8)
        losses['iou'] = iou_loss
        
        # Boundary Loss
        if target_boundary is not None:
            boundary_loss = F.binary_cross_entropy(pred_mask, target_boundary) * 0.5
            losses['boundary'] = boundary_loss
        else:
            losses['boundary'] = torch.tensor(0.0, device=pred_mask.device)
        
        # Semantic Loss (encourages sharp boundaries)
        edge = torch.abs(torch.nn.functional.conv2d(
            pred_mask,
            torch.tensor([[-1., 0., 1.], [-2., 0., 2.], [-1., 0., 1.]]).view(1, 1, 3, 3).to(pred_mask.device),
            padding=1
        ))
        semantic_loss = 1.0 - edge.mean()
        losses['semantic'] = semantic_loss
        
        # Total loss
        total_loss = (
            self.loss_weights['bce'] * losses['bce'] +
            self.loss_weights['iou'] * losses['iou'] +
            self.loss_weights['boundary'] * losses['boundary'] +
            self.loss_weights['semantic'] * losses['semantic']
        )
        losses['total'] = total_loss
        
        return losses
    
    def set_loss_weights(self, weights):
        """Set custom loss weights."""
        self.loss_weights.update(weights)


def build_model(backbone='resnet50', pretrained=True, ccsim_out=128, sgfl_out=64):
    """
    Build COD model.
    
    Args:
        backbone: Backbone architecture ('resnet50' or 'resnet18')
        pretrained: Use pretrained backbone weights
        ccsim_out: CCSIM output channels
        sgfl_out: SGFL output channels
    
    Returns:
        CODModel instance
    """
    model = CODModel(
        backbone=backbone,
        pretrained=pretrained,
        ccsim_out=ccsim_out,
        sgfl_out=sgfl_out
    )
    return model


__all__ = ['CODModel', 'build_model']
