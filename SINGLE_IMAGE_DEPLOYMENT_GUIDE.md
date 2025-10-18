# CCD2 单镜像完整部署方案

## ✅ 方案概述

本方案将**所有依赖(包括Redis)集成到一个Docker镜像中**,实现真正的单镜像部署。

### 核心特点

- ✅ **单镜像部署**: 所有服务(Nginx + FastAPI + React + Redis)都在一个镜像中
- ✅ **零外部依赖**: 除PostgreSQL数据库外,无需任何外部服务
- ✅ **极简部署**: 一条命令启动整个应用
- ✅ **完全自包含**: 镜像包含所有运行时依赖
- ✅ **生产就绪**: 包含健康检查、自动重启、数据持久化

---

## 📦 镜像信息

- **镜像名称**: `ccd2-app:all-in-one`
- **文件名**: `ccd2-app-all-in-one.tar`
- **大小**: 653.32 MB
- **包含服务**:
  - Nginx (反向代理 + 静态文件服务)
  - FastAPI (Python后端)
  - React (前端SPA)
  - Redis (缓存服务)
  - Supervisor (进程管理)

---

## 🏗️ 架构说明

### 单容器架构

```
┌─────────────────────────────────────────┐
│         Docker Container                │
│         (ccd2-app:all-in-one)           │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  Supervisor (进程管理器)        │   │
│  │                                 │   │
│  │  ┌──────────┐  ┌──────────┐    │   │
│  │  │  Redis   │  │  Nginx   │    │   │
│  │  │  :6379   │  │  :80     │    │   │
│  │  └──────────┘  └────┬─────┘    │   │
│  │                     │          │   │
│  │  ┌──────────────────┴────┐     │   │
│  │  │  FastAPI Backend      │     │   │
│  │  │  :8000                │     │   │
│  │  └───────────────────────┘     │   │
│  └─────────────────────────────────┘   │
│                                         │
│  Port Mapping: 8080 → 80                │
└─────────────────────────────────────────┘
                 │
                 │ (External Network)
                 ▼
      ┌──────────────────────────┐
      │  External PostgreSQL     │
      │  115.190.29.10:5433      │
      └──────────────────────────┘
```

### 服务说明

所有服务运行在同一个容器中,由Supervisor管理:

1. **Redis** (优先级10)
   - 端口: 127.0.0.1:6379 (仅容器内部)
   - 数据持久化: AOF + RDB
   - 自动启动和重启

2. **Nginx** (优先级20)
   - 端口: 80 (映射到宿主机8080)
   - 服务前端静态文件
   - 反向代理API请求到FastAPI

3. **FastAPI Backend** (优先级30)
   - 端口: 127.0.0.1:8000 (仅容器内部)
   - 连接内置Redis (127.0.0.1:6379)
   - 连接外部PostgreSQL

---

## 🚀 Windows端操作

### 1. 镜像已导出

镜像文件已生成:
- `ccd2-app-all-in-one.tar` (653.32 MB)
- `ccd2-app-all-in-one.tar.sha256` (SHA256校验文件)

### 2. 传输到服务器

```powershell
# 使用scp传输
scp ccd2-app-all-in-one.tar user@server-ip:/home/user/
scp ccd2-app-all-in-one.tar.sha256 user@server-ip:/home/user/

# 或使用WinSCP、FileZilla等工具
```

---

## 🖥️ Ubuntu服务器端操作

### 1. 验证文件完整性

```bash
# 验证SHA256
sha256sum -c ccd2-app-all-in-one.tar.sha256
```

预期输出:
```
ccd2-app-all-in-one.tar: OK
```

### 2. 加载Docker镜像

```bash
docker load -i ccd2-app-all-in-one.tar
```

预期输出:
```
Loaded image: ccd2-app:all-in-one
```

### 3. 启动容器

```bash
docker run -d \
  --name ccd2 \
  -p 8080:80 \
  -e DATABASE_URL="postgresql://flask_user:flask_password@115.190.29.10:5433/ccd_db_new" \
  -e SECRET_KEY="$(openssl rand -hex 32)" \
  -e LOG_LEVEL="INFO" \
  -v ccd2-uploads:/app/uploads \
  -v ccd2-logs:/app/logs \
  -v ccd2-redis-data:/var/lib/redis \
  --restart unless-stopped \
  ccd2-app:all-in-one
```

