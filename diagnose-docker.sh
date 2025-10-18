#!/bin/bash
# CCD2 Docker部署诊断脚本

set +e  # 不要在错误时退出，我们要收集所有信息

CONTAINER_NAME="${1:-ccd_app_prod}"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "================================================================"
echo "        CCD2 Docker 部署诊断工具"
echo "================================================================"
echo ""
echo "容器名称: ${CONTAINER_NAME}"
echo ""

# 1. 检查Docker是否运行
echo -e "${BLUE}[1/10] 检查Docker服务...${NC}"
if systemctl is-active --quiet docker 2>/dev/null || docker info >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Docker服务正常运行"
else
    echo -e "${RED}✗${NC} Docker服务未运行或无权限访问"
    echo "   请运行: sudo systemctl start docker"
    exit 1
fi
echo ""

# 2. 检查容器状态
echo -e "${BLUE}[2/10] 检查容器状态...${NC}"
CONTAINER_STATUS=$(docker ps -a --filter "name=${CONTAINER_NAME}" --format "{{.Status}}")
if [ -z "$CONTAINER_STATUS" ]; then
    echo -e "${RED}✗${NC} 容器不存在"
    echo "   容器名称: ${CONTAINER_NAME}"
else
    if echo "$CONTAINER_STATUS" | grep -q "Up"; then
        echo -e "${GREEN}✓${NC} 容器正在运行"
        echo "   状态: $CONTAINER_STATUS"
    else
        echo -e "${RED}✗${NC} 容器已停止"
        echo "   状态: $CONTAINER_STATUS"
    fi
fi
echo ""

# 3. 检查容器日志
echo -e "${BLUE}[3/10] 检查容器启动日志 (最近50行)...${NC}"
if docker logs --tail 50 "${CONTAINER_NAME}" 2>&1 | head -20; then
    echo "..."
    echo "(完整日志请运行: docker logs ${CONTAINER_NAME})"
else
    echo -e "${RED}✗${NC} 无法获取容器日志"
fi
echo ""

# 4. 检查环境变量
echo -e "${BLUE}[4/10] 检查环境变量...${NC}"
if docker exec "${CONTAINER_NAME}" env 2>/dev/null | grep -E '^(DATABASE_URL|REDIS_URL|LOG_LEVEL|STORAGE_TYPE)=' | while read line; do
    VAR_NAME=$(echo "$line" | cut -d'=' -f1)
    VAR_VALUE=$(echo "$line" | cut -d'=' -f2-)
    
    # 隐藏密码
    if [[ "$VAR_NAME" == "DATABASE_URL" ]]; then
        SAFE_VALUE=$(echo "$VAR_VALUE" | sed 's|://[^:]*:[^@]*@|://***:***@|')
        echo "   $VAR_NAME = $SAFE_VALUE"
    else
        echo "   $VAR_NAME = $VAR_VALUE"
    fi
done; then
    :
else
    echo -e "${RED}✗${NC} 无法获取环境变量（容器可能未运行）"
fi
echo ""

# 5. 检查后端错误日志
echo -e "${BLUE}[5/10] 检查后端错误日志...${NC}"
if docker exec "${CONTAINER_NAME}" cat /var/log/supervisor/backend_err.log 2>/dev/null | tail -20; then
    :
else
    echo -e "${YELLOW}⚠${NC} 无法获取后端错误日志（容器可能未运行或日志文件不存在）"
fi
echo ""

# 6. 检查后端标准输出日志
echo -e "${BLUE}[6/10] 检查后端输出日志 (最近20行)...${NC}"
if docker exec "${CONTAINER_NAME}" cat /var/log/supervisor/backend.log 2>/dev/null | tail -20; then
    :
else
    echo -e "${YELLOW}⚠${NC} 无法获取后端输出日志"
fi
echo ""

# 7. 测试API健康检查
echo -e "${BLUE}[7/10] 测试API健康检查...${NC}"
HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/api/health 2>/dev/null)
if [ "$HEALTH_CHECK" = "200" ]; then
    echo -e "${GREEN}✓${NC} API健康检查通过"
    curl -s http://localhost/api/health | python3 -m json.tool 2>/dev/null || echo ""
else
    echo -e "${RED}✗${NC} API健康检查失败"
    echo "   HTTP状态码: ${HEALTH_CHECK:-无响应}"
    echo "   URL: http://localhost/api/health"
fi
echo ""

# 8. 检查端口监听
echo -e "${BLUE}[8/10] 检查端口监听...${NC}"
if docker port "${CONTAINER_NAME}" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} 端口映射正常"
else
    echo -e "${RED}✗${NC} 无端口映射（容器可能未运行）"
fi
echo ""

# 9. 检查数据库连接
echo -e "${BLUE}[9/10] 检查数据库连接...${NC}"
DB_CHECK=$(docker exec "${CONTAINER_NAME}" python3 -c "
import os
import sys
try:
    from sqlalchemy import create_engine, text
    engine = create_engine(os.getenv('DATABASE_URL'))
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
        print('✓ 数据库连接成功')
        sys.exit(0)
except Exception as e:
    print(f'✗ 数据库连接失败: {e}')
    sys.exit(1)
" 2>&1)
echo "$DB_CHECK"
echo ""

# 10. 检查Redis连接
echo -e "${BLUE}[10/10] 检查Redis连接...${NC}"
REDIS_CHECK=$(docker exec "${CONTAINER_NAME}" python3 -c "
import os
import sys
try:
    import redis
    from urllib.parse import urlparse
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    parsed = urlparse(redis_url)
    r = redis.Redis(
        host=parsed.hostname or 'localhost',
        port=parsed.port or 6379,
        db=int(parsed.path.lstrip('/')) if parsed.path else 0,
        socket_connect_timeout=5
    )
    r.ping()
    print('✓ Redis连接成功')
    sys.exit(0)
except Exception as e:
    print(f'⚠ Redis连接失败: {e}')
    print('  注意: Redis失败不影响应用运行')
    sys.exit(0)
" 2>&1)
echo "$REDIS_CHECK"
echo ""

# 总结
echo "================================================================"
echo "                    诊断总结"
echo "================================================================"
echo ""

# 给出建议
if [ "$HEALTH_CHECK" = "200" ]; then
    echo -e "${GREEN}✓ 应用运行正常${NC}"
    echo ""
    echo "访问地址:"
    echo "  - Web界面: http://localhost"
    echo "  - API文档: http://localhost/docs"
    echo "  - 健康检查: http://localhost/api/health"
else
    echo -e "${RED}✗ 应用存在问题${NC}"
    echo ""
    echo "建议操作:"
    echo "  1. 查看完整日志: docker logs -f ${CONTAINER_NAME}"
    echo "  2. 查看错误日志: docker exec ${CONTAINER_NAME} cat /var/log/supervisor/backend_err.log"
    echo "  3. 检查环境变量: docker exec ${CONTAINER_NAME} env"
    echo "  4. 重启容器: docker restart ${CONTAINER_NAME}"
    echo "  5. 查看部署指南: cat DOCKER_DEPLOYMENT_FIX.md"
fi

echo ""
echo "================================================================"
echo ""

# 提供额外命令
echo "有用的命令:"
echo "  - 查看实时日志: docker logs -f ${CONTAINER_NAME}"
echo "  - 进入容器: docker exec -it ${CONTAINER_NAME} bash"
echo "  - 重启容器: docker restart ${CONTAINER_NAME}"
echo "  - 停止容器: docker stop ${CONTAINER_NAME}"
echo "  - 删除容器: docker rm -f ${CONTAINER_NAME}"
echo ""

