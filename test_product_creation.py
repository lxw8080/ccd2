#!/usr/bin/env python3
"""
测试产品创建功能
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_product_creation():
    print("=" * 60)
    print("测试产品创建功能")
    print("=" * 60)
    
    # 1. 登录获取token
    print("\n1. 登录...")
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ 登录失败: {login_response.status_code}")
        print(login_response.text)
        return False
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ 登录成功")
    print(f"   Token: {token[:30]}...")
    
    # 2. 获取当前用户信息
    print("\n2. 获取当前用户信息...")
    me_response = requests.get(
        f"{BASE_URL}/api/auth/me",
        headers=headers
    )
    
    if me_response.status_code != 200:
        print(f"❌ 获取用户信息失败: {me_response.status_code}")
        print(me_response.text)
        return False
    
    user = me_response.json()
    print("✅ 用户信息:")
    print(f"   用户名: {user.get('username')}")
    print(f"   角色: {user.get('role')}")
    print(f"   是否激活: {user.get('is_active')}")
    
    # 3. 测试创建产品
    print("\n3. 创建产品...")
    
    # 生成唯一的产品代码
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    product_code = f"TEST_{timestamp}"
    
    product_data = {
        "code": product_code,
        "name": "测试贷款产品",
        "description": "这是一个测试产品",
        "is_active": True
    }
    
    print(f"   产品数据: {json.dumps(product_data, ensure_ascii=False, indent=2)}")
    
    create_response = requests.post(
        f"{BASE_URL}/api/products/",
        json=product_data,
        headers=headers
    )
    
    print(f"\n   响应状态码: {create_response.status_code}")
    print(f"   响应头: {dict(create_response.headers)}")
    
    if create_response.status_code == 201:
        product = create_response.json()
        print("✅ 产品创建成功!")
        print(f"   产品ID: {product.get('id')}")
        print(f"   产品代码: {product.get('code')}")
        print(f"   产品名称: {product.get('name')}")
        return True
    elif create_response.status_code == 401:
        print("❌ 认证失败 (401 Unauthorized)")
        print(f"   响应: {create_response.text}")
        
        # 检查token是否有效
        print("\n   调试信息:")
        print(f"   - Token存在: {bool(token)}")
        print(f"   - Authorization头: {headers.get('Authorization', 'N/A')[:50]}...")
        
        return False
    elif create_response.status_code == 403:
        print("❌ 权限不足 (403 Forbidden)")
        print(f"   响应: {create_response.text}")
        print(f"\n   用户角色 '{user.get('role')}' 可能没有 'product.manage' 权限")
        return False
    else:
        print(f"❌ 创建失败: {create_response.status_code}")
        print(f"   响应: {create_response.text}")
        return False

def test_with_curl():
    """生成curl命令供手动测试"""
    print("\n" + "=" * 60)
    print("手动测试命令")
    print("=" * 60)
    
    print("\n1. 登录获取token:")
    print("""
curl -X POST http://localhost:8000/api/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{"username":"admin","password":"admin123"}'
""")
    
    print("\n2. 使用token创建产品 (替换 YOUR_TOKEN):")
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    print(f"""
curl -X POST http://localhost:8000/api/products/ \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -d '{{"code":"TEST_{timestamp}","name":"测试产品","description":"测试","is_active":true}}'
""")

if __name__ == "__main__":
    success = test_product_creation()
    
    if not success:
        test_with_curl()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 测试通过!")
    else:
        print("❌ 测试失败!")
    print("=" * 60)

