import os
import re
import shutil
import tempfile
from pathlib import Path
from collections import Counter

import cv2
import joblib
import numpy as np
from PIL import ExifTags, Image, ImageChops

# Try to import pytesseract - make it optional
try:
    import pytesseract
    from pytesseract import Output
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    print("WARNING: pytesseract not available, OCR will be disabled")

from sklearn.ensemble import AdaBoostClassifier, ExtraTreesClassifier, GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, classification_report, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import LeaveOneOut, StratifiedKFold, cross_val_predict, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


ROOT = Path(__file__).resolve().parent
UPLOADS_DIR = ROOT / "uploads"
MODELS_DIR = ROOT / "models"
MODEL_PATH = MODELS_DIR / "payment_screenshot_model.joblib"
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}


SUSPICIOUS_TERMS = [
    "edited", "fake", "photoshop", "canva", "mockup", "recreated",
    "manipulated", "forged", "sample",
]
PAYMENT_TERMS = [
    "transaction successful", "payment successful", "payment received",
    "success", "paid", "completed", "received", "credited", "upi",
    "debited", "bank", "google pay", "phonepe", "paytm", "razorpay",
]


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


configure_tesseract_path()


def preprocess_for_ocr(image):
    grayscale = image.convert("L")
    enlarged = grayscale.resize((grayscale.width * 2, grayscale.height * 2))
    return enlarged.point(lambda pixel: 255 if pixel > 170 else 0)


def extract_text(image_path):
    if not TESSERACT_AVAILABLE:
        return ""
    
    try:
        image = Image.open(image_path)
        preprocessed = preprocess_for_ocr(image)
        
        try:
            primary_text = pytesseract.image_to_string(preprocessed, config="--oem 3 --psm 6")
        except Exception:
            primary_text = ""
        
        try:
            fallback_text = pytesseract.image_to_string(image, config="--oem 3 --psm 11")
        except Exception:
            fallback_text = ""
        
        primary_clean = " ".join(primary_text.split())
        fallback_clean = " ".join(fallback_text.split())
        return primary_clean if len(primary_clean) >= len(fallback_clean) else fallback_clean
    except Exception:
        return ""


def extract_ocr_confidence(image_path):
    if not TESSERACT_AVAILABLE:
        return 0.0, 0
    
    try:
        image = Image.open(image_path)
        preprocessed = preprocess_for_ocr(image)
        
        try:
            data = pytesseract.image_to_data(preprocessed, output_type=Output.DICT, config="--oem 3 --psm 6")
        except Exception:
            return 0.0, 0

        confidences = []
        word_count = 0
        for text, confidence in zip(data.get("text", []), data.get("conf", [])):
            if text and text.strip():
                word_count += 1
                try:
                    value = float(confidence)
                    if value >= 0:
                        confidences.append(value)
                except (TypeError, ValueError):
                    continue

        average_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        return average_confidence, word_count
    except Exception:
        return 0.0, 0


def compute_ela_stats(image_path, quality=90):
    try:
        original = Image.open(image_path).convert("RGB")

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            original.save(temp_path, "JPEG", quality=quality)
            recompressed = Image.open(temp_path).convert("RGB")
            diff = ImageChops.difference(original, recompressed)
            diff_array = np.asarray(diff, dtype=np.float32)
            return {
                "mean": float(diff_array.mean() / 255.0),
                "std": float(diff_array.std() / 255.0),
                "max": float(diff_array.max() / 255.0),
            }
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    except Exception:
        return {"mean": 0.0, "std": 0.0, "max": 0.0}


def extract_metadata(image_path):
    try:
        image = Image.open(image_path)
        exif_data = image.getexif()
        exif_count = len(exif_data) if exif_data else 0
        return {
            "exif_count": exif_count,
            "image_format": image.format or "",
            "image_width": image.width,
            "image_height": image.height,
            "has_exif": 1.0 if exif_count > 0 else 0.0,
            "png_flag": 1.0 if (image.format or "").lower() == "png" else 0.0,
        }
    except Exception:
        return {
            "exif_count": 0,
            "image_format": "",
            "image_width": 0,
            "image_height": 0,
            "has_exif": 0.0,
            "png_flag": 0.0,
        }


