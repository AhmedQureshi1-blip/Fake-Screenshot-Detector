from PIL import Image
from PIL.ExifTags import TAGS
import argparse
import os

def print_metadata(image_path):
    # Image open karo
    image = Image.open(image_path)

    # EXIF metadata extract karo
    exif_data = image._getexif()

    if exif_data:
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag, tag)
            print(f"{tag_name}: {value}")
    else:
        print("No EXIF metadata found!")

def main():
    parser = argparse.ArgumentParser(description="Print image EXIF metadata.")
    parser.add_argument("image_path", help="Path to input image")
    args = parser.parse_args()

    if not os.path.exists(args.image_path):
        print(f"Image not found: {args.image_path}")
        return

    print_metadata(args.image_path)


if __name__ == "__main__":
    main()
