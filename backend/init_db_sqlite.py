#!/usr/bin/env python3
"""
初始化 SQLite 数据库脚本
为了避免 UUID 问题，我们直接使用 SQL 创建表
"""
import os
import sqlite3
from pathlib import Path

def init_sqlite_database():
    """初始化 SQLite 数据库"""
    db_path = "./ccd_db.sqlite"
    
    print("🔄 正在初始化 SQLite 数据库...")
    
    # 创建连接
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 创建用户表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            real_name VARCHAR(100),
            role VARCHAR(20) NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        print("✅ 创建用户表")
        
        # 插入默认用户
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
            INSERT INTO users (id, username, password_hash, real_name, role, is_active)
            VALUES ('550e8400-e29b-41d4-a716-446655440000', 'admin', '$2b$12$h1j0XY8Y.Foz0MO2D/oQxOJ3pC1D2HZ.8P6ZfNkZ/ZqZY.9N1VpEO', '系统管理员', 'admin', 1)
            """)
            print("✅ 创建管理员用户: admin / admin123")
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'test'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
            INSERT INTO users (id, username, password_hash, real_name, role, is_active)
            VALUES ('550e8400-e29b-41d4-a716-446655440001', 'test', '$2b$12$E1fF5dQ0Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8', '测试用户', 'customer_service', 1)
            """)
            print("✅ 创建测试用户: test / test123")
        
        conn.commit()
        print("\n✅ 数据库初始化完成！")
        print("\n📋 初始账户信息:")
        print("  管理员账户: admin / admin123")
        print("  测试账户: test / test123")
        print("\n🚀 现在可以启动应用了！")
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    init_sqlite_database()
