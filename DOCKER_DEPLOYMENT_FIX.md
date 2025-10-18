# Docker部署问题修复指南

## 问题诊断

您遇到的问题是后端服务不断重启并以 `exit status 3` 退出。这通常是由以下原因导致的：

### 主要原因
1. **数据库连接配置问题** - DATABASE_URL环境变量未正确传递或数据库不可访问
2. **Redis连接问题** - REDIS_URL配置为localhost但在容器中无法访问
3. **配置文件硬编码** - 之前的config.py硬编码了特定数据库地址

## 修复内容

### 1. 更新了 `backend/app/config.py`
- 移除了硬编码的数据库URL
- DATABASE_URL现在必须通过环境变量提供
- 改进了配置读取逻辑

### 2. 新增 `backend/check_startup.py`
- 启动前健康检查脚本
- 验证数据库连接
- 验证Redis连接（可选）
- 提供详细的错误信息

### 3. 更新了 `Dockerfile`
- 添加了启动检查脚本
- 改进了supervisor日志配置
- 增加了日志轮转

### 4. 更新了 `docker-entrypoint.sh`
- 在启动服务前运行健康检查
- 如果检查失败则不启动服务
- 提供更清晰的错误信息

## 部署步骤

### 步骤1: 重新构建Docker镜像

```bash
# 在项目根目录执行
docker build -t ccd2-app:fixed .
```

### 步骤2: 准备环境变量

创建一个 `.env` 文件或准备环境变量：

```bash
# 必需的环境变量
DATABASE_URL=postgresql://用户名:密码@数据库主机:端口/数据库名

# 可选的环境变量
REDIS_URL=redis://redis主机:6379/0
SECRET_KEY=your-secret-key-change-in-production
LOG_LEVEL=INFO
STORAGE_TYPE=local
```

**重要提示：**
- 如果数据库在同一台服务器上，使用服务器的实际IP地址或localhost（如果正确配置了网络）
- 如果Redis在同一台服务器上，也需要使用实际IP地址
- 在Docker容器中，`localhost` 指向容器本身，不是宿主机

### 步骤3: 运行容器（方式一 - 使用环境变量）

```bash
docker run -d \
  --name ccd2-app \
  -p 80:80 \
  -e DATABASE_URL="postgresql://user:password@host:5432/dbname" \
  -e REDIS_URL="redis://host:6379/0" \
  -e SECRET_KEY="your-secret-key" \
  -v /path/to/uploads:/app/uploads \
  ccd2-app:fixed
```

### 步骤4: 运行容器（方式二 - 使用.env文件）

```bash
docker run -d \
  --name ccd2-app \
  -p 80:80 \
  --env-file .env \
  -v /path/to/uploads:/app/uploads \
  ccd2-app:fixed
```

### 步骤5: 检查日志

```bash
# 查看容器日志
docker logs -f ccd2-app

# 如果容器启动了，可以查看backend的详细日志
docker exec ccd2-app tail -f /var/log/supervisor/backend.log
docker exec ccd2-app tail -f /var/log/supervisor/backend_err.log
```

## 常见问题排查

### 问题1: 数据库连接失败

**错误信息：**
```
❌ Database connection failed: could not connect to server
```

**解决方案：**
1. 检查DATABASE_URL是否正确
2. 确认数据库服务器是否运行
3. 检查防火墙规则
4. 如果数据库在同一服务器，尝试使用服务器IP而不是localhost

**测试数据库连接：**
```bash
# 在服务器上测试
psql "postgresql://user:password@host:port/dbname"
```

### 问题2: Redis连接失败

**错误信息：**
```
⚠️ Redis connection failed
```

**解决方案：**
Redis是可选的，不会阻止应用启动。但如果需要使用Redis：
1. 确认Redis服务器正在运行
2. 检查REDIS_URL配置
3. 检查防火墙规则

### 问题3: 权限问题

**错误信息：**
```
Permission denied
```

**解决方案：**
```bash
# 确保uploads目录有正确的权限
chmod 777 /path/to/uploads
```

### 问题4: 端口冲突

**错误信息：**
```
port is already allocated
```

**解决方案：**
```bash
# 使用不同的端口
docker run -d -p 8080:80 ...

# 或者停止占用端口的服务
netstat -tlnp | grep :80
```

## 网络配置说明

### Docker网络模式

#### 1. Bridge模式（默认）
容器有独立的网络栈，使用localhost访问宿主机服务需要特殊配置。

**正确的配置：**
```bash
# Linux: 使用宿主机IP
DATABASE_URL=postgresql://user:password@192.168.1.100:5432/dbname

# 或使用host.docker.internal (某些Docker版本支持)
DATABASE_URL=postgresql://user:password@host.docker.internal:5432/dbname
```

