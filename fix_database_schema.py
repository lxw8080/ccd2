#!/usr/bin/env python3
"""
修复数据库表结构
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

def fix_database_schema():
    """修复数据库表结构"""
    print("=" * 70)
    print("修复数据库表结构")
    print("=" * 70)
    
    db = SessionLocal()
    
    try:
        # 检查customer_documents表是否有updated_at字段
        print("\n🔍 检查 customer_documents 表...")
        result = db.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'customer_documents' AND column_name = 'updated_at'
        """))
        
        has_updated_at = result.fetchone() is not None
        
        if not has_updated_at:
            print("❌ customer_documents 表缺少 updated_at 字段")
            print("🔧 添加 updated_at 字段...")
            
            db.execute(text("""
                ALTER TABLE customer_documents 
                ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
            """))
            db.commit()
            print("✅ 成功添加 updated_at 字段")
        else:
            print("✅ customer_documents 表已有 updated_at 字段")
        
        # 更新模型以包含额外的字段
        print("\n📝 建议更新 CustomerDocument 模型以包含以下字段:")
        print("   - reviewed_by: 审核人ID")
        print("   - reviewed_at: 审核时间")
        print("   - review_note: 审核备注")
        
        print("\n✅ 数据库表结构修复完成!")
        
    except Exception as e:
        print(f"\n❌ 修复失败: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_database_schema()