**参数说明**:
- `-d`: 后台运行
- `--name ccd2`: 容器名称
- `-p 8080:80`: 端口映射
- `-e DATABASE_URL`: 数据库连接字符串 (必须修改)
- `-e SECRET_KEY`: 安全密钥 (自动生成随机值)
- `-v`: 数据卷挂载 (持久化数据)
- `--restart unless-stopped`: 自动重启策略

### 4. 查看启动日志

```bash
docker logs -f ccd2
```

等待约30秒,直到看到:
```
INFO success: redis entered RUNNING state
INFO success: nginx entered RUNNING state
INFO success: backend entered RUNNING state
```

按 `Ctrl+C` 退出日志查看。

### 5. 验证部署

```bash
# 测试健康检查
curl http://localhost:8080/api/health
```

预期输出:
```json
{"status":"healthy"}
```

### 6. 访问应用

在浏览器中打开: `http://<服务器IP>:8080`

---

## ⚙️ 环境变量配置

### 必需的环境变量

```bash
# 数据库连接 (必须修改为实际值)
DATABASE_URL=postgresql://flask_user:flask_password@115.190.29.10:5433/ccd_db_new

# 安全密钥 (必须修改为随机值)
SECRET_KEY=$(openssl rand -hex 32)
```

### 可选的环境变量

```bash
# 日志级别
LOG_LEVEL=INFO

# JWT算法
ALGORITHM=HS256

# Token过期时间(分钟)
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 存储类型
STORAGE_TYPE=local

# 上传目录
UPLOAD_DIR=/app/uploads
```

---

## 🔧 管理命令

### 查看日志

```bash
# 查看所有日志
docker logs -f ccd2

# 查看最近100行
docker logs --tail=100 ccd2

# 查看特定服务日志
docker exec ccd2 tail -f /var/log/supervisor/redis.log
docker exec ccd2 tail -f /var/log/supervisor/nginx.log
docker exec ccd2 tail -f /var/log/supervisor/backend.log
```

### 服务控制

```bash
# 重启容器
docker restart ccd2

# 停止容器
docker stop ccd2

# 启动容器
docker start ccd2

# 查看容器状态
docker ps -a | grep ccd2

# 查看资源使用
docker stats ccd2
```

### 进入容器

```bash
# 进入容器shell
docker exec -it ccd2 /bin/bash

# 检查Redis
docker exec ccd2 redis-cli ping

# 检查进程
docker exec ccd2 supervisorctl status
```

### 数据备份

```bash
# 备份Redis数据
docker run --rm \
  -v ccd2-redis-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/redis-backup.tar.gz -C /data .

# 备份上传文件
docker run --rm \
  -v ccd2-uploads:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/uploads-backup.tar.gz -C /data .

# 备份日志
docker run --rm \
  -v ccd2-logs:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/logs-backup.tar.gz -C /data .
```

---

## 🔍 故障排查

### 问题 1: 容器启动失败

```bash
# 查看详细日志
docker logs ccd2

# 查看Supervisor日志
docker exec ccd2 cat /var/log/supervisor/supervisord.log
```

### 问题 2: 后端服务不断重启

```bash
# 查看后端错误日志
docker exec ccd2 tail -n 100 /var/log/supervisor/backend_err.log

# 检查数据库连接
docker exec ccd2 pg_isready -h 115.190.29.10 -p 5433

# 检查环境变量
docker exec ccd2 env | grep DATABASE_URL
```

### 问题 3: Redis连接失败

```bash
# 检查Redis状态
docker exec ccd2 supervisorctl status redis

# 测试Redis连接
docker exec ccd2 redis-cli ping

# 查看Redis日志
docker exec ccd2 tail -f /var/log/redis/redis-server.log
```

### 问题 4: 无法访问应用

