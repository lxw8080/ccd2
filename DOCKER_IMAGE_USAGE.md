# Docker 镜像使用说明

## 📦 镜像信息

- **镜像名称**: ccd2-app:latest
- **镜像大小**: 656MB
- **导出文件**: ccd2-app-latest.tar
- **文件大小**: 676MB (676,774,400 字节)
- **SHA256**: `02E0E770D57FC598B935EA43622D6742193311FC6CB1EEBC4DD3F2CED0316ACE`
- **构建时间**: 约5.5分钟

---

## 🚀 在目标机器上加载和运行镜像

### 步骤 1: 传输文件

将以下文件传输到目标机器:
- `ccd2-app-latest.tar` (Docker镜像文件)
- `ccd2-app-latest.tar.sha256` (SHA256校验文件,可选)

### 步骤 2: 验证文件完整性 (可选但推荐)

在目标机器上验证文件完整性:

**Windows PowerShell:**
```powershell
Get-FileHash -Algorithm SHA256 ccd2-app-latest.tar
# 对比输出的Hash值是否为: 02E0E770D57FC598B935EA43622D6742193311FC6CB1EEBC4DD3F2CED0316ACE
```

**Linux/Mac:**
```bash
sha256sum ccd2-app-latest.tar
# 或
shasum -a 256 ccd2-app-latest.tar
```

### 步骤 3: 加载Docker镜像

```bash
docker load -i ccd2-app-latest.tar
```

输出示例:
```
Loaded image: ccd2-app:latest
```

### 步骤 4: 验证镜像已加载

```bash
docker images ccd2-app
```

输出示例:
```
REPOSITORY   TAG       IMAGE ID       CREATED          SIZE
ccd2-app     latest    dc03d2d0aed7   10 minutes ago   656MB
```

### 步骤 5: 运行容器

**基本运行命令:**
```bash
docker run -d \
  --name ccd2 \
  -p 8080:80 \
  -e DATABASE_URL="postgresql://user:password@host:5432/dbname" \
  -e REDIS_URL="redis://host:6379/0" \
  -e SECRET_KEY="your-production-secret-key" \
  ccd2-app:latest
```

**完整配置示例:**
```bash
docker run -d \
  --name ccd2 \
  -p 8080:80 \
  -e DATABASE_URL="postgresql://ccd_user:ccd_password@192.168.1.100:5432/ccd_db" \
  -e REDIS_URL="redis://192.168.1.100:6379/0" \
  -e SECRET_KEY="change-this-to-a-random-secret-key-in-production" \
  -e ALGORITHM="HS256" \
  -e ACCESS_TOKEN_EXPIRE_MINUTES="30" \
  -e STORAGE_TYPE="local" \
  -e UPLOAD_DIR="/app/uploads" \
  -e LOG_LEVEL="INFO" \
  -v /path/to/uploads:/app/uploads \
  -v /path/to/logs:/app/logs \
  --restart unless-stopped \
  ccd2-app:latest
```

### 步骤 6: 检查容器状态

```bash
# 查看运行中的容器
docker ps

# 查看容器日志
docker logs ccd2

# 实时查看日志
docker logs -f ccd2
```

### 步骤 7: 访问应用

在浏览器中访问: `http://localhost:8080` (或使用服务器的IP地址)

---

## 🔧 环境变量说明

| 环境变量 | 说明 | 默认值 | 必需 |
|---------|------|--------|------|
| `DATABASE_URL` | PostgreSQL数据库连接URL | `postgresql://ccd_user:ccd_password@localhost:5432/ccd_db` | ✅ |
| `REDIS_URL` | Redis连接URL | `redis://localhost:6379/0` | ✅ |
| `SECRET_KEY` | JWT密钥 | `your-secret-key-change-in-production` | ✅ |
| `ALGORITHM` | JWT算法 | `HS256` | ❌ |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token过期时间(分钟) | `30` | ❌ |
| `STORAGE_TYPE` | 存储类型 | `local` | ❌ |
| `UPLOAD_DIR` | 上传目录 | `/app/uploads` | ❌ |
| `LOG_LEVEL` | 日志级别 | `INFO` | ❌ |
| `APP_NAME` | 应用名称 | `客户资料收集系统` | ❌ |
| `APP_VERSION` | 应用版本 | `1.0.0` | ❌ |

