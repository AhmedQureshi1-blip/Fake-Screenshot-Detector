import cv2
import pytesseract
import argparse
import os
import shutil

def configure_tesseract_path():
    env_path = os.environ.get("TESSERACT_CMD")
    if env_path and os.path.exists(env_path):
        pytesseract.pytesseract.tesseract_cmd = env_path
        return

    detected_path = shutil.which("tesseract")
    if detected_path:
        pytesseract.pytesseract.tesseract_cmd = detected_path
        return

    default_windows_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.exists(default_windows_path):
        pytesseract.pytesseract.tesseract_cmd = default_windows_path

def extract_text(image_path):
    image = cv2.imread(image_path)
    
    if image is None:
        print("Error: Image not found!")
        return
    
    # Convert image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Text extract karo
    extracted_text = pytesseract.image_to_string(gray)

    print("📌 Extracted Text from Screenshot:\n")
    print(extracted_text)

def main():
    parser = argparse.ArgumentParser(description="Extract text from image using OpenCV + Tesseract.")
    parser.add_argument("image_path", help="Path to input image")
    args = parser.parse_args()

    if not os.path.exists(args.image_path):
        print(f"Image not found: {args.image_path}")
        return

    configure_tesseract_path()
    extract_text(args.image_path)


if __name__ == "__main__":
    main()
