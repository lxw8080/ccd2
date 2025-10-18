# Docker部署快速开始指南

## 问题已修复 ✅

您遇到的后端不断重启（exit status 3）问题已经修复。主要修复内容：

1. ✅ 修复了配置文件中的硬编码数据库地址
2. ✅ 添加了启动前健康检查
3. ✅ 改进了错误日志输出
4. ✅ 提供了完整的部署工具集

## 快速部署（推荐）

### 方式一：使用自动部署脚本

```bash
# 1. 给脚本执行权限
chmod +x deploy.sh diagnose-docker.sh

# 2. 运行部署脚本
bash deploy.sh
```

脚本会自动：
- 检查Docker环境
- 构建镜像
- 创建必要目录
- 启动服务
- 运行健康检查

### 方式二：手动部署

#### 步骤1: 创建配置文件

```bash
# 复制配置文件模板
cp env.production.example .env.production

# 编辑配置文件，修改数据库密码等
nano .env.production
```

**重要配置项：**
```bash
# 数据库密码（必须修改）
POSTGRES_PASSWORD=your_strong_password

# JWT密钥（必须修改）
# 生成方法: openssl rand -hex 32
SECRET_KEY=your-secret-key-here

# 其他根据需要修改
```

#### 步骤2: 重新构建镜像

```bash
# 构建新镜像
docker build -t ccd2-app:latest .
```

#### 步骤3: 启动服务

```bash
# 使用Docker Compose启动
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d

# 或者使用 docker compose (新版)
docker compose -f docker-compose.prod.yml --env-file .env.production up -d
```

#### 步骤4: 验证部署

```bash
# 查看服务状态
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f app

# 运行诊断工具
bash diagnose-docker.sh ccd_app_prod

# 测试API
curl http://localhost/api/health
```

## 如果使用外部数据库

如果您的PostgreSQL数据库已经在运行（不在Docker中），请按以下步骤操作：

### 步骤1: 创建仅应用配置文件

创建 `.env.production` 文件：

```bash
# 应用配置
APP_PORT=80
SECRET_KEY=your-secret-key-change-in-production
LOG_LEVEL=INFO

# 外部数据库连接
# 注意：在Docker容器中，localhost指向容器本身，不是宿主机
# 请使用服务器的实际IP地址
DATABASE_URL=postgresql://user:password@192.168.1.100:5432/dbname

# 外部Redis连接（可选）
REDIS_URL=redis://192.168.1.100:6379/0

# 文件存储
UPLOAD_DIR=./uploads
LOG_DIR=./logs
```

**重要提示：**
- ❌ 不要使用 `localhost` - Docker容器中的localhost是容器本身
- ✅ 使用服务器的实际IP地址（如 `192.168.1.100`）
- ✅ 或者使用 `host.docker.internal`（某些Docker版本支持）
- ✅ 确保数据库允许从Docker容器的IP连接

### 步骤2: 仅启动应用容器

```bash
# 构建镜像
docker build -t ccd2-app:latest .

# 只启动app服务（不启动postgres和redis）
docker run -d \
  --name ccd_app_prod \
  -p 80:80 \
  --env-file .env.production \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/logs:/app/logs \
  ccd2-app:latest
```

### 步骤3: 检查连接

启动容器后，会自动运行健康检查：

```bash
# 查看启动日志
docker logs ccd_app_prod

# 你应该看到：
# ✅ Database connection: OK
# ✅ Redis connection: OK (或警告)
# ✅ All critical checks passed!
```

如果看到数据库连接失败：

```bash
# 1. 检查数据库是否运行
systemctl status postgresql

# 2. 测试从容器连接数据库
docker exec ccd_app_prod psql "postgresql://user:password@host:port/dbname" -c "SELECT 1"

# 3. 检查防火墙
sudo ufw status
sudo ufw allow 5432/tcp  # 允许PostgreSQL端口

# 4. 检查PostgreSQL配置
# 编辑 postgresql.conf，确保监听所有地址
listen_addresses = '*'

# 编辑 pg_hba.conf，添加允许的IP
host    all    all    172.17.0.0/16    md5  # Docker默认网段
```

## 使用host网络模式（替代方案）

