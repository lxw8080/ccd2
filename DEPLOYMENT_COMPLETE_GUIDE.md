# CCD2 Docker完整部署方案 - 最终版

## ✅ 方案概述

本方案提供了一个**完整的容器化部署解决方案**,包含项目运行所需的所有依赖(除外部数据库)。

### 核心特点

- ✅ **完全容器化**: 应用和Redis都在容器中运行
- ✅ **一键导出**: Windows上构建并导出所有镜像
- ✅ **一键部署**: Ubuntu服务器上自动化部署
- ✅ **生产就绪**: 包含健康检查、自动重启、数据持久化
- ✅ **易于管理**: 使用Docker Compose统一管理

---

## 📦 部署包内容

### 导出目录: `docker-images-export/`

```
docker-images-export/
├── ccd2-app-latest.tar          # 应用镜像 (645.44 MB)
├── ccd2-app-latest.tar.sha256   # SHA256校验文件
├── redis-7-alpine.tar           # Redis镜像 (40.28 MB)
├── redis-7-alpine.tar.sha256    # SHA256校验文件
├── docker-compose.production.yml # Docker Compose配置
├── .env.production.example      # 环境变量模板
├── deploy-on-server.sh          # 自动部署脚本
├── README.md                    # 完整文档
└── QUICK_START.md               # 快速开始指南
```

**总大小**: 685.71 MB

---

## 🏗️ 架构说明

### 容器架构

```
┌─────────────────────────────────────────┐
│         Docker Host (Ubuntu)            │
│                                         │
│  ┌───────────────┐   ┌──────────────┐  │
│  │  ccd2-app     │   │  ccd2-redis  │  │
│  │  (Port 8080)  │───│  (Internal)  │  │
│  │               │   │              │  │
│  │  - Nginx      │   │  - Redis     │  │
│  │  - FastAPI    │   │  - Cache     │  │
│  │  - React      │   │              │  │
│  └───────┬───────┘   └──────────────┘  │
│          │                              │
│          │  ccd2-network (bridge)       │
└──────────┼──────────────────────────────┘
           │
           │ (External Network)
           ▼
┌──────────────────────────┐
│  External PostgreSQL     │
│  115.190.29.10:5433      │
└──────────────────────────┘
```

### 服务说明

1. **ccd2-app** 容器
   - Nginx (反向代理 + 静态文件)
   - FastAPI (Python后端API)
   - React (前端SPA)
   - 端口映射: 8080 → 80

2. **ccd2-redis** 容器
   - Redis 7 (缓存服务)
   - 仅容器内部访问
   - 数据持久化到Docker卷

3. **外部数据库**
   - PostgreSQL (115.190.29.10:5433)
   - 不在容器中,使用现有数据库

---

## 🚀 Windows端操作

### 1. 导出所有镜像

```powershell
# 运行导出脚本
.\export-images.ps1
```

脚本会自动:
- ✅ 检查并拉取缺失的镜像
- ✅ 导出所有镜像为tar文件
- ✅ 计算SHA256校验值
- ✅ 复制部署文件
- ✅ 创建README文档

### 2. 传输到服务器

```powershell
# 使用scp传输
scp -r docker-images-export user@server-ip:/home/user/

# 或使用WinSCP、FileZilla等工具
```

---

## 🖥️ Ubuntu服务器端操作

### 方法一: 自动部署 (推荐)

```bash
# 1. 进入部署目录
cd docker-images-export

# 2. 添加执行权限
chmod +x deploy-on-server.sh

# 3. 运行自动部署脚本
./deploy-on-server.sh
```

脚本会自动完成:
1. ✅ 验证镜像文件完整性
2. ✅ 加载Docker镜像
3. ✅ 配置环境变量
4. ✅ 启动服务
5. ✅ 验证部署

### 方法二: 手动部署

```bash
cd docker-images-export

# 1. 验证文件
sha256sum -c ccd2-app-latest.tar.sha256
sha256sum -c redis-7-alpine.tar.sha256

# 2. 加载镜像
docker load -i ccd2-app-latest.tar
docker load -i redis-7-alpine.tar

# 3. 配置环境变量
cp .env.production.example .env.production
nano .env.production  # 编辑配置

# 4. 启动服务
docker-compose -f docker-compose.production.yml --env-file .env.production up -d

# 5. 查看日志
docker-compose -f docker-compose.production.yml logs -f
```

---

## ⚙️ 环境变量配置

编辑 `.env.production` 文件:

