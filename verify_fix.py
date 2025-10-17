#!/usr/bin/env python3
"""
验证数据库修复
"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import requests

# 加载环境变量
env_path = Path(__file__).parent / 'backend' / '.env'
load_dotenv(env_path)

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from app.database import SessionLocal
from app.models.user import User
from app.models.customer import Customer
from app.models.loan_product import LoanProduct
from sqlalchemy import text

def verify_database():
    """验证数据库"""
    print("=" * 70)
    print("验证数据库修复")
    print("=" * 70)
    
    db = SessionLocal()
    
    try:
        # 1. 检查数据库连接
        print("\n✅ 步骤 1: 检查数据库连接")
        result = db.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        print(f"   数据库版本: {version[:50]}...")
        
        # 2. 检查表结构
        print("\n✅ 步骤 2: 检查 customer_documents 表结构")
        result = db.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'customer_documents'
            ORDER BY ordinal_position
        """))
        columns = [row[0] for row in result.fetchall()]
        
        required_columns = ['id', 'customer_id', 'document_type_id', 'file_name', 
                          'file_path', 'uploaded_by', 'created_at', 'updated_at']
        
        missing_columns = [col for col in required_columns if col not in columns]
        if missing_columns:
            print(f"   ❌ 缺少字段: {missing_columns}")
            return False
        else:
            print(f"   ✅ 所有必需字段都存在")
            print(f"   总字段数: {len(columns)}")
        
        # 3. 检查数据
        print("\n✅ 步骤 3: 检查数据")
        
        users = db.query(User).count()
        products = db.query(LoanProduct).count()
        customers = db.query(Customer).count()
        
        print(f"   用户数: {users}")
        print(f"   产品数: {products}")
        print(f"   客户数: {customers}")
        
        if customers == 0:
            print("\n   ⚠️  警告: 数据库中没有客户数据!")
            print("   这可能是正常的，如果这是一个新系统。")
        else:
            print(f"\n   ✅ 找到 {customers} 个客户")
            
            # 显示客户详情
            customer_list = db.query(Customer).limit(5).all()
            for customer in customer_list:
                print(f"      - {customer.customer_no}: {customer.name} ({customer.status})")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def verify_api():
    """验证API"""
    print("\n" + "=" * 70)
    print("验证API")
    print("=" * 70)
    
    BASE_URL = "http://localhost:8000"
    
    try:
        # 1. 检查健康状态
        print("\n✅ 步骤 1: 检查后端健康状态")
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"   ✅ 后端正常运行")
        else:
            print(f"   ❌ 后端健康检查失败: {response.status_code}")
            return False
        
        # 2. 登录
        print("\n✅ 步骤 2: 测试登录")
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": "admin", "password": "admin123"},
            timeout=5
        )
        
        if response.status_code != 200:
            print(f"   ❌ 登录失败: {response.status_code}")
            return False
        
        token = response.json()["access_token"]
        print(f"   ✅ 登录成功")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. 获取客户列表
        print("\n✅ 步骤 3: 获取客户列表")
        response = requests.get(
            f"{BASE_URL}/api/customers?page=1&page_size=20",
            headers=headers,
            timeout=5
        )
        
        if response.status_code != 200:
            print(f"   ❌ 获取客户列表失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return False
        
        data = response.json()
        total = data.get('total', 0)
        items = data.get('items', [])
        
        print(f"   ✅ 获取客户列表成功")
        print(f"   总客户数: {total}")
        print(f"   当前页客户数: {len(items)}")
        
        if items:
            print("\n   客户列表:")
            for customer in items:
                print(f"      - {customer.get('customer_no')}: {customer.get('name')}")
                print(f"        状态: {customer.get('status')}")
                product = customer.get('product', {})
                if product:
                    print(f"        产品: {product.get('name', 'N/A')}")
        else:
            print("\n   ⚠️  客户列表为空")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"\n❌ 无法连接到后端服务 ({BASE_URL})")
        print("   请确保后端服务正在运行")
        return False
    except Exception as e:
        print(f"\n❌ API验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("CCD2 系统验证")
    print("=" * 70)
    
    # 验证数据库
    db_ok = verify_database()
    
    # 验证API
    api_ok = verify_api()
    
    # 总结
    print("\n" + "=" * 70)
    print("验证总结")
    print("=" * 70)
    
    print(f"\n数据库验证: {'✅ 通过' if db_ok else '❌ 失败'}")
    print(f"API验证: {'✅ 通过' if api_ok else '❌ 失败'}")
    
    if db_ok and api_ok:
        print("\n🎉 所有验证通过！系统正常运行。")
        print("\n下一步:")
        print("1. 访问前端: http://localhost:5173")
        print("2. 使用 admin/admin123 登录")
        print("3. 查看客户列表")
        return 0
    else:
        print("\n❌ 验证失败，请检查上述错误信息。")
        return 1


if __name__ == "__main__":
    sys.exit(main())

