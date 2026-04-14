"""COD-Odisha App Modules Package"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class ChannelAttention(nn.Module):
    """Channel Attention Module for feature refinement."""
    
    def __init__(self, in_channels, reduction=16):
        super().__init__()
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.max_pool = nn.AdaptiveMaxPool2d(1)
        
        self.fc = nn.Sequential(
            nn.Conv2d(in_channels, in_channels // reduction, kernel_size=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels // reduction, in_channels, kernel_size=1)
        )
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        avg_out = self.fc(self.avg_pool(x))
        max_out = self.fc(self.max_pool(x))
        out = avg_out + max_out
        return self.sigmoid(out)


class SpatialAttention(nn.Module):
    """Spatial Attention Module."""
    
    def __init__(self, kernel_size=7):
        super().__init__()
        self.conv = nn.Conv2d(2, 1, kernel_size=kernel_size, padding=kernel_size // 2)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        avg_out = torch.mean(x, dim=1, keepdim=True)
        max_out, _ = torch.max(x, dim=1, keepdim=True)
        x = torch.cat([avg_out, max_out], dim=1)
        x = self.conv(x)
        return self.sigmoid(x)


class CCSIM(nn.Module):
    """
    Cross-Scale Channel Similarity & Interaction Module
    Aligns and fuses multi-scale feature maps using channel attention.
    """
    
    def __init__(self, in_channels, out_channels=128):
        super().__init__()
        self.out_channels = out_channels
        
        # Feature alignment for different scales
        self.align_c2 = nn.Conv2d(in_channels[0], out_channels, 1)
        self.align_c3 = nn.Conv2d(in_channels[1], out_channels, 1)
        self.align_c4 = nn.Conv2d(in_channels[2], out_channels, 1)
        self.align_c5 = nn.Conv2d(in_channels[3], out_channels, 1)
        
        # Channel attention for each scale
        self.ca_c2 = ChannelAttention(out_channels)
        self.ca_c3 = ChannelAttention(out_channels)
        self.ca_c4 = ChannelAttention(out_channels)
        self.ca_c5 = ChannelAttention(out_channels)
        
        # Cross-scale interaction
        self.interaction = nn.Sequential(
            nn.Conv2d(out_channels * 4, out_channels, 3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, 3, padding=1),
            nn.BatchNorm2d(out_channels)
        )
    
    def forward(self, features):
        """
        Args:
            features: List of feature maps [C2, C3, C4, C5]
        
        Returns:
            Fused multi-scale features
        """
        c2, c3, c4, c5 = features
        
        # Align to common channels
        c2_aligned = self.align_c2(c2)
        c3_aligned = self.align_c3(c3)
        c4_aligned = self.align_c4(c4)
        c5_aligned = self.align_c5(c5)
        
        # Apply channel attention
        c2_attended = c2_aligned * self.ca_c2(c2_aligned)
        c3_attended = c3_aligned * self.ca_c3(c3_aligned)
        c4_attended = c4_aligned * self.ca_c4(c4_aligned)
        c5_attended = c5_aligned * self.ca_c5(c5_aligned)
        
        # Resize all to C2 resolution
        h2, w2 = c2_attended.shape[-2:]
        c3_resized = F.interpolate(c3_attended, size=(h2, w2), mode='bilinear', align_corners=False)
        c4_resized = F.interpolate(c4_attended, size=(h2, w2), mode='bilinear', align_corners=False)
        c5_resized = F.interpolate(c5_attended, size=(h2, w2), mode='bilinear', align_corners=False)
        
        # Concatenate and fuse
        fused = torch.cat([c2_attended, c3_resized, c4_resized, c5_resized], dim=1)
        output = self.interaction(fused)
        
        return output


class SGFL(nn.Module):
    """
    Semantic Guided Feature Learning
    Suppresses background, enhances objects and boundaries using semantic guidance.
    """
    
    def __init__(self, in_channels, out_channels=64):
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        
        # Semantic guidance branches
        self.semantic_branch = nn.Sequential(
            nn.Conv2d(in_channels, in_channels // 2, 3, padding=1),
            nn.BatchNorm2d(in_channels // 2),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels // 2, out_channels, 3, padding=1),
            nn.BatchNorm2d(out_channels)
        )
        
        # Object enhancement branch
        self.object_branch = nn.Sequential(
            nn.Conv2d(in_channels, in_channels // 2, 3, padding=1),
            nn.BatchNorm2d(in_channels // 2),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels // 2, out_channels, 3, padding=1),
            nn.BatchNorm2d(out_channels)
        )
        
        # Boundary branch
        self.boundary_branch = nn.Sequential(
            nn.Conv2d(in_channels, in_channels // 2, 3, padding=1),
            nn.BatchNorm2d(in_channels // 2),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels // 2, out_channels, 3, padding=1),
            nn.BatchNorm2d(out_channels)
        )
        
        # Channel attention
        self.ca = ChannelAttention(out_channels)
        self.spatial_att = SpatialAttention()
    
    def forward(self, x):
        """
        Semantic guided feature learning.
        
        Args:
            x: Input features
        
        Returns:
            Enhanced features with semantic guidance
        """
        semantic = self.semantic_branch(x)
        object_feat = self.object_branch(x)
        boundary = self.boundary_branch(x)
        
        # Combine features with attention
        combined = semantic + object_feat + boundary
        combined = combined * self.ca(combined)
        combined = combined * self.spatial_att(combined)
        
        return combined


class BoundaryAwareDecoder(nn.Module):
    """
    Boundary-Aware Decoder with progressive upsampling and boundary loss.
    """
    
    def __init__(self, in_channels=64):
        super().__init__()
        self.in_channels = in_channels
        
        # Decoder stages
        self.decode4 = nn.Sequential(
            nn.Conv2d(in_channels, in_channels, 3, padding=1),
            nn.BatchNorm2d(in_channels),
            nn.ReLU(inplace=True)
        )
        
        self.decode3 = nn.Sequential(
            nn.Conv2d(in_channels, in_channels // 2, 3, padding=1),
            nn.BatchNorm2d(in_channels // 2),
            nn.ReLU(inplace=True)
        )
        
        self.decode2 = nn.Sequential(
            nn.Conv2d(in_channels // 2, in_channels // 4, 3, padding=1),
            nn.BatchNorm2d(in_channels // 4),
            nn.ReLU(inplace=True)
        )
        
        # Final prediction heads
        self.mask_head = nn.Conv2d(in_channels // 4, 1, 1)
        self.boundary_head = nn.Conv2d(in_channels // 4, 1, 1)
        
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x, target_size=None):
        """
        Args:
            x: Input features
            target_size: Target output size (H, W)
        
        Returns:
            Dictionary with mask and boundary predictions
        """
        # Progressive upsampling
        x = self.decode4(x)
        x = F.interpolate(x, scale_factor=2, mode='bilinear', align_corners=False)
        
        x = self.decode3(x)
        x = F.interpolate(x, scale_factor=2, mode='bilinear', align_corners=False)
        
        x = self.decode2(x)
        x = F.interpolate(x, scale_factor=2, mode='bilinear', align_corners=False)
        
        # Final predictions
        mask = self.sigmoid(self.mask_head(x))
        boundary = self.sigmoid(self.boundary_head(x))
        
        # Resize to target if provided
        if target_size is not None:
            mask = F.interpolate(mask, size=target_size, mode='bilinear', align_corners=False)
            boundary = F.interpolate(boundary, size=target_size, mode='bilinear', align_corners=False)
        
        return {
            'mask': mask,
            'boundary': boundary,
            'confidence': mask.max(dim=-1)[0].max(dim=-1)[0]
        }


__all__ = ['CCSIM', 'SGFL', 'BoundaryAwareDecoder', 'ChannelAttention', 'SpatialAttention']

