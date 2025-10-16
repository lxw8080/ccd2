@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ========================================
echo 客户资料收集系统 - 项目启动脚本
echo ========================================
echo.

REM 检查 Python
echo 检查 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 未安装或不在 PATH 中
    pause
    exit /b 1
)
echo ✅ Python 已安装

REM 检查 Node.js
echo 检查 Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js 未安装或不在 PATH 中
    pause
    exit /b 1
)
echo ✅ Node.js 已安装

echo.
echo 启动后端服务...
echo.

REM 启动后端
cd /d "%~dp0backend"
if not exist "venv\Scripts\activate.bat" (
    echo ❌ 后端虚拟环境不存在
    echo 请先运行: python -m venv backend\venv
    pause
    exit /b 1
)

echo 启动后端 (端口 8000)...
start "Backend - CCD" cmd /k "venv\Scripts\activate.bat && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 3 /nobreak

echo.
echo 启动前端服务...
echo.

REM 启动前端
cd /d "%~dp0frontend"
if not exist "package.json" (
    echo ❌ 前端目录不存在或不完整
    pause
    exit /b 1
)

echo 启动前端 (端口 5173)...
start "Frontend - CCD" cmd /k "npm run dev"
timeout /t 3 /nobreak

echo.
echo ========================================
echo ✅ 项目启动完成！
echo ========================================
echo.
echo 访问地址:
echo   前端:     http://localhost:5173
echo   后端 API: http://localhost:8000
echo   API 文档: http://localhost:8000/docs
echo.
echo 按任意键关闭此窗口...
pause >nul

