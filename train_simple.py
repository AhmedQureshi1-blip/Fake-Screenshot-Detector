#!/usr/bin/env python3
"""
Simple training script to train the model on existing data in uploads folder.
Images should be named: real_*.png or fake_*.png
"""

import sys
from pathlib import Path
from train_model import train

def main():
    try:
        print("=" * 60)
        print("Fake Payment Screenshot Detector - Model Training")
        print("=" * 60)
        
        uploads_dir = Path(__file__).parent / "uploads"
        
        # Check if uploads folder exists
        if not uploads_dir.exists():
            print(f"ERROR: {uploads_dir} folder does not exist!")
            print("Please create an 'uploads' folder with training images.")
            return False
        
        # Check if there are any images
        image_files = list(uploads_dir.glob("*.[pjb]*"))
        if not image_files:
            print(f"ERROR: No images found in {uploads_dir}")
            print("Please add images with names like: real_*.png or fake_*.png")
            return False
        
        print(f"\nFound {len(image_files)} images in {uploads_dir}")
        
        # Train the model
        print("\nStarting model training...")
        print("-" * 60)
        train()
        print("-" * 60)
        print("\n✓ Model training completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n✗ Error during training: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
