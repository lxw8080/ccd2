# Docker容器诊断脚本
# 用于查看容器内的详细日志和状态

param(
    [string]$ContainerName = "ccd2"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Docker容器诊断工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查容器是否存在
Write-Host "1. 检查容器状态..." -ForegroundColor Yellow
docker ps -a --filter "name=$ContainerName" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
Write-Host ""

# 查看Supervisor日志
Write-Host "2. 查看Supervisor主日志..." -ForegroundColor Yellow
docker exec $ContainerName cat /var/log/supervisor/supervisord.log 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "无法读取Supervisor日志" -ForegroundColor Red
}
Write-Host ""

# 查看后端错误日志
Write-Host "3. 查看后端错误日志 (最后50行)..." -ForegroundColor Yellow
docker exec $ContainerName tail -n 50 /var/log/supervisor/backend_err.log 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "无法读取后端错误日志" -ForegroundColor Red
}
Write-Host ""

# 查看后端标准输出日志
Write-Host "4. 查看后端标准输出日志 (最后50行)..." -ForegroundColor Yellow
docker exec $ContainerName tail -n 50 /var/log/supervisor/backend.log 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "无法读取后端标准输出日志" -ForegroundColor Red
}
Write-Host ""

# 查看Nginx错误日志
Write-Host "5. 查看Nginx错误日志 (最后30行)..." -ForegroundColor Yellow
docker exec $ContainerName tail -n 30 /var/log/supervisor/nginx_err.log 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "无法读取Nginx错误日志" -ForegroundColor Red
}
Write-Host ""

# 检查环境变量
Write-Host "6. 检查环境变量配置..." -ForegroundColor Yellow
docker exec $ContainerName env | Select-String -Pattern "DATABASE_URL|REDIS_URL|SECRET_KEY|LOG_LEVEL"
Write-Host ""

# 检查进程状态
Write-Host "7. 检查容器内进程状态..." -ForegroundColor Yellow
docker exec $ContainerName ps aux
Write-Host ""

# 测试数据库连接
Write-Host "8. 测试数据库连接..." -ForegroundColor Yellow
docker exec $ContainerName bash -c 'python3 -c "import os; print(\"DATABASE_URL:\", os.getenv(\"DATABASE_URL\"))"' 2>$null
Write-Host ""

# 检查Python包
Write-Host "9. 检查关键Python包..." -ForegroundColor Yellow
docker exec $ContainerName pip list | Select-String -Pattern "fastapi|uvicorn|sqlalchemy|psycopg2|redis"
Write-Host ""

# 尝试手动启动后端查看错误
Write-Host "10. 尝试手动启动后端查看详细错误..." -ForegroundColor Yellow
Write-Host "执行命令: cd /app/backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000" -ForegroundColor Gray
docker exec $ContainerName bash -c 'cd /app/backend && timeout 5 python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 2>&1 || true'
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "诊断完成" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "常见问题和解决方案:" -ForegroundColor Yellow
Write-Host "1. 数据库连接失败: 检查DATABASE_URL是否正确,数据库服务器是否可访问" -ForegroundColor White
Write-Host "2. Redis连接失败: 检查REDIS_URL是否正确,Redis服务器是否可访问" -ForegroundColor White
Write-Host "3. 模块导入错误: 检查Python依赖是否完整安装" -ForegroundColor White
Write-Host "4. 权限问题: 检查/app/uploads和/app/logs目录权限" -ForegroundColor White
Write-Host ""
Write-Host "查看实时日志:" -ForegroundColor Yellow
Write-Host "  docker logs -f $ContainerName" -ForegroundColor White
Write-Host ""
Write-Host "进入容器调试:" -ForegroundColor Yellow
Write-Host "  docker exec -it $ContainerName /bin/bash" -ForegroundColor White

