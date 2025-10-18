#!/bin/bash
# Docker容器启动脚本
# 自动处理环境变量和网络配置

set -e

echo "========================================="
echo "CCD2 Application Starting..."
echo "========================================="

# 检查必需的环境变量
if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL is not set!"
    echo "Please provide DATABASE_URL environment variable."
    echo "Example: postgresql://user:password@host:5432/dbname"
    exit 1
fi

# 显示配置信息(隐藏密码)
echo "Configuration:"
echo "  DATABASE_URL: ${DATABASE_URL%%:*}://***"
echo "  REDIS_URL: redis://127.0.0.1:6379/0 (built-in)"
echo "  LOG_LEVEL: ${LOG_LEVEL:-INFO}"
echo "  STORAGE_TYPE: ${STORAGE_TYPE:-local}"
echo ""

# Redis is now built into the container, no need for external configuration
export REDIS_URL="redis://127.0.0.1:6379/0"

# 创建必要的目录
mkdir -p /app/uploads
mkdir -p /app/logs
chmod 777 /app/uploads
chmod 777 /app/logs

echo ""
echo "Starting services with Supervisor..."
echo "========================================="

# 启动Supervisor (Redis会先启动,然后是Nginx和Backend)
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf

