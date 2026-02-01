#!/bin/bash

# Quick start script for Rubik's Cube Solver Web App

echo "🧊 Starting Rubik's Cube Solver Web Application..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Start the server
echo ""
echo "🚀 Starting Flask server..."
echo "📍 Open http://localhost:5001 in your browser"
echo "   (Port 5001 avoids conflict with macOS AirPlay)"
echo ""

python app.py
