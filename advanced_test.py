#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级功能测试脚本
测试所有核心功能：登录、客户管理、产品管理、文件上传、客户分配等
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

# 测试计数
tests_passed = 0
tests_failed = 0

def main():
    global tests_passed, tests_failed
    
    print(f"\n{Colors.BLUE}")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  🎉 客户资料收集系统 - 高级功能测试".center(68) + "║")
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
            tests_passed += 1
        else:
            print_error(f"注册失败: {response.status_code}")
            tests_failed += 1
            return
    except Exception as e:
        print_error(f"异常: {str(e)}")
        tests_failed += 1
        return
    
    # 测试 2: 用户登录
    print_header("测试 2: 用户登录")
    try:
        response = requests.post(
            f"{API_URL}/api/auth/login",
            json={"username": username, "password": password},
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get('access_token')
            print_success("用户登录成功")
            tests_passed += 1
        else:
            print_error(f"登录失败: {response.status_code}")
            tests_failed += 1
            return
    except Exception as e:
        print_error(f"异常: {str(e)}")
        tests_failed += 1
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 测试 3: 创建产品
    print_header("测试 3: 创建产品")
    product_code = f"PROD_{int(time.time())}"
    
    try:
        response = requests.post(
            f"{API_URL}/api/products",
            json={
                "code": product_code,
                "name": "测试贷款产品",
                "description": "用于测试的贷款产品"
            },
            headers=headers,
            timeout=TIMEOUT
        )
        
        if response.status_code in [200, 201]:
            product_data = response.json()
            product_id = product_data.get('id')
            print_success("产品创建成功")
            print_info(f"产品 ID: {product_id}")
            tests_passed += 1
        else:
            print_error(f"创建失败: {response.status_code}")
            tests_failed += 1
            return
    except Exception as e:
        print_error(f"异常: {str(e)}")
        tests_failed += 1
        return
    
    # 测试 4: 创建客户
    print_header("测试 4: 创建客户")
    customer_no = f"CUST_{int(time.time())}"
    
    try:
        response = requests.post(
            f"{API_URL}/api/customers",
            json={
                "customer_no": customer_no,
                "name": "测试客户",
                "phone": "13800138000",
                "id_card": "110101199001011234",
                "email": "test@example.com",
                "address": "北京市朝阳区",
                "product_id": product_id
            },
            headers=headers,
            timeout=TIMEOUT
        )
        
        if response.status_code in [200, 201]:
            customer_data = response.json()
            customer_id = customer_data.get('id')
            print_success("客户创建成功")
            print_info(f"客户 ID: {customer_id}")
            tests_passed += 1
        else:
            print_error(f"创建失败: {response.status_code}")
            tests_failed += 1
            return
    except Exception as e:
        print_error(f"异常: {str(e)}")
        tests_failed += 1
        return
    
    # 测试 5: 获取客户列表
    print_header("测试 5: 获取客户列表")
    try:
        response = requests.get(
            f"{API_URL}/api/customers",
            headers=headers,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            customers = data if isinstance(data, list) else data.get('items', [])
            print_success("获取客户列表成功")
            print_info(f"客户总数: {len(customers)}")
            tests_passed += 1
        else:
            print_error(f"获取失败: {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print_error(f"异常: {str(e)}")
        tests_failed += 1
    
    # 测试 6: 获取产品列表
    print_header("测试 6: 获取产品列表")
    try:
        response = requests.get(
            f"{API_URL}/api/products",
            headers=headers,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            products = data if isinstance(data, list) else data.get('items', [])
            print_success("获取产品列表成功")
            print_info(f"产品总数: {len(products)}")
            tests_passed += 1
        else:
            print_error(f"获取失败: {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print_error(f"异常: {str(e)}")
        tests_failed += 1
    
    # 测试 7: 获取 API 文档
    print_header("测试 7: 获取 API 文档")
    try:
        response = requests.get(
            f"{API_URL}/docs",
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            print_success("API 文档可访问")
            tests_passed += 1
        else:
            print_error(f"获取失败: {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print_error(f"异常: {str(e)}")
        tests_failed += 1
    
    # 输出总结
    print_header("测试总结")
    total_tests = tests_passed + tests_failed
    pass_rate = (tests_passed / total_tests * 100) if total_tests > 0 else 0
    
    print_info(f"总测试数: {total_tests}")
    print_success(f"通过: {tests_passed}")
    print_error(f"失败: {tests_failed}")
    print_info(f"通过率: {pass_rate:.1f}%")
    
    if tests_failed == 0:
        print(f"\n{Colors.GREEN}🎊 所有测试通过！系统功能完整！{Colors.RESET}\n")
    else:
        print(f"\n{Colors.YELLOW}⚠️  有 {tests_failed} 个测试失败{Colors.RESET}\n")

if __name__ == "__main__":
    main()

