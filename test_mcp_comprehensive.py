#!/usr/bin/env python3
"""
MCP 综合测试脚本 - 测试所有主要功能
"""
import requests
import json
import sys
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8000"

class Colors:
    """ANSI 颜色代码"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{'='*70}")
    print(f"{text:^70}")
    print(f"{'='*70}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.END}")

class ComprehensiveTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
        self.results = {}
        
    def login(self, username="admin", password="admin123"):
        """登录"""
        print_info(f"登录用户: {username}")
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json={"username": username, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                print_success("登录成功!")
                return True
            else:
                print_error(f"登录失败: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"登录异常: {e}")
            return False
    
    def test_database_connection(self):
        """测试数据库连接"""
        print_header("测试 1: 数据库连接")
        try:
            # 通过获取用户信息来测试数据库连接
            response = self.session.get(f"{self.base_url}/api/auth/me")
            
            if response.status_code == 200:
                user = response.json()
                print_success("数据库连接正常")
                print_info(f"当前用户: {user.get('username')} ({user.get('role')})")
                self.results['database_connection'] = True
                return True
            else:
                print_error(f"无法获取用户信息: {response.status_code}")
                self.results['database_connection'] = False
                return False
        except Exception as e:
            print_error(f"数据库连接测试失败: {e}")
            self.results['database_connection'] = False
            return False
    
    def test_customers(self):
        """测试客户数据"""
        print_header("测试 2: 客户数据")
        try:
            response = self.session.get(f"{self.base_url}/api/customers?page=1&page_size=20")
            
            if response.status_code == 200:
                data = response.json()
                total = data.get('total', 0)
                items = data.get('items', [])
                
                print_success(f"成功获取客户列表")
                print_info(f"总客户数: {total}")
                print_info(f"当前页客户数: {len(items)}")
                
                if items:
                    print_info("\n客户详情:")
                    for customer in items:
                        print(f"  📋 客户编号: {customer.get('customer_no')}")
                        print(f"     姓名: {customer.get('name')}")
                        print(f"     电话: {customer.get('phone')}")
                        print(f"     身份证: {customer.get('id_card')}")
                        print(f"     状态: {customer.get('status')}")
                        product = customer.get('product', {})
                        if product:
                            print(f"     产品: {product.get('name')} ({product.get('code')})")
                        print()
                    
                    # 测试获取单个客户详情
                    first_customer = items[0]
                    customer_id = first_customer.get('id')
                    print_info(f"测试获取客户详情: {customer_id}")
                    
                    detail_response = self.session.get(f"{self.base_url}/api/customers/{customer_id}")
                    if detail_response.status_code == 200:
                        print_success("成功获取客户详情")
                    else:
                        print_error(f"获取客户详情失败: {detail_response.status_code}")
                else:
                    print_info("⚠️  数据库中没有客户数据")
                
                self.results['customers'] = True
                return True
            else:
                print_error(f"获取客户列表失败: {response.status_code}")
                self.results['customers'] = False
                return False
        except Exception as e:
            print_error(f"客户数据测试失败: {e}")
            self.results['customers'] = False
            return False
    
    def test_products(self):
        """测试产品数据"""
        print_header("测试 3: 产品数据")
        try:
            response = self.session.get(f"{self.base_url}/api/products")
            
            if response.status_code == 200:
                products = response.json()
                print_success(f"成功获取产品列表 (共 {len(products)} 个)")
                
                if products:
                    print_info("\n产品详情:")
                    for product in products:
                        print(f"  📦 产品代码: {product.get('code')}")
                        print(f"     产品名称: {product.get('name')}")
                        print(f"     状态: {'启用' if product.get('is_active') else '禁用'}")
                        print()
                
                self.results['products'] = True
                return True
            else:
                print_error(f"获取产品列表失败: {response.status_code}")
                self.results['products'] = False
                return False
        except Exception as e:
            print_error(f"产品数据测试失败: {e}")
            self.results['products'] = False
            return False
    
    def test_document_types(self):
        """测试文档类型"""
        print_header("测试 4: 文档类型")
        try:
            response = self.session.get(f"{self.base_url}/api/products/document-types")
            
            if response.status_code == 200:
                doc_types = response.json()
                print_success(f"成功获取文档类型列表 (共 {len(doc_types)} 个)")
                
                if doc_types:
                    # 按类别分组
                    categories = {}
                    for doc_type in doc_types:
                        category = doc_type.get('category', 'other')
                        if category not in categories:
                            categories[category] = []
                        categories[category].append(doc_type)
                    
                    print_info("\n文档类型 (按类别):")
                    for category, types in categories.items():
                        category_name = {
                            'identity': '身份证明',
                            'financial': '财务证明',
                            'credit': '信用证明',
                            'other': '其他'
                        }.get(category, category)
                        
                        print(f"\n  📁 {category_name}:")
                        for doc_type in types:
                            status = '✓' if doc_type.get('is_active') else '✗'
                            required = '必需' if doc_type.get('is_required') else '可选'
                            print(f"     {status} {doc_type.get('name')} ({required})")
                
                self.results['document_types'] = True
                return True
            else:
                print_error(f"获取文档类型失败: {response.status_code}")
                self.results['document_types'] = False
                return False
        except Exception as e:
            print_error(f"文档类型测试失败: {e}")
            self.results['document_types'] = False
            return False
    
    def test_database_schema(self):
        """测试数据库表结构"""
        print_header("测试 5: 数据库表结构")
        
        # 这个测试通过检查API响应来间接验证表结构
        print_info("通过API响应验证数据库表结构...")
        
        all_ok = True
        
        # 检查客户表字段
        try:
            response = self.session.get(f"{self.base_url}/api/customers?page=1&page_size=1")
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                if items:
                    customer = items[0]
                    required_fields = ['id', 'customer_no', 'name', 'phone', 'status', 'product']
                    missing_fields = [f for f in required_fields if f not in customer]
                    
                    if missing_fields:
                        print_error(f"客户表缺少字段: {missing_fields}")
                        all_ok = False
                    else:
                        print_success("客户表结构正常")
        except Exception as e:
            print_error(f"检查客户表失败: {e}")
            all_ok = False
        
        self.results['database_schema'] = all_ok
        return all_ok
    
    def print_summary(self):
        """打印测试总结"""
        print_header("📊 测试总结")
        
        passed = sum(1 for v in self.results.values() if v)
        total = len(self.results)
        
        print(f"\n{Colors.BOLD}测试结果:{Colors.END}\n")
        for test_name, result in self.results.items():
            status = f"{Colors.GREEN}✅ 通过{Colors.END}" if result else f"{Colors.RED}❌ 失败{Colors.END}"
            print(f"  {test_name.replace('_', ' ').title():.<50} {status}")
        
        print(f"\n{Colors.BOLD}总体成绩: {passed}/{total} 通过 ({int(passed/total*100)}%){Colors.END}")
        
        if passed == total:
            print_success("\n🎉 所有测试通过！数据库数据正常显示。")
        else:
            print_error(f"\n⚠️  有 {total - passed} 个测试失败")

def main():
    """主函数"""
    print_header("CCD2 系统 MCP 综合测试")
    print_info(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"API 地址: {BASE_URL}")
    
    tester = ComprehensiveTester(BASE_URL)
    
    # 登录
    if not tester.login():
        print_error("登录失败，无法继续测试")
        return 1
    
    # 运行所有测试
    tester.test_database_connection()
    tester.test_customers()
    tester.test_products()
    tester.test_document_types()
    tester.test_database_schema()
    
    # 打印总结
    tester.print_summary()
    
    return 0 if all(tester.results.values()) else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n测试被中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}未预期的错误: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

