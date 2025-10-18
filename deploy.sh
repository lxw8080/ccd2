#!/bin/bash
# CCD2 Docker 部署脚本
# 用于快速部署或更新应用

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "================================================================"
echo "        CCD2 Docker 部署脚本"
echo "================================================================"
echo ""

# 检查是否为root用户或有sudo权限
if [ "$EUID" -ne 0 ] && ! sudo -n true 2>/dev/null; then
    echo -e "${YELLOW}提示: 某些操作可能需要sudo权限${NC}"
fi

# 1. 检查Docker
echo -e "${BLUE}[1/7] 检查Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker未安装${NC}"
    echo "请先安装Docker: https://docs.docker.com/engine/install/"
    exit 1
fi
echo -e "${GREEN}✓ Docker已安装: $(docker --version)${NC}"
echo ""

# 2. 检查Docker Compose
echo -e "${BLUE}[2/7] 检查Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}✗ Docker Compose未安装${NC}"
    echo "请先安装Docker Compose"
    exit 1
fi
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
    echo -e "${GREEN}✓ Docker Compose已安装: $(docker-compose --version)${NC}"
else
    COMPOSE_CMD="docker compose"
    echo -e "${GREEN}✓ Docker Compose已安装: $(docker compose version)${NC}"
fi
echo ""

# 3. 检查配置文件
echo -e "${BLUE}[3/7] 检查配置文件...${NC}"
if [ ! -f ".env.production" ] && [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠ 未找到配置文件${NC}"
    echo ""
    echo "请创建配置文件:"
    echo "  cp env.production.example .env.production"
    echo ""
    echo "然后编辑 .env.production 文件，设置正确的数据库密码等配置"
    echo ""
    read -p "是否使用示例配置继续？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
    ENV_FILE="env.production.example"
    ENV_FLAG="--env-file ${ENV_FILE}"
else
    if [ -f ".env.production" ]; then
        ENV_FILE=".env.production"
    else
        ENV_FILE=".env"
    fi
    echo -e "${GREEN}✓ 找到配置文件: ${ENV_FILE}${NC}"
    ENV_FLAG="--env-file ${ENV_FILE}"
fi
echo ""

# 4. 选择部署模式
echo -e "${BLUE}[4/7] 选择部署模式...${NC}"
echo "1) 完整部署（包括PostgreSQL和Redis）"
echo "2) 仅部署应用（使用外部数据库）"
echo ""
read -p "请选择 [1-2]: " -n 1 -r
echo
echo ""

if [[ $REPLY == "1" ]]; then
    DEPLOY_MODE="full"
    COMPOSE_FILE="docker-compose.prod.yml"
    echo -e "${GREEN}✓ 选择: 完整部署${NC}"
else
    DEPLOY_MODE="app-only"
    COMPOSE_FILE="docker-compose.prod.yml"
    echo -e "${GREEN}✓ 选择: 仅部署应用${NC}"
    echo ""
    echo -e "${YELLOW}注意: 请确保已在 ${ENV_FILE} 中配置了外部数据库连接${NC}"
    echo ""
    read -p "按Enter继续..."
fi
echo ""

# 5. 构建或拉取镜像
echo -e "${BLUE}[5/7] 准备Docker镜像...${NC}"
if [ -f "Dockerfile" ]; then
    echo "检测到Dockerfile，是否要重新构建镜像？"
    read -p "(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "构建Docker镜像..."
        docker build -t ccd2-app:latest .
        echo -e "${GREEN}✓ 镜像构建完成${NC}"
    fi
else
    echo "未找到Dockerfile，将使用现有镜像"
fi
echo ""

# 6. 创建必要的目录
echo -e "${BLUE}[6/7] 创建必要的目录...${NC}"
mkdir -p uploads logs backups
chmod 777 uploads logs
echo -e "${GREEN}✓ 目录创建完成${NC}"
echo ""

# 7. 启动服务
echo -e "${BLUE}[7/7] 启动服务...${NC}"
if [ "$DEPLOY_MODE" == "full" ]; then
    echo "启动所有服务（数据库、Redis、应用）..."
    $COMPOSE_CMD -f $COMPOSE_FILE $ENV_FLAG up -d
else
    echo "仅启动应用服务..."
    $COMPOSE_CMD -f $COMPOSE_FILE $ENV_FLAG up -d app
fi

echo ""
echo -e "${GREEN}✓ 服务启动命令已执行${NC}"
echo ""

# 等待服务启动
echo "等待服务启动..."
sleep 5

# 检查服务状态
echo ""
echo -e "${BLUE}检查服务状态...${NC}"
$COMPOSE_CMD -f $COMPOSE_FILE ps
echo ""

# 测试健康检查
echo -e "${BLUE}测试API健康检查...${NC}"
sleep 5
for i in {1..6}; do
    if curl -s http://localhost/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ API健康检查通过${NC}"
        break
    else
        if [ $i -eq 6 ]; then
            echo -e "${YELLOW}⚠ API尚未响应，可能还在启动中${NC}"
        else
            echo "等待API启动... ($i/6)"
            sleep 5
        fi
    fi
done
echo ""

# 显示日志
echo "最近的日志："
echo "---"
$COMPOSE_CMD -f $COMPOSE_FILE logs --tail=20 app
echo "---"
echo ""

# 完成
echo "================================================================"
echo "                    部署完成"
echo "================================================================"
echo ""
echo "访问地址:"
echo "  - Web界面: http://localhost"
echo "  - Web界面: http://$(hostname -I | awk '{print $1}')"
echo "  - API文档: http://localhost/docs"
echo "  - 健康检查: http://localhost/api/health"
echo ""
echo "有用的命令:"
echo "  - 查看日志: $COMPOSE_CMD -f $COMPOSE_FILE logs -f app"
echo "  - 查看状态: $COMPOSE_CMD -f $COMPOSE_FILE ps"
echo "  - 重启服务: $COMPOSE_CMD -f $COMPOSE_FILE restart"
echo "  - 停止服务: $COMPOSE_CMD -f $COMPOSE_FILE down"
echo "  - 运行诊断: bash diagnose-docker.sh ccd_app_prod"
echo ""
echo "如果遇到问题，请查看:"
echo "  - 部署文档: cat DOCKER_DEPLOYMENT_FIX.md"
echo "  - 诊断工具: bash diagnose-docker.sh"
echo ""

