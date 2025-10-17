#!/usr/bin/env python3
"""
检查数据库表结构
"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent / 'backend' / '.env'
load_dotenv(env_path)

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from app.database import SessionLocal
from sqlalchemy import text

def check_table_structure():
    """检查数据库表结构"""
    print("=" * 70)
    print("检查数据库表结构")
    print("=" * 70)
    
    db = SessionLocal()
    
    try:
        # 检查customer_documents表结构
        print("\n🔍 检查 customer_documents 表结构...")
        result = db.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'customer_documents'
            ORDER BY ordinal_position
        """))
        
        columns = result.fetchall()
        print(f"✅ 找到 {len(columns)} 个字段:")
        for col in columns:
            print(f"   - {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
        
        # 检查customers表结构
        print("\n🔍 检查 customers 表结构...")
        result = db.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'customers'
            ORDER BY ordinal_position
        """))
        
        columns = result.fetchall()
        print(f"✅ 找到 {len(columns)} 个字段:")
        for col in columns:
            print(f"   - {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
        
        # 检查customers表数据
        print("\n🔍 检查 customers 表数据...")
        result = db.execute(text("SELECT * FROM customers"))
        customers = result.fetchall()
        print(f"✅ 找到 {len(customers)} 个客户:")
        for customer in customers:
            print(f"   - {customer}")
        
    except Exception as e:
        print(f"\n❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_table_structure()

