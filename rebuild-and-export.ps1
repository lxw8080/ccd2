# CCD2 Docker镜像重新构建和导出脚本（Windows PowerShell）
# 用于修复后端崩溃问题

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "        CCD2 Docker 镜像重新构建和导出" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# 检查Docker
Write-Host "[1/5] 检查Docker..." -ForegroundColor Blue
try {
    $dockerVersion = docker --version
    Write-Host "✓ Docker已安装: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker未安装或未运行" -ForegroundColor Red
    Write-Host "请先安装Docker Desktop: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# 确认项目目录
Write-Host "[2/5] 确认项目目录..." -ForegroundColor Blue
if (-not (Test-Path "Dockerfile")) {
    Write-Host "✗ 未找到Dockerfile" -ForegroundColor Red
    Write-Host "请在项目根目录运行此脚本" -ForegroundColor Yellow
    exit 1
}
Write-Host "✓ 当前目录: $(Get-Location)" -ForegroundColor Green
Write-Host ""

# 构建镜像
Write-Host "[3/5] 构建Docker镜像..." -ForegroundColor Blue
Write-Host "这可能需要几分钟时间，请耐心等待..." -ForegroundColor Yellow
Write-Host ""

$buildStart = Get-Date
docker build -t ccd2-app:fixed .

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "✗ 镜像构建失败" -ForegroundColor Red
    exit 1
}

$buildEnd = Get-Date
$buildDuration = ($buildEnd - $buildStart).TotalSeconds
Write-Host ""
Write-Host "✓ 镜像构建成功 (耗时: $([math]::Round($buildDuration, 2))秒)" -ForegroundColor Green
Write-Host ""

# 导出镜像
Write-Host "[4/5] 导出镜像..." -ForegroundColor Blue
$exportFile = "ccd2-app-fixed.tar"
$exportFileGz = "ccd2-app-fixed.tar.gz"

Write-Host "导出到: $exportFile" -ForegroundColor Gray

# 先导出为tar
docker save ccd2-app:fixed -o $exportFile

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ 镜像导出失败" -ForegroundColor Red
    exit 1
}

# 如果有7zip，使用它压缩；否则保持tar格式
if (Get-Command 7z -ErrorAction SilentlyContinue) {
    Write-Host "使用7zip压缩..." -ForegroundColor Gray
    7z a -tgzip $exportFileGz $exportFile
    Remove-Item $exportFile
    $finalFile = $exportFileGz
} else {
    Write-Host "未安装7zip，跳过压缩" -ForegroundColor Yellow
    Write-Host "提示: 可以手动压缩 $exportFile 以减小文件大小" -ForegroundColor Yellow
    $finalFile = $exportFile
}

Write-Host "✓ 镜像已导出: $finalFile" -ForegroundColor Green
Write-Host ""

# 生成校验和
Write-Host "[5/5] 生成校验和..." -ForegroundColor Blue
$hash = Get-FileHash -Path $finalFile -Algorithm SHA256
$hashFile = "$finalFile.sha256"
$hash.Hash + "  " + $finalFile | Out-File -FilePath $hashFile -Encoding ASCII
Write-Host "✓ 校验和已生成: $hashFile" -ForegroundColor Green
Write-Host "   SHA256: $($hash.Hash)" -ForegroundColor Gray
Write-Host ""

# 显示文件信息
$fileSize = (Get-Item $finalFile).Length / 1MB
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "                    完成" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "生成的文件:" -ForegroundColor Green
Write-Host "  - $finalFile ($([math]::Round($fileSize, 2)) MB)" -ForegroundColor White
Write-Host "  - $hashFile" -ForegroundColor White
Write-Host ""
Write-Host "下一步操作:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. 将文件传输到Ubuntu服务器:" -ForegroundColor White
Write-Host "   scp $finalFile* user@server:/path/to/" -ForegroundColor Gray
Write-Host ""
Write-Host "2. 在服务器上加载镜像:" -ForegroundColor White
if ($finalFile -match ".gz$") {
    Write-Host "   gunzip -c $finalFile | docker load" -ForegroundColor Gray
} else {
    Write-Host "   docker load -i $finalFile" -ForegroundColor Gray
}
Write-Host ""
Write-Host "3. 运行容器（重要：配置正确的数据库地址）:" -ForegroundColor White
Write-Host "   docker run -d \" -ForegroundColor Gray
Write-Host "     --name ccd2-app \" -ForegroundColor Gray
Write-Host "     -p 80:80 \" -ForegroundColor Gray
Write-Host "     -e DATABASE_URL='postgresql://user:pass@数据库IP:端口/数据库名' \" -ForegroundColor Gray
Write-Host "     -e REDIS_URL='redis://RedisIP:6379/0' \" -ForegroundColor Gray
Write-Host "     -e SECRET_KEY='your-secret-key' \" -ForegroundColor Gray
Write-Host "     -v /data/uploads:/app/uploads \" -ForegroundColor Gray
Write-Host "     ccd2-app:fixed" -ForegroundColor Gray
Write-Host ""
Write-Host "4. 查看日志验证启动:" -ForegroundColor White
Write-Host "   docker logs -f ccd2-app" -ForegroundColor Gray
Write-Host ""
Write-Host "详细文档:" -ForegroundColor Yellow
Write-Host "  - DEPLOYMENT_FIX_SUMMARY.md - 问题总结和快速修复" -ForegroundColor White
Write-Host "  - DOCKER_DEPLOYMENT_QUICKSTART.md - 完整部署指南" -ForegroundColor White
Write-Host "  - DOCKER_DEPLOYMENT_FIX.md - 详细修复文档" -ForegroundColor White
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

