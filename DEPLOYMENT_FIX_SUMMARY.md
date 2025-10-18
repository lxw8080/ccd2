# Docker部署问题修复总结

## 🎯 问题原因

您的后端服务不断以 `exit status 3` 退出，主要原因是：

### 1. 配置文件硬编码问题 ❌
`backend/app/config.py` 第19行硬编码了特定的数据库地址：
```python
DATABASE_URL: str = "postgresql://flask_user:flask_password@115.190.29.10:5433/ccd_db_new"
```
这导致即使传入了正确的环境变量，应用仍然尝试连接错误的数据库。

### 2. 环境变量未生效 ❌
Docker容器中的环境变量没有正确覆盖硬编码的默认值。

### 3. 网络配置问题 ❌
`REDIS_URL` 配置为 `localhost`，但在Docker容器中localhost指向容器本身，无法访问宿主机服务。

### 4. 缺少错误诊断 ❌
没有启动前健康检查，导致无法快速定位问题。

## ✅ 已修复内容

### 1. 更新 `backend/app/config.py`
```python
# 修改前（❌ 错误）
DATABASE_URL: str = "postgresql://flask_user:flask_password@115.190.29.10:5433/ccd_db_new"

# 修改后（✅ 正确）
DATABASE_URL: str  # 必须从环境变量读取
```

### 2. 新增启动健康检查
- 新增 `backend/check_startup.py` - 启动前验证数据库和Redis连接
- 如果连接失败，容器会立即退出并显示清晰的错误信息
- 不会无限重启，更容易诊断问题

### 3. 改进日志配置
- 增加了详细的错误日志
- 添加了日志轮转
- 更好的错误信息输出

### 4. 提供完整工具集
- ✅ `deploy.sh` - 自动部署脚本
- ✅ `diagnose-docker.sh` - 诊断工具
- ✅ `docker-compose.prod.yml` - 生产环境配置
- ✅ `env.production.example` - 配置模板
- ✅ 详细的部署文档

## 🚀 立即修复（三步）

### 第一步：重新构建镜像

在您的本地开发机器上：

```bash
# 进入项目目录
cd /path/to/ccd2

# 重新构建镜像
docker build -t ccd2-app:fixed .

# 导出镜像（用于传输到服务器）
docker save ccd2-app:fixed | gzip > ccd2-app-fixed.tar.gz
```

### 第二步：传输到服务器并加载

```bash
# 从本地传输到服务器
scp ccd2-app-fixed.tar.gz user@your-server:/path/to/

# 在服务器上加载镜像
ssh user@your-server
gunzip -c ccd2-app-fixed.tar.gz | docker load
```

### 第三步：在服务器上运行（正确配置）

**重要：数据库连接配置**

在Ubuntu服务器上，如果数据库在同一台机器：

```bash
# 停止旧容器
docker stop <container-name>
docker rm <container-name>

# 运行新容器 - 使用正确的数据库地址
docker run -d \
  --name ccd2-app \
  -p 80:80 \
  -e DATABASE_URL="postgresql://你的用户名:你的密码@你的数据库IP:端口/数据库名" \
  -e REDIS_URL="redis://你的RedisIP:6379/0" \
  -e SECRET_KEY="$(openssl rand -hex 32)" \
  -v /data/uploads:/app/uploads \
  ccd2-app:fixed

# 查看日志确认启动
docker logs -f ccd2-app
```

**关键点：DATABASE_URL配置**

❌ **错误示例（不要使用）：**
```bash
DATABASE_URL="postgresql://user:pass@localhost:5432/db"
```
在Docker容器中，`localhost` 指向容器本身，不是宿主机！

✅ **正确示例（请使用）：**
```bash
# 方式1: 使用实际IP地址
DATABASE_URL="postgresql://user:pass@192.168.1.100:5432/db"

# 方式2: 使用host.docker.internal（某些版本支持）
DATABASE_URL="postgresql://user:pass@host.docker.internal:5432/db"

# 方式3: 使用host网络模式
docker run --network host -e DATABASE_URL="postgresql://user:pass@localhost:5432/db" ...
```

## 📋 完整部署示例

### 场景1：数据库在同一服务器上

