#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试登录功能修复后的完整流程
"""

import requests
import json
import time

# 创建新用户
username = f'testuser_login_fix_{int(time.time())}'
password = 'password123'

print('='*70)
print('  登录功能修复后的完整测试')
print('='*70)

# 注册
print('\n1. 注册用户...')
response = requests.post(
    'http://localhost:8000/api/auth/register',
    json={
        'username': username,
        'password': password,
        'full_name': '测试用户',
        'role': 'admin'
    },
    timeout=10
)
print(f'   状态码: {response.status_code}')
if response.status_code not in [200, 201]:
    print(f'   错误: {response.text}')
    exit(1)
print(f'   ✅ 用户注册成功')

# 登录
print('\n2. 用户登录...')
response = requests.post(
    'http://localhost:8000/api/auth/login',
    json={'username': username, 'password': password},
    timeout=10
)
print(f'   状态码: {response.status_code}')
if response.status_code != 200:
    print(f'   错误: {response.text}')
    exit(1)

data = response.json()
token = data.get('access_token')
print(f'   Token: {token[:50]}...')
print(f'   ✅ 用户登录成功')

# 获取用户信息
print('\n3. 获取用户信息...')
response = requests.get(
    'http://localhost:8000/api/auth/me',
    headers={'Authorization': f'Bearer {token}'},
    timeout=10
)
print(f'   状态码: {response.status_code}')
if response.status_code != 200:
    print(f'   错误: {response.text}')
    exit(1)

user_data = response.json()
username_result = user_data.get('username')
role_result = user_data.get('role')
print(f'   用户名: {username_result}')
print(f'   角色: {role_result}')
print(f'   ✅ 获取用户信息成功')

print('\n' + '='*70)
print('✅ 所有测试通过！登录功能修复成功！')
print('='*70)

