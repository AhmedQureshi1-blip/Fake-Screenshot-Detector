@echo off
REM Fake Payment Screenshot Detector - Startup Script

echo ================================
echo Fake Payment Screenshot Detector
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    exit /b 1
)

echo [1/5] Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install Python dependencies
    exit /b 1
)

echo.
echo [2/5] Checking for Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: Node.js not found. Skipping React frontend setup.
    echo To set up the frontend, install Node.js from https://nodejs.org/
    goto skip_frontend
)

echo.
echo [3/5] Installing React dependencies...
cd fake-screenshot-detector
npm install
if errorlevel 1 (
    echo ERROR: Failed to install React dependencies
    cd ..
    exit /b 1
)
cd ..

:skip_frontend

echo.
echo [4/5] Verifying environment...
if not exist .env (
    echo .env file created successfully
) else (
    echo .env file already exists
)

if not exist uploads (
    mkdir uploads
    echo Created uploads folder
)

if not exist reports (
    mkdir reports
    echo Created reports folder
)

if not exist models (
    echo WARNING: models folder not found
)

echo.
echo [5/5] Starting Flask server...
echo.
echo Server will start on http://localhost:5000
echo.
python server.py
