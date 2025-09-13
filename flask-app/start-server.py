#!/usr/bin/env python3
"""
Startup script for the Flask AutoShop Management server
"""

import os
import sys
import subprocess

def main():
    """Main startup function"""
    print("🚗 Starting AutoShop Management Flask Server...")
    
    # Check if virtual environment exists
    venv_path = "venv"
    if not os.path.exists(venv_path):
        print("⚠️  Virtual environment not found. Creating one...")
        subprocess.run([sys.executable, "-m", "venv", venv_path])
        print("✅ Virtual environment created.")
    
    # Determine the correct activation script based on OS
    if os.name == 'nt':  # Windows
        activate_script = os.path.join(venv_path, "Scripts", "activate.bat")
        pip_cmd = os.path.join(venv_path, "Scripts", "pip.exe")
        python_cmd = os.path.join(venv_path, "Scripts", "python.exe")
    else:  # Unix/Linux/macOS
        activate_script = os.path.join(venv_path, "bin", "activate")
        pip_cmd = os.path.join(venv_path, "bin", "pip")
        python_cmd = os.path.join(venv_path, "bin", "python")
    
    # Install requirements if they don't exist
    try:
        subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully.")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies. Please check requirements.txt")
        return 1
    
    # Set environment variables
    os.environ.setdefault('FLASK_APP', 'app.py')
    os.environ.setdefault('FLASK_ENV', 'development')
    
    print("🌐 Starting Flask development server...")
    print("📍 Server will be available at: http://localhost:5000")
    print("📍 API Health Check: http://localhost:5000/api/health")
    print("🛑 Press Ctrl+C to stop the server")
    
    # Start the Flask application
    try:
        subprocess.run([python_cmd, "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user.")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Server failed to start: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 