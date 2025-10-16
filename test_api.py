#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 测试脚本
测试后端 API 的基本功能
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"

def print_header(text):
    print("\n" + "="*50)
    print(f"🧪 {text}")
    print("="*50)

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_warning(text):
    print(f"⚠️  {text}")

def test_api_availability():
    """测试 API 是否可用"""
    print_header("测试 1: 检查 API 可用性")
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code == 200:
            print_success(f"API 可用 (HTTP {response.status_code})")
            return True
        else:
            print_error(f"API 返回错误状态码: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"API 不可用: {e}")
        return False

def test_user_registration():
    """测试用户注册"""
    print_header("测试 2: 创建管理员用户")
    user_data = {
        "username": "admin",
        "password": "admin123",
        "full_name": "管理员",
        "role": "admin"
    }
    
    try:
        response = requests.post(
            f"{API_URL}/auth/register",
            json=user_data,
            timeout=5
        )
        if response.status_code in [200, 201]:
            user = response.json()
            print_success("用户创建成功")
            print(f"   用户 ID: {user.get('id', 'N/A')}")
            return user.get('id')
        else:
            print_warning(f"用户创建失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return None
    except Exception as e:
        print_warning(f"用户创建异常: {e}")
        return None

def test_user_login():
    """测试用户登录"""
    print_header("测试 3: 用户登录")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            json=login_data,
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print_success("登录成功")
            print(f"   Token: {token[:20]}...")
            return token
        else:
            print_warning(f"登录失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return None
    except Exception as e:
        print_warning(f"登录异常: {e}")
        return None

def test_create_product(token):
    """测试创建产品"""
    print_header("测试 4: 创建贷款产品")
    product_data = {
        "code": "PRODUCT001",
        "name": "个人消费贷",
        "description": "用于个人消费的贷款产品"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(
            f"{API_URL}/products",
            json=product_data,
            headers=headers,
            timeout=5
        )
        if response.status_code in [200, 201]:
            product = response.json()
            print_success("产品创建成功")
            print(f"   产品 ID: {product.get('id', 'N/A')}")
            return product.get('id')
        else:
            print_warning(f"产品创建失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return None
    except Exception as e:
        print_warning(f"产品创建异常: {e}")
        return None

def test_get_products(token):
    """测试获取产品列表"""
    print_header("测试 5: 获取产品列表")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{API_URL}/products",
            headers=headers,
            timeout=5
        )
        if response.status_code == 200:
            products = response.json()
            print_success("获取产品列表成功")
            if isinstance(products, list):
                print(f"   产品数量: {len(products)}")
            else:
                print(f"   响应: {products}")
            return True
        else:
            print_warning(f"获取产品列表失败: {response.status_code}")
            return False
    except Exception as e:
        print_warning(f"获取产品列表异常: {e}")
        return False

def main():
    """主测试函数"""
    print("\n" + "="*50)
    print("🚀 客户资料收集系统 - API 测试")
    print("="*50)
    
    # 测试 1: API 可用性
    if not test_api_availability():
        print_error("API 不可用，停止测试")
        sys.exit(1)
    
    # 测试 2: 用户注册
    user_id = test_user_registration()
    
    # 测试 3: 用户登录
    token = test_user_login()
    if not token:
        print_error("无法获取 token，停止测试")
        sys.exit(1)
    
    # 测试 4: 创建产品
    product_id = test_create_product(token)
    
    # 测试 5: 获取产品列表
    test_get_products(token)
    
    # 总结
    print("\n" + "="*50)
    print("✅ API 测试完成！")
    print("="*50)
    print(f"\n访问 API 文档: {BASE_URL}/docs")
    print(f"访问 ReDoc: {BASE_URL}/redoc")
    print()

if __name__ == "__main__":
    main()