```bash
# 检查端口映射
docker port ccd2

# 检查防火墙
sudo ufw status
sudo ufw allow 8080/tcp

# 测试本地访问
curl http://localhost:8080/api/health

# 查看Nginx日志
docker exec ccd2 tail -f /var/log/nginx/access.log
docker exec ccd2 tail -f /var/log/nginx/error.log
```

---

## 📊 测试结果

### ✅ 本机测试 (Windows Docker Desktop)

- ✅ 镜像构建成功 (653.32 MB)
- ✅ 容器启动成功
- ✅ Redis服务正常运行
- ✅ Nginx服务正常运行
- ✅ 后端服务正常运行
- ✅ 健康检查通过: `/api/health` 返回 `{"status":"healthy"}`
- ✅ 前端页面正常访问
- ✅ 所有服务稳定运行

### 服务信息

- **应用地址**: http://localhost:8080
- **健康检查**: http://localhost:8080/api/health
- **容器名称**: ccd2-all-in-one
- **镜像标签**: ccd2-app:all-in-one

---

## 📝 重要说明

### 1. 数据库配置

- ✅ 使用外部PostgreSQL数据库 (115.190.29.10:5433)
- ✅ 确保服务器可以访问该数据库
- ✅ 数据库不在容器中,独立管理

### 2. Redis配置

- ✅ Redis在容器内部运行 (127.0.0.1:6379)
- ✅ 数据持久化到Docker卷 `ccd2-redis-data`
- ✅ 仅容器内部访问,不对外暴露
- ✅ 使用AOF和RDB双重持久化

### 3. 数据持久化

以下数据会持久化到Docker卷:
- `ccd2-redis-data`: Redis数据
- `ccd2-uploads`: 应用上传的文件
- `ccd2-logs`: 应用日志

### 4. 安全建议

- ✅ 必须修改默认的 `SECRET_KEY`
- ✅ 使用强密码
- ✅ 配置防火墙规则
- ✅ 定期备份数据卷
- ✅ 定期更新镜像

---

## 🎯 优势对比

### 单镜像方案 vs 多镜像方案

| 特性 | 单镜像方案 | 多镜像方案 (Docker Compose) |
|------|-----------|---------------------------|
| 镜像数量 | 1个 | 2个 (app + redis) |
| 文件大小 | 653 MB | 686 MB (645 + 40) |
| 部署复杂度 | ✅ 极简 (一条命令) | 中等 (需要Docker Compose) |
| 网络配置 | ✅ 无需配置 | 需要配置网络 |
| 服务管理 | Docker命令 | Docker Compose命令 |
| 资源隔离 | 低 (同一容器) | 高 (独立容器) |
| 扩展性 | 低 | ✅ 高 (可独立扩展Redis) |
| 适用场景 | ✅ 小型部署 | 大型/生产环境 |

### 推荐使用场景

**单镜像方案适合**:
- ✅ 小型项目或测试环境
- ✅ 简单快速部署
- ✅ 资源有限的服务器
- ✅ 不需要独立扩展Redis

**多镜像方案适合**:
- ✅ 生产环境
- ✅ 需要独立扩展服务
- ✅ 需要更好的资源隔离
- ✅ 需要独立管理Redis

---

## 📞 技术支持

### 诊断信息收集

```bash
# 收集诊断信息
docker ps -a | grep ccd2 > status.txt
docker logs ccd2 > logs.txt
docker exec ccd2 supervisorctl status > supervisor_status.txt
docker exec ccd2 cat /var/log/supervisor/backend_err.log > backend_err.txt
```

---

## 🎉 总结

### 部署流程

1. ✅ Windows端导出镜像 (653.32 MB)
2. ✅ 传输到Ubuntu服务器
3. ✅ 加载镜像
4. ✅ 一条命令启动容器
5. ✅ 访问应用

### 关键优势

- **极简部署**: 一条命令完成所有配置
- **零外部依赖**: 除数据库外无需其他服务
- **完全自包含**: 所有依赖都在镜像中
- **生产就绪**: 包含所有必要的生产特性

---

**部署方案版本**: 3.0 (单镜像版)  
**创建时间**: 2025-10-18  
**状态**: ✅ 已测试通过  
**镜像大小**: 653.32 MB  
**适用环境**: Ubuntu Server + Docker

