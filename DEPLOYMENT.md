# 部署文档

## 生产环境部署指南

本文档介绍如何将客户资料收集系统部署到生产环境。

---

## 📋 部署前准备

### 1. 服务器要求

**最低配置**:
- CPU: 2核
- 内存: 4GB
- 硬盘: 50GB
- 操作系统: Ubuntu 20.04+ / CentOS 7+

**推荐配置**:
- CPU: 4核
- 内存: 8GB
- 硬盘: 100GB SSD
- 操作系统: Ubuntu 22.04 LTS

### 2. 软件依赖

- Docker 20.10+
- Docker Compose 2.0+
- Nginx 1.18+
- SSL证书（Let's Encrypt或其他）

---

## 🚀 部署步骤

### 步骤1: 安装Docker和Docker Compose

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version
docker-compose --version
```

### 步骤2: 克隆项目代码

```bash
# 创建项目目录
sudo mkdir -p /opt/ccd
cd /opt/ccd

# 克隆代码（或上传代码包）
git clone <your-repo-url> .
# 或
scp -r ./ccd user@server:/opt/ccd
```

### 步骤3: 配置环境变量

```bash
# 后端环境变量
cd /opt/ccd/backend
cp .env.example .env
nano .env
```

**生产环境配置** (`backend/.env`):
```env
# 数据库配置
DATABASE_URL=postgresql://ccd_user:STRONG_PASSWORD_HERE@postgres:5432/ccd_db

# Redis配置
REDIS_URL=redis://redis:6379/0

# JWT密钥（必须修改为强密钥）
SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 应用配置
APP_NAME=客户资料收集系统
APP_VERSION=1.0.0
DEBUG=false

# CORS配置（修改为实际域名）
CORS_ORIGINS=["https://yourdomain.com"]

# 文件存储
STORAGE_TYPE=local
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=20971520

# 阿里云OSS（可选）
# STORAGE_TYPE=oss
# OSS_ACCESS_KEY_ID=your_access_key
# OSS_ACCESS_KEY_SECRET=your_access_secret
# OSS_BUCKET=your_bucket
# OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
```

**前端环境变量** (`frontend/.env.production`):
```env
VITE_API_BASE_URL=https://yourdomain.com/api
```

### 步骤4: 修改Docker Compose配置

编辑 `docker-compose.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: ccd_postgres
    environment:
      POSTGRES_USER: ccd_user
      POSTGRES_PASSWORD: STRONG_PASSWORD_HERE  # 修改密码
      POSTGRES_DB: ccd_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always
    networks:
      - ccd_network

  redis:
    image: redis:7-alpine
    container_name: ccd_redis
    restart: always
    networks:
      - ccd_network

  backend:
    build: ./backend
    container_name: ccd_backend
    env_file:
      - ./backend/.env
    volumes:
      - ./backend/uploads:/app/uploads
    depends_on:
      - postgres
      - redis
    restart: always
    networks:
      - ccd_network

  frontend:
    build:
      context: ./frontend
      args:
        - VITE_API_BASE_URL=https://yourdomain.com/api
    container_name: ccd_frontend
    restart: always
    networks:
      - ccd_network

  nginx:
    image: nginx:alpine
    container_name: ccd_nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./backend/uploads:/var/www/uploads:ro
    depends_on:
      - backend
      - frontend
    restart: always
    networks:
      - ccd_network

volumes:
  postgres_data:

networks:
  ccd_network:
    driver: bridge
```

### 步骤5: 配置Nginx

创建 `nginx/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # 日志配置
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    # 上传文件大小限制
    client_max_body_size 20M;

    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;

    # HTTP重定向到HTTPS
    server {
        listen 80;
        server_name yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS配置
    server {
        listen 443 ssl http2;
        server_name yourdomain.com;

        # SSL证书
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # 前端
        location / {
            proxy_pass http://frontend:80;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # 后端API
        location /api {
            proxy_pass http://backend:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # WebSocket
        location /api/ws {
            proxy_pass http://backend:8000;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # 静态文件
        location /uploads {
            alias /var/www/uploads;
            expires 30d;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

### 步骤6: 获取SSL证书

使用Let's Encrypt免费证书:

```bash
# 安装certbot
sudo apt install certbot

# 获取证书
sudo certbot certonly --standalone -d yourdomain.com

# 复制证书到项目目录
sudo mkdir -p /opt/ccd/nginx/ssl
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem /opt/ccd/nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem /opt/ccd/nginx/ssl/

# 设置自动续期
sudo crontab -e
# 添加: 0 0 1 * * certbot renew --quiet
```

### 步骤7: 启动服务

```bash
cd /opt/ccd

# 构建并启动所有服务
docker-compose up -d --build

# 查看日志
docker-compose logs -f

# 检查服务状态
docker-compose ps
```

### 步骤8: 初始化数据

```bash
# 进入后端容器
docker-compose exec backend bash

# 运行数据迁移脚本
python scripts/migrate_data.py

# 或手动创建管理员
python -c "
from app.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

db = SessionLocal()
admin = User(
    username='admin',
    password_hash=get_password_hash('your_secure_password'),
    full_name='系统管理员',
    role='admin',
    is_active=True
)
db.add(admin)
db.commit()
print('管理员创建成功')
"
```

---

## 🔒 安全加固

### 1. 防火墙配置

```bash
# 安装UFW
sudo apt install ufw

# 配置规则
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 启用防火墙
sudo ufw enable
```

### 2. 定期备份

创建备份脚本 `/opt/ccd/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/opt/backups/ccd"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份数据库
docker-compose exec -T postgres pg_dump -U ccd_user ccd_db > $BACKUP_DIR/db_$DATE.sql

# 备份上传文件
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz backend/uploads

# 删除30天前的备份
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

设置定时备份:
```bash
chmod +x /opt/ccd/backup.sh
crontab -e
# 添加: 0 2 * * * /opt/ccd/backup.sh
```

### 3. 监控和日志

```bash
# 查看容器日志
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f nginx

# 查看资源使用
docker stats

# 设置日志轮转
sudo nano /etc/logrotate.d/docker-containers
```

---

## 📊 性能优化

### 1. 数据库优化

```sql
-- 连接到数据库
docker-compose exec postgres psql -U ccd_user -d ccd_db

-- 运行索引迁移
-- 或手动创建索引（见 backend/alembic/versions/001_add_indexes.py）
```

### 2. Redis缓存

已在代码中实现，确保Redis正常运行。

### 3. CDN配置（可选）

将静态资源上传到CDN，修改前端配置使用CDN URL。

---

## 🔄 更新部署

```bash
cd /opt/ccd

# 拉取最新代码
git pull

# 重新构建并启动
docker-compose down
docker-compose up -d --build

# 运行数据库迁移（如有）
docker-compose exec backend alembic upgrade head
```

---

## 🐛 故障排查

### 问题1: 容器无法启动

```bash
# 查看日志
docker-compose logs backend
docker-compose logs postgres

# 检查端口占用
sudo netstat -tulpn | grep :5432
sudo netstat -tulpn | grep :8000
```

### 问题2: 数据库连接失败

```bash
# 检查数据库是否运行
docker-compose ps postgres

# 测试连接
docker-compose exec postgres psql -U ccd_user -d ccd_db
```

### 问题3: 前端无法访问后端

- 检查CORS配置
- 检查Nginx配置
- 检查防火墙规则

---

## 📞 技术支持

如遇问题，请检查:
1. Docker和Docker Compose版本
2. 环境变量配置
3. 网络连接
4. 日志文件

---

**部署完成后，访问 https://yourdomain.com 即可使用系统！**