如果上述方法仍有问题，可以使用host网络模式：

```bash
docker run -d \
  --name ccd_app_prod \
  --network host \
  -e DATABASE_URL="postgresql://user:password@localhost:5432/dbname" \
  -e REDIS_URL="redis://localhost:6379/0" \
  -e SECRET_KEY="your-secret-key" \
  -v $(pwd)/uploads:/app/uploads \
  ccd2-app:latest
```

**注意：** host模式下容器与宿主机共享网络，可以直接使用localhost。

## 故障排查

### 问题1: 后端仍然崩溃

```bash
# 运行诊断工具
bash diagnose-docker.sh ccd_app_prod

# 查看详细错误日志
docker logs ccd_app_prod
docker exec ccd_app_prod cat /var/log/supervisor/backend_err.log
```

### 问题2: 数据库连接失败

```bash
# 1. 确认数据库地址
docker exec ccd_app_prod env | grep DATABASE_URL

# 2. 从容器内测试连接
docker exec -it ccd_app_prod bash
python3 /app/backend/check_startup.py

# 3. 检查数据库配置
# 确保 postgresql.conf 中:
# listen_addresses = '*'

# 确保 pg_hba.conf 中有:
# host    all    all    0.0.0.0/0    md5
```

### 问题3: 端口被占用

```bash
# 查看端口占用
netstat -tlnp | grep :80

# 停止占用端口的服务或使用其他端口
docker run -d -p 8080:80 ... ccd2-app:latest
```

### 问题4: 权限问题

```bash
# 给uploads目录权限
chmod -R 777 uploads logs

# 或者使用特定用户
chown -R 1000:1000 uploads logs
```

## 导出和传输镜像

如果您需要在不同服务器之间传输镜像：

```bash
# 在构建服务器上导出
docker save ccd2-app:latest | gzip > ccd2-app-latest.tar.gz
sha256sum ccd2-app-latest.tar.gz > ccd2-app-latest.tar.gz.sha256

# 传输到目标服务器
scp ccd2-app-latest.tar.gz* user@target-server:/path/to/

# 在目标服务器上加载
sha256sum -c ccd2-app-latest.tar.gz.sha256
gunzip -c ccd2-app-latest.tar.gz | docker load
```

## 常用命令

```bash
# 查看日志
docker logs -f ccd_app_prod
docker-compose -f docker-compose.prod.yml logs -f

# 进入容器
docker exec -it ccd_app_prod bash

# 重启服务
docker restart ccd_app_prod
docker-compose -f docker-compose.prod.yml restart

# 停止服务
docker stop ccd_app_prod
docker-compose -f docker-compose.prod.yml down

# 查看资源使用
docker stats ccd_app_prod

# 查看容器详情
docker inspect ccd_app_prod

# 清理未使用的资源
docker system prune -a
```

## 生产环境建议

1. **使用反向代理（Nginx/Caddy）**
   ```bash
   # 安装Nginx
   sudo apt install nginx
   
   # 配置SSL证书（Let's Encrypt）
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com
   ```

2. **设置自动备份**
   ```bash
   # 添加到crontab
   0 2 * * * docker exec ccd_postgres_prod pg_dump -U ccd_user ccd_db > /backups/db_$(date +\%Y\%m\%d).sql
   ```

3. **监控和日志**
   - 使用 Docker logs 或集中日志系统
   - 设置资源限制和告警
   - 定期检查容器健康状态

4. **安全加固**
   - 修改默认密码
   - 配置防火墙规则
   - 定期更新镜像
   - 使用非root用户运行容器

## 获取帮助

如果问题仍然存在，请提供以下信息：

```bash
# 收集诊断信息
bash diagnose-docker.sh ccd_app_prod > diagnostic_report.txt
docker logs ccd_app_prod >> diagnostic_report.txt
docker inspect ccd_app_prod >> diagnostic_report.txt
```

然后查看详细文档：
- `DOCKER_DEPLOYMENT_FIX.md` - 完整部署修复指南
- `DOCKER_DEPLOYMENT_GUIDE.md` - 原始部署指南
- `TROUBLESHOOTING.md` - 故障排查指南

