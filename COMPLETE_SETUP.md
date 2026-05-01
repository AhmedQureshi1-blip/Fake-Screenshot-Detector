# 🧾 Fake Payment Screenshot Detector - Complete Setup Guide

## ✨ Project Overview

**Fake Payment Screenshot Detector** is an AI-powered web application that detects forged or tampered payment transaction screenshots using advanced image forensics, machine learning, and OCR technology.

### Key Capabilities
- ✅ Image forensics (ELA, edge detection)
- ✅ AI-based classification (Real vs. Fake)
- ✅ OCR text extraction (Tesseract)
- ✅ Metadata analysis
- ✅ PDF report generation
- ✅ Dark mode support

---

## 🛠️ Prerequisites

### Required
- **Python 3.8+** - [Download](https://www.python.org/downloads/)
- **pip** (comes with Python)

### Recommended
- **Node.js 14+** (for React frontend) - [Download](https://nodejs.org/)
- **Tesseract OCR** (for text extraction) - [Download](https://github.com/UB-Mannheim/tesseract/wiki)

---

## 🚀 Quick Start

### Windows Users - One-Click Setup

```bash
start.bat
```

### Linux/Mac Users

```bash
chmod +x start.sh
./start.sh
```

### Manual Setup (All Platforms)

#### 1️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

#### 2️⃣ (Optional) Configure Tesseract

If you installed Tesseract in a non-default location, edit `.env`:

```ini
TESSERACT_CMD=C:\Your\Path\To\tesseract.exe
```

#### 3️⃣ Start Backend Server

```bash
python server.py
```

✅ Server running on: **http://localhost:5000**

#### 4️⃣ (Optional) Start React Frontend

In a new terminal:

```bash
cd fake-screenshot-detector
npm install
npm start
```

✅ Frontend running on: **http://localhost:3000**

---

## 📋 Environment Configuration (.env)

All settings are managed in the `.env` file. Key variables:

```ini
# Server
FLASK_ENV=production
FLASK_DEBUG=False
SERVER_HOST=0.0.0.0
SERVER_PORT=5000

# Folders
UPLOAD_FOLDER=uploads
REPORTS_FOLDER=reports
MAX_CONTENT_LENGTH=10485760

# Model
MODEL_PATH=models/payment_screenshot_model.joblib

# OCR (Tesseract)
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe

# Frontend
REACT_APP_API_URL=http://localhost:5000
REACT_APP_DEBUG=false
```

---

## 🧪 Testing the API

### Test 1: Upload and Analyze Image

```bash
curl -X POST http://localhost:5000/analyze \
  -F "file=@path/to/screenshot.png"
```

**Expected Response:**
```json
{
  "result": "Real",
  "real_probability": 0.95,
  "fake_probability": 0.05,
  "confidence": 95,
  "summary": "Analysis shows signs of authenticity...",
  "metadata": {
    "source": "screenshot",
    "dimensions": "1920x1080"
  },
  "report_filename": "analysis_20240101_120000.pdf"
}
```

### Test 2: Download PDF Report

```bash
curl http://localhost:5000/report/analysis_20240101_120000.pdf -o report.pdf
```

---

## 📊 Project Structure

```
📦 Fake-Payment-Screenshot-Detector
├── 📄 server.py                    # Main Flask backend
├── 📄 train_model.py               # ML model training
├── 📄 requirements.txt             # Python dependencies
├── 📄 .env                         # Configuration file ⭐
├── 📄 start.bat                    # Windows startup script
├── 📄 start.sh                     # Linux/Mac startup script
│
├── 📁 models/
│   └── payment_screenshot_model.joblib  # Trained ML model
│
├── 📁 uploads/                     # User uploads (auto-created)
├── 📁 reports/                     # Generated reports (auto-created)
│
├── 📁 fake-screenshot-detector/    # React Frontend
│   ├── 📄 package.json
│   ├── 📄 .env                     # Frontend config
│   └── 📁 src/
│       └── App.js                  # Main component
│
└── 📄 README.md                    # Original README
```

---

## ✅ Verification Checklist

- [ ] `.env` file created
- [ ] All Python packages installed: `pip list | grep -E "flask|opencv|scikit"`
- [ ] Model file exists: `models/payment_screenshot_model.joblib`
- [ ] Folders exist: `uploads/`, `reports/`
- [ ] Server starts without errors
- [ ] API responds on `http://localhost:5000/analyze`
- [ ] React frontend loads on `http://localhost:3000` (if Node.js installed)

---

## 🔧 Troubleshooting

### ❌ "Module not found: dotenv"
```bash
pip install python-dotenv
```

### ❌ "Tesseract not found"
1. Install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
2. Update `TESSERACT_CMD` in `.env`

### ❌ "Port 5000 already in use"
**Option A:** Change port in `.env`:
```ini
SERVER_PORT=5001
```

**Option B:** Kill the process:
- **Windows:** `netstat -ano | findstr :5000` then `taskkill /PID <PID>`
- **Linux/Mac:** `lsof -ti:5000 | xargs kill -9`

### ❌ "Model not loaded"
```bash
python train_model.py
```

### ❌ "CORS errors in browser"
Ensure `.env` has:
```ini
REACT_APP_API_URL=http://localhost:5000
```

### ❌ "No such file or directory: uploads"
```bash
mkdir uploads
mkdir reports
```

---

## 📡 API Documentation

### POST `/analyze`
Upload an image for analysis

**Request:**
```
Content-Type: multipart/form-data
Body: file (PNG/JPG/JPEG)
```

**Response:**
```json
{
  "result": "Real|Fake",
  "real_probability": 0-1,
  "fake_probability": 0-1,
  "confidence": 0-100,
  "summary": "string",
  "metadata": {...},
  "report_filename": "string"
}
```

### GET `/report/<filename>`
Download analysis PDF report

**Response:** PDF file

---

## 🎯 Features

| Feature | Status | Technology |
|---------|--------|-----------|
| Image Upload | ✅ | Flask multipart |
| ELA Analysis | ✅ | OpenCV |
| Edge Detection | ✅ | OpenCV |
| ML Classification | ✅ | scikit-learn |
| OCR | ✅ | Tesseract |
| Metadata Analysis | ✅ | PIL |
| PDF Reports | ✅ | ReportLab |
| React Frontend | ✅ | React.js |
| Dark Mode | ✅ | CSS |

---

## 📚 Learn More

- **Flask Documentation:** https://flask.palletsprojects.com/
- **scikit-learn:** https://scikit-learn.org/
- **Tesseract OCR:** https://github.com/UB-Mannheim/tesseract/wiki
- **React:** https://react.dev/

---

## 💾 Files Created/Modified

| File | Purpose |
|------|---------|
| `.env` | Environment configuration |
| `start.bat` | Windows startup script |
| `start.sh` | Linux/Mac startup script |
| `requirements.txt` | Updated with python-dotenv |
| `server.py` | Updated to use .env |
| `.gitignore` | Prevent sensitive files from git |
| `SETUP_INSTRUCTIONS.md` | Detailed setup guide |
| `fake-screenshot-detector/.env` | React frontend config |

---

## 🎉 Success!

If you see this output when running `python server.py`:

```
Starting Flask server on 0.0.0.0:5000
DEBUG mode: False
Threaded: False
Use Reloader: False
WARNING:werkzeug:Running on http://127.0.0.1:5000 (Press CTRL+C to quit)
```

✅ **Your project is ready to use!**

Access it at: **http://localhost:5000**

---

## 📞 Support

If you encounter issues:
1. Check `server.log` for error details
2. Review the Troubleshooting section above
3. Ensure all prerequisites are installed
4. Verify `.env` configuration

---

**Last Updated:** April 28, 2026
**Status:** ✅ Ready to Deploy
