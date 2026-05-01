# 🧾 Fake Payment Screenshot Detector  
### Detecting Digital Payment Fraud with AI and Image Forensics

## 🔍 Overview

The **Fake Payment Screenshot Detector** is an AI-powered web-based tool designed to identify forged or tampered payment transaction screenshots. It uses image forensics, machine learning, and metadata analysis to verify the authenticity of payment proof images submitted during transactions.

Whether you're a business, freelancer, or platform that accepts digital payments, this tool helps protect against scams involving **edited screenshots** from apps like Google Pay, PhonePe, Paytm, or bank portals.

---

## ⚙️ Key Features

- ✅ **Image Forensics (ELA & Edge Detection)**  
  Detects manipulations using Error Level Analysis (ELA), edge inconsistencies, and compression anomalies.

- 🧠 **AI-Based Classification**  
  Trained ML model distinguishes between real and fake transaction images with high accuracy.

- 🕵️ **OCR Verification**  
  Extracts text using Tesseract OCR to check if the content (like transaction ID, amount, etc.) matches expected patterns.

- 📸 **Metadata Analysis**  
  Examines image EXIF data to determine the source (camera, WhatsApp, screenshots, etc.).

- 🖼️ **Image Preview + Drag & Drop UI**  
  Users can preview uploaded images with a clean, responsive drag-and-drop interface.

- 📄 **PDF Report Generation**  
  Generates downloadable forensic reports summarizing the analysis results.

- 🌓 **Dark Mode Support**  
  Fully styled for light and dark themes to enhance usability.

---

## 🛠️ Tech Stack

| Layer        | Technology Used               |
|--------------|-------------------------------|
| **Frontend** | React.js, Bootstrap           |
| **Backend**  | Flask / Express.js            |
| **AI/ML**    | TensorFlow, OpenCV, scikit-learn |
| **OCR**      | Tesseract                     |
| **Database** | MongoDB (for user tracking, history) |
| **Extras**   | Pillow, PDFKit/ReportLab, EXIFTools |

---

## 🚀 How It Works

1. **User uploads a payment screenshot**
2. **Backend processes the image**:
   - Performs ELA & Edge Detection
   - Extracts text using OCR
   - Checks metadata for social media signs (e.g. WhatsApp compression)
   - Uses an AI model to classify authenticity
3. **Results are displayed** with visual evidence
4. **PDF report** is generated and optionally sent via email

---

## 📂 Folder Structure

fake-payment-detector/
│
├── client/ # React frontend
│ ├── public/
│ └── src/
│ ├── components/
│ ├── pages/
│ └── App.js
│
├── server/ # Flask/Express backend
│ ├── models/
│ ├── utils/
│ ├── routes/
│ └── app.py / index.js
│
├── ml_model/ # ML training and saved model
│ ├── training.ipynb
│ └── model.h5 / model.pkl
│
├── README.md
└── requirements.txt / package.json


- 🔐 **User Login & History Tracking**
- ⛔ **Deepfake Nude Image Detection Add-on** *(in progress)*

---

## 💡 Use Cases

- Freelancers accepting UPI payments
- Online sellers verifying buyer payments
- Businesses preventing digital transaction scams
- Forensics and cybercrime investigators

---

## 👨‍💻 Author

Developed by: Ahmed Qureshi 
Feel free to reach out via  Email: ahmedak47qureshi@gmail.com for collaboration or suggestions!

---

## 📜 License

This project is licensed under the **MIT License** — feel free to use and contribute.

---

## 🙌 Contributions Welcome!

Found a bug? Want to add a feature? Contributions are welcome!  
Please fork the repository and submit a pull request.
