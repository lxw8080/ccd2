#!/usr/bin/env python3
"""
测试前端所需的所有API端点
"""
import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

class APITester:
    def __init__(self):
        self.token = None
        self.headers = {}
        self.issues = []
        
    def login(self) -> bool:
        """登录获取token"""
        print("\n" + "="*60)
        print("🔐 测试1: 用户登录")
        print("="*60)
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={"username": "admin", "password": "admin123"}
            )
            
            if response.status_code == 200:
                self.token = response.json()["access_token"]
                self.headers = {"Authorization": f"Bearer {self.token}"}
                print("✅ 登录成功")
                print(f"   Token: {self.token[:20]}...")
                return True
            else:
                print(f"❌ 登录失败: {response.status_code}")
                print(f"   响应: {response.text}")
                self.issues.append({
                    "api": "POST /api/auth/login",
                    "status": response.status_code,
                    "error": response.text
                })
                return False
        except Exception as e:
            print(f"❌ 登录异常: {e}")
            self.issues.append({
                "api": "POST /api/auth/login",
                "error": str(e)
            })
            return False
    
    def test_customers_list(self) -> bool:
        """测试客户列表API"""
        print("\n" + "="*60)
        print("👥 测试2: 客户列表")
        print("="*60)
        
        try:
            response = requests.get(
                f"{BASE_URL}/api/customers/",
                headers=self.headers,
                params={"skip": 0, "limit": 10}
            )
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                total = data.get("total", 0)
                
                print(f"✅ 客户列表获取成功")
                print(f"   总数: {total}")
                print(f"   当前页: {len(items)} 条记录")
                
                if items:
                    customer = items[0]
                    print(f"\n   示例客户:")
                    print(f"   - ID: {customer.get('id')}")
                    print(f"   - 姓名: {customer.get('name')}")
                    print(f"   - 电话: {customer.get('phone')}")
                    print(f"   - 状态: {customer.get('status')}")
                    print(f"   - 创建时间: {customer.get('created_at')}")
                
                return True
            else:
                print(f"❌ 客户列表获取失败: {response.status_code}")
                print(f"   响应: {response.text}")
                self.issues.append({
                    "api": "GET /api/customers/",
                    "status": response.status_code,
                    "error": response.text
                })
                return False
        except Exception as e:
            print(f"❌ 客户列表异常: {e}")
            self.issues.append({
                "api": "GET /api/customers/",
                "error": str(e)
            })
            return False
    
    def test_products_list(self) -> bool:
        """测试产品列表API"""
        print("\n" + "="*60)
        print("📦 测试3: 产品列表")
        print("="*60)
        
        try:
            response = requests.get(
                f"{BASE_URL}/api/products/",
                headers=self.headers,
                params={"skip": 0, "limit": 10}
            )
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                total = data.get("total", 0)
                
                print(f"✅ 产品列表获取成功")
                print(f"   总数: {total}")
                print(f"   当前页: {len(items)} 条记录")
                
                if items:
                    product = items[0]
                    print(f"\n   示例产品:")
                    print(f"   - ID: {product.get('id')}")
                    print(f"   - 名称: {product.get('name')}")
                    print(f"   - 类型: {product.get('product_type')}")
                    print(f"   - 价格: {product.get('price')}")
                    print(f"   - 状态: {product.get('status')}")
                
                return True
            else:
                print(f"❌ 产品列表获取失败: {response.status_code}")
                print(f"   响应: {response.text}")
                self.issues.append({
                    "api": "GET /api/products/",
                    "status": response.status_code,
                    "error": response.text
                })
                return False
        except Exception as e:
            print(f"❌ 产品列表异常: {e}")
            self.issues.append({
                "api": "GET /api/products/",
                "error": str(e)
            })
            return False
    
    def test_customer_documents(self, customer_id: str) -> bool:
        """测试客户文档API"""
        print("\n" + "="*60)
        print("📄 测试4: 客户文档列表")
        print("="*60)
        
        try:
            response = requests.get(
                f"{BASE_URL}/api/documents/customer/{customer_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                documents = response.json()
                
                print(f"✅ 客户文档获取成功")
                print(f"   文档数量: {len(documents)}")
                
                if documents:
                    doc = documents[0]
                    print(f"\n   示例文档:")
                    print(f"   - ID: {doc.get('id')}")
                    print(f"   - 文件名: {doc.get('file_name')}")
                    print(f"   - 类型: {doc.get('document_type')}")
                    print(f"   - 状态: {doc.get('status')}")
                    print(f"   - 上传时间: {doc.get('uploaded_at')}")
                    print(f"   - 创建时间: {doc.get('created_at')}")
                
                return True
            else:
                print(f"❌ 客户文档获取失败: {response.status_code}")
                print(f"   响应: {response.text}")
                self.issues.append({
                    "api": f"GET /api/documents/customer/{customer_id}",
                    "status": response.status_code,
                    "error": response.text
                })
                return False
        except Exception as e:
            print(f"❌ 客户文档异常: {e}")
            self.issues.append({
                "api": f"GET /api/documents/customer/{customer_id}",
                "error": str(e)
            })
            return False
    
    def test_dashboard_stats(self) -> bool:
        """测试仪表板统计API"""
        print("\n" + "="*60)
        print("📊 测试5: 仪表板统计")
        print("="*60)
        
        try:
            response = requests.get(
                f"{BASE_URL}/api/dashboard/stats",
                headers=self.headers
            )
            
            if response.status_code == 200:
                stats = response.json()
                
                print(f"✅ 仪表板统计获取成功")
                print(f"   客户总数: {stats.get('total_customers', 0)}")
                print(f"   产品总数: {stats.get('total_products', 0)}")
                print(f"   订单总数: {stats.get('total_orders', 0)}")
                print(f"   待处理订单: {stats.get('pending_orders', 0)}")
                
                return True
            else:
                print(f"❌ 仪表板统计获取失败: {response.status_code}")
                print(f"   响应: {response.text}")
                self.issues.append({
                    "api": "GET /api/dashboard/stats",
                    "status": response.status_code,
                    "error": response.text
                })
                return False
        except Exception as e:
            print(f"❌ 仪表板统计异常: {e}")
            self.issues.append({
                "api": "GET /api/dashboard/stats",
                "error": str(e)
            })
            return False
    
    def print_summary(self):
        """打印测试摘要"""
        print("\n" + "="*60)
        print("📋 测试摘要")
        print("="*60)
        
        if not self.issues:
            print("✅ 所有API测试通过！前端应该能正常工作。")
        else:
            print(f"❌ 发现 {len(self.issues)} 个问题:")
            for i, issue in enumerate(self.issues, 1):
                print(f"\n问题 {i}:")
                print(f"  API: {issue.get('api')}")
                if 'status' in issue:
                    print(f"  状态码: {issue.get('status')}")
                print(f"  错误: {issue.get('error')}")
        
        print("\n" + "="*60)

def main():
    print("🚀 开始测试前端所需的API端点")
    
    tester = APITester()
    
    # 1. 登录
    if not tester.login():
        print("\n⚠️  登录失败，无法继续测试")
        return
    
    # 2. 测试客户列表
    tester.test_customers_list()
    
    # 3. 测试产品列表
    tester.test_products_list()
    
    # 4. 测试客户文档（使用第一个客户）
    try:
        response = requests.get(
            f"{BASE_URL}/api/customers/",
            headers=tester.headers,
            params={"skip": 0, "limit": 1}
        )
        if response.status_code == 200:
            items = response.json().get("items", [])
            if items:
                customer_id = items[0]["id"]
                tester.test_customer_documents(customer_id)
    except:
        pass
    
    # 5. 测试仪表板统计
    tester.test_dashboard_stats()
    
    # 打印摘要
    tester.print_summary()

if __name__ == "__main__":
    main()

