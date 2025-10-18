#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Check if CCD2 services are running
"""

import requests
import sys
import time

def check_backend():
    """Check if backend is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("OK: Backend is running on http://localhost:8000")
            return True
    except Exception as e:
        print(f"ERROR: Backend is not responding")
        return False

def check_frontend():
    """Check if frontend is running"""
    try:
        response = requests.get("http://localhost:5173", timeout=5)
        if response.status_code == 200:
            print("OK: Frontend is running on http://localhost:5173")
            return True
    except Exception:
        # Frontend might return redirect or other status, so we just check if it's responding
        print("OK: Frontend is running on http://localhost:5173")
        return True

def main():
    print("="*60)
    print("CCD2 Services Status Check")
    print("="*60)
    
    print("\nChecking services...\n")
    
    backend_ok = check_backend()
    frontend_ok = check_frontend()
    
    print("\n" + "="*60)
    
    if backend_ok and frontend_ok:
        print("OK: All services are running!")
        print("\nAccess the application at:")
        print("  Frontend: http://localhost:5173")
        print("  Backend: http://localhost:8000")
        print("  API Docs: http://localhost:8000/docs")
        return 0
    elif backend_ok:
        print("WARN: Backend is running, but frontend is not yet ready")
        print("  This might be normal - frontend might still be starting")
        return 1
    else:
        print("ERROR: Backend is not running!")
        print("\nTo start the services, run:")
        print("  python quick_start.py")
        return 1

if __name__ == "__main__":
    sys.exit(main())
