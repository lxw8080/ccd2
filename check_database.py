#!/usr/bin/env python3
"""
检查外部数据库数据
"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent / 'backend' / '.env'
load_dotenv(env_path)
print(f"📝 加载环境变量文件: {env_path}")
print(f"📝 DATABASE_URL: {os.getenv('DATABASE_URL', 'Not set')}")

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from app.database import SessionLocal
from app.models.user import User
from app.models.customer import Customer
from app.models.loan_product import LoanProduct
from app.models.document import DocumentType, CustomerDocument
from sqlalchemy import text

def check_database():
    """检查数据库数据"""
    print("=" * 70)
    print("检查外部数据库数据")
    print("=" * 70)
    
    db = SessionLocal()
    
    try:
        # 检查数据库连接
        print("\n🔍 检查数据库连接...")
        result = db.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        print(f"✅ 数据库连接成功!")
        print(f"   PostgreSQL 版本: {version[:50]}...")
        
        # 检查所有表
        print("\n🔍 检查数据库表...")
        result = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """))
        tables = [row[0] for row in result.fetchall()]
        print(f"✅ 找到 {len(tables)} 个表:")
        for table in tables:
            print(f"   - {table}")
        
        # 检查用户数据
        print("\n🔍 检查用户数据...")
        users = db.query(User).all()
        print(f"✅ 找到 {len(users)} 个用户:")
        for user in users:
            print(f"   - {user.username} ({user.role}) - Active: {user.is_active}")
        
        # 检查产品数据
        print("\n🔍 检查贷款产品数据...")
        products = db.query(LoanProduct).all()
        print(f"✅ 找到 {len(products)} 个产品:")
        for product in products:
            print(f"   - {product.code}: {product.name} - Active: {product.is_active}")
        
        # 检查客户数据
        print("\n🔍 检查客户数据...")
        customers = db.query(Customer).all()
        print(f"✅ 找到 {len(customers)} 个客户:")
        if customers:
            for customer in customers[:10]:  # 只显示前10个
                print(f"   - {customer.customer_no}: {customer.name} - 状态: {customer.status}")
            if len(customers) > 10:
                print(f"   ... 还有 {len(customers) - 10} 个客户")
        else:
            print("   ⚠️  没有客户数据!")
        
        # 检查文档类型数据
        print("\n🔍 检查文档类型数据...")
        doc_types = db.query(DocumentType).all()
        print(f"✅ 找到 {len(doc_types)} 个文档类型:")
        for doc_type in doc_types[:10]:  # 只显示前10个
            print(f"   - {doc_type.name} ({doc_type.category}) - Active: {doc_type.is_active}")
        if len(doc_types) > 10:
            print(f"   ... 还有 {len(doc_types) - 10} 个文档类型")
        
        # 检查客户文档数据
        print("\n🔍 检查客户文档数据...")
        documents = db.query(CustomerDocument).all()
        print(f"✅ 找到 {len(documents)} 个客户文档:")
        if documents:
            for doc in documents[:10]:  # 只显示前10个
                print(f"   - 客户: {doc.customer_id}, 类型: {doc.document_type_id}, 状态: {doc.status}")
            if len(documents) > 10:
                print(f"   ... 还有 {len(documents) - 10} 个文档")
        else:
            print("   ⚠️  没有客户文档数据!")
        
        # 统计信息
        print("\n" + "=" * 70)
        print("📊 数据库统计")
        print("=" * 70)
        print(f"用户数量: {len(users)}")
        print(f"产品数量: {len(products)}")
        print(f"客户数量: {len(customers)}")
        print(f"文档类型数量: {len(doc_types)}")
        print(f"客户文档数量: {len(documents)}")
        
        # 诊断
        print("\n" + "=" * 70)
        print("🔧 诊断结果")
        print("=" * 70)
        
        if len(customers) == 0:
            print("❌ 问题: 数据库中没有客户数据!")
            print("   可能原因:")
            print("   1. 数据库是新创建的，还没有导入客户数据")
            print("   2. 客户数据在其他数据库中")
            print("   3. 需要从旧系统迁移数据")
            print("\n   建议:")
            print("   1. 检查是否有客户数据的备份文件")
            print("   2. 确认是否需要从其他数据库导入数据")
            print("   3. 使用批量导入功能导入客户数据")
        else:
            print("✅ 数据库中有客户数据，应该可以正常显示")
        
    except Exception as e:
        print(f"\n❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_database()

