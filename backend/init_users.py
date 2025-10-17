#!/usr/bin/env python3
"""
创建默认用户的脚本
"""
import sys
sys.path.insert(0, '.')

from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.core.security import get_password_hash
from datetime import datetime

def init_users():
    """创建默认用户"""
    
    # 创建所有表
    print("📝 创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建完成")
    
    db = SessionLocal()
    
    try:
        # 检查管理员是否存在
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                id='550e8400-e29b-41d4-a716-446655440000',
                username="admin",
                password_hash=get_password_hash("admin123"),
                real_name="系统管理员",
                role="admin",
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(admin)
            print("✅ 创建管理员账户: admin / admin123")
        else:
            print("⏭️  管理员账户已存在")
        
        # 检查测试用户是否存在
        test = db.query(User).filter(User.username == "test").first()
        if not test:
            test = User(
                id='550e8400-e29b-41d4-a716-446655440001',
                username="test",
                password_hash=get_password_hash("test123"),
                real_name="测试用户",
                role="customer_service",
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(test)
            print("✅ 创建测试账户: test / test123")
        else:
            print("⏭️  测试账户已存在")
        
        db.commit()
        print("\n✅ 用户初始化完成！")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_users()
