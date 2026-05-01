#!/usr/bin/env python3
"""
Project Verification Script
Checks if everything is properly configured for the Fake Payment Screenshot Detector
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists"""
    exists = os.path.exists(filepath)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {filepath}")
    return exists

def check_folder_exists(folderpath, description):
    """Check if a folder exists"""
    exists = os.path.isdir(folderpath)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {folderpath}")
    return exists

def check_env_var(varname, default=None):
    """Check if an environment variable is set"""
    value = os.getenv(varname, default)
    status = "✅" if value else "⚠️"
    print(f"{status} {varname}: {value if value else '(not set)'}")
    return bool(value)

def main():
    print("=" * 60)
    print("🔍 PROJECT VERIFICATION SCRIPT")
    print("Fake Payment Screenshot Detector")
    print("=" * 60)
    print()
    
    all_good = True
    
    # Check Python version
    print("📦 Python Environment:")
    print(f"  Python Version: {sys.version.split()[0]}")
    if sys.version_info < (3, 8):
        print("  ❌ Python 3.8+ required")
        all_good = False
    else:
        print("  ✅ Python version OK")
    print()
    
    # Check essential files
    print("📄 Essential Files:")
    all_good &= check_file_exists(".env", "Environment config")
    all_good &= check_file_exists("server.py", "Flask server")
    all_good &= check_file_exists("train_model.py", "Model training")
    all_good &= check_file_exists("requirements.txt", "Dependencies")
    print()
    
    # Check folders
    print("📁 Folders:")
    all_good &= check_folder_exists("uploads", "Uploads folder")
    all_good &= check_folder_exists("reports", "Reports folder")
    all_good &= check_folder_exists("models", "Models folder")
    print()
    
    # Check model file
    print("🤖 Machine Learning Model:")
    all_good &= check_file_exists("models/payment_screenshot_model.joblib", "Trained model")
    print()
    
    # Check environment variables (from .env)
    print("⚙️  Environment Configuration:")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        check_env_var("FLASK_ENV", "production")
        check_env_var("SERVER_PORT", "5000")
        check_env_var("UPLOAD_FOLDER", "uploads")
        check_env_var("REACT_APP_API_URL", "http://localhost:5000")
    except ImportError:
        print("❌ python-dotenv not installed")
        all_good = False
    print()
    
    # Check Python packages
    print("📦 Python Packages:")
    required_packages = [
        "flask",
        "flask_cors",
        "cv2",  # opencv-python
        "numpy",
        "pytesseract",
        "PIL",  # pillow
        "reportlab",
        "requests",
        "joblib",
        "sklearn",  # scikit-learn
        "dotenv",  # python-dotenv
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing_packages.append(package)
            all_good = False
    
    if missing_packages:
        print(f"\n  Install missing packages:")
        print(f"  pip install {' '.join(missing_packages)}")
    print()
    
    # Final status
    print("=" * 60)
    if all_good:
        print("✅ ALL CHECKS PASSED - Project is ready!")
        print()
        print("Next steps:")
        print("  1. python server.py")
        print("  2. Open http://localhost:5000 in your browser")
        return 0
    else:
        print("❌ Some checks failed - Please review the output above")
        print()
        print("Common fixes:")
        print("  • Install dependencies: pip install -r requirements.txt")
        print("  • Create folders: mkdir uploads reports")
        print("  • Check .env file exists: ls -la .env")
        return 1

if __name__ == "__main__":
    sys.exit(main())
