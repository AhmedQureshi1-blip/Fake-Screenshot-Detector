#!/usr/bin/env python3
"""Test the upload endpoint"""
import requests
from pathlib import Path

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
                
                if r.status_code == 200:
                    result = r.json()
                    print(f'\nResult: {result.get("result")}')
                    print(f'Confidence: {result.get("confidence")}%')
                    print(f'Summary: {result.get("summary")}')
                    print('\n✅ Upload endpoint WORKS PERFECTLY!')
                    return True
                else:
                    print(f'\n❌ Error: {r.text}')
                    return False
            except Exception as e:
                print(f'\n❌ Error: {e}')
                return False
    else:
        print('No test images found')
        return False

if __name__ == '__main__':
    test_upload()