def image_entropy(gray_image):
    histogram = cv2.calcHist([gray_image], [0], None, [256], [0, 256]).flatten()
    histogram = histogram / max(histogram.sum(), 1.0)
    histogram = histogram[histogram > 0]
    if not len(histogram):
        return 0.0
    return float(-(histogram * np.log2(histogram)).sum())


def connected_component_count(binary_image):
    count, labels = cv2.connectedComponents(binary_image)
    return float(max(count - 1, 0))


def extract_feature_dict(image_path):
    try:
        gray_image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
        if gray_image is None:
            raise ValueError(f"Could not read image: {image_path}")

        image = Image.open(image_path)
        
        try:
            metadata = extract_metadata(image_path)
        except Exception as e:
            print(f"Warning: Metadata extraction failed: {e}")
            metadata = {
                "exif_count": 0,
                "image_format": "",
                "image_width": image.width,
                "image_height": image.height,
                "has_exif": 0.0,
                "png_flag": 0.0,
            }
        
        try:
            extracted_text = extract_text(image_path)
        except Exception as e:
            print(f"Warning: Text extraction failed: {e}")
            extracted_text = ""
        
        try:
            ocr_confidence, ocr_word_count = extract_ocr_confidence(image_path)
        except Exception as e:
            print(f"Warning: OCR confidence extraction failed: {e}")
            ocr_confidence, ocr_word_count = 0.0, 0
        
        try:
            ela_stats = compute_ela_stats(image_path)
        except Exception as e:
            print(f"Warning: ELA computation failed: {e}")
            ela_stats = {"mean": 0.0, "std": 0.0, "max": 0.0}

        edges = cv2.Canny(gray_image, 60, 180)
        edge_ratio = float(np.count_nonzero(edges)) / max(gray_image.shape[0] * gray_image.shape[1], 1)
        _, binary_otsu = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        text = " ".join(extracted_text.lower().split())
        amount_pattern = re.compile(r"(?:₹|rs\.?|inr)\s?\d[\d,]*(?:\.\d{1,2})?", re.IGNORECASE)
        transaction_patterns = [
            r"\btxn(?:id| no| number)?\b",
            r"\butr\b",
            r"\bref(?:erence)?\b",
            r"\border\s?id\b",
            r"\bupi\b",
            r"\bimps\b",
            r"\bneft\b",
            r"\btimestamp\b",
        ]
        date_patterns = [
            r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
            r"\b\d{1,2}:\d{2}(?:\s?[ap]m)?\b",
        ]

        chars = len(text)
        alpha_count = sum(char.isalpha() for char in text)
        digit_count = sum(char.isdigit() for char in text)
        alpha_ratio = alpha_count / max(chars, 1)
        digit_ratio = digit_count / max(chars, 1)
        payment_hits = sum(term in text for term in PAYMENT_TERMS)
        suspicious_hits = sum(term in text for term in SUSPICIOUS_TERMS)
        transaction_hits = sum(bool(re.search(pattern, text)) for pattern in transaction_patterns)
        date_hits = sum(bool(re.search(pattern, text)) for pattern in date_patterns)
        amount_hits = 1 if amount_pattern.search(text) else 0

        mean_brightness = float(gray_image.mean() / 255.0)
        std_brightness = float(gray_image.std() / 255.0)
        dark_ratio = float((gray_image < 60).mean())
        bright_ratio = float((gray_image > 220).mean())
        laplacian_var = float(cv2.Laplacian(gray_image, cv2.CV_64F).var())
        component_count = connected_component_count(binary_otsu)
        text_mask_ratio = float((binary_otsu > 0).mean())
        entropy = image_entropy(gray_image)

        feature_dict = {
            "image_width": float(metadata["image_width"]),
            "image_height": float(metadata["image_height"]),
            "aspect_ratio": float(metadata["image_width"] / max(metadata["image_height"], 1)),
            "file_size_kb": float(os.path.getsize(image_path) / 1024.0),
            "mean_brightness": mean_brightness,
            "std_brightness": std_brightness,
            "dark_ratio": dark_ratio,
            "bright_ratio": bright_ratio,
            "laplacian_var": laplacian_var,
            "component_count": component_count,
            "text_mask_ratio": text_mask_ratio,
            "edge_ratio": edge_ratio,
            "ela_mean": ela_stats["mean"],
            "ela_std": ela_stats["std"],
            "ela_max": ela_stats["max"],
            "ocr_confidence": float(ocr_confidence),
            "ocr_word_count": float(ocr_word_count),
            "ocr_char_count": float(chars),
            "alpha_ratio": float(alpha_ratio),
            "digit_ratio": float(digit_ratio),
            "payment_hits": float(payment_hits),
            "suspicious_hits": float(suspicious_hits),
            "transaction_hits": float(transaction_hits),
            "date_hits": float(date_hits),
            "amount_hits": float(amount_hits),
            "exif_count": float(metadata["exif_count"]),
            "has_exif": float(metadata["has_exif"]),
            "png_flag": float(metadata["png_flag"]),
            "entropy": float(entropy),
        }

        return feature_dict, extracted_text
    except Exception as e:
        print(f"Error in extract_feature_dict: {e}")
        raise


