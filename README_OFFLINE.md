# Azimuth Converter - Offline Mobile App

A complete offline-capable coordinate conversion application for Android phones.

## 🚀 Quick Start for Android

### Method 1: Termux (Recommended)
1. Install **Termux** from F-Droid or Google Play Store
2. Run the installation script:
   ```bash
   bash install_android.sh
   ```
3. Copy all app files to your device
4. Run: `python run_offline.py`
5. Open browser: `http://localhost:8501`

### Method 2: Pydroid 3
1. Install **Pydroid 3** from Google Play Store
2. Install packages: streamlit, pandas, numpy
3. Copy `app.py` to Pydroid 3
4. Run the app

## 📱 Offline Features

### ✅ Works Without Internet
- All mathematical calculations (trigonometry)
- Coordinate conversions (azimuth to X,Y)
- Polygon area calculations
- DMS to decimal conversions
- File upload/download (CSV)
- Language switching (English/Spanish)
- All user interface elements

### 🧮 Core Functions
- Single point coordinate conversion
- Batch processing with CSV
- Polygon traversal (accumulating reference points)
- Closure error detection with color coding
- Mobile-friendly input formats (no special symbols needed)

## 📁 Files Included
- `app.py` - Main application
- `.streamlit/config.toml` - Configuration
- `run_offline.py` - Offline launcher
- `install_android.sh` - Android setup script
- `offline_setup.md` - Detailed setup guide

## 🔧 Technical Details
- Pure Python implementation
- No external API dependencies
- Uses only built-in math libraries
- Streamlit for mobile-optimized UI
- Self-contained package

## 💾 Storage Requirements
- App size: < 5MB
- Python + libraries: ~200MB
- Total installation: ~205MB

Perfect for field work, surveying, and navigation where internet access is limited or unavailable.