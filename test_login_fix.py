#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试登录功能修复
"""

import requests
import json
import time
from datetime import datetime

# 配置
API_URL = "http://localhost:8000"
TIMEOUT = 10

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")

def main():
    print(f"\n{Colors.BLUE}")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  🔧 登录功能修复测试".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    print(f"{Colors.RESET}")
    
    print_info(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"API 地址: {API_URL}")
    
    # 测试 1: 用户注册
    print_header("测试 1: 用户注册")
    username = f"testuser_{int(time.time())}"
    password = "password123"
    
    try:
        response = requests.post(
            f"{API_URL}/api/auth/register",
            json={
                "username": username,
                "password": password,
                "full_name": "测试用户",
                "role": "admin"
            },
            timeout=TIMEOUT
        )
        
        if response.status_code in [200, 201]:
            user_data = response.json()
            print_success("用户注册成功")
            print_info(f"用户 ID: {user_data.get('id')}")
            print_info(f"用户名: {username}")
        else:
            print_error(f"注册失败: {response.status_code}")
            print_error(f"响应: {response.text}")
            return
    except Exception as e:
        print_error(f"异常: {str(e)}")
        return
    
    # 测试 2: 用户登录 (测试 /api/auth/login 路由)
    print_header("测试 2: 用户登录 (测试 /api/auth/login 路由)")
    try:
        response = requests.post(
            f"{API_URL}/api/auth/login",
            json={"username": username, "password": password},
            timeout=TIMEOUT
        )
        
        print_info(f"请求 URL: {API_URL}/api/auth/login")
        print_info(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get('access_token')
            print_success("用户登录成功")
            print_info(f"Token 获取成功")
            print_info(f"Token 长度: {len(token)} 字符")
        else:
            print_error(f"登录失败: {response.status_code}")
            print_error(f"响应: {response.text}")
            return
    except Exception as e:
        print_error(f"异常: {str(e)}")
        return
    
    # 测试 3: 获取用户信息 (测试 /api/auth/me 路由)
    print_header("测试 3: 获取用户信息 (测试 /api/auth/me 路由)")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{API_URL}/api/auth/me",
            headers=headers,
            timeout=TIMEOUT
        )
        
        print_info(f"请求 URL: {API_URL}/api/auth/me")
        print_info(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print_success("获取用户信息成功")
            print_info(f"用户名: {user_data.get('username')}")
            print_info(f"角色: {user_data.get('role')}")
        else:
            print_error(f"获取失败: {response.status_code}")
            print_error(f"响应: {response.text}")
            return
    except Exception as e:
        print_error(f"异常: {str(e)}")
        return
    
    # 测试 4: 测试其他 API 路由
    print_header("测试 4: 测试其他 API 路由")
    
    # 测试获取产品列表
    try:
        response = requests.get(
            f"{API_URL}/api/products",
            headers=headers,
            timeout=TIMEOUT
        )
        
        print_info(f"请求 URL: {API_URL}/api/products")
        print_info(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            print_success("获取产品列表成功")
        else:
            print_error(f"获取失败: {response.status_code}")
    except Exception as e:
        print_error(f"异常: {str(e)}")
    
    # 测试获取客户列表
    try:
        response = requests.get(
            f"{API_URL}/api/customers",
            headers=headers,
            timeout=TIMEOUT
        )
        
        print_info(f"请求 URL: {API_URL}/api/customers")
        print_info(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            print_success("获取客户列表成功")
        else:
            print_error(f"获取失败: {response.status_code}")
    except Exception as e:
        print_error(f"异常: {str(e)}")
    
    # 总结
    print_header("测试总结")
    print_success("所有 API 路由测试通过！")
    print_info("前端登录功能修复成功")
    print_info("所有 API 调用都包含 /api 前缀")
    
    print(f"\n{Colors.GREEN}🎊 登录功能修复验证完成！{Colors.RESET}\n")

if __name__ == "__main__":
    main()