```bash
# 1. 获取服务器IP（如果数据库在本机）
SERVER_IP=$(hostname -I | awk '{print $1}')

# 2. 配置PostgreSQL允许Docker连接
sudo nano /etc/postgresql/15/main/pg_hba.conf
# 添加：host    all    all    172.17.0.0/16    md5

sudo systemctl restart postgresql

# 3. 运行容器
docker run -d \
  --name ccd2-app \
  -p 80:80 \
  -e DATABASE_URL="postgresql://ccd_user:your_password@${SERVER_IP}:5432/ccd_db" \
  -e REDIS_URL="redis://${SERVER_IP}:6379/0" \
  -e SECRET_KEY="$(openssl rand -hex 32)" \
  -v /data/uploads:/app/uploads \
  -v /data/logs:/app/logs \
  ccd2-app:fixed

# 4. 检查日志
docker logs -f ccd2-app

# 你应该看到：
# ✅ Database connection: OK
# ✅ Redis connection: OK
# ✅ All critical checks passed! Starting application...
```

### 场景2：使用外部数据库

```bash
docker run -d \
  --name ccd2-app \
  -p 80:80 \
  -e DATABASE_URL="postgresql://user:pass@external-db-host:5432/dbname" \
  -e REDIS_URL="redis://external-redis-host:6379/0" \
  -e SECRET_KEY="your-secret-key" \
  -v /data/uploads:/app/uploads \
  ccd2-app:fixed
```

### 场景3：使用Docker Compose（推荐）

```bash
# 1. 创建配置文件
cat > .env.production << 'EOF'
POSTGRES_PASSWORD=strong_password_here
SECRET_KEY=your-secret-key-change-in-production
APP_PORT=80
EOF

# 2. 启动所有服务
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d

# 3. 查看状态
docker-compose -f docker-compose.prod.yml ps
```

## 🔍 验证部署

运行以下命令确认一切正常：

```bash
# 1. 查看启动日志（应该看到健康检查通过）
docker logs ccd2-app | grep "✅"

# 2. 测试API健康检查
curl http://localhost/api/health
# 期望输出：{"status":"healthy"}

# 3. 运行完整诊断
bash diagnose-docker.sh ccd2-app

# 4. 访问Web界面
curl -I http://localhost/
# 期望：HTTP/1.1 200 OK
```

## ⚠️ 常见错误和解决方案

### 错误1: "Database connection failed"

```bash
# 原因：数据库连接配置错误
# 解决：
# 1. 检查DATABASE_URL
docker exec ccd2-app env | grep DATABASE_URL

# 2. 从容器内测试数据库连接
docker exec ccd2-app python3 /app/backend/check_startup.py

# 3. 确保PostgreSQL配置允许远程连接
sudo nano /etc/postgresql/15/main/postgresql.conf
# listen_addresses = '*'

sudo nano /etc/postgresql/15/main/pg_hba.conf
# host    all    all    172.17.0.0/16    md5

sudo systemctl restart postgresql
```

### 错误2: 容器立即退出

```bash
# 查看完整错误日志
docker logs ccd2-app

# 查看后端错误日志
docker exec ccd2-app cat /var/log/supervisor/backend_err.log 2>/dev/null
```

### 错误3: "Redis connection failed"

Redis是可选的，不会阻止应用启动。如果需要Redis：

```bash
# 确保Redis运行
systemctl status redis

# 或安装Redis
sudo apt install redis-server
sudo systemctl start redis
```

## 📚 相关文档

- `DOCKER_DEPLOYMENT_QUICKSTART.md` - 快速开始指南
- `DOCKER_DEPLOYMENT_FIX.md` - 详细修复文档
- `diagnose-docker.sh` - 诊断工具使用
- `deploy.sh` - 自动部署脚本

## 💡 需要帮助？

如果仍然遇到问题，请运行诊断并提供信息：

```bash
# 收集诊断信息
bash diagnose-docker.sh ccd2-app > diagnostic_report.txt

# 查看报告
cat diagnostic_report.txt
```

提供以下信息可以帮助快速解决问题：
1. `docker logs ccd2-app` 的输出
2. 数据库连接字符串（隐藏密码）
3. 服务器网络配置
4. `diagnose-docker.sh` 的输出

