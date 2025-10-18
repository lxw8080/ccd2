#!/bin/bash
# Docker容器运行脚本 (Linux版本)
# 用于在服务器上正确配置和运行CCD2容器

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
CONTAINER_NAME="ccd2"
IMAGE_NAME="ccd2-app:latest"
HOST_PORT="8080"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}CCD2 Docker容器启动脚本${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: Docker未安装${NC}"
    exit 1
fi

# 检查镜像是否存在
if ! docker images | grep -q "ccd2-app"; then
    echo -e "${RED}错误: Docker镜像 ccd2-app:latest 不存在${NC}"
    echo -e "${YELLOW}请先使用以下命令加载镜像:${NC}"
    echo -e "  docker load -i ccd2-app-latest.tar"
    exit 1
fi

# 停止并删除已存在的容器
if docker ps -a | grep -q "$CONTAINER_NAME"; then
    echo -e "${YELLOW}停止并删除已存在的容器...${NC}"
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    docker rm "$CONTAINER_NAME" 2>/dev/null || true
    echo -e "${GREEN}✓ 已清理旧容器${NC}"
fi

# 提示用户输入配置
echo -e "${YELLOW}请输入配置信息 (按Enter使用默认值):${NC}"
echo ""

# 数据库配置
read -p "数据库主机 [localhost]: " DB_HOST
DB_HOST=${DB_HOST:-localhost}

read -p "数据库端口 [5432]: " DB_PORT
DB_PORT=${DB_PORT:-5432}

read -p "数据库名称 [ccd_db]: " DB_NAME
DB_NAME=${DB_NAME:-ccd_db}

read -p "数据库用户名 [ccd_user]: " DB_USER
DB_USER=${DB_USER:-ccd_user}

read -sp "数据库密码 [ccd_password]: " DB_PASSWORD
echo ""
DB_PASSWORD=${DB_PASSWORD:-ccd_password}

DATABASE_URL="postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}"

# Redis配置
read -p "Redis主机 [localhost]: " REDIS_HOST
REDIS_HOST=${REDIS_HOST:-localhost}

read -p "Redis端口 [6379]: " REDIS_PORT
REDIS_PORT=${REDIS_PORT:-6379}

read -p "Redis数据库编号 [0]: " REDIS_DB
REDIS_DB=${REDIS_DB:-0}

REDIS_URL="redis://${REDIS_HOST}:${REDIS_PORT}/${REDIS_DB}"

# 密钥配置
read -sp "JWT密钥 (留空自动生成): " SECRET_KEY
echo ""
if [ -z "$SECRET_KEY" ]; then
    SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 64 | head -n 1)
    echo -e "${GREEN}✓ 已自动生成密钥${NC}"
fi

# 端口配置
read -p "主机端口 [8080]: " HOST_PORT
HOST_PORT=${HOST_PORT:-8080}

# 创建数据卷目录
echo ""
echo -e "${YELLOW}创建数据卷目录...${NC}"
mkdir -p ./docker-volumes/uploads
mkdir -p ./docker-volumes/logs
chmod 777 ./docker-volumes/uploads
chmod 777 ./docker-volumes/logs
echo -e "${GREEN}✓ 数据卷目录已创建${NC}"