def load_dataset():
    rows = []
    labels = []
    for path in sorted(UPLOADS_DIR.iterdir()):
        if path.suffix.lower() not in ALLOWED_EXTENSIONS:
            continue
        label_name = path.stem.lower()
        if label_name.startswith("real"):
            label = 1
        elif label_name.startswith("fake"):
            label = 0
        else:
            continue

        feature_dict, _ = extract_feature_dict(path)
        rows.append(feature_dict)
        labels.append(label)

    return rows, labels


def build_candidates():
    return {
        "logistic_c01": Pipeline([
            ("scaler", StandardScaler()),
            ("model", LogisticRegression(max_iter=10000, class_weight="balanced", random_state=42, C=0.1)),
        ]),
        "logistic_c1": Pipeline([
            ("scaler", StandardScaler()),
            ("model", LogisticRegression(max_iter=10000, class_weight="balanced", random_state=42, C=1.0)),
        ]),
        "logistic_c3": Pipeline([
            ("scaler", StandardScaler()),
            ("model", LogisticRegression(max_iter=10000, class_weight="balanced", random_state=42, C=3.0)),
        ]),
        "svm_c1": Pipeline([
            ("scaler", StandardScaler()),
            ("model", SVC(probability=True, class_weight="balanced", kernel="rbf", C=1.0, gamma="auto", random_state=42)),
        ]),
        "svm_c2": Pipeline([
            ("scaler", StandardScaler()),
            ("model", SVC(probability=True, class_weight="balanced", kernel="rbf", C=2.0, gamma="scale", random_state=42)),
        ]),
        "svm_c5": Pipeline([
            ("scaler", StandardScaler()),
            ("model", SVC(probability=True, class_weight="balanced", kernel="rbf", C=5.0, gamma="scale", random_state=42)),
        ]),
        "forest_100": RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            class_weight="balanced_subsample",
            min_samples_leaf=1,
            max_depth=15,
        ),
        "forest_300": RandomForestClassifier(
            n_estimators=300,
            random_state=42,
            class_weight="balanced_subsample",
            min_samples_leaf=1,
            max_depth=20,
        ),
        "extra_trees_300": ExtraTreesClassifier(
            n_estimators=300,
            random_state=42,
            class_weight="balanced",
            min_samples_leaf=1,
            max_depth=20,
        ),
        "extra_trees_500": ExtraTreesClassifier(
            n_estimators=500,
            random_state=42,
            class_weight="balanced",
            min_samples_leaf=1,
            max_depth=25,
        ),
        "gboost": GradientBoostingClassifier(
            random_state=42,
            n_estimators=200,
            learning_rate=0.05,
            max_depth=5,
            min_samples_split=2,
            min_samples_leaf=1,
        ),
        "adaboost": AdaBoostClassifier(
            random_state=42,
            n_estimators=300,
            learning_rate=0.5,
        ),
    }


