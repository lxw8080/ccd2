# Docker容器运行脚本 (Windows PowerShell版本)
# 用于在服务器上正确配置和运行CCD2容器

param(
    [string]$ContainerName = "ccd2",
    [string]$ImageName = "ccd2-app:latest",
    [int]$HostPort = 8080
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CCD2 Docker容器启动脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查Docker是否安装
try {
    docker --version | Out-Null
} catch {
    Write-Host "错误: Docker未安装或未运行" -ForegroundColor Red
    exit 1
}

# 检查镜像是否存在
$imageExists = docker images --format "{{.Repository}}:{{.Tag}}" | Select-String -Pattern "^ccd2-app:latest$"
if (-not $imageExists) {
    Write-Host "错误: Docker镜像 ccd2-app:latest 不存在" -ForegroundColor Red
    Write-Host "请先使用以下命令加载镜像:" -ForegroundColor Yellow
    Write-Host "  docker load -i ccd2-app-latest.tar" -ForegroundColor White
    exit 1
}

# 停止并删除已存在的容器
$existingContainer = docker ps -a --filter "name=$ContainerName" --format "{{.Names}}"
if ($existingContainer) {
    Write-Host "停止并删除已存在的容器..." -ForegroundColor Yellow
    docker stop $ContainerName 2>$null | Out-Null
    docker rm $ContainerName 2>$null | Out-Null
    Write-Host "✓ 已清理旧容器" -ForegroundColor Green
}

# 提示用户输入配置
Write-Host "请输入配置信息 (按Enter使用默认值):" -ForegroundColor Yellow
Write-Host ""

# 数据库配置
$dbHost = Read-Host "数据库主机 [localhost]"
if ([string]::IsNullOrWhiteSpace($dbHost)) { $dbHost = "localhost" }

$dbPort = Read-Host "数据库端口 [5432]"
if ([string]::IsNullOrWhiteSpace($dbPort)) { $dbPort = "5432" }

$dbName = Read-Host "数据库名称 [ccd_db]"
if ([string]::IsNullOrWhiteSpace($dbName)) { $dbName = "ccd_db" }

$dbUser = Read-Host "数据库用户名 [ccd_user]"
if ([string]::IsNullOrWhiteSpace($dbUser)) { $dbUser = "ccd_user" }

$dbPasswordSecure = Read-Host "数据库密码 [ccd_password]" -AsSecureString
$dbPassword = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($dbPasswordSecure)
)
if ([string]::IsNullOrWhiteSpace($dbPassword)) { $dbPassword = "ccd_password" }

$databaseUrl = "postgresql://${dbUser}:${dbPassword}@${dbHost}:${dbPort}/${dbName}"

# Redis配置
$redisHost = Read-Host "Redis主机 [localhost]"
if ([string]::IsNullOrWhiteSpace($redisHost)) { $redisHost = "localhost" }

$redisPort = Read-Host "Redis端口 [6379]"
if ([string]::IsNullOrWhiteSpace($redisPort)) { $redisPort = "6379" }

$redisDb = Read-Host "Redis数据库编号 [0]"
if ([string]::IsNullOrWhiteSpace($redisDb)) { $redisDb = "0" }

$redisUrl = "redis://${redisHost}:${redisPort}/${redisDb}"

# 密钥配置
$secretKeySecure = Read-Host "JWT密钥 (留空自动生成)" -AsSecureString
$secretKey = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secretKeySecure)
)
if ([string]::IsNullOrWhiteSpace($secretKey)) {
    # 生成随机密钥
    $secretKey = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 64 | ForEach-Object {[char]$_})
    Write-Host "✓ 已自动生成密钥" -ForegroundColor Green
}

# 端口配置
$hostPortInput = Read-Host "主机端口 [$HostPort]"
if (-not [string]::IsNullOrWhiteSpace($hostPortInput)) { 
    $HostPort = [int]$hostPortInput 
}

# 创建数据卷目录
Write-Host ""
Write-Host "创建数据卷目录..." -ForegroundColor Yellow
$uploadsDir = Join-Path $PSScriptRoot "docker-volumes\uploads"
$logsDir = Join-Path $PSScriptRoot "docker-volumes\logs"

New-Item -ItemType Directory -Force -Path $uploadsDir | Out-Null
New-Item -ItemType Directory -Force -Path $logsDir | Out-Null
Write-Host "✓ 数据卷目录已创建" -ForegroundColor Green

# 显示配置摘要
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "配置摘要" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "容器名称: " -NoNewline; Write-Host $ContainerName -ForegroundColor Green
Write-Host "镜像名称: " -NoNewline; Write-Host $ImageName -ForegroundColor Green
Write-Host "主机端口: " -NoNewline; Write-Host $HostPort -ForegroundColor Green
Write-Host "数据库URL: " -NoNewline; Write-Host $databaseUrl -ForegroundColor Green
Write-Host "Redis URL: " -NoNewline; Write-Host $redisUrl -ForegroundColor Green
Write-Host "上传目录: " -NoNewline; Write-Host $uploadsDir -ForegroundColor Green
Write-Host "日志目录: " -NoNewline; Write-Host $logsDir -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 确认启动
$confirm = Read-Host "是否继续启动容器? (y/n) [y]"
if ([string]::IsNullOrWhiteSpace($confirm)) { $confirm = "y" }
if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "已取消" -ForegroundColor Yellow
    exit 0
}

