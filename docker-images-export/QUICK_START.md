# CCD2 快速部署指南

## 🚀 5分钟快速部署

### 前提条件

- ✅ Ubuntu服务器 (已安装Docker和Docker Compose)
- ✅ 服务器可以访问外部数据库 (115.190.29.10:5433)
- ✅ 已将 `docker-images-export` 目录传输到服务器

---

## 📝 部署步骤

### 1. 进入部署目录

```bash
cd docker-images-export
```

### 2. 运行自动部署脚本

```bash
chmod +x deploy-on-server.sh
./deploy-on-server.sh
```

### 3. 配置环境变量

脚本会提示编辑 `.env.production` 文件:

```bash
# 生成随机密钥并替换
SECRET_KEY=$(openssl rand -hex 32)

# 编辑文件
nano .env.production
```

将生成的密钥粘贴到 `SECRET_KEY=` 后面。

### 4. 验证部署

```bash
# 测试健康检查
curl http://localhost:8080/api/health

# 预期输出: {"status":"healthy"}
```

### 5. 访问应用

在浏览器中打开: `http://<服务器IP>:8080`

---

## ✅ 完成!

应用已成功部署并运行。

---

## 📋 常用命令

```bash
# 查看日志
docker-compose -f docker-compose.production.yml logs -f

# 重启服务
docker-compose -f docker-compose.production.yml restart

# 停止服务
docker-compose -f docker-compose.production.yml stop

# 启动服务
docker-compose -f docker-compose.production.yml start
```

---

## ❓ 遇到问题?

查看完整文档: [README.md](README.md)

### 快速诊断

```bash
# 查看容器状态
docker-compose -f docker-compose.production.yml ps

# 查看错误日志
docker exec ccd2-app tail -n 100 /var/log/supervisor/backend_err.log

# 测试数据库连接
docker exec ccd2-app pg_isready -h 115.190.29.10 -p 5433
```

---

**提示**: 如果后端不断重启,通常是数据库连接问题,请检查 `DATABASE_URL` 配置。