# 显示配置摘要
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}配置摘要${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "容器名称: ${GREEN}$CONTAINER_NAME${NC}"
echo -e "镜像名称: ${GREEN}$IMAGE_NAME${NC}"
echo -e "主机端口: ${GREEN}$HOST_PORT${NC}"
echo -e "数据库URL: ${GREEN}$DATABASE_URL${NC}"
echo -e "Redis URL: ${GREEN}$REDIS_URL${NC}"
echo -e "上传目录: ${GREEN}./docker-volumes/uploads${NC}"
echo -e "日志目录: ${GREEN}./docker-volumes/logs${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 确认启动
read -p "是否继续启动容器? (y/n) [y]: " CONFIRM
CONFIRM=${CONFIRM:-y}

if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo -e "${YELLOW}已取消${NC}"
    exit 0
fi

# 启动容器
echo ""
echo -e "${YELLOW}启动Docker容器...${NC}"

docker run -d \
  --name "$CONTAINER_NAME" \
  -p "$HOST_PORT:80" \
  -e DATABASE_URL="$DATABASE_URL" \
  -e REDIS_URL="$REDIS_URL" \
  -e SECRET_KEY="$SECRET_KEY" \
  -e ALGORITHM="HS256" \
  -e ACCESS_TOKEN_EXPIRE_MINUTES="30" \
  -e STORAGE_TYPE="local" \
  -e UPLOAD_DIR="/app/uploads" \
  -e LOG_LEVEL="INFO" \
  -e APP_NAME="客户资料收集系统" \
  -e APP_VERSION="1.0.0" \
  -v "$(pwd)/docker-volumes/uploads:/app/uploads" \
  -v "$(pwd)/docker-volumes/logs:/app/logs" \
  --restart unless-stopped \
  "$IMAGE_NAME"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 容器启动成功${NC}"
else
    echo -e "${RED}✗ 容器启动失败${NC}"
    exit 1
fi

# 等待容器启动
echo ""
echo -e "${YELLOW}等待容器启动 (最多60秒)...${NC}"
for i in {1..60}; do
    if docker ps | grep -q "$CONTAINER_NAME"; then
        # 检查后端进程
        if docker exec "$CONTAINER_NAME" pgrep -f uvicorn > /dev/null 2>&1; then
            echo -e "${GREEN}✓ 容器已启动并运行${NC}"
            break
        fi
    fi
    
    if [ $i -eq 60 ]; then
        echo -e "${RED}✗ 容器启动超时${NC}"
        echo -e "${YELLOW}查看日志:${NC}"
        docker logs "$CONTAINER_NAME" | tail -n 30
        exit 1
    fi
    
    echo -n "."
    sleep 1
done
echo ""

# 显示容器状态
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}容器状态${NC}"
echo -e "${BLUE}========================================${NC}"
docker ps --filter "name=$CONTAINER_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

# 检查日志中是否有错误
echo -e "${YELLOW}检查启动日志...${NC}"
sleep 3
LOGS=$(docker logs "$CONTAINER_NAME" 2>&1 | tail -n 20)

if echo "$LOGS" | grep -qi "error\|exception\|failed\|exited"; then
    echo -e "${RED}⚠ 发现错误日志:${NC}"
    echo "$LOGS"
    echo ""
    echo -e "${YELLOW}建议操作:${NC}"
    echo "1. 检查数据库连接: docker exec $CONTAINER_NAME pg_isready -h $DB_HOST -p $DB_PORT"
    echo "2. 检查Redis连接: docker exec $CONTAINER_NAME redis-cli -h $REDIS_HOST -p $REDIS_PORT ping"
    echo "3. 查看详细日志: docker logs -f $CONTAINER_NAME"
    echo "4. 进入容器调试: docker exec -it $CONTAINER_NAME /bin/bash"
else
    echo -e "${GREEN}✓ 未发现明显错误${NC}"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}部署完成!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "访问地址: ${GREEN}http://localhost:$HOST_PORT${NC}"
echo -e "或使用服务器IP: ${GREEN}http://<服务器IP>:$HOST_PORT${NC}"
echo ""
echo -e "${YELLOW}常用命令:${NC}"
echo -e "  查看日志: ${GREEN}docker logs -f $CONTAINER_NAME${NC}"
echo -e "  停止容器: ${GREEN}docker stop $CONTAINER_NAME${NC}"
echo -e "  启动容器: ${GREEN}docker start $CONTAINER_NAME${NC}"
echo -e "  重启容器: ${GREEN}docker restart $CONTAINER_NAME${NC}"
echo -e "  进入容器: ${GREEN}docker exec -it $CONTAINER_NAME /bin/bash${NC}"
echo ""

