from PIL import Image
from PIL.ExifTags import TAGS
import argparse
import os

def extract_metadata(image_path):
    image = Image.open(image_path)
    exif_data = image._getexif()

    if not exif_data:
        print("No metadata found.")
        return

    for tag_id, value in exif_data.items():
        tag_name = TAGS.get(tag_id, tag_id)
        print(f"{tag_name}: {value}")

def main():
    parser = argparse.ArgumentParser(description="Extract EXIF metadata from an image.")
    parser.add_argument("image_path", help="Path to input image")
    args = parser.parse_args()

    if not os.path.exists(args.image_path):
        print(f"Image not found: {args.image_path}")
        return

    extract_metadata(args.image_path)


if __name__ == "__main__":
    main()
