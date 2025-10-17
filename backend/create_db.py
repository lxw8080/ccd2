#!/usr/bin/env python3
"""
创建数据库脚本
连接到 PostgreSQL 服务器并创建新数据库
"""
import psycopg2
from psycopg2 import sql
import sys

# 数据库连接参数
DB_HOST = "115.190.29.10"
DB_PORT = 5433
DB_USER = "flask_user"
DB_PASSWORD = "flask_password"
DB_NAME = "ccd_db_new"  # 新数据库名称

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

