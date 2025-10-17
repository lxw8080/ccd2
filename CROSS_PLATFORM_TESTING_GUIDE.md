# 🧪 Cross-Platform Testing Guide

This guide provides step-by-step instructions for testing the CCD2 system across different platforms and devices.

---

## 📋 Prerequisites

- Python 3.8+ installed
- Node.js 16+ installed (for frontend)
- PostgreSQL or SQLite database
- Network access between devices (for cross-device testing)

---

## 🖥️ Platform-Specific Setup

### Windows

1. **Install Dependencies**:
   ```powershell
   # Backend
   cd backend
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   
   # Frontend
   cd ..\frontend
   npm install
   ```

2. **Start Backend**:
   ```powershell
   cd backend
   .\venv\Scripts\activate
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Start Frontend**:
   ```powershell
   cd frontend
   npm run dev -- --host 0.0.0.0
   ```

4. **Verify Upload Directory**:
   ```powershell
   # Should be in project root
   dir uploads
   ```

### macOS

1. **Install Dependencies**:
   ```bash
   # Backend
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Frontend
   cd ../frontend
   npm install
   ```

2. **Start Backend**:
   ```bash
   cd backend
   source venv/bin/activate
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Start Frontend**:
   ```bash
   cd frontend
   npm run dev -- --host 0.0.0.0
   ```

4. **Verify Upload Directory**:
   ```bash
   # Should be in project root
   ls -la uploads
   ```

### Linux

1. **Install Dependencies**:
   ```bash
   # Backend
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Frontend
   cd ../frontend
   npm install
   ```

2. **Start Backend**:
   ```bash
   cd backend
   source venv/bin/activate
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Start Frontend**:
   ```bash
   cd frontend
   npm run dev -- --host 0.0.0.0
   ```

4. **Verify Upload Directory**:
   ```bash
   # Should be in project root
   ls -la uploads
   ```

---

## 🧪 Testing Procedures

### Test 1: File Upload with DateTime Validation

**Objective**: Verify that file uploads work without Pydantic validation errors.

**Steps**:
1. Login to the system
2. Navigate to a customer detail page
3. Upload a file (image or PDF)
4. Verify the upload succeeds without errors
5. Check that the uploaded file appears in the document list

**Expected Result**:
- ✅ File uploads successfully
- ✅ No Pydantic validation errors
- ✅ `uploaded_at` field shows the correct timestamp
- ✅ File appears in the document list

**Automated Test**:
```bash
python test_file_upload_fixes.py
```

---

### Test 2: File Viewing and Access

**Objective**: Verify that uploaded files can be viewed and downloaded.

**Steps**:
1. Upload a file (if not already done)
2. Click on the file to preview it
3. Verify the file preview loads correctly
4. Click the download button
5. Verify the file downloads successfully

**Expected Result**:
- ✅ File preview opens in modal
- ✅ Image files display correctly
- ✅ PDF files render in the viewer
- ✅ Download works correctly
- ✅ File content is intact

---

### Test 3: Cross-Device Access

**Objective**: Verify that files uploaded on one device can be accessed from another device.

**Setup**:
- Device A: Computer where files are uploaded
- Device B: Another computer or mobile device on the same network

**Steps on Device A**:
1. Start the backend and frontend servers
2. Note the IP address (e.g., `192.168.1.100`)
3. Login and upload a file
4. Note the customer and file details

**Steps on Device B**:
1. Open browser and navigate to `http://<Device-A-IP>:5173`
2. Login with the same credentials
3. Navigate to the same customer
4. Try to view the uploaded file
5. Try to download the file

**Expected Result**:
- ✅ Can access the application from Device B
- ✅ Can see the uploaded files
- ✅ Can preview the files
- ✅ Can download the files
- ✅ File URLs work correctly

---

### Test 4: Storage Location Verification

**Objective**: Verify that files are stored in the correct location.

**Steps**:
1. Upload a file through the web interface
2. Check the `uploads` directory in the project root
3. Verify the file structure: `uploads/{customer_id}/{document_type_code}/{filename}`
4. Verify the file exists and is readable

**Expected Result**:
- ✅ `uploads` directory exists in project root
- ✅ Files are organized by customer and document type
- ✅ Files are readable and not corrupted
- ✅ File paths in database match actual file locations

**Manual Verification**:
```bash
# Windows
dir /s uploads

# macOS/Linux
find uploads -type f -ls
```

---

### Test 5: Cross-Platform Path Handling

**Objective**: Verify that path handling works correctly across platforms.

