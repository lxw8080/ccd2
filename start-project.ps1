# 项目启动脚本
# 用法: .\start-project.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "客户资料收集系统 - 项目启动脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 PostgreSQL
Write-Host "检查 PostgreSQL..." -ForegroundColor Yellow
$pgService = Get-Service -Name "PostgreSQL15" -ErrorAction SilentlyContinue
if ($pgService -and $pgService.Status -eq "Running") {
    Write-Host "✅ PostgreSQL 已运行" -ForegroundColor Green
} else {
    Write-Host "⚠️  PostgreSQL 未运行，请先启动 PostgreSQL" -ForegroundColor Red
    Write-Host "   Windows: 使用 Services 应用启动 PostgreSQL15" -ForegroundColor Yellow
    Write-Host "   或运行: net start PostgreSQL15" -ForegroundColor Yellow
}

# 检查 Redis
Write-Host "检查 Redis..." -ForegroundColor Yellow
$redisProcess = Get-Process -Name "redis-server" -ErrorAction SilentlyContinue
if ($redisProcess) {
    Write-Host "✅ Redis 已运行" -ForegroundColor Green
} else {
    Write-Host "⚠️  Redis 未运行，请先启动 Redis" -ForegroundColor Red
    Write-Host "   运行: redis-server" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "启动后端服务..." -ForegroundColor Cyan
Write-Host ""

# 启动后端
$backendPath = Join-Path $PSScriptRoot "backend"
$backendVenv = Join-Path $backendPath "venv\Scripts\Activate.ps1"

if (Test-Path $backendVenv) {
    Write-Host "启动后端 (端口 8000)..." -ForegroundColor Green
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; & '$backendVenv'; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    Start-Sleep -Seconds 3
} else {
    Write-Host "❌ 后端虚拟环境不存在，请先运行: python -m venv backend\venv" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "启动前端服务..." -ForegroundColor Cyan
Write-Host ""

# 启动前端
$frontendPath = Join-Path $PSScriptRoot "frontend"
if (Test-Path $frontendPath) {
    Write-Host "启动前端 (端口 5173)..." -ForegroundColor Green
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; npm run dev"
    Start-Sleep -Seconds 3
} else {
    Write-Host "❌ 前端目录不存在" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ 项目启动完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "访问地址:" -ForegroundColor Yellow
Write-Host "  前端:     http://localhost:5173" -ForegroundColor Cyan
Write-Host "  后端 API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "  API 文档: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "按 Ctrl+C 停止服务" -ForegroundColor Yellow
Write-Host ""