# 启动容器
Write-Host ""
Write-Host "启动Docker容器..." -ForegroundColor Yellow

$dockerCmd = @(
    "run", "-d",
    "--name", $ContainerName,
    "-p", "${HostPort}:80",
    "-e", "DATABASE_URL=$databaseUrl",
    "-e", "REDIS_URL=$redisUrl",
    "-e", "SECRET_KEY=$secretKey",
    "-e", "ALGORITHM=HS256",
    "-e", "ACCESS_TOKEN_EXPIRE_MINUTES=30",
    "-e", "STORAGE_TYPE=local",
    "-e", "UPLOAD_DIR=/app/uploads",
    "-e", "LOG_LEVEL=INFO",
    "-e", "APP_NAME=客户资料收集系统",
    "-e", "APP_VERSION=1.0.0",
    "-v", "${uploadsDir}:/app/uploads",
    "-v", "${logsDir}:/app/logs",
    "--restart", "unless-stopped",
    $ImageName
)

try {
    & docker $dockerCmd
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ 容器启动成功" -ForegroundColor Green
    } else {
        Write-Host "✗ 容器启动失败" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ 容器启动失败: $_" -ForegroundColor Red
    exit 1
}

# 等待容器启动
Write-Host ""
Write-Host "等待容器启动 (最多60秒)..." -ForegroundColor Yellow
$started = $false
for ($i = 1; $i -le 60; $i++) {
    $containerRunning = docker ps --filter "name=$ContainerName" --format "{{.Names}}"
    if ($containerRunning) {
        # 检查后端进程
        $backendRunning = docker exec $ContainerName pgrep -f uvicorn 2>$null
        if ($backendRunning) {
            Write-Host "✓ 容器已启动并运行" -ForegroundColor Green
            $started = $true
            break
        }
    }
    
    Write-Host "." -NoNewline
    Start-Sleep -Seconds 1
}
Write-Host ""

if (-not $started) {
    Write-Host "✗ 容器启动超时或后端进程未运行" -ForegroundColor Red
    Write-Host "查看日志:" -ForegroundColor Yellow
    docker logs $ContainerName | Select-Object -Last 30
    Write-Host ""
    Write-Host "建议使用诊断脚本查看详细信息:" -ForegroundColor Yellow
    Write-Host "  .\docker-diagnose.ps1" -ForegroundColor White
    exit 1
}

# 显示容器状态
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "容器状态" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
docker ps --filter "name=$ContainerName" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
Write-Host ""

# 检查日志中是否有错误
Write-Host "检查启动日志..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
$logs = docker logs $ContainerName 2>&1 | Select-Object -Last 20

$hasErrors = $logs | Select-String -Pattern "error|exception|failed|exited" -SimpleMatch
if ($hasErrors) {
    Write-Host "⚠ 发现错误日志:" -ForegroundColor Red
    $logs | ForEach-Object { Write-Host $_ }
    Write-Host ""
    Write-Host "建议操作:" -ForegroundColor Yellow
    Write-Host "1. 运行诊断脚本: .\docker-diagnose.ps1" -ForegroundColor White
    Write-Host "2. 查看详细日志: docker logs -f $ContainerName" -ForegroundColor White
    Write-Host "3. 进入容器调试: docker exec -it $ContainerName /bin/bash" -ForegroundColor White
} else {
    Write-Host "✓ 未发现明显错误" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "部署完成!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "访问地址: " -NoNewline
Write-Host "http://localhost:$HostPort" -ForegroundColor Green
Write-Host "或使用服务器IP: " -NoNewline
Write-Host "http://<服务器IP>:$HostPort" -ForegroundColor Green
Write-Host ""
Write-Host "常用命令:" -ForegroundColor Yellow
Write-Host "  查看日志: " -NoNewline; Write-Host "docker logs -f $ContainerName" -ForegroundColor Green
Write-Host "  停止容器: " -NoNewline; Write-Host "docker stop $ContainerName" -ForegroundColor Green
Write-Host "  启动容器: " -NoNewline; Write-Host "docker start $ContainerName" -ForegroundColor Green
Write-Host "  重启容器: " -NoNewline; Write-Host "docker restart $ContainerName" -ForegroundColor Green
Write-Host "  进入容器: " -NoNewline; Write-Host "docker exec -it $ContainerName /bin/bash" -ForegroundColor Green
Write-Host "  运行诊断: " -NoNewline; Write-Host ".\docker-diagnose.ps1" -ForegroundColor Green
Write-Host ""

