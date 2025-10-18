# CCD2 Docker镜像部署指南 (修复版)

## ✅ 修复完成!

所有问题已修复,新镜像已成功构建和测试。

---

## 📦 镜像信息

- **镜像名称**: ccd2-app:latest
- **镜像大小**: 656MB
- **导出文件**: ccd2-app-fixed.tar
- **文件大小**: 676MB (676,789,248 字节)
- **SHA256**: `B9F4852EEA1AAAC58ED449518D783C1FB9112F34DC4C0ACF140A64AFBFDB7BDD`
- **构建时间**: 2025-10-18 19:06

---

## 🔧 修复内容

### 1. ✅ 健康检查路由统一
- **修改前**: `/health` (无法通过Nginx访问)
- **修改后**: `/api/health` (统一API路由规范)

### 2. ✅ 添加智能启动脚本
- 自动检查必需的环境变量
- 在Docker Desktop环境中自动将`localhost`替换为`host.docker.internal`
- 提供清晰的配置信息和错误提示

### 3. ✅ 优化容器启动流程
- 使用ENTRYPOINT而不是CMD
- 更好的环境变量处理
- 自动创建必要的目录

---

## 🚀 本机测试 (Windows Docker Desktop)

### 启动容器

```powershell
docker run -d `
  --name ccd2 `
  -p 8080:80 `
  -e DATABASE_URL="postgresql://flask_user:flask_password@115.190.29.10:5433/ccd_db_new" `
  -e REDIS_URL="redis://host.docker.internal:6379/0" `
  -e SECRET_KEY="your-random-secret-key" `
  ccd2-app:latest
```

**注意**: 
- 使用 `host.docker.internal` 访问宿主机的Redis
- 数据库已经使用实际IP地址

### 验证服务

```powershell
# 1. 检查容器状态
docker ps

# 2. 查看启动日志
docker logs ccd2

# 3. 测试健康检查
curl http://localhost:8080/api/health
# 预期输出: {"status":"healthy"}

# 4. 测试前端
curl http://localhost:8080/
# 预期输出: HTML页面

# 5. 在浏览器中访问
# http://localhost:8080
```

---

## 🌐 服务器部署

### 步骤 1: 传输文件

将以下文件传输到服务器:
- `ccd2-app-fixed.tar` (Docker镜像)
- `ccd2-app-fixed.tar.sha256` (SHA256校验文件)

### 步骤 2: 验证文件完整性

**Linux:**
```bash
sha256sum -c ccd2-app-fixed.tar.sha256
```

**Windows PowerShell:**
```powershell
$hash = Get-FileHash -Algorithm SHA256 ccd2-app-fixed.tar
$expected = Get-Content ccd2-app-fixed.tar.sha256
if ($hash.Hash -eq $expected.Split()[0]) {
    Write-Host "✓ 文件完整性验证通过" -ForegroundColor Green
} else {
    Write-Host "✗ 文件完整性验证失败" -ForegroundColor Red
}
```

### 步骤 3: 加载镜像

```bash
docker load -i ccd2-app-fixed.tar
```

### 步骤 4: 配置环境变量

**重要**: 必须正确配置以下环境变量:

1. **DATABASE_URL** - 数据库连接URL
   ```
   postgresql://用户名:密码@数据库主机IP:端口/数据库名
   ```
   示例: `postgresql://flask_user:flask_password@115.190.29.10:5433/ccd_db_new`

2. **REDIS_URL** - Redis连接URL
   ```
   redis://Redis主机IP:端口/数据库编号
   ```
   示例: `redis://192.168.1.100:6379/0`
   
   **⚠️ 重要**: 
   - 不要使用 `localhost`
   - 使用实际的Redis服务器IP地址
   - 如果Redis在同一台服务器上,使用服务器的内网IP

3. **SECRET_KEY** - JWT密钥 (必须是随机字符串)
   ```bash
   # 生成随机密钥
   openssl rand -hex 32
   ```

### 步骤 5: 启动容器

**基本命令:**
```bash
docker run -d \
  --name ccd2 \
  -p 8080:80 \
  -e DATABASE_URL="postgresql://flask_user:flask_password@115.190.29.10:5433/ccd_db_new" \
  -e REDIS_URL="redis://192.168.1.100:6379/0" \
  -e SECRET_KEY="$(openssl rand -hex 32)" \
  ccd2-app:latest
```

