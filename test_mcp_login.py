#!/usr/bin/env python3
"""
MCP 实际测试脚本 - 测试登录功能
"""
import requests
import json
import sys
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api"

class Colors:
    """ANSI 颜色代码"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*70}")
    print(f"{text:^70}")
    print(f"{'='*70}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.END}")

def print_test(text):
    print(f"{Colors.BLUE}🧪 {text}{Colors.END}")

class APITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
        self.user = None
        
    def test_backend_health(self):
        """测试后端健康状态"""
        print_test("测试后端健康状态...")
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                print_success(f"后端正常运行: {data}")
                return True
            else:
                print_error(f"后端返回异常状态码: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"无法连接到后端: {e}")
            return False
    
    def test_login(self, username, password):
        """测试登录"""
        print_test(f"测试登录: {username}")
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json={"username": username, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user = data
                
                print_success(f"登录成功!")
                print_info(f"Token: {self.token[:20]}..." if self.token else "No token")
                print_info(f"Token 类型: {data.get('token_type')}")
                
                # 设置认证头
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                return True
            else:
                print_error(f"登录失败: {response.status_code}")
                print_error(f"响应: {response.text}")
                return False
        except Exception as e:
            print_error(f"登录异常: {e}")
            return False
    
    def test_list_products(self):
        """测试获取产品列表"""
        print_test("测试获取贷款产品列表...")
        try:
            response = self.session.get(f"{self.base_url}/api/products")
            
            if response.status_code == 200:
                data = response.json()
                count = len(data) if isinstance(data, list) else 0
                print_success(f"获取产品列表成功! (共 {count} 个)")
                if data:
                    print_info(f"产品列表:\n{json.dumps(data, indent=2, ensure_ascii=False)[:300]}...")
                return True
            else:
                print_error(f"获取产品列表失败: {response.status_code}")
                print_error(f"响应: {response.text}")
                return False
        except Exception as e:
            print_error(f"获取产品列表异常: {e}")
            return False
    
    def test_create_product(self):
        """测试创建产品"""
        print_test("测试创建贷款产品...")
        try:
            import uuid
            product_data = {
                "code": f"test_product_{str(uuid.uuid4())[:8]}",
                "name": "测试贷款产品",
                "description": "用于 MCP 测试的贷款产品",
                "is_active": True
            }
            
            response = self.session.post(
                f"{self.base_url}/api/products",
                json=product_data
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                print_success("创建产品成功!")
                print_info(f"产品 ID: {data.get('id')}")
                print_info(f"产品名称: {data.get('name')}")
                print_info(f"产品代码: {data.get('code')}")
                return True
            else:
                print_error(f"创建产品失败: {response.status_code}")
                print_error(f"响应: {response.text}")
                return False
        except Exception as e:
            print_error(f"创建产品异常: {e}")
            return False
    
    def test_list_customers(self):
        """测试获取客户列表"""
        print_test("测试获取客户列表...")
        try:
            response = self.session.get(f"{self.base_url}/api/customers?page=1&page_size=20")

            if response.status_code == 200:
                data = response.json()
                # API返回分页对象，包含 items, total, page 等字段
                if isinstance(data, dict):
                    total = data.get('total', 0)
                    items = data.get('items', [])
                    count = len(items)
                    print_success(f"获取客户列表成功! (总数: {total}, 当前页: {count} 个)")

                    # 显示客户详情
                    if items:
                        print_info("客户列表:")
                        for customer in items[:5]:  # 只显示前5个
                            print(f"    - {customer.get('customer_no')}: {customer.get('name')} ({customer.get('status')})")
                            product = customer.get('product', {})
                            if product:
                                print(f"      产品: {product.get('name', 'N/A')}")
                    else:
                        print_info("客户列表为空")
                else:
                    # 兼容旧版本返回列表的情况
                    count = len(data) if isinstance(data, list) else 0
                    print_success(f"获取客户列表成功! (共 {count} 个)")
                return True
            else:
                print_error(f"获取客户列表失败: {response.status_code}")
                print_error(f"响应: {response.text}")
                return False
        except Exception as e:
            print_error(f"获取客户列表异常: {e}")
            return False
    
    def test_get_api_docs(self):
        """测试获取 API 文档"""
        print_test("测试 API 文档可用性...")
        try:
            response = self.session.get(f"{self.base_url}/docs")
            
            if response.status_code == 200:
                print_success("Swagger UI 文档可用!")
                return True
            else:
                print_error(f"获取 Swagger UI 失败: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"获取 API 文档异常: {e}")
            return False

def run_all_tests():
    """运行所有测试"""
    print_header("CCD2 系统 MCP 实际测试")
    print_info(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"API 地址: {BASE_URL}")
    
    tester = APITester(BASE_URL)
    
    results = {}
    
    # 测试1: 后端健康状态
    print_header("第1步: 测试后端连接")
    results['backend_health'] = tester.test_backend_health()
    
    if not results['backend_health']:
        print_error("后端无法连接,停止测试")
        return results
    
    # 测试1.5: API 文档
    print_header("第1.5步: 测试 API 文档")
    results['api_docs'] = tester.test_get_api_docs()
    
    # 测试2: 管理员登录
    print_header("第2步: 测试管理员登录")
    results['admin_login'] = tester.test_login("admin", "admin123")
    
    if not results['admin_login']:
        print_error("管理员登录失败,尝试测试用户...")
        # 尝试测试用户
        print_header("第2.5步: 测试测试用户登录")
        results['test_login'] = tester.test_login("test", "test123")
        if not results['test_login']:
            print_error("两个账户都无法登录,停止测试")
            return results
    
    # 测试3: 获取产品列表
    print_header("第3步: 测试获取产品列表")
    results['list_products'] = tester.test_list_products()
    
    # 测试4: 创建产品
    print_header("第4步: 测试创建产品")
    results['create_product'] = tester.test_create_product()
    
    # 测试5: 获取客户列表
    print_header("第5步: 测试获取客户列表")
    results['list_customers'] = tester.test_list_customers()
    
    # 总结
    print_header("📊 测试总结")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\n{Colors.BOLD}测试结果:{Colors.END}\n")
    for test_name, result in results.items():
        status = f"{Colors.GREEN}✅ 通过{Colors.END}" if result else f"{Colors.RED}❌ 失败{Colors.END}"
        print(f"  {test_name:.<50} {status}")
    
    print(f"\n{Colors.BOLD}总体成绩: {passed}/{total} 通过{Colors.END}")
    
    if passed == total:
        print_success("🎉 所有测试通过!")
    elif passed >= total * 0.7:
        print_info(f"✓ 大部分测试通过 ({int(passed/total*100)}%)")
    else:
        print_error(f"✗ 有 {total - passed} 个测试失败")
    
    return results

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\n测试被中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}未预期的错误: {e}{Colors.END}")
        sys.exit(1)
