#!/usr/bin/env python3
"""
Test file upload functionality
"""
import requests
import io

# Login first
login_response = requests.post(
    'http://localhost:8000/api/auth/login',
    json={'username': 'admin', 'password': 'admin123'}
)

if login_response.status_code != 200:
    print(f"Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

token = login_response.json()['access_token']
print(f"✅ Login successful, token: {token[:20]}...")

# Create test image files (2 files for ID card front and back)
test_image1 = io.BytesIO(b'fake image content - front')
test_image1.name = 'id_front.jpg'

test_image2 = io.BytesIO(b'fake image content - back')
test_image2.name = 'id_back.jpg'

# Prepare upload data - multiple files with same key
files = [
    ('files', ('id_front.jpg', test_image1, 'image/jpeg')),
    ('files', ('id_back.jpg', test_image2, 'image/jpeg')),
]

data = {
    'customer_id': 'e0266c89-5f69-49da-8c71-d0e9c583ecc2',
    'document_type_id': '2c7981ff-d2bc-4c63-b08a-604baaf99de0',  # 身份证
}

headers = {
    'Authorization': f'Bearer {token}'
}

# Try to upload
print("\n📤 Attempting to upload file...")
upload_response = requests.post(
    'http://localhost:8000/api/documents/upload',
    files=files,
    data=data,
    headers=headers
)

print(f"Status code: {upload_response.status_code}")
print(f"Response: {upload_response.text}")

if upload_response.status_code in [200, 201]:
    print("✅ Upload successful!")
else:
    print("❌ Upload failed!")

