@echo off
chcp 65001 >nul
echo 🚀 客户资料收集系统 - 启动脚本
echo ================================
echo.

REM 检查Docker是否安装
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker未安装，请先安装Docker Desktop
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose未安装，请先安装Docker Compose
    pause
    exit /b 1
)

echo ✅ Docker环境检查通过
echo.

REM 检查.env文件
if not exist "backend\.env" (
    echo 📝 创建后端环境变量文件...
    copy "backend\.env.example" "backend\.env" >nul
    echo ✅ 已创建 backend\.env，请根据需要修改配置
)

if not exist "frontend\.env" (
    echo 📝 创建前端环境变量文件...
    copy "frontend\.env.example" "frontend\.env" >nul
    echo ✅ 已创建 frontend\.env
)

echo.
echo 🐳 启动Docker容器...
docker-compose up -d

echo.
echo ⏳ 等待服务启动...
timeout /t 5 /nobreak >nul

echo.
echo ✅ 服务启动完成！
echo.
echo 📍 访问地址：
echo    前端应用: http://localhost:5173
echo    后端API:  http://localhost:8000
echo    API文档:  http://localhost:8000/docs
echo.
echo 📊 查看日志：
echo    docker-compose logs -f
echo.
echo 🛑 停止服务：
echo    docker-compose down
echo.
pause

