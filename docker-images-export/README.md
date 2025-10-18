# CCD2 Docker完整部署包

## 📦 包含内容

### Docker镜像文件

1. **ccd2-app-latest.tar** (645.44 MB)
   - 镜像: `ccd2-app:latest`
   - 说明: CCD2完整应用 (Nginx + FastAPI后端 + React前端)
   - SHA256: `A72B8154402327934B6436793E510D068A730572E6C1AB8E57DF934F9601ED2D`

2. **redis-7-alpine.tar** (40.28 MB)
   - 镜像: `redis:7-alpine`
   - 说明: Redis缓存服务
   - SHA256: `ACF9072322FE22D2FD78529FB55EF05FB432CBE4F22B4EBACA883F7B4842E6AD`

### 配置文件

- **docker-compose.production.yml** - Docker Compose生产环境配置
- **.env.production.example** - 环境变量配置模板
- **deploy-on-server.sh** - Ubuntu服务器自动部署脚本

---

## 🚀 快速部署 (推荐)

### 1. 传输文件到服务器

```bash
# 使用scp传输整个目录
scp -r docker-images-export user@server-ip:/home/user/

# 或使用rsync (更快,支持断点续传)
rsync -avz --progress docker-images-export/ user@server-ip:/home/user/ccd2/
```

### 2. 在服务器上运行自动部署脚本

```bash
# SSH登录到服务器
ssh user@server-ip

# 进入部署目录
cd docker-images-export

# 添加执行权限
chmod +x deploy-on-server.sh

# 运行自动部署脚本
./deploy-on-server.sh
```

脚本会自动完成:
- ✅ 验证镜像文件完整性
- ✅ 加载Docker镜像
- ✅ 配置环境变量
- ✅ 启动服务
- ✅ 验证部署

### 3. 配置环境变量

脚本会提示您编辑 `.env.production` 文件,**必须修改**:

```bash
# 生成随机密钥
SECRET_KEY=$(openssl rand -hex 32)

# 确认数据库连接
DATABASE_URL=postgresql://flask_user:flask_password@115.190.29.10:5433/ccd_db_new
```

### 4. 访问应用

在浏览器中访问: `http://<服务器IP>:8080`

---

## 📖 手动部署步骤

如果您不想使用自动脚本,可以手动部署:

### 步骤 1: 验证文件完整性

```bash
cd docker-images-export

# 验证镜像文件
sha256sum -c ccd2-app-latest.tar.sha256
sha256sum -c redis-7-alpine.tar.sha256
```

预期输出:
```
ccd2-app-latest.tar: OK
redis-7-alpine.tar: OK
```

### 步骤 2: 加载Docker镜像

```bash
# 加载应用镜像
docker load -i ccd2-app-latest.tar

# 加载Redis镜像
docker load -i redis-7-alpine.tar

# 验证镜像已加载
docker images
```

预期输出应包含:
```
REPOSITORY   TAG        IMAGE ID       CREATED        SIZE
ccd2-app     latest     ...            ...            656MB
redis        7-alpine   ...            ...            40.3MB
```

### 步骤 3: 配置环境变量

```bash
# 复制环境变量模板
cp .env.production.example .env.production

# 编辑配置文件
nano .env.production
```

**必须修改的配置:**

```bash
# 1. 生成随机密钥
SECRET_KEY=your-random-secret-key-here

# 生成方法:
openssl rand -hex 32

# 2. 确认数据库连接 (已配置,确认即可)
DATABASE_URL=postgresql://flask_user:flask_password@115.190.29.10:5433/ccd_db_new

# 3. 其他可选配置
LOG_LEVEL=INFO
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 步骤 4: 启动服务

```bash
# 使用Docker Compose启动所有服务
docker-compose -f docker-compose.production.yml --env-file .env.production up -d

