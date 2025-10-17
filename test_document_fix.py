#!/usr/bin/env python3
"""
测试文档API修复
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_document_api():
    # 1. 登录获取token
    print("1. 登录...")
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
    
    # 2. 获取客户列表
    print("\n2. 获取客户列表...")
    customers_response = requests.get(
        f"{BASE_URL}/api/customers/",
        headers=headers
    )
    
    if customers_response.status_code != 200:
        print(f"❌ 获取客户列表失败: {customers_response.status_code}")
        return False
    
    customers = customers_response.json()["items"]
    if not customers:
        print("⚠️  没有客户数据")
        return True
    
    customer_id = customers[0]["id"]
    print(f"✅ 找到客户: {customers[0]['name']} (ID: {customer_id})")
    
    # 3. 获取客户文档 - 这是之前失败的API
    print(f"\n3. 获取客户文档 (customer_id={customer_id})...")
    documents_response = requests.get(
        f"{BASE_URL}/api/documents/customer/{customer_id}",
        headers=headers
    )
    
    if documents_response.status_code != 200:
        print(f"❌ 获取文档失败: {documents_response.status_code}")
        print(documents_response.text)
        return False
    
    documents = documents_response.json()
    print(f"✅ 成功获取 {len(documents)} 个文档")
    
    # 4. 检查文档数据结构
    if documents:
        doc = documents[0]
        print(f"\n4. 检查文档数据结构...")
        print(f"   - file_name: {doc.get('file_name')}")
        print(f"   - created_at: {doc.get('created_at')}")
        print(f"   - uploaded_at: {doc.get('uploaded_at')}")  # 这个字段之前缺失
        
        if 'uploaded_at' in doc:
            print("✅ uploaded_at 字段存在!")
            return True
        else:
            print("❌ uploaded_at 字段仍然缺失")
            return False
    else:
        print("⚠️  客户没有文档")
        return True

if __name__ == "__main__":
    print("=" * 60)
    print("测试文档API修复")
    print("=" * 60)
    
    try:
        success = test_document_api()
        print("\n" + "=" * 60)
        if success:
            print("✅ 测试通过!")
        else:
            print("❌ 测试失败!")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()

