"""
数据库迁移脚本：为 customer_documents 表添加新字段
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.database import engine
from sqlalchemy import text


def migrate_customer_documents():
    """为 customer_documents 表添加新字段"""
    
    migrations = [
        ("note", "ALTER TABLE customer_documents ADD COLUMN IF NOT EXISTS note TEXT;"),
        ("reviewed_by", "ALTER TABLE customer_documents ADD COLUMN IF NOT EXISTS reviewed_by UUID REFERENCES users(id);"),
        ("reviewed_at", "ALTER TABLE customer_documents ADD COLUMN IF NOT EXISTS reviewed_at TIMESTAMP WITH TIME ZONE;"),
        ("review_note", "ALTER TABLE customer_documents ADD COLUMN IF NOT EXISTS review_note TEXT;"),
    ]
    
    with engine.connect() as conn:
        print("开始迁移 customer_documents 表...")
        
        for field_name, sql in migrations:
            try:
                conn.execute(text(sql))
                conn.commit()
                print(f"✅ 字段 '{field_name}' 添加成功")
            except Exception as e:
                print(f"⚠️  字段 '{field_name}' 添加失败或已存在: {e}")
        
        print("\n✅ customer_documents 表迁移完成！")


if __name__ == "__main__":
    migrate_customer_documents()

