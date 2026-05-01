import requests
import argparse
import os

def test_upload(api_base_url, file_path):
    url = f"{api_base_url.rstrip('/')}/upload"

    with open(file_path, "rb") as f:
        files = {"file": f}
        response = requests.post(url, files=files, timeout=30)

    print("Status Code:", response.status_code)
    print("Response Text:", response.text)

    try:
        print("JSON Response:", response.json())
    except requests.exceptions.JSONDecodeError:
        print("Error: Response is not in JSON format!")

def main():
    parser = argparse.ArgumentParser(description="Test /upload API endpoint with an image file.")
    parser.add_argument("image_path", help="Path to image to upload")
    parser.add_argument("--api", default="http://127.0.0.1:5000", help="API base URL")
    args = parser.parse_args()

    if not os.path.exists(args.image_path):
        print(f"Image not found: {args.image_path}")
        return

    test_upload(args.api, args.image_path)


if __name__ == "__main__":
    main()

