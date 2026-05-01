from PIL import Image, ImageChops, ImageEnhance
import argparse
import os

def error_level_analysis(image_path, output_path="lakshtransaction.jpg", quality=90):
    # Open image
    original = Image.open(image_path).convert('RGB')
    
    # Save image with lower quality
    original.save("lakshtransaction.jpg", "JPEG", quality=quality)

    # Re-open saved image
    recompressed = Image.open("lakshtransaction.jpg")

    # Compute difference
    diff = ImageChops.difference(original, recompressed)

    # Enhance the difference
    extrema = diff.getextrema()
    max_diff = max([ex[1] for ex in extrema])
    scale = 255.0 / max_diff if max_diff else 1
    diff = ImageEnhance.Brightness(diff).enhance(scale)

    # Save the ELA image
    diff.save(output_path)
    print(f"ELA analysis saved as {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Run Error Level Analysis (ELA) on an image.")
    parser.add_argument("image_path", help="Path to input image")
    parser.add_argument("--output", default="ela_output.jpg", help="Path to output ELA image")
    parser.add_argument("--quality", type=int, default=90, help="JPEG recompression quality")
    args = parser.parse_args()

    if not os.path.exists(args.image_path):
        print(f"Image not found: {args.image_path}")
        return

    error_level_analysis(args.image_path, output_path=args.output, quality=args.quality)


if __name__ == "__main__":
    main()
