#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick start script for CCD2 project with PostgreSQL
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def main():
    project_root = Path(__file__).parent
    backend_path = str(project_root / "backend")
    frontend_path = str(project_root / "frontend")
    
    print("="*60)
    print("CCD2 Project Quick Start with PostgreSQL")
    print("="*60)
    
    # Step 1: Install backend dependencies
    print("\n[STEP 1] Installing backend dependencies...")
    print("Backend path:", backend_path)
    
    # Upgrade pip
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--upgrade", "pip"], 
                   cwd=backend_path, capture_output=False)
    
    # Install requirements
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt"], 
                   cwd=backend_path, capture_output=False)
    
    print("[OK] Backend dependencies installed")
    
    # Step 2: Start backend in background
    print("\n[STEP 2] Starting FastAPI backend...")
    print("Backend will run on: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    
    backend_cmd = [sys.executable, "-m", "uvicorn", "app.main:app", 
                   "--host", "0.0.0.0", "--port", "8000", "--reload"]
    
    backend_proc = subprocess.Popen(backend_cmd, cwd=backend_path)
    print("[OK] Backend started (PID: {})".format(backend_proc.pid))
    
    # Wait for backend to start
    print("Waiting for backend to initialize...")
    time.sleep(6)
    
    # Step 3: Install frontend dependencies if needed
    print("\n[STEP 3] Checking frontend dependencies...")
    frontend_node_modules = Path(frontend_path) / "node_modules"
    if not frontend_node_modules.exists():
        print("Installing npm packages (this may take a minute)...")
        subprocess.run(["npm", "install", "--quiet"], cwd=frontend_path)
        print("[OK] npm packages installed")
    else:
        print("[OK] npm packages already installed")
    
    # Step 4: Start frontend
    print("\n[STEP 4] Starting Vite frontend...")
    print("Frontend will run on: http://localhost:5173")
    print("\n" + "="*60)
    print("Both services are running!")
    print("="*60)
    print("Backend: http://localhost:8000")
    print("Frontend: http://localhost:5173")
    print("API Docs: http://localhost:8000/docs")
    print("="*60)
    print("\nPress Ctrl+C to stop services\n")
    
    frontend_cmd = ["npm", "run", "dev"]
    
    try:
        subprocess.run(frontend_cmd, cwd=frontend_path)
    except KeyboardInterrupt:
        print("\n\nShutting down services...")
        backend_proc.terminate()
        print("[OK] Services stopped")
        sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Error: {}".format(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)
