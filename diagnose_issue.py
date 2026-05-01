#!/usr/bin/env python
"""
Diagnostic script to isolate the analyze_image failure.
"""
import os
import sys
import traceback

print("=" * 60)
print("DIAGNOSTIC: Checking core dependencies and functions")
print("=" * 60)

# 1. Check model file exists
MODEL_PATH = "models/payment_screenshot_model.joblib"
print(f"\n1. Model file check: {MODEL_PATH}")
if os.path.exists(MODEL_PATH):
    print(f"   ✓ File exists, size: {os.path.getsize(MODEL_PATH)} bytes")
else:
    print(f"   ✗ File NOT found")
    sys.exit(1)

# 2. Check training data
print(f"\n2. Training data check (uploads/)")
if os.path.isdir("uploads"):
    files = [f for f in os.listdir("uploads") if f.endswith((".jpg", ".jpeg", ".png"))]
    print(f"   ✓ Found {len(files)} images in uploads/")
else:
    print(f"   ✗ uploads/ directory not found")

# 3. Try loading model
print(f"\n3. Loading trained model")
try:
    import joblib
    bundle = joblib.load(MODEL_PATH)
    print(f"   ✓ Loaded model bundle")
    print(f"   ✓ Bundle keys: {list(bundle.keys())}")
    if 'feature_names' in bundle:
        print(f"   ✓ feature_names: {len(bundle['feature_names'])} names")
    if 'model' in bundle:
        print(f"   ✓ model: {type(bundle['model'])}")
except Exception as e:
    print(f"   ✗ Failed to load model: {e}")
    traceback.print_exc()
    sys.exit(1)

# 4. Try extracting features from a sample image
print(f"\n4. Testing feature extraction")
try:
    from train_model import extract_feature_dict
    sample = "uploads/real1.jpeg"
    if os.path.exists(sample):
        feature_dict, text = extract_feature_dict(sample)
        print(f"   ✓ Extracted {len(feature_dict)} features from {sample}")
        print(f"   ✓ Text length: {len(text)} chars")
    else:
        print(f"   ✗ Sample image {sample} not found")
except Exception as e:
    print(f"   ✗ Feature extraction failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# 5. Try predict_real_probability
print(f"\n5. Testing predict_real_probability")
try:
    from server import predict_real_probability
    sample = "uploads/real1.jpeg"
    if os.path.exists(sample):
        prob, feat_dict, bundle_ret = predict_real_probability(sample)
        print(f"   ✓ Probability: {prob}")
        print(f"   ✓ Feature count: {len(feat_dict)}")
    else:
        print(f"   ✗ Sample image {sample} not found")
except Exception as e:
    print(f"   ✗ predict_real_probability failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# 6. Try analyze_image
print(f"\n6. Testing analyze_image")
try:
    from server import analyze_image
    sample = "uploads/real1.jpeg"
    if os.path.exists(sample):
        result, metadata = analyze_image(sample)
        print(f"   ✓ Result: {result}")
        print(f"   ✓ Metadata keys: {list(metadata.keys())}")
        if 'confidence' in metadata:
            print(f"   ✓ Confidence: {metadata['confidence']}")
    else:
        print(f"   ✗ Sample image {sample} not found")
except Exception as e:
    print(f"   ✗ analyze_image failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ ALL DIAGNOSTIC CHECKS PASSED")
print("=" * 60)