```bash
# 必须修改
SECRET_KEY=your-random-secret-key-here  # 使用: openssl rand -hex 32

# 确认配置
DATABASE_URL=postgresql://flask_user:flask_password@115.190.29.10:5433/ccd_db_new

# 可选配置
LOG_LEVEL=INFO
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## ✅ 验证部署

### 1. 检查容器状态

```bash
docker-compose -f docker-compose.production.yml ps
```

预期输出:
```
NAME        IMAGE              STATUS         PORTS
ccd2-app    ccd2-app:latest    Up (healthy)   0.0.0.0:8080->80/tcp
ccd2-redis  redis:7-alpine     Up (healthy)   6379/tcp
```

### 2. 测试健康检查

```bash
curl http://localhost:8080/api/health
```

预期输出:
```json
{"status":"healthy"}
```

### 3. 访问应用

在浏览器中打开: `http://<服务器IP>:8080`

---

## 🔧 管理命令

### 查看日志

```bash
# 所有服务日志
docker-compose -f docker-compose.production.yml logs -f

# 只看应用日志
docker-compose -f docker-compose.production.yml logs -f app

# 只看Redis日志
docker-compose -f docker-compose.production.yml logs -f redis
```

### 服务控制

```bash
# 重启服务
docker-compose -f docker-compose.production.yml restart

# 停止服务
docker-compose -f docker-compose.production.yml stop

# 启动服务
docker-compose -f docker-compose.production.yml start

# 查看状态
docker-compose -f docker-compose.production.yml ps
```

### 数据备份

```bash
# 备份Redis数据
docker run --rm \
  -v ccd2_redis-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/redis-backup.tar.gz -C /data .

# 备份上传文件
docker run --rm \
  -v ccd2_app-uploads:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/uploads-backup.tar.gz -C /data .
```

---

## 🔍 故障排查

### 问题 1: 后端不断重启

```bash
# 查看错误日志
docker exec ccd2-app tail -n 100 /var/log/supervisor/backend_err.log

# 检查数据库连接
docker exec ccd2-app pg_isready -h 115.190.29.10 -p 5433

# 检查Redis连接
docker exec ccd2-app redis-cli -h redis ping
```

### 问题 2: 无法访问应用

```bash
# 检查容器状态
docker-compose -f docker-compose.production.yml ps

# 检查端口
docker port ccd2-app

# 检查防火墙
sudo ufw allow 8080/tcp
```

---

## 📊 测试结果

### ✅ 本机测试 (Windows Docker Desktop)

- ✅ 镜像构建成功
- ✅ 镜像导出成功 (685.71 MB)
- ✅ Docker Compose启动成功
- ✅ 健康检查通过: `/api/health` 返回 `{"status":"healthy"}`
- ✅ 前端页面正常访问
- ✅ 后端服务稳定运行 (不再重启)
- ✅ Redis连接正常

### 服务信息

- **应用地址**: http://localhost:8080
- **健康检查**: http://localhost:8080/api/health
- **容器网络**: ccd2-network (bridge)
- **数据卷**: redis-data, app-uploads, app-logs

---

## 📝 重要说明

### 1. 数据库配置

- ✅ 使用外部PostgreSQL数据库 (115.190.29.10:5433)
- ✅ 确保服务器可以访问该数据库
- ✅ 数据库不在容器中,独立管理

### 2. Redis配置

- ✅ Redis在容器中运行
- ✅ 数据持久化到Docker卷 `redis-data`
- ✅ 仅容器内部访问,不对外暴露

### 3. 数据持久化

以下数据会持久化到Docker卷:
- `redis-data`: Redis数据
- `app-uploads`: 应用上传的文件
- `app-logs`: 应用日志

### 4. 安全建议

- ✅ 必须修改默认的 `SECRET_KEY`
- ✅ 使用强密码
- ✅ 配置防火墙规则
- ✅ 定期备份数据卷
- ✅ 定期更新镜像

---

## 📞 技术支持

### 文档

- **完整文档**: `docker-images-export/README.md`
- **快速开始**: `docker-images-export/QUICK_START.md`
- **本文档**: `DEPLOYMENT_COMPLETE_GUIDE.md`

### 诊断信息收集

```bash
# 收集诊断信息
docker-compose -f docker-compose.production.yml ps > status.txt
docker-compose -f docker-compose.production.yml logs > logs.txt
docker exec ccd2-app cat /var/log/supervisor/backend_err.log > backend_err.txt
```

---

## 🎯 总结

### 优势

1. **完全容器化**: 除数据库外,所有依赖都在容器中
2. **一键部署**: 自动化脚本简化部署流程
3. **生产就绪**: 包含健康检查、自动重启、数据持久化
4. **易于管理**: Docker Compose统一管理所有服务
5. **可移植性**: 镜像文件可在任何支持Docker的环境运行

### 下一步

1. ✅ 将 `docker-images-export` 目录传输到Ubuntu服务器
2. ✅ 运行 `deploy-on-server.sh` 自动部署
3. ✅ 配置 `.env.production` 文件
4. ✅ 访问 `http://<服务器IP>:8080` 验证部署

---

**部署方案版本**: 2.0  
**创建时间**: 2025-10-18  
**状态**: ✅ 已测试通过  
**适用环境**: Ubuntu Server + Docker + Docker Compose

