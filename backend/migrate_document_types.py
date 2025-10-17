"""
数据库迁移脚本：为 document_types 表添加新字段
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.database import engine, SessionLocal
from app.models.document import DocumentType


def migrate_document_types():
    """为 document_types 表添加新字段"""
    
    print("开始迁移 document_types 表...")
    
    with engine.connect() as conn:
        # 检查表是否存在
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'document_types'
            );
        """))
        table_exists = result.scalar()
        
        if not table_exists:
            print("表 document_types 不存在，跳过迁移")
            return
        
        # 添加新字段（如果不存在）
        migrations = [
            ("is_required", "ALTER TABLE document_types ADD COLUMN IF NOT EXISTS is_required BOOLEAN DEFAULT FALSE;"),
            ("allowed_file_types", "ALTER TABLE document_types ADD COLUMN IF NOT EXISTS allowed_file_types VARCHAR(200);"),
            ("max_file_size", "ALTER TABLE document_types ADD COLUMN IF NOT EXISTS max_file_size INTEGER DEFAULT 10485760;"),
            ("min_files", "ALTER TABLE document_types ADD COLUMN IF NOT EXISTS min_files INTEGER DEFAULT 1;"),
            ("max_files", "ALTER TABLE document_types ADD COLUMN IF NOT EXISTS max_files INTEGER DEFAULT 1;"),
            ("is_active", "ALTER TABLE document_types ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;"),
            ("updated_at", "ALTER TABLE document_types ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();"),
        ]
        
        for field_name, sql in migrations:
            try:
                print(f"添加字段: {field_name}")
                conn.execute(text(sql))
                conn.commit()
                print(f"✓ 字段 {field_name} 添加成功")
            except Exception as e:
                print(f"✗ 字段 {field_name} 添加失败: {e}")
                conn.rollback()
    
    print("\n迁移完成！")


def seed_default_document_types():
    """添加默认的资料类型"""
    
    print("\n开始添加默认资料类型...")
    
    db = SessionLocal()
    
    try:
        # 检查是否已有数据
        existing_count = db.query(DocumentType).count()
        if existing_count > 0:
            print(f"已存在 {existing_count} 个资料类型，跳过初始化")
            return
        
        # 默认资料类型
        default_types = [
            {
                "code": "id_card",
                "name": "身份证",
                "category": "identity",
                "description": "身份证正反面照片",
                "is_required": True,
                "allowed_file_types": "jpg,jpeg,png,pdf",
                "max_file_size": 5242880,  # 5MB
                "min_files": 2,
                "max_files": 2,
                "is_active": True,
                "sort_order": 1
            },
            {
                "code": "business_license",
                "name": "营业执照",
                "category": "identity",
                "description": "企业营业执照",
                "is_required": True,
                "allowed_file_types": "jpg,jpeg,png,pdf",
                "max_file_size": 5242880,
                "min_files": 1,
                "max_files": 1,
                "is_active": True,
                "sort_order": 2
            },
            {
                "code": "bank_statement",
                "name": "银行流水",
                "category": "financial",
                "description": "近6个月银行流水",
                "is_required": True,
                "allowed_file_types": "pdf,jpg,jpeg,png,xls,xlsx",
                "max_file_size": 10485760,  # 10MB
                "min_files": 1,
                "max_files": 10,
                "is_active": True,
                "sort_order": 3
            },
            {
                "code": "income_proof",
                "name": "收入证明",
                "category": "financial",
                "description": "工资单或收入证明",
                "is_required": True,
                "allowed_file_types": "pdf,jpg,jpeg,png,doc,docx",
                "max_file_size": 5242880,
                "min_files": 1,
                "max_files": 5,
                "is_active": True,
                "sort_order": 4
            },
            {
                "code": "credit_report",
                "name": "征信报告",
                "category": "credit",
                "description": "个人或企业征信报告",
                "is_required": True,
                "allowed_file_types": "pdf",
                "max_file_size": 10485760,
                "min_files": 1,
                "max_files": 1,
                "is_active": True,
                "sort_order": 5
            },
            {
                "code": "property_proof",
                "name": "资产证明",
                "category": "financial",
                "description": "房产证、车辆登记证等",
                "is_required": False,
                "allowed_file_types": "pdf,jpg,jpeg,png",
                "max_file_size": 10485760,
                "min_files": 1,
                "max_files": 10,
                "is_active": True,
                "sort_order": 6
            },
            {
                "code": "contract",
                "name": "合同文件",
                "category": "other",
                "description": "相关合同文件",
                "is_required": False,
                "allowed_file_types": "pdf,doc,docx",
                "max_file_size": 10485760,
                "min_files": 1,
                "max_files": 5,
                "is_active": True,
                "sort_order": 7
            },
            {
                "code": "other",
                "name": "其他资料",
                "category": "other",
                "description": "其他补充资料",
                "is_required": False,
                "allowed_file_types": "pdf,jpg,jpeg,png,doc,docx,xls,xlsx",
                "max_file_size": 10485760,
                "min_files": 1,
                "max_files": 20,
                "is_active": True,
                "sort_order": 99
            }
        ]
        
        for type_data in default_types:
            doc_type = DocumentType(**type_data)
            db.add(doc_type)
            print(f"✓ 添加资料类型: {type_data['name']}")
        
        db.commit()
        print(f"\n成功添加 {len(default_types)} 个默认资料类型！")
        
    except Exception as e:
        print(f"添加默认资料类型失败: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("资料类型表迁移脚本")
    print("=" * 60)
    
    # 执行迁移
    migrate_document_types()
    
    # 添加默认数据
    seed_default_document_types()
    
    print("\n" + "=" * 60)
    print("迁移完成！")
    print("=" * 60)