# 查看启动日志
docker-compose -f docker-compose.production.yml logs -f
```

等待约30秒,直到看到:
```
ccd2-app    | INFO success: backend entered RUNNING state
ccd2-app    | INFO success: nginx entered RUNNING state
ccd2-redis  | Ready to accept connections
```

按 `Ctrl+C` 退出日志查看。

### 步骤 5: 验证部署

```bash
# 检查容器状态
docker-compose -f docker-compose.production.yml ps

# 测试健康检查
curl http://localhost:8080/api/health

# 预期输出: {"status":"healthy"}
```

---

## 🏗️ 架构说明

### 容器架构

```
┌─────────────────────────────────────────┐
│         Docker Host (Ubuntu)            │
│                                         │
│  ┌───────────────┐   ┌──────────────┐  │
│  │  ccd2-app     │   │  ccd2-redis  │  │
│  │  (Port 8080)  │   │  (Internal)  │  │
│  │               │   │              │  │
│  │  - Nginx      │   │  - Redis     │  │
│  │  - FastAPI    │   │  - Cache     │  │
│  │  - React      │   │              │  │
│  └───────┬───────┘   └──────┬───────┘  │
│          │                  │          │
│          └──────────────────┘          │
│              ccd2-network               │
└─────────────────────────────────────────┘
                 │
                 │ (Network)
                 ▼
    ┌────────────────────────┐
    │  External PostgreSQL   │
    │  115.190.29.10:5433    │
    └────────────────────────┘
```

### 服务说明

1. **ccd2-app** 容器
   - **Nginx** (端口80): 反向代理和静态文件服务
   - **FastAPI** (端口8000): Python后端API
   - **React**: 前端单页应用
   - **对外端口**: 8080 → 80

2. **ccd2-redis** 容器
   - **Redis**: 缓存服务
   - **端口**: 6379 (仅容器内部访问)
   - **数据持久化**: redis-data卷

3. **外部数据库**
   - **PostgreSQL**: 115.190.29.10:5433
   - **不在容器中**: 使用现有数据库

### 数据持久化

Docker卷用于数据持久化:

- `redis-data`: Redis数据
- `app-uploads`: 应用上传的文件
- `app-logs`: 应用日志

---

## 🔧 管理命令

### 查看日志

```bash
# 查看所有服务日志
docker-compose -f docker-compose.production.yml logs -f

# 只查看应用日志
docker-compose -f docker-compose.production.yml logs -f app

# 只查看Redis日志
docker-compose -f docker-compose.production.yml logs -f redis

# 查看最近100行日志
docker-compose -f docker-compose.production.yml logs --tail=100 app
```

### 服务控制

```bash
# 重启所有服务
docker-compose -f docker-compose.production.yml restart

# 重启单个服务
docker-compose -f docker-compose.production.yml restart app

# 停止服务
docker-compose -f docker-compose.production.yml stop

# 启动服务
docker-compose -f docker-compose.production.yml start

# 查看服务状态
docker-compose -f docker-compose.production.yml ps
```

### 容器管理

```bash
# 进入应用容器
docker exec -it ccd2-app /bin/bash

# 进入Redis容器
docker exec -it ccd2-redis sh

# 查看容器资源使用
docker stats ccd2-app ccd2-redis
```

### 数据备份

```bash
# 备份Redis数据
docker run --rm -v ccd2_redis-data:/data -v $(pwd):/backup alpine tar czf /backup/redis-backup.tar.gz -C /data .

# 备份上传文件
docker run --rm -v ccd2_app-uploads:/data -v $(pwd):/backup alpine tar czf /backup/uploads-backup.tar.gz -C /data .

# 备份日志
docker run --rm -v ccd2_app-logs:/data -v $(pwd):/backup alpine tar czf /backup/logs-backup.tar.gz -C /data .
```

### 清理和重置

```bash
# 停止并删除容器 (保留数据)
docker-compose -f docker-compose.production.yml down

# 停止并删除容器和数据卷 (删除所有数据!)
docker-compose -f docker-compose.production.yml down -v

