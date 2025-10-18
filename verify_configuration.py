#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verify CCD2 project configuration for PostgreSQL
"""

import os
import sys
from pathlib import Path

def check_file_exists(path, description):
    """Check if a file exists"""
    if Path(path).exists():
        print(f"OK: {description}")
        return True
    else:
        print(f"MISSING: {description} - {path}")
        return False

def check_env_file():
    """Check if .env file exists and contains required variables"""
    env_path = Path("backend/.env")
    if not env_path.exists():
        print("MISSING: backend/.env file")
        return False
    
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_vars = [
            'DATABASE_URL',
            'API_KEY',
            'FLASK_ENV'
        ]
        
        all_found = True
        for var in required_vars:
            if var in content:
                print(f"OK: {var} found in .env")
            else:
                print(f"MISSING: {var} not found in .env")
                all_found = False
        
        return all_found
    except Exception as e:
        print(f"ERROR: Failed to read .env file: {e}")
        return False

def check_config_file():
    """Check if config.py contains PostgreSQL settings"""
    config_path = Path("backend/app/config.py")
    if not config_path.exists():
        print("MISSING: backend/app/config.py")
        return False
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if '115.190.29.10' in content:
            print("OK: PostgreSQL address found in config.py")
            return True
        else:
            print("MISSING: PostgreSQL address not found in config.py")
            return False
    except Exception as e:
        print(f"ERROR: Failed to read config.py: {e}")
        return False

def check_startup_scripts():
    """Check if startup scripts exist"""
    scripts = [
        ('quick_start.py', 'Quick start script'),
        ('start_backend.py', 'Backend startup script'),
        ('start_frontend.py', 'Frontend startup script'),
        ('check_services.py', 'Service check script')
    ]
    
    all_found = True
    for script, description in scripts:
        if not check_file_exists(script, description):
            all_found = False
    
    return all_found

def check_documentation():
    """Check if documentation files exist"""
    docs = [
        ('POSTGRESQL_STARTUP_GUIDE.md', 'PostgreSQL startup guide'),
        ('PROJECT_STARTUP_SUMMARY.md', 'Project startup summary'),
        ('QUICK_REFERENCE.md', 'Quick reference'),
        ('COMPLETION_REPORT.md', 'Completion report')
    ]
    
    all_found = True
    for doc, description in docs:
        if not check_file_exists(doc, description):
            all_found = False
    
    return all_found

def check_project_structure():
    """Check if project structure is correct"""
    directories = [
        'backend',
        'backend/app',
        'backend/alembic',
        'frontend',
        'frontend/src'
    ]
    
    all_found = True
    for directory in directories:
        if Path(directory).exists():
            print(f"OK: Directory found - {directory}")
        else:
            print(f"MISSING: Directory not found - {directory}")
            all_found = False
    
    return all_found

def main():
    print("="*60)
    print("CCD2 Configuration Verification")
    print("="*60)
    print()
    
    print("[1] Checking project structure...")
    structure_ok = check_project_structure()
    print()
    
    print("[2] Checking environment configuration...")
    env_ok = check_env_file()
    print()
    
    print("[3] Checking application configuration...")
    config_ok = check_config_file()
    print()
    
    print("[4] Checking startup scripts...")
    scripts_ok = check_startup_scripts()
    print()
    
    print("[5] Checking documentation...")
    docs_ok = check_documentation()
    print()
    
    print("="*60)
    print("Verification Summary")
    print("="*60)
    
    results = {
        'Project Structure': structure_ok,
        'Environment Configuration': env_ok,
        'Application Configuration': config_ok,
        'Startup Scripts': scripts_ok,
        'Documentation': docs_ok
    }
    
    all_ok = all(results.values())
    
    for check, result in results.items():
        status = "OK" if result else "FAILED"
        print(f"{check}: {status}")
    
    print()
    
    if all_ok:
        print("SUCCESS: All configurations are correct!")
        print("\nYou can now start the project with:")
        print("  python quick_start.py")
        print("\nOr separately:")
        print("  python start_backend.py  (Terminal 1)")
        print("  python start_frontend.py (Terminal 2)")
        return 0
    else:
        print("ERROR: Some configuration checks failed!")
        print("\nPlease fix the missing items and try again.")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


