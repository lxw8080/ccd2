#!/bin/bash
# CCD2 Docker镜像重新构建和导出脚本（Linux/Mac）
# 用于修复后端崩溃问题

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo ""
echo -e "${CYAN}================================================================${NC}"
echo -e "${CYAN}        CCD2 Docker 镜像重新构建和导出${NC}"
echo -e "${CYAN}================================================================${NC}"
echo ""

# 检查Docker
echo -e "${BLUE}[1/5] 检查Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker未安装${NC}"
    echo -e "${YELLOW}请先安装Docker: https://docs.docker.com/engine/install/${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker已安装: $(docker --version)${NC}"
echo ""

# 确认项目目录
echo -e "${BLUE}[2/5] 确认项目目录...${NC}"
if [ ! -f "Dockerfile" ]; then
    echo -e "${RED}✗ 未找到Dockerfile${NC}"
    echo -e "${YELLOW}请在项目根目录运行此脚本${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 当前目录: $(pwd)${NC}"
echo ""

# 构建镜像
echo -e "${BLUE}[3/5] 构建Docker镜像...${NC}"
echo -e "${YELLOW}这可能需要几分钟时间，请耐心等待...${NC}"
echo ""

BUILD_START=$(date +%s)
docker build -t ccd2-app:fixed .
BUILD_END=$(date +%s)
BUILD_DURATION=$((BUILD_END - BUILD_START))

echo ""
echo -e "${GREEN}✓ 镜像构建成功 (耗时: ${BUILD_DURATION}秒)${NC}"
echo ""

# 导出镜像
echo -e "${BLUE}[4/5] 导出并压缩镜像...${NC}"
EXPORT_FILE="ccd2-app-fixed.tar.gz"
echo "导出到: $EXPORT_FILE"

docker save ccd2-app:fixed | gzip > $EXPORT_FILE

echo -e "${GREEN}✓ 镜像已导出: $EXPORT_FILE${NC}"
echo ""

# 生成校验和
echo -e "${BLUE}[5/5] 生成校验和...${NC}"
HASH_FILE="${EXPORT_FILE}.sha256"
sha256sum $EXPORT_FILE > $HASH_FILE
HASH=$(cat $HASH_FILE | awk '{print $1}')
echo -e "${GREEN}✓ 校验和已生成: $HASH_FILE${NC}"
echo -e "   SHA256: $HASH"
echo ""

# 显示文件信息
FILE_SIZE=$(du -h $EXPORT_FILE | cut -f1)
echo -e "${CYAN}================================================================${NC}"
echo -e "${CYAN}                    完成${NC}"
echo -e "${CYAN}================================================================${NC}"
echo ""
echo -e "${GREEN}生成的文件:${NC}"
echo "  - $EXPORT_FILE ($FILE_SIZE)"
echo "  - $HASH_FILE"
echo ""
echo -e "${YELLOW}下一步操作:${NC}"
echo ""
echo -e "${NC}1. 将文件传输到Ubuntu服务器:${NC}"
echo -e "   ${CYAN}scp $EXPORT_FILE* user@server:/path/to/${NC}"
echo ""
echo -e "${NC}2. 在服务器上验证和加载镜像:${NC}"
echo -e "   ${CYAN}sha256sum -c $HASH_FILE${NC}"
echo -e "   ${CYAN}gunzip -c $EXPORT_FILE | docker load${NC}"
echo ""
echo -e "${NC}3. 运行容器（重要：配置正确的数据库地址）:${NC}"
echo -e "   ${CYAN}docker run -d \\${NC}"
echo -e "   ${CYAN}  --name ccd2-app \\${NC}"
echo -e "   ${CYAN}  -p 80:80 \\${NC}"
echo -e "   ${CYAN}  -e DATABASE_URL='postgresql://user:pass@数据库IP:端口/数据库名' \\${NC}"
echo -e "   ${CYAN}  -e REDIS_URL='redis://RedisIP:6379/0' \\${NC}"
echo -e "   ${CYAN}  -e SECRET_KEY='your-secret-key' \\${NC}"
echo -e "   ${CYAN}  -v /data/uploads:/app/uploads \\${NC}"
echo -e "   ${CYAN}  ccd2-app:fixed${NC}"
echo ""
echo -e "${NC}4. 查看日志验证启动:${NC}"
echo -e "   ${CYAN}docker logs -f ccd2-app${NC}"
echo ""
echo -e "   ${GREEN}你应该看到:${NC}"
echo -e "   ${GREEN}✅ Database connection: OK${NC}"
echo -e "   ${GREEN}✅ Redis connection: OK (或警告)${NC}"
echo -e "   ${GREEN}✅ All critical checks passed!${NC}"
echo ""
echo -e "${YELLOW}详细文档:${NC}"
echo "  - DEPLOYMENT_FIX_SUMMARY.md - 问题总结和快速修复"
echo "  - DOCKER_DEPLOYMENT_QUICKSTART.md - 完整部署指南"
echo "  - DOCKER_DEPLOYMENT_FIX.md - 详细修复文档"
echo ""
echo -e "${CYAN}================================================================${NC}"
echo ""

