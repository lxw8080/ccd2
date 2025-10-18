#!/bin/bash

#############################################
# CCD2 单镜像部署脚本 (Ubuntu服务器)
# 用途: 自动加载和部署单镜像Docker容器
#############################################

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
IMAGE_FILE="ccd2-app-all-in-one.tar"
IMAGE_TAG="ccd2-app:all-in-one"
CONTAINER_NAME="ccd2"
HOST_PORT="8080"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}CCD2 单镜像自动部署脚本${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

#############################################
# 1. 检查Docker是否安装
#############################################
echo -e "${YELLOW}[1/7] 检查Docker环境...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker未安装!${NC}"
    echo "请先安装Docker: https://docs.docker.com/engine/install/ubuntu/"
    exit 1
fi
echo -e "${GREEN}✅ Docker已安装: $(docker --version)${NC}"
echo ""

#############################################
# 2. 检查镜像文件
#############################################
echo -e "${YELLOW}[2/7] 检查镜像文件...${NC}"
if [ ! -f "$IMAGE_FILE" ]; then
    echo -e "${RED}❌ 镜像文件不存在: $IMAGE_FILE${NC}"
    echo "请确保镜像文件在当前目录"
    exit 1
fi

FILE_SIZE=$(du -h "$IMAGE_FILE" | cut -f1)
echo -e "${GREEN}✅ 镜像文件存在: $IMAGE_FILE ($FILE_SIZE)${NC}"
echo ""

#############################################
# 3. 验证SHA256校验和(可选)
#############################################
echo -e "${YELLOW}[3/7] 验证文件完整性...${NC}"
if [ -f "${IMAGE_FILE}.sha256" ]; then
    EXPECTED_HASH=$(cat "${IMAGE_FILE}.sha256" | tr -d '[:space:]')
    ACTUAL_HASH=$(sha256sum "$IMAGE_FILE" | awk '{print $1}')
    
    if [ "$EXPECTED_HASH" = "$ACTUAL_HASH" ]; then
        echo -e "${GREEN}✅ SHA256校验通过${NC}"
    else
        echo -e "${RED}❌ SHA256校验失败!${NC}"
        echo "期望: $EXPECTED_HASH"
        echo "实际: $ACTUAL_HASH"
        read -p "是否继续部署? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    echo -e "${YELLOW}⚠️  未找到SHA256校验文件,跳过校验${NC}"
fi
echo ""

#############################################
# 4. 停止并删除旧容器
#############################################
echo -e "${YELLOW}[4/7] 清理旧容器...${NC}"
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "停止旧容器..."
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    echo "删除旧容器..."
    docker rm "$CONTAINER_NAME" 2>/dev/null || true
    echo -e "${GREEN}✅ 旧容器已清理${NC}"
else
    echo -e "${GREEN}✅ 无需清理${NC}"
fi
echo ""

#############################################
# 5. 加载Docker镜像
#############################################
echo -e "${YELLOW}[5/7] 加载Docker镜像...${NC}"
echo "这可能需要几分钟,请耐心等待..."
docker load -i "$IMAGE_FILE"
echo -e "${GREEN}✅ 镜像加载完成${NC}"
echo ""

#############################################
# 6. 配置环境变量
#############################################
echo -e "${YELLOW}[6/7] 配置环境变量...${NC}"
echo ""
echo "请输入以下配置信息:"
echo ""

# 数据库URL
read -p "数据库URL (例: postgresql://user:pass@host:port/db): " DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}❌ 数据库URL不能为空${NC}"
    exit 1
fi

# SECRET_KEY
echo ""
echo "生成随机SECRET_KEY? (推荐)"
read -p "使用随机生成的SECRET_KEY? (Y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    read -p "请输入SECRET_KEY: " SECRET_KEY
else
    SECRET_KEY=$(openssl rand -hex 32)
    echo "已生成SECRET_KEY: $SECRET_KEY"
fi

# 日志级别
echo ""
read -p "日志级别 (INFO/DEBUG/WARNING/ERROR) [默认: INFO]: " LOG_LEVEL
LOG_LEVEL=${LOG_LEVEL:-INFO}

echo -e "${GREEN}✅ 配置完成${NC}"
echo ""

#############################################
# 7. 启动容器
#############################################
echo -e "${YELLOW}[7/7] 启动容器...${NC}"
docker run -d \
    --name "$CONTAINER_NAME" \
    -p "${HOST_PORT}:80" \
    -e DATABASE_URL="$DATABASE_URL" \
    -e SECRET_KEY="$SECRET_KEY" \
    -e LOG_LEVEL="$LOG_LEVEL" \
    -e STORAGE_TYPE="local" \
    -v ccd2-uploads:/app/uploads \
    -v ccd2-logs:/app/logs \
    -v ccd2-redis-data:/var/lib/redis \
    --restart unless-stopped \
    "$IMAGE_TAG"

echo -e "${GREEN}✅ 容器启动成功${NC}"
echo ""

#############################################
# 8. 等待服务启动
#############################################
echo -e "${YELLOW}等待服务启动...${NC}"
sleep 10

# 检查容器状态
if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${GREEN}✅ 容器运行中${NC}"
else
    echo -e "${RED}❌ 容器启动失败!${NC}"
    echo "查看日志:"
    docker logs "$CONTAINER_NAME"
    exit 1
fi

# 健康检查
echo ""
echo -e "${YELLOW}执行健康检查...${NC}"
sleep 5
HEALTH_CHECK=$(curl -s http://localhost:${HOST_PORT}/api/health || echo "failed")
if echo "$HEALTH_CHECK" | grep -q "healthy"; then
    echo -e "${GREEN}✅ 健康检查通过${NC}"
else
    echo -e "${YELLOW}⚠️  健康检查未通过,请查看日志${NC}"
fi

#############################################
# 部署完成
#############################################
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🎉 部署完成!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "容器信息:"
echo "  名称: $CONTAINER_NAME"
echo "  镜像: $IMAGE_TAG"
echo "  端口: http://localhost:${HOST_PORT}"
echo ""
echo "常用命令:"
echo "  查看日志: docker logs -f $CONTAINER_NAME"
echo "  停止容器: docker stop $CONTAINER_NAME"
echo "  启动容器: docker start $CONTAINER_NAME"
echo "  重启容器: docker restart $CONTAINER_NAME"
echo "  删除容器: docker stop $CONTAINER_NAME && docker rm $CONTAINER_NAME"
echo ""
echo "访问应用:"
echo "  浏览器打开: http://<服务器IP>:${HOST_PORT}"
echo ""
echo -e "${BLUE}========================================${NC}"

