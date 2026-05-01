#!/bin/bash

# Fake Payment Screenshot Detector - Startup Script

echo "================================"
echo "Fake Payment Screenshot Detector"
echo "================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 is not installed"
    exit 1
fi

echo "[1/5] Installing Python dependencies..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install Python dependencies"
    exit 1
fi

echo ""
echo "[2/5] Checking for Node.js..."
if ! command -v node &> /dev/null; then
    echo "WARNING: Node.js not found. Skipping React frontend setup."
    echo "To set up the frontend, install Node.js from https://nodejs.org/"
else
    echo ""
    echo "[3/5] Installing React dependencies..."
    cd fake-screenshot-detector
    npm install
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install React dependencies"
        cd ..
        exit 1
    fi
    cd ..
fi

echo ""
echo "[4/5] Verifying environment..."
if [ ! -f .env ]; then
    echo "Creating .env file..."
else
    echo ".env file already exists"
fi

[ ! -d uploads ] && mkdir -p uploads && echo "Created uploads folder"
[ ! -d reports ] && mkdir -p reports && echo "Created reports folder"
[ ! -d models ] && echo "WARNING: models folder not found"

echo ""
echo "[5/5] Starting Flask server..."
echo ""
echo "Server will start on http://localhost:5000"
echo ""

python3 server.py
