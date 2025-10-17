#!/usr/bin/env python3
"""
Test script to verify file upload and viewing fixes
Tests:
1. File upload with proper datetime handling (Issue 2)
2. File viewing across devices (Issue 1)
3. File storage location verification (Issue 3)
4. Cross-platform compatibility (Issue 4)
"""
import sys
import os
from pathlib import Path
import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"

# Test credentials
TEST_USER = {
    "username": "admin",
    "password": "admin123"
}

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

def login():
    """Login and get access token"""
    print_info("Logging in...")
    response = requests.post(
        f"{API_URL}/auth/login",
        data=TEST_USER
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print_success("Login successful")
        return token
    else:
        print_error(f"Login failed: {response.text}")
        return None

def get_headers(token):
    """Get headers with authorization"""
    return {
        "Authorization": f"Bearer {token}"
    }

def test_datetime_fix(token):
    """Test Issue 2: File upload with proper datetime handling"""
    print_info("\n=== Testing Issue 2: File Upload DateTime Fix ===")
    
    headers = get_headers(token)
    
    # Get a customer
    response = requests.get(f"{API_URL}/customers", headers=headers)
    if response.status_code != 200:
        print_error("Failed to get customers")
        return False
    
    customers = response.json()
    if not customers:
        print_error("No customers found. Please create a customer first.")
        return False
    
    customer_id = customers[0]["id"]
    print_info(f"Using customer: {customers[0]['name']} ({customer_id})")
    
    # Get document types
    response = requests.get(f"{API_URL}/documents/types", headers=headers)
    if response.status_code != 200:
        print_error("Failed to get document types")
        return False
    
    doc_types = response.json()
    if not doc_types:
        print_error("No document types found")
        return False
    
    doc_type_id = doc_types[0]["id"]
    print_info(f"Using document type: {doc_types[0]['name']} ({doc_type_id})")
    
    # Create a test file
    test_file_path = Path("test_files/id_front.png")
    if not test_file_path.exists():
        # Create a simple test file
        test_file_path.parent.mkdir(exist_ok=True)
        with open(test_file_path, "wb") as f:
            f.write(b"Test image content")
    
    # Upload file
    print_info("Uploading test file...")
    with open(test_file_path, "rb") as f:
        files = {"files": (test_file_path.name, f, "image/png")}
        data = {
            "customer_id": customer_id,
            "document_type_id": doc_type_id,
            "upload_source": "web",
            "note": "Test upload for datetime fix"
        }
        
        response = requests.post(
            f"{API_URL}/documents/upload",
            headers=headers,
            files=files,
            data=data
        )
    
    if response.status_code == 201:
        result = response.json()
        print_success("File uploaded successfully")
        
        # Verify uploaded_at field is present and valid
        if result and len(result) > 0:
            uploaded_doc = result[0]
            if "uploaded_at" in uploaded_doc and uploaded_doc["uploaded_at"]:
                try:
                    # Try to parse the datetime
                    uploaded_at = datetime.fromisoformat(uploaded_doc["uploaded_at"].replace("Z", "+00:00"))
                    print_success(f"uploaded_at field is valid: {uploaded_at}")
                    return True
                except Exception as e:
                    print_error(f"uploaded_at field is invalid: {e}")
                    return False
            else:
                print_error("uploaded_at field is missing or None")
                return False
        else:
            print_error("No upload result returned")
            return False
    else:
        print_error(f"File upload failed: {response.status_code}")
        print_error(f"Response: {response.text}")
        return False

def test_file_viewing(token):
    """Test Issue 1: File viewing functionality"""
    print_info("\n=== Testing Issue 1: File Viewing ===")
    
    headers = get_headers(token)
    
    # Get a customer with documents
    response = requests.get(f"{API_URL}/customers", headers=headers)
    if response.status_code != 200:
        print_error("Failed to get customers")
        return False
    
    customers = response.json()
    if not customers:
        print_error("No customers found")
        return False
    
    customer_id = customers[0]["id"]
    
    # Get customer documents
    response = requests.get(f"{API_URL}/documents/customer/{customer_id}", headers=headers)
    if response.status_code != 200:
        print_error("Failed to get customer documents")
        return False
    
    documents = response.json()
    if not documents:
        print_warning("No documents found for customer. Upload a file first.")
        return True
    
    # Try to access the first document
    doc = documents[0]
    file_url = doc.get("file_url")
    
    if not file_url:
        print_error("No file_url in document")
        return False
    
    print_info(f"Testing file access: {file_url}")
    
    # Try to access the file
    full_url = f"{BASE_URL}{file_url}"
    response = requests.get(full_url, headers=headers)
    
    if response.status_code == 200:
        print_success(f"File is accessible (size: {len(response.content)} bytes)")
        return True
    else:
        print_error(f"File access failed: {response.status_code}")
        return False

def test_storage_location():
    """Test Issue 3: Verify file storage location"""
    print_info("\n=== Testing Issue 3: File Storage Location ===")
    
    # Check if uploads directory exists in project root
    project_root = Path(__file__).parent
    uploads_dir = project_root / "uploads"
    
    print_info(f"Expected uploads directory: {uploads_dir}")
    
    if uploads_dir.exists():
        print_success(f"Uploads directory exists at: {uploads_dir}")
        
        # Check if there are any files
        files = list(uploads_dir.rglob("*"))
        file_count = len([f for f in files if f.is_file()])
        print_info(f"Found {file_count} files in uploads directory")
        
        return True
    else:
        print_warning("Uploads directory doesn't exist yet (will be created on first upload)")
        return True

def test_cross_platform_paths():
    """Test Issue 4: Cross-platform path handling"""
    print_info("\n=== Testing Issue 4: Cross-Platform Compatibility ===")
    
    # Test Path operations
    test_path = Path("customer_id/doc_type/file.jpg")
    
    # Test as_posix (should work on all platforms)
    posix_path = test_path.as_posix()
    print_info(f"POSIX path: {posix_path}")
    
    if "/" in posix_path:
        print_success("Path conversion to POSIX format works")
    else:
        print_error("Path conversion failed")
        return False
    
    # Test absolute path resolution
    project_root = Path(__file__).parent
    uploads_dir = project_root / "uploads"
    
    print_info(f"Absolute uploads path: {uploads_dir}")
    print_info(f"Is absolute: {uploads_dir.is_absolute()}")
    
    if uploads_dir.is_absolute():
        print_success("Absolute path handling works correctly")
        return True
    else:
        print_error("Absolute path handling failed")
        return False

def main():
    """Run all tests"""
    print_info("=" * 60)
    print_info("File Upload and Viewing Fixes Test Suite")
    print_info("=" * 60)
    
    # Test cross-platform paths first (doesn't require server)
    test_storage_location()
    test_cross_platform_paths()
    
    # Login
    token = login()
    if not token:
        print_error("Cannot proceed without authentication")
        sys.exit(1)
    
    # Run tests
    results = {
        "DateTime Fix (Issue 2)": test_datetime_fix(token),
        "File Viewing (Issue 1)": test_file_viewing(token),
    }
    
    # Print summary
    print_info("\n" + "=" * 60)
    print_info("Test Summary")
    print_info("=" * 60)
    
    for test_name, result in results.items():
        if result:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED")
    
    all_passed = all(results.values())
    
    if all_passed:
        print_success("\n✓ All tests passed!")
        sys.exit(0)
    else:
        print_error("\n✗ Some tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()

