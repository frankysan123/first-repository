#!/bin/bash
# Android Installation Script for Azimuth Converter
# Run this in Termux on your Android device

echo "🧭 Azimuth Converter - Android Installation"
echo "================================================"
echo ""

# Update Termux packages
echo "📦 Updating Termux packages..."
pkg update -y && pkg upgrade -y

# Install Python and required tools
echo "🐍 Installing Python and tools..."
pkg install -y python git

# Install Python packages
echo "📚 Installing Python libraries..."
pip install --upgrade pip
pip install streamlit pandas numpy

# Create app directory
APP_DIR="$HOME/azimuth-converter"
echo "📁 Creating app directory at $APP_DIR"
mkdir -p "$APP_DIR"

# Instructions for user
echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Copy your app files (app.py, .streamlit folder) to: $APP_DIR"
echo "2. Navigate to the app: cd $APP_DIR"
echo "3. Run the app: python run_offline.py"
echo "4. Open browser and go to: http://localhost:8501"
echo ""
echo "📱 The app will work completely offline on your Android device!"
echo "🌐 No internet connection needed for calculations"