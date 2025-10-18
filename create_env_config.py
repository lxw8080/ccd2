#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

# Set stdout encoding to utf-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

backend_path = r"C:\Users\16094\Desktop\项目\ccd2\backend\.env"

env_content = """DATABASE_URL=postgresql://flask_user:flask_password@115.190.29.10:5433/ccd_db_new
API_KEY=lxw8025031
LOG_FILE_PATH=logs/server.log
FLASK_ENV=development
DEBUG=True
APP_NAME=客户资料收集系统
APP_VERSION=1.0.0
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
STORAGE_TYPE=local
REDIS_URL=redis://localhost:6379/0
LOG_LEVEL=INFO
"""

with open(backend_path, 'w', encoding='utf-8') as f:
    f.write(env_content)

print("SUCCESS: .env file created")
print(f"Path: {backend_path}")
