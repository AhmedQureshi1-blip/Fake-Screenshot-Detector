import cv2
import argparse
import os

def detect_edges(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    if image is None:
        print("Image not found!")
        return
    
    edges = cv2.Canny(image, 50, 150)
    
    cv2.imshow("Edges", edges)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def main():
    parser = argparse.ArgumentParser(description="Run Canny edge detection on an image.")
    parser.add_argument("image_path", help="Path to input image")
    args = parser.parse_args()

    if not os.path.exists(args.image_path):
        print(f"Image not found: {args.image_path}")
        return

    detect_edges(args.image_path)


if __name__ == "__main__":
    main()
