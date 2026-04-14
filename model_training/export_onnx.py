"""
Export COD-Odisha model to ONNX format for edge deployment.

Usage:
    python export_onnx.py --checkpoint checkpoints/best_model.pth --output cod_odisha.onnx
"""

import argparse
from pathlib import Path

import torch
import yaml

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from backend.app.models import build_model


def export_to_onnx(model, output_path, input_size=(1, 3, 416, 416), opset=13):
    """
    Export PyTorch model to ONNX format.
    
    Args:
        model: PyTorch model
        output_path: Path to save ONNX file
        input_size: (batch, channels, height, width)
        opset: ONNX opset version
    """
    model.eval()
    
    # Create dummy input
    dummy_input = torch.randn(*input_size)
    
    # Move to same device as model
    device = next(model.parameters()).device
    dummy_input = dummy_input.to(device)
    
    # Export
    torch.onnx.export(
        model,
        dummy_input,
        output_path,
        export_params=True,
        opset_version=opset,
        do_constant_folding=True,
        input_names=['image'],
        output_names=['mask', 'heatmap', 'confidence'],
        dynamic_axes={
            'image': {0: 'batch_size', 2: 'height', 3: 'width'},
            'mask': {0: 'batch_size', 2: 'height', 3: 'width'},
            'heatmap': {0: 'batch_size', 2: 'height', 3: 'width'},
            'confidence': {0: 'batch_size'}
        },
        verbose=False
    )
    
    print(f"Exported to: {output_path}")
    
    # Verify export
    try:
        import onnx
        onnx_model = onnx.load(output_path)
        onnx.checker.check_model(onnx_model)
        print("ONNX model validation passed!")
        
        # Print model info
        print(f"\nModel info:")
        print(f"  IR version: {onnx_model.ir_version}")
        print(f"  Opset: {opset}")
        print(f"  Producer: {onnx_model.producer_name}")
        
    except ImportError:
        print("onnx package not installed, skipping validation")
    except Exception as e:
        print(f"ONNX validation warning: {e}")


def main():
    parser = argparse.ArgumentParser(description='Export COD-Odisha to ONNX')
    parser.add_argument('--checkpoint', type=str, required=True, help='Path to checkpoint')
    parser.add_argument('--config', type=str, default=None, help='Path to config YAML')
    parser.add_argument('--output', type=str, default='cod_odisha.onnx', help='Output ONNX path')
    parser.add_argument('--input-size', type=int, nargs=4, default=[1, 3, 416, 416],
                        help='Input size as batch channels height width')
    parser.add_argument('--opset', type=int, default=13, help='ONNX opset version')
    args = parser.parse_args()
    
    print("=" * 60)
    print("COD-Odisha ONNX Export")
    print("=" * 60)
    print(f"Checkpoint: {args.checkpoint}")
    print(f"Output: {args.output}")
    print(f"Input size: {args.input_size}")
    print("=" * 60)
    
    # Load config if provided
    if args.config:
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
        backbone = config['model']['backbone']
    else:
        backbone = 'resnet50'
    
    # Build model
    print(f"\nBuilding model with {backbone} backbone...")
    model = build_model(backbone=backbone, pretrained=False)
    
    # Load checkpoint
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    checkpoint = torch.load(args.checkpoint, map_location=device)
    
    state_dict = checkpoint['model_state_dict']
    # Remove DataParallel prefix if present
    state_dict = {k.replace('module.', ''): v for k, v in state_dict.items()}
    
    model.load_state_dict(state_dict, strict=False)
    model = model.to(device)
    
    print(f"Loaded checkpoint from epoch {checkpoint.get('epoch', 'unknown')}")
    
    # Export
    print("\nExporting to ONNX...")
    input_size = tuple(args.input_size)
    export_to_onnx(model, args.output, input_size, args.opset)
    
    print("\nExport complete!")
    print(f"Model saved to: {Path(args.output).absolute()}")


if __name__ == '__main__':
    main()