#### 2. Host模式
容器与宿主机共享网络栈，可以直接使用localhost。

```bash
docker run -d \
  --network host \
  -e DATABASE_URL="postgresql://user:password@localhost:5432/dbname" \
  ccd2-app:fixed
```

**注意：** host模式在某些系统上可能不可用（如Docker Desktop for Mac/Windows）

### 推荐配置

对于Ubuntu服务器部署，推荐以下配置：

```bash
# 1. 使用Docker Compose（推荐）
# 创建 docker-compose.prod.yml:

version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ccd_user
      POSTGRES_PASSWORD: ccd_password
      POSTGRES_DB: ccd_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - ccd_network

  redis:
    image: redis:7-alpine
    networks:
      - ccd_network

  app:
    image: ccd2-app:fixed
    ports:
      - "80:80"
    environment:
      DATABASE_URL: postgresql://ccd_user:ccd_password@postgres:5432/ccd_db
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: your-secret-key-change-in-production
    volumes:
      - ./uploads:/app/uploads
    depends_on:
      - postgres
      - redis
    networks:
      - ccd_network

networks:
  ccd_network:
    driver: bridge

volumes:
  postgres_data:
```

启动：
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 验证部署

### 1. 检查容器状态
```bash
docker ps
```

应该看到容器状态为 `Up`，而不是不断重启。

### 2. 检查健康状态
```bash
curl http://localhost/api/health
```

应该返回：
```json
{"status": "healthy"}
```

### 3. 检查日志
```bash
# 查看启动日志
docker logs ccd2-app

# 应该看到：
# ✅ Database connection: OK
# ✅ Redis connection: OK (或警告)
# ✅ All critical checks passed! Starting application...
```

## 快速诊断脚本

创建一个诊断脚本 `diagnose.sh`：

```bash
#!/bin/bash

echo "=== CCD2 Docker Deployment Diagnostics ==="
echo ""

echo "1. Checking Docker status..."
docker ps -a | grep ccd2

echo ""
echo "2. Checking recent logs..."
docker logs --tail 50 ccd2-app

echo ""
echo "3. Checking backend error logs..."
docker exec ccd2-app tail -20 /var/log/supervisor/backend_err.log 2>/dev/null || echo "Container not running"

echo ""
echo "4. Testing API health..."
curl -s http://localhost/api/health || echo "API not responding"

echo ""
echo "5. Checking environment variables..."
docker exec ccd2-app env | grep -E 'DATABASE_URL|REDIS_URL' 2>/dev/null || echo "Container not running"

echo ""
echo "=== Diagnostics Complete ==="
```

运行诊断：
```bash
chmod +x diagnose.sh
./diagnose.sh
```

## 导出和加载镜像

### 导出镜像
```bash
# 导出修复后的镜像
docker save ccd2-app:fixed | gzip > ccd2-app-fixed.tar.gz

# 生成校验和
sha256sum ccd2-app-fixed.tar.gz > ccd2-app-fixed.tar.gz.sha256
```

### 在目标服务器上加载
```bash
# 1. 上传文件到服务器
scp ccd2-app-fixed.tar.gz* user@server:/path/to/

# 2. 在服务器上验证和加载
sha256sum -c ccd2-app-fixed.tar.gz.sha256
gunzip -c ccd2-app-fixed.tar.gz | docker load

# 3. 运行容器
docker run -d \
  --name ccd2-app \
  -p 80:80 \
  -e DATABASE_URL="your_database_url" \
  -v /data/uploads:/app/uploads \
  ccd2-app:fixed
```

## 生产环境建议

1. **使用Docker Compose** - 更容易管理多容器应用
2. **使用环境变量文件** - 不要在命令行中暴露敏感信息
3. **配置日志轮转** - 防止日志文件过大
4. **设置健康检查** - 自动检测和重启失败的服务
5. **使用持久化卷** - 保护上传的文件数据
6. **定期备份数据库** - 设置自动备份任务
7. **使用反向代理** - 配置Nginx或Traefik处理SSL
8. **监控和告警** - 使用Prometheus + Grafana等工具

## 需要帮助？

如果问题仍然存在，请提供以下信息：

1. `docker logs ccd2-app` 的完整输出
2. 数据库配置信息（隐藏敏感信息）
3. 网络配置（容器如何连接数据库）
4. 运行 `diagnose.sh` 的输出

## 更新日志

- 2024-10-18: 修复配置文件硬编码问题
- 2024-10-18: 添加启动健康检查
- 2024-10-18: 改进日志输出和错误提示

