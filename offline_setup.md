# Offline Setup Guide

This application is designed to work offline on your Android device. Here's how to set it up:

## For Android Phones

### Option 1: Using Termux (Recommended)
1. Install Termux from F-Droid or Google Play Store
2. Update packages: `pkg update && pkg upgrade`
3. Install Python and required packages:
   ```bash
   pkg install python
   pip install streamlit pandas numpy
   ```
4. Copy the app files (app.py and .streamlit folder) to your phone
5. Navigate to the app directory: `cd /path/to/your/app`
6. Run the app: `streamlit run app.py --server.port 8501`
7. Open browser and go to: `localhost:8501`

### Option 2: Using Pydroid 3
1. Install Pydroid 3 from Google Play Store
2. Install required packages using pip in the app:
   - streamlit
   - pandas  
   - numpy
3. Copy app.py to Pydroid 3
4. Run the script

## Features that work offline:
- All coordinate calculations (uses built-in Python math)
- DMS to decimal conversion
- Polygon area calculation
- All user interface elements
- CSV file upload and download
- Language switching (English/Spanish)
- All input validation

## No internet required for:
- Core mathematical calculations
- File processing
- User interface
- Data storage and retrieval
- Language translation (built-in)

The app is completely self-contained with no external API calls or internet dependencies.