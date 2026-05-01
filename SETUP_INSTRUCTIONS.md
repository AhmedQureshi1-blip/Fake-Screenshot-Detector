# Setup Instructions - Fake Payment Screenshot Detector

## 📋 Prerequisites

- **Python 3.8+** - [Download](https://www.python.org/)
- **Node.js 14+** (optional, for React frontend) - [Download](https://nodejs.org/)
- **Tesseract OCR** (for text extraction) - [Download](https://github.com/UB-Mannheim/tesseract/wiki)

## 🚀 Quick Start

### Option 1: Automated Setup (Windows)

```bash
start.bat
```

### Option 2: Automated Setup (Linux/Mac)

```bash
chmod +x start.sh
./start.sh
```

### Option 3: Manual Setup

#### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

#### Step 2: Configure Tesseract (Windows only)

**Default Location:** `C:\Program Files\Tesseract-OCR\tesseract.exe`

If Tesseract is installed in a different location, update `.env`:
```
TESSERACT_CMD=C:\Your\Path\To\tesseract.exe
```

#### Step 3: Start Backend Server

```bash
python server.py
```

The server will start on `http://localhost:5000`

#### Step 4: Setup React Frontend (Optional)

```bash
cd fake-screenshot-detector
npm install
npm start
```

The frontend will open on `http://localhost:3000`

---

## 📁 .env Configuration

The `.env` file contains all configuration variables:

```ini
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=5000

# Folders
UPLOAD_FOLDER=uploads
REPORTS_FOLDER=reports
MAX_CONTENT_LENGTH=10485760

# Model Configuration
MODEL_PATH=models/payment_screenshot_model.joblib

# OCR Configuration (Tesseract)
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe

# Frontend API URL
REACT_APP_API_URL=http://localhost:5000
```

---

## 🧪 Testing the API

### Upload an Image and Analyze

```bash
curl -X POST http://localhost:5000/analyze \
  -F "file=@path/to/screenshot.png"
```

**Response:**
```json
{
  "result": "Real or Fake",
  "real_probability": 0.95,
  "fake_probability": 0.05,
  "confidence": 95,
  "summary": "Analysis summary",
  "metadata": {...}
}
```

### Generate PDF Report

```bash
curl http://localhost:5000/report/<filename> -o report.pdf
```

---

## 📊 Folder Structure

```
├── server.py                    # Main Flask server
├── train_model.py              # ML model training
├── models/
│   └── payment_screenshot_model.joblib  # Trained model
├── uploads/                    # Uploaded images (auto-created)
├── reports/                    # Generated PDF reports (auto-created)
├── .env                        # Configuration file
├── requirements.txt            # Python dependencies
└── fake-screenshot-detector/   # React frontend
    ├── src/
    │   └── App.js             # Main React component
    ├── package.json
    └── .env                    # Frontend config
```

---

## 🔧 Troubleshooting

### 1. **Tesseract Not Found**
```
ERROR: Tesseract executable not found. OCR will be disabled.
```

**Solution:**
- Install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
- Update `TESSERACT_CMD` in `.env` with the correct path

### 2. **Model Not Loaded**
```
ERROR: Failed to load trained model
```

**Solution:**
- Ensure `models/payment_screenshot_model.joblib` exists
- Run `python train_model.py` to train a new model

### 3. **Port Already in Use**
```
ERROR: Address already in use
```

**Solution:**
- Change `SERVER_PORT` in `.env` to an available port
- Or kill the process: `lsof -ti:5000 | xargs kill -9` (Mac/Linux)

### 4. **CORS Errors in React**
```
ERROR: No 'Access-Control-Allow-Origin' header
```

**Solution:**
- Ensure `REACT_APP_API_URL` in `fake-screenshot-detector/.env` matches the backend URL
- Check that Flask-CORS is enabled in `server.py`

---

## 📚 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/analyze` | Analyze an uploaded image |
| GET | `/report/<filename>` | Download generated PDF report |

---

## 🎯 Features

✅ Image forensics (ELA, edge detection)
✅ ML-based classification (Real vs Fake)
✅ OCR text extraction
✅ Metadata analysis
✅ PDF report generation
✅ Dark mode support

---

## 📝 License

This project is provided as-is for educational purposes.

---

## 💡 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the log file: `server.log`
3. Check error details: `error_debug.txt`