def train():
    MODELS_DIR.mkdir(exist_ok=True)
    features, labels = load_dataset()
    if len(features) < 4:
        raise RuntimeError("Need at least 4 labeled images to train a model.")

    class_counts = Counter(labels)
    print("Class distribution:", dict(class_counts))

    feature_names = list(features[0].keys())
    X = np.array([[row[name] for name in feature_names] for row in features], dtype=np.float32)
    y = np.array(labels, dtype=int)

    candidates = build_candidates()
    min_class_count = min(class_counts.values())
    if min_class_count >= 3 and len(y) >= 6:
        cv = StratifiedKFold(n_splits=min(5, min_class_count), shuffle=True, random_state=42)
    else:
        cv = LeaveOneOut()

    scores = {}
    fitted_models = {}
    threshold_by_model = {}

    for name, model in candidates.items():
        try:
            accuracy_scores = cross_val_score(model, X, y, cv=cv, scoring="accuracy")
            balanced_scores = cross_val_score(model, X, y, cv=cv, scoring="balanced_accuracy")
            f1_scores = cross_val_score(model, X, y, cv=cv, scoring="f1")

            scores[name] = {
                "accuracy": float(accuracy_scores.mean()),
                "balanced_accuracy": float(balanced_scores.mean()),
                "f1": float(f1_scores.mean()),
            }

            try:
                oof_probabilities = cross_val_predict(model, X, y, cv=cv, method="predict_proba")[:, 1]
                thresholds = np.linspace(0.2, 0.8, 61)
                best_threshold = 0.5
                best_threshold_f1 = -1.0
                for threshold in thresholds:
                    threshold_predictions = (oof_probabilities >= threshold).astype(int)
                    threshold_f1 = f1_score(y, threshold_predictions)
                    if threshold_f1 > best_threshold_f1:
                        best_threshold_f1 = threshold_f1
                        best_threshold = float(threshold)
                threshold_by_model[name] = best_threshold
            except Exception:
                threshold_by_model[name] = 0.5

            model.fit(X, y)
            fitted_models[name] = model
            print(
                f"{name}: accuracy={scores[name]['accuracy']:.3f}, "
                f"balanced={scores[name]['balanced_accuracy']:.3f}, f1={scores[name]['f1']:.3f}, "
                f"threshold={threshold_by_model[name]:.2f}"
            )
        except Exception as exc:
            print(f"{name}: failed -> {exc}")

    if not fitted_models:
        raise RuntimeError("No model trained successfully.")

    best_name = max(scores, key=lambda key: (scores[key]["balanced_accuracy"], scores[key]["f1"], scores[key]["accuracy"]))
    best_model = fitted_models[best_name]
    decision_threshold = threshold_by_model.get(best_name, 0.5)

    predictions = best_model.predict(X)
    training_accuracy = float(accuracy_score(y, predictions))
    training_balanced_accuracy = float(balanced_accuracy_score(y, predictions))
    print("\nBest model:", best_name)
    print("Training accuracy:", round(training_accuracy, 3))
    print("Training balanced accuracy:", round(training_balanced_accuracy, 3))
    print("Confusion matrix:\n", confusion_matrix(y, predictions))
    print(classification_report(y, predictions, target_names=["fake", "real"]))

    bundle = {
        "model": best_model,
        "feature_names": feature_names,
        "candidate_scores": scores,
        "best_model_name": best_name,
        "training_accuracy": training_accuracy,
        "training_balanced_accuracy": training_balanced_accuracy,
        "decision_threshold": decision_threshold,
        "label_map": {0: "Fake", 1: "Real"},
        "class_counts": dict(class_counts),
    }
    joblib.dump(bundle, MODEL_PATH)
    print(f"\nSaved model to {MODEL_PATH}")


if __name__ == "__main__":
    train()
