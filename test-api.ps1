# API 测试脚本
# 测试后端 API 的基本功能

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "API 测试脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:8000"
$apiUrl = "$baseUrl/api"

# 测试 1: 检查 API 是否可用
Write-Host "测试 1: 检查 API 可用性..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/docs" -UseBasicParsing -ErrorAction Stop
    Write-Host "✅ API 可用 (HTTP $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "❌ API 不可用: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 测试 2: 创建用户
Write-Host "测试 2: 创建管理员用户..." -ForegroundColor Yellow
$userData = @{
    username = "admin"
    password = "admin123"
    real_name = "管理员"
    role = "admin"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "$apiUrl/auth/register" `
        -Method POST `
        -ContentType "application/json" `
        -Body $userData `
        -UseBasicParsing -ErrorAction Stop
    Write-Host "✅ 用户创建成功" -ForegroundColor Green
    $user = $response.Content | ConvertFrom-Json
    Write-Host "   用户 ID: $($user.id)" -ForegroundColor Cyan
} catch {
    Write-Host "⚠️  用户创建失败: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host ""

# 测试 3: 用户登录
Write-Host "测试 3: 用户登录..." -ForegroundColor Yellow
$loginData = @{
    username = "admin"
    password = "admin123"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "$apiUrl/auth/login" `
        -Method POST `
        -ContentType "application/json" `
        -Body $loginData `
        -UseBasicParsing -ErrorAction Stop
    Write-Host "✅ 登录成功" -ForegroundColor Green
    $token = ($response.Content | ConvertFrom-Json).access_token
    Write-Host "   Token: $($token.Substring(0, 20))..." -ForegroundColor Cyan
} catch {
    Write-Host "⚠️  登录失败: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host ""

# 测试 4: 创建产品
Write-Host "测试 4: 创建贷款产品..." -ForegroundColor Yellow
$productData = @{
    code = "PRODUCT001"
    name = "个人消费贷"
    description = "用于个人消费的贷款产品"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "$apiUrl/products" `
        -Method POST `
        -ContentType "application/json" `
        -Body $productData `
        -Headers @{ Authorization = "Bearer $token" } `
        -UseBasicParsing -ErrorAction Stop
    Write-Host "✅ 产品创建成功" -ForegroundColor Green
    $product = $response.Content | ConvertFrom-Json
    Write-Host "   产品 ID: $($product.id)" -ForegroundColor Cyan
} catch {
    Write-Host "⚠️  产品创建失败: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host ""

# 测试 5: 获取产品列表
Write-Host "测试 5: 获取产品列表..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$apiUrl/products" `
        -Method GET `
        -Headers @{ Authorization = "Bearer $token" } `
        -UseBasicParsing -ErrorAction Stop
    Write-Host "✅ 获取产品列表成功" -ForegroundColor Green
    $products = $response.Content | ConvertFrom-Json
    Write-Host "   产品数量: $($products.Count)" -ForegroundColor Cyan
} catch {
    Write-Host "⚠️  获取产品列表失败: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ API 测试完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "访问 API 文档: $baseUrl/docs" -ForegroundColor Yellow
Write-Host ""