**Steps**:
1. Upload files on Windows
2. Copy the database and uploads folder to macOS/Linux
3. Start the application on macOS/Linux
4. Verify files are accessible
5. Upload new files on macOS/Linux
6. Verify new files are accessible

**Expected Result**:
- ✅ Files uploaded on Windows work on macOS/Linux
- ✅ Files uploaded on macOS/Linux work on Windows
- ✅ No path-related errors in logs
- ✅ File URLs use forward slashes consistently

---

## 🔍 Troubleshooting

### Issue: Files not accessible after upload

**Symptoms**:
- Upload succeeds but file preview fails
- 404 errors when accessing files

**Solutions**:
1. Check that the backend is running
2. Verify the `uploads` directory exists
3. Check file permissions
4. Verify static file mounting in `main.py`

```bash
# Check if uploads directory exists
ls -la uploads

# Check backend logs for errors
# Look for static file mounting messages
```

### Issue: Pydantic validation error on upload

**Symptoms**:
- Upload fails with datetime validation error
- Error message mentions `uploaded_at` field

**Solutions**:
1. Verify database models have default datetime values
2. Check that `func.now()` is imported from `sqlalchemy.sql`
3. Restart the backend server

```python
# Verify in models
from sqlalchemy.sql import func

created_at = Column(DateTime(timezone=True), default=func.now())
```

### Issue: Cross-device access fails

**Symptoms**:
- Cannot access application from another device
- Connection refused errors

**Solutions**:
1. Ensure backend is running with `--host 0.0.0.0`
2. Ensure frontend is running with `--host 0.0.0.0`
3. Check firewall settings
4. Verify devices are on the same network

```bash
# Backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Frontend
npm run dev -- --host 0.0.0.0
```

### Issue: Upload directory in wrong location

**Symptoms**:
- Files uploaded but not found
- Different upload locations on different runs

**Solutions**:
1. Verify `UPLOAD_DIR` uses absolute path in `config.py`
2. Check that path calculation is correct
3. Restart the backend server

```python
# In backend/app/config.py
from pathlib import Path

UPLOAD_DIR: str = str(Path(__file__).parent.parent.parent / "uploads")
```

---

## 📊 Test Results Template

Use this template to document your test results:

```markdown
## Test Results - [Date] - [Platform]

**Platform**: Windows 10 / macOS 13 / Ubuntu 22.04
**Python Version**: 3.x.x
**Node Version**: 16.x.x

### Test 1: File Upload with DateTime Validation
- [ ] PASS / [ ] FAIL
- Notes: 

### Test 2: File Viewing and Access
- [ ] PASS / [ ] FAIL
- Notes: 

### Test 3: Cross-Device Access
- [ ] PASS / [ ] FAIL
- Notes: 

### Test 4: Storage Location Verification
- [ ] PASS / [ ] FAIL
- Notes: 

### Test 5: Cross-Platform Path Handling
- [ ] PASS / [ ] FAIL
- Notes: 

### Overall Result
- [ ] ALL TESTS PASSED
- [ ] SOME TESTS FAILED (see notes above)
```

---

## 🚀 Automated Testing

Run the automated test suite:

```bash
# Make sure backend is running first
cd backend
python -m uvicorn app.main:app --reload

# In another terminal
python test_file_upload_fixes.py
```

The test script will:
- ✅ Test datetime validation
- ✅ Test file upload
- ✅ Test file viewing
- ✅ Test storage location
- ✅ Test cross-platform paths

---

## 📝 Reporting Issues

If you encounter any issues during testing, please report them with:

1. **Platform**: Windows/macOS/Linux version
2. **Python Version**: `python --version`
3. **Error Message**: Full error message and stack trace
4. **Steps to Reproduce**: Detailed steps
5. **Expected vs Actual**: What you expected vs what happened
6. **Logs**: Relevant backend/frontend logs

---

## ✅ Sign-off Checklist

Before deploying to production, ensure:

- [ ] All tests pass on Windows
- [ ] All tests pass on macOS
- [ ] All tests pass on Linux
- [ ] Cross-device access works
- [ ] File uploads work correctly
- [ ] File viewing works correctly
- [ ] Storage location is correct
- [ ] No Pydantic validation errors
- [ ] Automated tests pass
- [ ] Documentation is up to date

---

## 📚 Additional Resources

- `FILE_UPLOAD_FIXES_REPORT.md` - Detailed fix documentation
- `QUICKSTART.md` - Quick start guide
- `DEPLOYMENT.md` - Deployment instructions
- `test_file_upload_fixes.py` - Automated test script

