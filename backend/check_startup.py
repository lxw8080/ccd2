#!/usr/bin/env python3
"""
后端启动前的健康检查脚本
检查数据库和Redis连接
"""
import sys
import os
from sqlalchemy import create_engine, text
import redis
from urllib.parse import urlparse

def check_database():
    """检查数据库连接"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable is not set!")
        return False
    
    print(f"📊 Checking database connection...")
    print(f"   URL: {database_url.split('@')[0].split('://')[0]}://****@{database_url.split('@')[1] if '@' in database_url else 'invalid'}")
    
    try:
        engine = create_engine(database_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        print("✅ Database connection: OK")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print(f"   Full error: {str(e)}")
        return False

def check_redis():
    """检查Redis连接"""
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    print(f"\n🔴 Checking Redis connection...")
    print(f"   URL: {redis_url}")
    
    try:
        parsed = urlparse(redis_url)
        r = redis.Redis(
            host=parsed.hostname or 'localhost',
            port=parsed.port or 6379,
            db=int(parsed.path.lstrip('/')) if parsed.path else 0,
            socket_connect_timeout=5
        )
        r.ping()
        print("✅ Redis connection: OK")
        return True
    except Exception as e:
        print(f"⚠️  Redis connection failed: {e}")
        print("   Note: Redis is optional, application can still work without it")
        return True  # Redis失败不影响启动

def main():
    """主函数"""
    print("=" * 60)
    print("🔍 CCD2 Backend Startup Health Check")
    print("=" * 60)
    print()
    
    # 显示关键环境变量
    print("📋 Environment Variables:")
    print(f"   DATABASE_URL: {'✓ Set' if os.getenv('DATABASE_URL') else '✗ Not Set'}")
    print(f"   REDIS_URL: {os.getenv('REDIS_URL', 'Using default')}")
    print(f"   LOG_LEVEL: {os.getenv('LOG_LEVEL', 'INFO')}")
    print(f"   STORAGE_TYPE: {os.getenv('STORAGE_TYPE', 'local')}")
    print()
    
    # 检查数据库
    db_ok = check_database()
    
    # 检查Redis
    redis_ok = check_redis()
    
    print()
    print("=" * 60)
    if db_ok:
        print("✅ All critical checks passed! Starting application...")
        print("=" * 60)
        return 0
    else:
        print("❌ Critical checks failed! Cannot start application.")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())

