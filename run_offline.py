#!/usr/bin/env python3
"""
Offline runner for Azimuth Converter App
This script runs the Streamlit app in offline mode for mobile devices
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = ['streamlit', 'pandas', 'numpy']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install " + " ".join(missing_packages))
        return False
    return True

def run_offline():
    """Run the Streamlit app in offline mode"""
    if not check_dependencies():
        return
    
    # Get the directory of this script
    app_dir = Path(__file__).parent
    app_file = app_dir / "app.py"
    
    if not app_file.exists():
        print("Error: app.py not found!")
        return
    
    print("🧭 Starting Azimuth Converter in offline mode...")
    print("📱 Optimized for mobile devices")
    print("🌐 Access at: http://localhost:8501")
    print("🔌 No internet connection required")
    print("\n" + "="*50)
    
    # Run Streamlit with offline-optimized settings
    cmd = [
        sys.executable, "-m", "streamlit", "run", str(app_file),
        "--server.address", "0.0.0.0",
        "--server.port", "8501",
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false",
        "--runner.magicEnabled", "false"
    ]
    
    try:
        subprocess.run(cmd, cwd=app_dir)
    except KeyboardInterrupt:
        print("\n\n👋 App stopped. Have a great day!")

if __name__ == "__main__":
    run_offline()