---

## 📝 常用Docker命令

### 容器管理

```bash
# 启动容器
docker start ccd2

# 停止容器
docker stop ccd2

# 重启容器
docker restart ccd2

# 删除容器
docker rm ccd2

# 强制删除运行中的容器
docker rm -f ccd2
```

### 日志和调试

```bash
# 查看容器日志
docker logs ccd2

# 实时查看日志(最后100行)
docker logs -f --tail 100 ccd2

# 进入容器shell
docker exec -it ccd2 /bin/bash

# 查看容器详细信息
docker inspect ccd2

# 查看容器资源使用情况
docker stats ccd2
```

### 镜像管理

```bash
# 查看所有镜像
docker images

# 删除镜像
docker rmi ccd2-app:latest

# 导出镜像(如需备份)
docker save -o ccd2-app-backup.tar ccd2-app:latest

# 清理未使用的镜像
docker image prune
```

---

## 🔍 故障排查

### ⚠️ 后端服务不断重启 (Exit Status 3)

这是最常见的问题,通常是由于数据库或Redis连接失败导致的。

**快速诊断**:
```bash
# Windows PowerShell
.\docker-diagnose.ps1

# Linux/Mac
./docker-diagnose.sh
```

**快速修复**:
```bash
# 停止并删除容器
docker stop ccd2 && docker rm ccd2

# 使用正确的配置重新运行
# Windows
.\docker-run-with-env.ps1

# Linux/Mac
./docker-run-with-env.sh
```

**详细故障排查指南**: 请查看 `TROUBLESHOOTING.md` 文件

### 容器无法启动

1. 检查容器日志:
   ```bash
   docker logs ccd2
   ```

2. 检查端口是否被占用:
   ```bash
   # Windows
   netstat -ano | findstr :8080

   # Linux/Mac
   lsof -i :8080
   ```

3. 检查环境变量是否正确配置

### 无法连接数据库

1. 确认 `DATABASE_URL` 格式正确
2. 确认数据库服务器可访问
3. 检查防火墙设置
4. 查看容器日志中的错误信息

**重要**: 如果数据库在同一台机器上,请使用主机IP地址而不是`localhost`:
```bash
# ❌ 错误
DATABASE_URL="postgresql://user:pass@localhost:5432/db"

# ✅ 正确
DATABASE_URL="postgresql://user:pass@192.168.1.100:5432/db"
```

### 应用无法访问

1. 确认容器正在运行: `docker ps`
2. 确认端口映射正确: `docker port ccd2`
3. 检查防火墙是否允许访问端口8080
4. 尝试从容器内部访问: `docker exec ccd2 curl http://localhost:80`

---

## 📊 性能优化建议

1. **使用数据卷持久化数据**:
   ```bash
   -v /path/to/uploads:/app/uploads \
   -v /path/to/logs:/app/logs
   ```

2. **限制容器资源使用**:
   ```bash
   --memory="1g" \
   --cpus="1.0"
   ```

3. **配置自动重启**:
   ```bash
   --restart unless-stopped
   ```

4. **使用Docker Compose管理多容器应用** (如果需要同时运行数据库和Redis)

---

## 🔐 安全建议

1. **更改默认密钥**: 务必修改 `SECRET_KEY` 为强随机字符串
2. **使用环境变量文件**: 不要在命令行中直接暴露敏感信息
3. **限制网络访问**: 使用防火墙规则限制访问
4. **定期更新**: 定期重新构建镜像以获取安全更新
5. **使用HTTPS**: 在生产环境中配置反向代理(如Nginx)启用HTTPS

---

## 📞 技术支持

如有问题,请检查:
1. Docker日志: `docker logs ccd2`
2. 应用日志: `/app/logs/` 目录
3. Supervisor日志: `/var/log/supervisor/`

---

**构建日期**: 2025-10-18  
**镜像版本**: latest  
**Docker版本要求**: Docker 20.10+

