import joblib
from pathlib import Path
from train_model import extract_feature_dict
import numpy as np
import traceback

MODEL_PATH = 'models/payment_screenshot_model.joblib'

print('1. Loading model...')
try:
    bundle = joblib.load(MODEL_PATH)
    print(f'✓ Model loaded. Keys: {list(bundle.keys())}')
except Exception as e:
    print(f'✗ Model loading failed: {e}')
    traceback.print_exc()
    exit(1)

print('\n2. Checking model structure...')
model = bundle.get('model')
feature_names = bundle.get('feature_names')
print(f'✓ Model type: {type(model).__name__}')
print(f'✓ Feature names count: {len(feature_names) if feature_names else "None"}')

print('\n3. Testing with image...')
uploads_dir = Path('uploads')
images = list(uploads_dir.glob('real*.jpeg'))[:1]

if images:
    img_path = images[0]
    print(f'Image: {img_path.name}')
    
    try:
        feature_dict, text = extract_feature_dict(img_path)
        print(f'✓ Features extracted: {len(feature_dict)} features')
        
        # Build feature vector
        feature_vector = np.array([feature_dict.get(name, 0.0) for name in feature_names]).reshape(1, -1)
        print(f'✓ Feature vector shape: {feature_vector.shape}')
        
        # Make prediction
        probabilities = model.predict_proba(feature_vector)
        print(f'✓ Prediction: {probabilities}')
        
        real_prob = float(probabilities[0][1])
        print(f'✓ Real probability: {real_prob:.4f}')
        print(f'✓ Prediction: {"Real" if real_prob >= 0.5 else "Fake"}')
        
    except Exception as e:
        print(f'✗ Error: {e}')
        traceback.print_exc()
else:
    print('No images found')
