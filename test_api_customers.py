#!/usr/bin/env python3
"""
测试API客户数据
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    """测试API"""
    print("=" * 70)
    print("测试API客户数据")
    print("=" * 70)
    
    # 1. 登录
    print("\n🔐 登录...")
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    
    if response.status_code != 200:
        print(f"❌ 登录失败: {response.status_code}")
        print(response.text)
        return
    
    token = response.json()["access_token"]
    print(f"✅ 登录成功! Token: {token[:50]}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. 获取客户列表
    print("\n📋 获取客户列表...")
    response = requests.get(
        f"{BASE_URL}/api/customers?page=1&page_size=20",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ 获取客户列表失败: {response.status_code}")
        print(response.text)
        return
    
    data = response.json()
    print(f"✅ 获取客户列表成功!")
    print(f"   总数: {data.get('total', 0)}")
    print(f"   当前页: {data.get('page', 0)}")
    print(f"   每页数量: {data.get('page_size', 0)}")
    print(f"   客户数量: {len(data.get('items', []))}")
    
    if data.get('items'):
        print("\n📝 客户列表:")
        for customer in data['items']:
            print(f"   - {customer.get('customer_no')}: {customer.get('name')}")
            print(f"     电话: {customer.get('phone')}")
            print(f"     状态: {customer.get('status')}")
            print(f"     产品: {customer.get('product', {}).get('name', 'N/A')}")
            print()
    else:
        print("\n⚠️  客户列表为空!")
    
    # 3. 获取产品列表
    print("\n📦 获取产品列表...")
    response = requests.get(
        f"{BASE_URL}/api/products",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ 获取产品列表失败: {response.status_code}")
        print(response.text)
        return
    
    products = response.json()
    print(f"✅ 获取产品列表成功! (共 {len(products)} 个)")
    for product in products:
        print(f"   - {product.get('code')}: {product.get('name')}")

if __name__ == "__main__":
    test_api()

