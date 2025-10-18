#!/bin/bash

# ============================================
# CCD2 服务器部署脚本 (Ubuntu)
# ============================================
# 功能: 在Ubuntu服务器上自动部署CCD2应用
# 前提: 已将docker-images-export目录传输到服务器
# ============================================

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}==========================================${NC}"
echo -e "${CYAN}CCD2 服务器部署工具${NC}"
echo -e "${CYAN}==========================================${NC}"
echo ""

# 检查是否在正确的目录
if [ ! -f "docker-compose.production.yml" ]; then
    echo -e "${RED}错误: 未找到 docker-compose.production.yml${NC}"
    echo -e "${YELLOW}请确保在 docker-images-export 目录中运行此脚本${NC}"
    exit 1
fi

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: Docker未安装${NC}"
    echo -e "${YELLOW}请先安装Docker: https://docs.docker.com/engine/install/ubuntu/${NC}"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}错误: Docker Compose未安装${NC}"
    echo -e "${YELLOW}请先安装Docker Compose${NC}"
    exit 1
fi

# 使用正确的docker-compose命令
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    DOCKER_COMPOSE="docker compose"
fi

echo -e "${GREEN}✓ Docker环境检查通过${NC}"
echo ""

# 步骤1: 验证镜像文件
echo -e "${YELLOW}步骤 1/5: 验证镜像文件完整性${NC}"
echo ""

if [ -f "ccd2-app-latest.tar.sha256" ]; then
    if sha256sum -c ccd2-app-latest.tar.sha256; then
        echo -e "${GREEN}✓ ccd2-app-latest.tar 验证通过${NC}"
    else
        echo -e "${RED}✗ ccd2-app-latest.tar 验证失败${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠ 未找到SHA256校验文件,跳过验证${NC}"
fi

if [ -f "redis-7-alpine.tar.sha256" ]; then
    if sha256sum -c redis-7-alpine.tar.sha256; then
        echo -e "${GREEN}✓ redis-7-alpine.tar 验证通过${NC}"
    else
        echo -e "${RED}✗ redis-7-alpine.tar 验证失败${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠ 未找到SHA256校验文件,跳过验证${NC}"
fi

echo ""

# 步骤2: 加载Docker镜像
echo -e "${YELLOW}步骤 2/5: 加载Docker镜像${NC}"
echo ""

if [ -f "ccd2-app-latest.tar" ]; then
    echo -e "${CYAN}加载 ccd2-app:latest ...${NC}"
    docker load -i ccd2-app-latest.tar
    echo -e "${GREEN}✓ ccd2-app:latest 加载成功${NC}"
else
    echo -e "${RED}✗ 未找到 ccd2-app-latest.tar${NC}"
    exit 1
fi

if [ -f "redis-7-alpine.tar" ]; then
    echo -e "${CYAN}加载 redis:7-alpine ...${NC}"
    docker load -i redis-7-alpine.tar
    echo -e "${GREEN}✓ redis:7-alpine 加载成功${NC}"
else
    echo -e "${RED}✗ 未找到 redis-7-alpine.tar${NC}"
    exit 1
fi

echo ""

# 验证镜像已加载
echo -e "${CYAN}验证镜像...${NC}"
docker images | grep -E "ccd2-app|redis"
echo ""

# 步骤3: 配置环境变量
echo -e "${YELLOW}步骤 3/5: 配置环境变量${NC}"
echo ""

if [ ! -f ".env.production" ]; then
    if [ -f ".env.production.example" ]; then
        echo -e "${CYAN}创建 .env.production 文件...${NC}"
        cp .env.production.example .env.production
        echo -e "${GREEN}✓ 已从示例文件创建 .env.production${NC}"
        echo ""
        echo -e "${YELLOW}⚠ 重要: 请编辑 .env.production 文件并配置以下内容:${NC}"
        echo -e "  1. SECRET_KEY - 生成随机密钥: ${CYAN}openssl rand -hex 32${NC}"
        echo -e "  2. DATABASE_URL - 确认数据库连接信息"
        echo ""
        read -p "是否现在编辑配置文件? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ${EDITOR:-nano} .env.production
        else
            echo -e "${YELLOW}请稍后手动编辑 .env.production 文件${NC}"
            echo -e "${YELLOW}编辑完成后,运行: $DOCKER_COMPOSE -f docker-compose.production.yml up -d${NC}"
            exit 0
        fi
    else
        echo -e "${RED}✗ 未找到 .env.production.example${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ .env.production 已存在${NC}"
fi

echo ""

# 步骤4: 启动服务
echo -e "${YELLOW}步骤 4/5: 启动服务${NC}"
echo ""

echo -e "${CYAN}使用Docker Compose启动服务...${NC}"
$DOCKER_COMPOSE -f docker-compose.production.yml --env-file .env.production up -d

echo ""
echo -e "${GREEN}✓ 服务启动命令已执行${NC}"
echo ""

# 等待服务启动
echo -e "${CYAN}等待服务启动 (30秒)...${NC}"
sleep 30

# 步骤5: 验证部署
echo -e "${YELLOW}步骤 5/5: 验证部署${NC}"
echo ""

# 检查容器状态
echo -e "${CYAN}容器状态:${NC}"
$DOCKER_COMPOSE -f docker-compose.production.yml ps
echo ""

# 测试健康检查
echo -e "${CYAN}测试健康检查...${NC}"
if curl -f http://localhost:8080/api/health 2>/dev/null; then
    echo ""
    echo -e "${GREEN}✓ 健康检查通过${NC}"
else
    echo ""
    echo -e "${YELLOW}⚠ 健康检查失败,查看日志:${NC}"
    echo -e "${CYAN}$DOCKER_COMPOSE -f docker-compose.production.yml logs app${NC}"
fi

echo ""
echo -e "${CYAN}==========================================${NC}"
echo -e "${GREEN}部署完成!${NC}"
echo -e "${CYAN}==========================================${NC}"
echo ""

# 获取服务器IP
SERVER_IP=$(hostname -I | awk '{print $1}')

echo -e "${YELLOW}访问信息:${NC}"
echo -e "  应用地址: ${CYAN}http://$SERVER_IP:8080${NC}"
echo -e "  健康检查: ${CYAN}http://$SERVER_IP:8080/api/health${NC}"
echo ""

echo -e "${YELLOW}常用命令:${NC}"
echo -e "  查看日志: ${CYAN}$DOCKER_COMPOSE -f docker-compose.production.yml logs -f${NC}"
echo -e "  重启服务: ${CYAN}$DOCKER_COMPOSE -f docker-compose.production.yml restart${NC}"
echo -e "  停止服务: ${CYAN}$DOCKER_COMPOSE -f docker-compose.production.yml stop${NC}"
echo -e "  查看状态: ${CYAN}$DOCKER_COMPOSE -f docker-compose.production.yml ps${NC}"
echo ""

echo -e "${YELLOW}查看应用日志:${NC}"
echo -e "  ${CYAN}$DOCKER_COMPOSE -f docker-compose.production.yml logs -f app${NC}"
echo ""

