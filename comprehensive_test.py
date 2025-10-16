#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的系统功能测试脚本
测试所有核心功能：登录、客户管理、产品管理、文件上传等
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

def print_test(text):
    print(f"{Colors.YELLOW}🧪 {text}{Colors.RESET}")

# 测试计数
tests_passed = 0
tests_failed = 0

def test_1_user_registration():
    """测试 1: 用户注册"""
    global tests_passed, tests_failed
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
            data = response.json()
            print_success("用户注册成功")
            print_info(f"用户 ID: {data.get('id')}")
            print_info(f"用户名: {data.get('username')}")
            tests_passed += 1
            return username, password
        else:
            print_error(f"注册失败: {response.status_code}")
            tests_failed += 1
            return None, None
    except Exception as e:
        print_error(f"异常: {str(e)}")
        tests_failed += 1
        return None, None

def test_2_user_login(username, password):
    """测试 2: 用户登录"""
    global tests_passed, tests_failed
    print_header("测试 2: 用户登录")
    
    try:
        response = requests.post(
            f"{API_URL}/api/auth/login",
            json={"username": username, "password": password},
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
            tests_failed += 1
            return None
    except Exception as e:
        print_error(f"异常: {str(e)}")
        tests_failed += 1
        return None

def test_3_get_user_info(token):
    """测试 3: 获取用户信息"""
    global tests_passed, tests_failed
    print_header("测试 3: 获取用户信息")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{API_URL}/api/auth/me",
            headers=headers,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("获取用户信息成功")
            print_info(f"用户名: {data.get('username')}")
            print_info(f"角色: {data.get('role')}")
            tests_passed += 1
            return data
        else:
            print_error(f"获取失败: {response.status_code}")
            tests_failed += 1
            return None
    except Exception as e:
        print_error(f"异常: {str(e)}")
        tests_failed += 1
        return None

def test_4_create_product(token):
    """测试 4: 创建产品"""
    global tests_passed, tests_failed
    print_header("测试 4: 创建产品")
    
    headers = {"Authorization": f"Bearer {token}"}
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
            data = response.json()
            print_success("产品创建成功")
            print_info(f"产品 ID: {data.get('id')}")
            print_info(f"产品名称: {data.get('name')}")
            tests_passed += 1
            return data.get('id')
        else:
            print_error(f"创建失败: {response.status_code}")
            tests_failed += 1
            return None
    except Exception as e:
        print_error(f"异常: {str(e)}")
        tests_failed += 1
        return None

def test_5_create_customer(token, product_id):
    """测试 5: 创建客户"""
    global tests_passed, tests_failed
    print_header("测试 5: 创建客户")

    headers = {"Authorization": f"Bearer {token}"}
    customer_no = f"CUST_{int(time.time())}"
    customer_name = f"客户_{int(time.time())}"

    try:
        response = requests.post(
            f"{API_URL}/api/customers",
            json={
                "customer_no": customer_no,
                "name": customer_name,
                "phone": "13800138000",
                "id_card": "110101199001011234",
                "product_id": product_id
            },
            headers=headers,
            timeout=TIMEOUT
        )

        if response.status_code in [200, 201]:
            data = response.json()
            print_success("客户创建成功")
            print_info(f"客户 ID: {data.get('id')}")
            print_info(f"客户编号: {data.get('customer_no')}")
            print_info(f"客户名称: {data.get('name')}")
            print_info(f"客户电话: {data.get('phone')}")
            tests_passed += 1
            return data.get('id')
        else:
            print_error(f"创建失败: {response.status_code}")
            print_error(f"响应: {response.text}")
            tests_failed += 1
            return None
    except Exception as e:
        print_error(f"异常: {str(e)}")
        tests_failed += 1
        return None

def test_6_get_customer_list(token):
    """测试 6: 获取客户列表"""
    global tests_passed, tests_failed
    print_header("测试 6: 获取客户列表")
    
    headers = {"Authorization": f"Bearer {token}"}
    
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
            for customer in customers[:3]:
                print_info(f"  - {customer.get('name')} ({customer.get('phone')})")
            tests_passed += 1
            return True
        else:
            print_error(f"获取失败: {response.status_code}")
            tests_failed += 1
            return False
    except Exception as e:
        print_error(f"异常: {str(e)}")
        tests_failed += 1
        return False

def test_7_get_product_list(token):
    """测试 7: 获取产品列表"""
    global tests_passed, tests_failed
    print_header("测试 7: 获取产品列表")
    
    headers = {"Authorization": f"Bearer {token}"}
    
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
            for product in products[:3]:
                print_info(f"  - {product.get('name')} ({product.get('code')})")
            tests_passed += 1
            return True
        else:
            print_error(f"获取失败: {response.status_code}")
            tests_failed += 1
            return False
    except Exception as e:
        print_error(f"异常: {str(e)}")
        tests_failed += 1
        return False

def main():
    """主测试函数"""
    global tests_passed, tests_failed
    
    print(f"\n{Colors.BLUE}")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  🎉 客户资料收集系统 - 完整功能测试".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    print(f"{Colors.RESET}")
    
    print_info(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"API 地址: {API_URL}")
    
    # 执行测试
    username, password = test_1_user_registration()

    if username and password:
        token = test_2_user_login(username, password)

        if token:
            test_3_get_user_info(token)
            product_id = test_4_create_product(token)
            if product_id:
                test_5_create_customer(token, product_id)
            test_6_get_customer_list(token)
            test_7_get_product_list(token)
    
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