# 重新启动
docker-compose -f docker-compose.production.yml up -d
```

---

## 🔍 故障排查

### 问题 1: 后端服务不断重启

**症状:**
```
ccd2-app | WARN exited: backend (exit status 3; not expected)
```

**原因:** 数据库或Redis连接失败

**解决方法:**

1. 查看详细错误日志:
```bash
docker exec ccd2-app tail -n 100 /var/log/supervisor/backend_err.log
```

2. 检查数据库连接:
```bash
# 测试数据库连接
docker exec ccd2-app pg_isready -h 115.190.29.10 -p 5433
```

3. 检查Redis连接:
```bash
# 测试Redis连接
docker exec ccd2-app redis-cli -h redis ping
```

4. 检查环境变量:
```bash
docker exec ccd2-app env | grep -E "DATABASE_URL|REDIS_URL"
```

### 问题 2: 无法访问应用

**检查清单:**

```bash
# 1. 检查容器是否运行
docker-compose -f docker-compose.production.yml ps

# 2. 检查端口映射
docker port ccd2-app

# 3. 检查防火墙
sudo ufw status
sudo ufw allow 8080/tcp

# 4. 测试本地访问
curl http://localhost:8080/api/health

# 5. 查看Nginx日志
docker exec ccd2-app tail -f /var/log/nginx/access.log
docker exec ccd2-app tail -f /var/log/nginx/error.log
```

### 问题 3: Redis连接失败

**检查:**

```bash
# 1. 检查Redis容器状态
docker-compose -f docker-compose.production.yml ps redis

# 2. 测试Redis连接
docker exec ccd2-redis redis-cli ping

# 3. 查看Redis日志
docker-compose -f docker-compose.production.yml logs redis
```

### 问题 4: 数据库连接失败

**检查:**

```bash
# 1. 测试网络连通性
ping 115.190.29.10

# 2. 测试端口连通性
telnet 115.190.29.10 5433

# 3. 检查DATABASE_URL配置
cat .env.production | grep DATABASE_URL
```

---

## 📊 监控和维护

### 健康检查

```bash
# 应用健康检查
curl http://localhost:8080/api/health

# 预期输出: {"status":"healthy"}
```

### 性能监控

```bash
# 实时查看资源使用
docker stats ccd2-app ccd2-redis

# 查看磁盘使用
docker system df

# 查看卷使用
docker volume ls
```

### 日志轮转

建议配置日志轮转以防止日志文件过大:

```bash
# 编辑Docker daemon配置
sudo nano /etc/docker/daemon.json
```

添加:
```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

重启Docker:
```bash
sudo systemctl restart docker
```

---

## ⚠️ 重要注意事项

1. **安全性**
   - ✅ 必须修改默认的 `SECRET_KEY`
   - ✅ 使用强密码
   - ✅ 定期更新镜像
   - ✅ 配置防火墙规则

2. **数据备份**
   - ✅ 定期备份Docker卷
   - ✅ 备份 `.env.production` 配置文件
   - ✅ 备份外部数据库

3. **网络**
   - ✅ 确保服务器可以访问外部数据库 (115.190.29.10:5433)
   - ✅ 配置防火墙允许8080端口
   - ✅ 考虑使用Nginx反向代理和SSL证书

4. **资源**
   - ✅ 建议至少2GB内存
   - ✅ 建议至少10GB磁盘空间
   - ✅ 监控资源使用情况

---

## 📞 技术支持

### 收集诊断信息

如果遇到问题,请收集以下信息:

```bash
# 1. 容器状态
docker-compose -f docker-compose.production.yml ps > status.txt

# 2. 容器日志
docker-compose -f docker-compose.production.yml logs > logs.txt

# 3. 后端错误日志
docker exec ccd2-app cat /var/log/supervisor/backend_err.log > backend_err.txt

# 4. 环境变量 (注意脱敏)
docker exec ccd2-app env > env.txt

# 5. 系统信息
docker version > docker_version.txt
docker-compose version >> docker_version.txt
```

---

**部署包版本**: 2025-10-18  
**总大小**: 685.71 MB  
**镜像数量**: 2  
**状态**: ✅ 已测试通过

