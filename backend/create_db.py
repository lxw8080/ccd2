#!/usr/bin/env python3
"""
创建数据库脚本
连接到 PostgreSQL 服务器并创建新数据库
"""
import os
from urllib.parse import urlparse
import psycopg2
from psycopg2 import sql
import sys

# 从环境变量读取数据库连接信息：优先使用 DATABASE_URL，其次使用 DB_HOST/DB_PORT/DB_USER/DB_PASSWORD/DB_NAME
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    parsed = urlparse(DATABASE_URL)
    DB_HOST = parsed.hostname or "localhost"
    DB_PORT = parsed.port or 5432
    DB_USER = parsed.username or ""
    DB_PASSWORD = parsed.password or ""
    DB_NAME = (parsed.path or "").lstrip("/") or ""
else:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "5432"))
    DB_USER = os.getenv("DB_USER", "")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "")

if not all([DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME]):
    print("❌ 缺少数据库环境变量，请设置 DATABASE_URL 或 DB_HOST/DB_PORT/DB_USER/DB_PASSWORD/DB_NAME")
    sys.exit(2)

def create_database():
    """创建数据库"""
    print(f"🔄 正在连接到 PostgreSQL 服务器 {DB_HOST}:{DB_PORT}...")
    
    try:
        # 连接到默认的 postgres 数据库
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database="postgres"
        )
        
        # 设置自动提交模式
        conn.autocommit = True
        cursor = conn.cursor()
        
        print(f"✅ 已连接到 PostgreSQL 服务器")
        
        # 检查数据库是否已存在
        cursor.execute(
            sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"),
            [DB_NAME]
        )
        
        if cursor.fetchone():
            print(f"⚠️  数据库 '{DB_NAME}' 已存在")
            response = input(f"是否要删除并重新创建? (y/n): ").strip().lower()
            
            if response == 'y':
                print(f"🗑️  正在删除数据库 '{DB_NAME}'...")
                cursor.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(
                    sql.Identifier(DB_NAME)
                ))
                print(f"✅ 数据库已删除")
            else:
                print("❌ 操作已取消")
                cursor.close()
                conn.close()
                return False
        
        # 创建新数据库
        print(f"📝 正在创建数据库 '{DB_NAME}'...")
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(
            sql.Identifier(DB_NAME)
        ))
        print(f"✅ 数据库 '{DB_NAME}' 创建成功")
        
        cursor.close()
        conn.close()
        
        print("\n✅ 数据库创建完成！")
        print(f"📋 数据库信息:")
        print(f"  主机: {DB_HOST}")
        print(f"  端口: {DB_PORT}")
        print(f"  用户: {DB_USER}")
        print(f"  数据库: {DB_NAME}")
        print(f"\n🚀 现在可以运行 'python3 init_db.py' 来初始化表和数据")
        
        return True
        
    except psycopg2.Error as e:
        print(f"\n❌ 数据库操作失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    create_database()

