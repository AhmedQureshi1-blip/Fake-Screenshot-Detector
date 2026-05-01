import hashlib
import logging
import os
import random
import re
import shutil
import string
import tempfile
from datetime import datetime

import cv2
import joblib
import numpy as np
from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, request, send_file, url_for
from flask_cors import CORS
from PIL import ExifTags, Image, ImageChops
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from werkzeug.utils import secure_filename

# Load environment variables from .env file
load_dotenv()

# Try to import pytesseract - make it optional
try:
    import pytesseract
    from pytesseract import Output
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    print("WARNING: pytesseract not available, OCR will be disabled")

from train_model import MODEL_PATH, extract_feature_dict

logging.basicConfig(level=logging.INFO)

# Add file logging so tracebacks are persisted for debugging
log_file = os.getenv("LOG_FILE", "server.log")
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logging.getLogger().addHandler(file_handler)
app = Flask(__name__)
CORS(app)

# Configuration from .env
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
REPORTS_FOLDER = os.getenv("REPORTS_FOLDER", "reports")
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", "10485760"))

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORTS_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["REPORTS_FOLDER"] = REPORTS_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

TRAINED_MODEL_BUNDLE = None


def configure_tesseract_path():
    if not TESSERACT_AVAILABLE:
        return
    
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
        return

    logging.warning("Tesseract executable not found. OCR will be disabled.")


configure_tesseract_path()


def load_trained_model():
    global TRAINED_MODEL_BUNDLE
    if TRAINED_MODEL_BUNDLE is not None:
        return TRAINED_MODEL_BUNDLE

    if os.path.exists(MODEL_PATH):
        try:
            TRAINED_MODEL_BUNDLE = joblib.load(MODEL_PATH)
            logging.info("Loaded trained model from %s", MODEL_PATH)
        except Exception as exc:
            logging.exception("Failed to load trained model: %s", exc)
            TRAINED_MODEL_BUNDLE = None

    return TRAINED_MODEL_BUNDLE


def predict_real_probability(image_path):
    bundle = load_trained_model()
    if not bundle:
        return None, {}, None
    
    try:
        # Extract features
        feature_dict, extracted_text = extract_feature_dict(image_path)
        
        # Get model and feature names from bundle
        model = bundle.get("model")
        feature_names = bundle.get("feature_names", list(feature_dict.keys()))
        
        if model is None:
            return None, feature_dict, bundle
        
        # Prepare feature vector in correct order
        feature_vector = np.array([feature_dict.get(name, 0.0) for name in feature_names]).reshape(1, -1)
        
        # Get probability for real class (class 1)
        probabilities = model.predict_proba(feature_vector)
        real_probability = float(probabilities[0][1])  # Probability of class 1 (Real)
        
        return real_probability, feature_dict, bundle
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        logging.exception("Error in predict_real_probability: %s", e)
        # Persist traceback for easier debugging
        try:
            with open("error_debug.txt", "a", encoding="utf-8") as f:
                f.write("\n=== predict_real_probability traceback ===\n")
                f.write(tb)
        except Exception:
            logging.exception("Failed to write error_debug.txt for predict_real_probability")
        return None, {}, bundle


