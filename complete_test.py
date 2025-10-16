#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的系统测试脚本
测试后端 API 和前端集成
"""

import requests
import json
import time
from datetime import datetime

# 配置
API_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"
TIMEOUT = 10
FRONTEND_TIMEOUT = 15

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")

# 测试计数
tests_passed = 0
tests_failed = 0

def test_api_health():
    """测试 API 健康检查"""
    global tests_passed, tests_failed
    print_header("1. API 健康检查")
    
    try:
        response = requests.get(f"{API_URL}/health", timeout=TIMEOUT)
        if response.status_code == 200:
            print_success("API 健康检查通过")
            tests_passed += 1
            return True
        else:
            print_error(f"API 返回状态码: {response.status_code}")
            tests_failed += 1
            return False
    except Exception as e:
        print_error(f"API 连接失败: {str(e)}")
        tests_failed += 1
        return False

def test_user_registration():
    """测试用户注册"""
    global tests_passed, tests_failed
    print_header("2. 用户注册")

    user_data = {
        "username": f"testuser_{int(time.time())}",
        "password": "password123",
        "full_name": "测试用户",
        "role": "admin"
    }

    try:
        response = requests.post(
            f"{API_URL}/api/auth/register",
            json=user_data,
            timeout=TIMEOUT
        )

        if response.status_code in [200, 201]:
            data = response.json()
            print_success(f"用户注册成功")
            print_info(f"用户 ID: {data.get('id')}")
            print_info(f"用户名: {data.get('username')}")
            tests_passed += 1
            return data.get('username'), user_data['password']
        else:
            print_error(f"注册失败: {response.status_code}")
            print_error(f"响应: {response.text}")
            tests_failed += 1
            return None, None
    except Exception as e:
        print_error(f"注册异常: {str(e)}")
        tests_failed += 1
        return None, None

def test_user_login(username, password):
    """测试用户登录"""
    global tests_passed, tests_failed
    print_header("3. 用户登录")
    
    login_data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(
            f"{API_URL}/api/auth/login",
            json=login_data,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print_success("用户登录成功")
            print_info(f"Token: {token[:50]}...")
            tests_passed += 1
            return token
        else:
            print_error(f"登录失败: {response.status_code}")
            print_error(f"响应: {response.text}")
            tests_failed += 1
            return None
    except Exception as e:
        print_error(f"登录异常: {str(e)}")
        tests_failed += 1
        return None

def test_product_creation(token):
    """测试产品创建"""
    global tests_passed, tests_failed
    print_header("4. 产品创建")

    product_data = {
        "code": f"PRODUCT_{int(time.time())}",
        "name": "个人贷款产品",
        "description": "用于测试的个人贷款产品"
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            f"{API_URL}/api/products",
            json=product_data,
            headers=headers,
            timeout=TIMEOUT
        )

        if response.status_code in [200, 201]:
            data = response.json()
            print_success("产品创建成功")
            print_info(f"产品 ID: {data.get('id')}")
            print_info(f"产品名称: {data.get('name')}")
            tests_passed += 1
            return data.get('id')
        else:
            print_error(f"创建失败: {response.status_code}")
            print_error(f"响应: {response.text}")
            tests_failed += 1
            return None
    except Exception as e:
        print_error(f"创建异常: {str(e)}")
        tests_failed += 1
        return None

def test_product_list(token):
    """测试产品列表"""
    global tests_passed, tests_failed
    print_header("5. 产品列表查询")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(
            f"{API_URL}/api/products",
            headers=headers,
            timeout=TIMEOUT
        )

        if response.status_code == 200:
            data = response.json()
            # 处理两种可能的响应格式
            if isinstance(data, dict):
                products = data.get('items', [])
            else:
                products = data if isinstance(data, list) else []

            print_success(f"产品列表查询成功")
            print_info(f"产品总数: {len(products)}")
            for product in products[:3]:
                if isinstance(product, dict):
                    print_info(f"  - {product.get('name')} ({product.get('code')})")
            tests_passed += 1
            return True
        else:
            print_error(f"查询失败: {response.status_code}")
            tests_failed += 1
            return False
    except Exception as e:
        print_error(f"查询异常: {str(e)}")
        tests_failed += 1
        return False

def test_frontend_availability():
    """测试前端可用性"""
    global tests_passed, tests_failed
    print_header("6. 前端可用性")

    try:
        response = requests.get(
            f"{FRONTEND_URL}/test.html",
            timeout=FRONTEND_TIMEOUT
        )

        if response.status_code == 200:
            print_success("前端测试页面可访问")
            print_info(f"页面大小: {len(response.text)} 字节")
            tests_passed += 1
            return True
        else:
            print_error(f"前端返回状态码: {response.status_code}")
            tests_failed += 1
            return False
    except Exception as e:
        print_error(f"前端连接失败: {str(e)}")
        tests_failed += 1
        return False

def test_api_documentation():
    """测试 API 文档"""
    global tests_passed, tests_failed
    print_header("7. API 文档")
    
    try:
        response = requests.get(
            f"{API_URL}/docs",
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            print_success("API 文档可访问")
            print_info(f"文档页面大小: {len(response.text)} 字节")
            tests_passed += 1
            return True
        else:
            print_error(f"文档返回状态码: {response.status_code}")
            tests_failed += 1
            return False
    except Exception as e:
        print_error(f"文档连接失败: {str(e)}")
        tests_failed += 1
        return False

def main():
    """主测试函数"""
    global tests_passed, tests_failed
    
    print(f"\n{Colors.BLUE}")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  🎉 客户资料收集系统 - 完整测试".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    print(f"{Colors.RESET}")
    
    print_info(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"后端 API: {API_URL}")
    print_info(f"前端地址: {FRONTEND_URL}")
    
    # 执行测试
    test_api_health()
    username, password = test_user_registration()
    
    if username and password:
        token = test_user_login(username, password)
        
        if token:
            test_product_creation(token)
            test_product_list(token)
    
    test_frontend_availability()
    test_api_documentation()
    
    # 输出总结
    print_header("测试总结")
    total_tests = tests_passed + tests_failed
    pass_rate = (tests_passed / total_tests * 100) if total_tests > 0 else 0
    
    print_info(f"总测试数: {total_tests}")
    print_success(f"通过: {tests_passed}")
    print_error(f"失败: {tests_failed}")
    print_info(f"通过率: {pass_rate:.1f}%")
    
    if tests_failed == 0:
        print(f"\n{Colors.GREEN}🎊 所有测试通过！系统完全可用！{Colors.RESET}\n")
    else:
        print(f"\n{Colors.YELLOW}⚠️  有 {tests_failed} 个测试失败，请检查日志{Colors.RESET}\n")
    
    # 输出访问地址
    print_header("快速访问")
    print_info(f"前端测试页面: {FRONTEND_URL}/test.html")
    print_info(f"API 文档: {API_URL}/docs")
    print_info(f"后端首页: {API_URL}")

if __name__ == "__main__":
    main()

