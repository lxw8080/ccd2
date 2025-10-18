#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Start CCD2 FastAPI backend
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    # Get backend path
    project_root = Path(__file__).parent
    backend_path = project_root / "backend"
    
    print("="*60)
    print("CCD2 Backend Startup")
    print("="*60)
    
    # Change to backend directory
    os.chdir(backend_path)
    
    print("\nBackend path: {}".format(backend_path))
    print("Installing/updating dependencies...")
    
    # Upgrade pip
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--upgrade", "pip"], 
                   capture_output=True)
    
    # Install requirements
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt"], 
                   capture_output=True)
    
    print("Starting FastAPI server...")
    print("Backend will run on: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("\n" + "="*60)
    print("Press Ctrl+C to stop\n")
    
    # Start uvicorn
    subprocess.run([sys.executable, "-m", "uvicorn", "app.main:app",
                    "--host", "0.0.0.0", "--port", "8000", "--reload"])

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBackend stopped")
        sys.exit(0)
    except Exception as e:
        print("Error: {}".format(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)