def analyze_image(image_path):
    try:
        # Read image (cv2) with PIL fallback
        grayscale = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if grayscale is None:
            try:
                img = Image.open(image_path).convert("L")
                grayscale = np.array(img)
            except Exception:
                logging.exception("Failed to read image with both cv2 and PIL: %s", image_path)
                return "Error: Could not read image", {}
        
        # Edge detection
        try:
            edges = cv2.Canny(grayscale, 60, 180)
            edge_ratio = float(np.count_nonzero(edges)) / max(grayscale.shape[0] * grayscale.shape[1], 1)
        except Exception:
            edge_ratio = 0.0
        
        # Model prediction
        try:
            model_probability, feature_dict, model_bundle = predict_real_probability(image_path)
        except Exception as e:
            logging.warning("Model prediction failed: %s", e)
            model_probability, feature_dict, model_bundle = None, {}, None
        
        # Decision logic
        metadata_info = {}
        
        # Simple heuristic: if model gives probability, use it
        if model_probability is not None:
            confidence = int(round(max(model_probability, 1.0 - model_probability) * 100))
            verdict = "Real" if model_probability >= 0.5 else "Fake"
            metadata_info.update({
                "confidence": confidence,
                "prediction_confidence": confidence,
                "model_probability": round(model_probability, 4),
                "analysis_summary": f"Model prediction: {verdict} ({confidence}%)"
            })
        else:
            # Fallback: use edge ratio heuristic
            confidence = 50  # Default confidence when model is unavailable
            verdict = "Needs Review"
            metadata_info.update({
                "confidence": confidence,
                "prediction_confidence": confidence,
                "analysis_summary": "Model unavailable; manual review recommended"
            })
        
        metadata_info.update({
            "edge_ratio": round(edge_ratio, 4),
            "result": verdict,
        })
        
        return verdict, metadata_info
    
    except Exception as exc:
        import traceback
        tb = traceback.format_exc()
        logging.exception("Image processing failed: %s", exc)
        # Save traceback to a file for the user to inspect
        try:
            with open("error_debug.txt", "a", encoding="utf-8") as f:
                f.write("\n=== analyze_image traceback ===\n")
                f.write(tb)
        except Exception:
            logging.exception("Failed to write error_debug.txt for analyze_image")
        # Also write into reports folder for easier retrieval
        try:
            rpt = os.path.join(app.config.get("REPORTS_FOLDER", "reports"), "error_debug.txt")
            with open(rpt, "a", encoding="utf-8") as f:
                f.write("\n=== analyze_image traceback ===\n")
                f.write(tb)
        except Exception:
            logging.exception("Failed to write reports/error_debug.txt for analyze_image")
        return "Error: Image processing failed", {}


def generate_pdf_report(report_path, filename, result, metadata):
    try:
        c = canvas.Canvas(report_path, pagesize=letter)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, 750, "Fake Transaction Detection Report")
        c.setFont("Helvetica", 12)
        c.drawString(100, 730, f"File Name: {filename}")
        c.drawString(100, 710, f"Result: {result}")

        y_position = 690
        for key, value in metadata.items():
            c.drawString(100, y_position, f"{key}: {value}")
            y_position -= 18
            if y_position < 50:
                c.showPage()
                y_position = 750

        c.save()
    except Exception as exc:
        logging.exception("PDF report generation failed: %s", exc)


@app.route("/")
def home():
    return "Welcome to Fake Transaction Detector API!"


@app.route("/upload", methods=["POST"])
def upload_image():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file found"}), 400

        file = request.files["file"]
        if not file.filename:
            return jsonify({"error": "No file selected"}), 400

        original_name = secure_filename(file.filename)
        file_ext = os.path.splitext(original_name)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            return jsonify({"error": "Unsupported file type. Upload PNG/JPG/JPEG/WEBP/BMP only."}), 400

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_str = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
        unique_filename = f"{timestamp}_{random_str}{file_ext}"
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
        file.save(file_path)

        if not os.path.exists(file_path):
            return jsonify({"error": "File was not saved properly!"}), 500

        result, metadata_info = analyze_image(file_path)

        report_filename = f"{timestamp}_{random_str}.pdf"
        report_path = os.path.join(app.config["REPORTS_FOLDER"], report_filename)
        generate_pdf_report(report_path, file.filename, result, metadata_info)

        response = make_response(jsonify({
            "filename": unique_filename,
            "result": result,
            "confidence": metadata_info.get("confidence", 0),
            "summary": metadata_info.get("analysis_summary", ""),
            "metadata": metadata_info,
            "report_url": url_for("download_report", filename=report_filename, _external=True),
        }))
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    except Exception as exc:
        logging.exception("Processing failed: %s", exc)
        return jsonify({"error": f"Processing Failed: {exc}"}), 500


@app.route("/download_report/<filename>")
def download_report(filename):
    report_path = os.path.join(app.config["REPORTS_FOLDER"], filename)
    if os.path.exists(report_path):
        return send_file(report_path, as_attachment=True)
    return jsonify({"error": "Report not found"}), 404


if __name__ == "__main__":
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    threaded = os.getenv("SERVER_THREADED", "False").lower() == "true"
    use_reloader = os.getenv("SERVER_USE_RELOADER", "False").lower() == "true"
    
    print(f"Starting Flask server on {host}:{port}")
    print(f"DEBUG mode: {debug}")
    print(f"Threaded: {threaded}")
    print(f"Use Reloader: {use_reloader}")
    
    app.run(debug=debug, threaded=threaded, use_reloader=use_reloader, host=host, port=port)
