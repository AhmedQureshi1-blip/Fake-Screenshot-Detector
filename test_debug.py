#!/usr/bin/env python3
"""Test with error logging to file"""
import requests
import json
from pathlib import Path
import time

# Wait for server to process any previous request
time.sleep(2)

# Clear error log
error_log = Path('error_debug.txt')
if error_log.exists():
    error_log.unlink()

def test_upload():
    uploads_dir = Path('uploads')
    images = list(uploads_dir.glob('real*.jpeg'))[:1]
    
    if images:
        img_path = images[0]
        print(f'Testing upload with: {img_path.name}')
        print('-' * 60)
        
        with open(img_path, 'rb') as f:
            files = {'file': f}
            try:
                r = requests.post('http://localhost:5000/upload', files=files, timeout=60)
                print(f'Status Code: {r.status_code}')
                print(f'Response: {json.dumps(r.json(), indent=2)}')
                
                time.sleep(2)
                
                # Check if error log was created
                if error_log.exists():
                    print('\n❌ ERROR LOG:')
                    print(error_log.read_text())
                    
            except Exception as e:
                print(f'Request error: {e}')

if __name__ == '__main__':
    test_upload()
