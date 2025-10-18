#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Start CCD2 Vite frontend
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def main():
    # Get frontend path
    project_root = Path(__file__).parent
    frontend_path = project_root / "frontend"
    
    print("="*60)
    print("CCD2 Frontend Startup")
    print("="*60)
    
    # Change to frontend directory
    os.chdir(frontend_path)
    
    print("\nFrontend path: {}".format(frontend_path))
    print("Checking npm packages...")
    
    # Check if node_modules exists
    node_modules = frontend_path / "node_modules"
    if not node_modules.exists():
        print("Installing npm packages (this may take a minute)...")
        subprocess.run(["npm", "install", "--quiet"], capture_output=True)
        print("[OK] npm packages installed")
    else:
        print("[OK] npm packages already installed")
    
    print("Starting Vite dev server...")
    print("Frontend will run on: http://localhost:5173")
    print("\n" + "="*60)
    print("Press Ctrl+C to stop\n")
    
    # Start npm dev
    subprocess.run(["npm", "run", "dev"])

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nFrontend stopped")
        sys.exit(0)
    except Exception as e:
        print("Error: {}".format(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)
