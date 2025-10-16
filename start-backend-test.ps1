# 启动后端测试服务器
# 使用 SQLite 数据库，无需 PostgreSQL 和 Redis

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "启动后端测试服务器" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 设置环境变量
$env:ENV_FILE = "backend/.env.test"

# 进入后端目录
cd backend

# 激活虚拟环境
Write-Host "激活虚拟环境..." -ForegroundColor Yellow
if (Test-Path "venv\Scripts\Activate.ps1") {
    & "venv\Scripts\Activate.ps1"
} else {
    Write-Host "❌ 虚拟环境不存在，请先运行: python -m venv backend\venv" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "启动后端服务器..." -ForegroundColor Green
Write-Host "访问地址: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API 文档: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

# 启动服务器
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

