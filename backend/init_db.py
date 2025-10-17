#!/usr/bin/env python3
"""
初始化数据库脚本
创建所有表并插入初始数据
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from app.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.customer import Customer
from app.models.loan_product import LoanProduct
from app.models.document import DocumentType, CustomerDocument
from app.models.audit_log import AuditLog
from app.models.import_record import ImportRecord
from app.core.security import get_password_hash
from uuid import uuid4
from datetime import datetime


def init_database():
    """初始化数据库"""
    print("🔄 正在初始化数据库...")
    
    try:
        # 创建所有表
        print("📝 创建数据库表...")
        Base.metadata.create_all(bind=engine)
        print("✅ 数据库表创建成功")
        
        # 创建初始数据
        print("📊 插入初始数据...")
        db = SessionLocal()
        
        try:
            # 检查是否已有管理员用户
            admin_user = db.query(User).filter(User.username == "admin").first()

            if not admin_user:
                # 创建管理员用户
                admin_user = User(
                    id=uuid4(),
                    username="admin",
                    password_hash=get_password_hash("admin123"),
                    real_name="系统管理员",
                    role="admin",
                    is_active=True
                )
                db.add(admin_user)
                print("✅ 创建管理员用户: admin / admin123")

            # 检查是否已有测试用户
            test_user = db.query(User).filter(User.username == "test").first()

            if not test_user:
                # 创建测试用户
                test_user = User(
                    id=uuid4(),
                    username="test",
                    password_hash=get_password_hash("test123"),
                    real_name="测试用户",
                    role="customer_service",
                    is_active=True
                )
                db.add(test_user)
                print("✅ 创建测试用户: test / test123")
            
            # 提交事务
            db.commit()
            print("✅ 初始数据插入成功")
            
        except Exception as e:
            db.rollback()
            print(f"❌ 插入初始数据失败: {e}")
            raise
        finally:
            db.close()
        
        print("\n✅ 数据库初始化完成！")
        print("\n📋 初始账户信息:")
        print("  管理员账户: admin / admin123")
        print("  测试账户: test / test123")
        print("\n🚀 现在可以启动应用了！")
        
    except Exception as e:
        print(f"\n❌ 数据库初始化失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    init_database()