**完整配置 (推荐):**
```bash
docker run -d \
  --name ccd2 \
  -p 8080:80 \
  -e DATABASE_URL="postgresql://flask_user:flask_password@115.190.29.10:5433/ccd_db_new" \
  -e REDIS_URL="redis://192.168.1.100:6379/0" \
  -e SECRET_KEY="$(openssl rand -hex 32)" \
  -e ALGORITHM="HS256" \
  -e ACCESS_TOKEN_EXPIRE_MINUTES="30" \
  -e STORAGE_TYPE="local" \
  -e UPLOAD_DIR="/app/uploads" \
  -e LOG_LEVEL="INFO" \
  -v $(pwd)/docker-volumes/uploads:/app/uploads \
  -v $(pwd)/docker-volumes/logs:/app/logs \
  --restart unless-stopped \
  ccd2-app:latest
```

### 步骤 6: 监控启动

```bash
# 实时查看日志
docker logs -f ccd2
```

**成功的启动日志应该包含:**
```
=========================================
CCD2 Application Starting...
=========================================
Configuration:
  DATABASE_URL: postgresql://***
  REDIS_URL: redis://192.168.1.100:6379/0
  LOG_LEVEL: INFO
  STORAGE_TYPE: local

Starting services with Supervisor...
=========================================
INFO supervisord started with pid 1
INFO spawned: 'backend' with pid XX
INFO spawned: 'nginx' with pid XX
INFO success: backend entered RUNNING state
INFO success: nginx entered RUNNING state
```

**⚠️ 如果看到后端不断重启:**
```
WARN exited: backend (exit status 3; not expected)
```
这表示数据库或Redis连接失败,请检查环境变量配置。

### 步骤 7: 验证部署

```bash
# 1. 检查容器状态
docker ps --filter "name=ccd2"

# 2. 测试健康检查
curl http://localhost:8080/api/health

# 3. 测试前端
curl http://localhost:8080/

# 4. 在浏览器中访问
# http://<服务器IP>:8080
```

---

## 🔍 故障排查

### 问题 1: 后端不断重启

**症状:**
```
WARN exited: backend (exit status 3; not expected)
```

**原因**: 数据库或Redis连接失败

**解决方案:**
1. 查看详细错误日志:
   ```bash
   docker exec ccd2 tail -n 100 /var/log/supervisor/backend_err.log
   ```

2. 检查环境变量:
   ```bash
   docker exec ccd2 env | grep -E "DATABASE_URL|REDIS_URL"
   ```

3. 测试数据库连接:
   ```bash
   docker exec ccd2 pg_isready -h 115.190.29.10 -p 5433
   ```

4. 测试Redis连接:
   ```bash
   docker exec ccd2 redis-cli -h <Redis主机IP> -p 6379 ping
   ```

### 问题 2: 无法访问应用

**检查清单:**
- [ ] 容器是否正在运行: `docker ps`
- [ ] 端口是否正确映射: `docker port ccd2`
- [ ] 防火墙是否允许8080端口
- [ ] 后端服务是否正常运行 (查看日志)

### 问题 3: 健康检查失败

**检查:**
```bash
# 从容器内部测试
docker exec ccd2 curl http://localhost/api/health
```

如果容器内部可以访问但外部不行,检查端口映射和防火墙。

---

## 📝 常用命令

```bash
# 查看日志
docker logs ccd2
docker logs -f ccd2  # 实时查看

# 查看后端错误日志
docker exec ccd2 tail -n 100 /var/log/supervisor/backend_err.log

# 进入容器
docker exec -it ccd2 /bin/bash

# 重启容器
docker restart ccd2

# 停止容器
docker stop ccd2

# 删除容器
docker rm ccd2

# 查看容器资源使用
docker stats ccd2
```

---

## 🎯 成功标准

- ✅ 容器启动后后端不重启
- ✅ `/api/health` 返回 `{"status":"healthy"}`
- ✅ 前端页面可以正常访问
- ✅ 可以登录和使用系统功能

---

## 📞 技术支持

如果遇到问题:

1. **收集诊断信息:**
   ```bash
   docker logs ccd2 > container.log
   docker exec ccd2 cat /var/log/supervisor/backend_err.log > backend_err.log
   docker exec ccd2 env > env.txt
   ```

2. **检查配置:**
   - DATABASE_URL 格式是否正确
   - REDIS_URL 是否使用实际IP (不是localhost)
   - 网络连接是否正常
   - 防火墙设置是否正确

3. **使用诊断脚本:**
   ```powershell
   .\docker-diagnose.ps1
   ```

---

**最后更新**: 2025-10-18 19:07  
**镜像版本**: ccd2-app:latest (fixed)  
**状态**: ✅ 已测试通过

