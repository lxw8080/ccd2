# Docker容器故障排查指南

## 🔴 问题: 后端服务不断重启 (Exit Status 3)

### 症状
```
WARN exited: backend (exit status 3; not expected)
INFO spawned: 'backend' with pid XX
```

### 常见原因和解决方案

#### 1. 数据库连接失败 ⭐ 最常见

**原因**: 
- `DATABASE_URL` 配置错误
- 数据库服务器不可访问
- 数据库用户名/密码错误
- 数据库不存在

**诊断命令**:
```bash
# 查看后端错误日志
docker exec ccd2 tail -n 50 /var/log/supervisor/backend_err.log

# 测试数据库连接
docker exec ccd2 pg_isready -h <数据库主机> -p 5432

# 从容器内测试连接
docker exec -it ccd2 bash
psql "postgresql://user:password@host:5432/dbname"
```

**解决方案**:
1. 确认数据库服务器正在运行
2. 确认数据库URL格式正确: `postgresql://用户名:密码@主机:端口/数据库名`
3. 如果数据库在同一台机器上,使用主机IP而不是`localhost`
4. 检查防火墙是否允许数据库端口访问

**正确的运行命令**:
```bash
docker run -d \
  --name ccd2 \
  -p 8080:80 \
  -e DATABASE_URL="postgresql://ccd_user:your_password@192.168.1.100:5432/ccd_db" \
  -e REDIS_URL="redis://192.168.1.100:6379/0" \
  -e SECRET_KEY="your-secret-key" \
  ccd2-app:latest
```

#### 2. Redis连接失败

**原因**:
- `REDIS_URL` 配置错误
- Redis服务器不可访问

**诊断命令**:
```bash
# 测试Redis连接
docker exec ccd2 redis-cli -h <Redis主机> -p 6379 ping

# 查看错误日志
docker exec ccd2 tail -n 50 /var/log/supervisor/backend_err.log
```

**解决方案**:
1. 确认Redis服务器正在运行
2. 确认Redis URL格式正确: `redis://主机:端口/数据库编号`
3. 如果Redis在同一台机器上,使用主机IP而不是`localhost`

#### 3. 环境变量未正确传递

**原因**:
- 启动容器时未设置必需的环境变量
- 环境变量格式错误

**诊断命令**:
```bash
# 查看容器环境变量
docker exec ccd2 env | grep -E "DATABASE_URL|REDIS_URL|SECRET_KEY"
```

**解决方案**:
使用 `-e` 参数正确传递所有必需的环境变量

#### 4. Python依赖问题

**原因**:
- 某些Python包未正确安装
- 包版本不兼容

**诊断命令**:
```bash
# 检查Python包
docker exec ccd2 pip list | grep -E "fastapi|uvicorn|sqlalchemy|psycopg2|redis"

# 手动启动后端查看详细错误
docker exec ccd2 bash -c 'cd /app/backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000'
```

#### 5. 文件权限问题

**原因**:
- `/app/uploads` 或 `/app/logs` 目录权限不足

**诊断命令**:
```bash
# 检查目录权限
docker exec ccd2 ls -la /app/

# 修复权限
docker exec ccd2 chmod 777 /app/uploads /app/logs
```

---

## 🔧 诊断工具

### 使用诊断脚本 (推荐)

**Windows PowerShell**:
```powershell
.\docker-diagnose.ps1
```

**Linux/Mac**:
```bash
chmod +x docker-diagnose.sh
./docker-diagnose.sh
```

### 手动诊断步骤

#### 1. 查看容器状态
```bash
docker ps -a --filter "name=ccd2"
```

#### 2. 查看容器日志
```bash
# 查看所有日志
docker logs ccd2

# 实时查看日志
docker logs -f ccd2

# 查看最后50行
docker logs --tail 50 ccd2
```

#### 3. 查看后端错误日志
```bash
docker exec ccd2 tail -n 100 /var/log/supervisor/backend_err.log
```

#### 4. 查看后端标准输出
```bash
docker exec ccd2 tail -n 100 /var/log/supervisor/backend.log
```

#### 5. 进入容器调试
```bash
docker exec -it ccd2 /bin/bash

# 在容器内:
cd /app/backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

#### 6. 检查进程状态
```bash
docker exec ccd2 ps aux
```

#### 7. 测试网络连接
```bash
# 测试数据库连接
docker exec ccd2 pg_isready -h <数据库主机> -p 5432

# 测试Redis连接
docker exec ccd2 redis-cli -h <Redis主机> -p 6379 ping

# 测试DNS解析
docker exec ccd2 nslookup <数据库主机>
```

---

## 🚀 快速修复步骤

### 步骤 1: 停止并删除容器
```bash
docker stop ccd2
docker rm ccd2
```

### 步骤 2: 使用正确的配置重新运行

**使用自动化脚本 (推荐)**:

**Windows**:
```powershell
.\docker-run-with-env.ps1
```

**Linux/Mac**:
```bash
chmod +x docker-run-with-env.sh
./docker-run-with-env.sh
```

**手动运行**:
```bash
docker run -d \
  --name ccd2 \
  -p 8080:80 \
  -e DATABASE_URL="postgresql://ccd_user:password@<数据库主机>:5432/ccd_db" \
  -e REDIS_URL="redis://<Redis主机>:6379/0" \
  -e SECRET_KEY="$(openssl rand -hex 32)" \
  -e ALGORITHM="HS256" \
  -e ACCESS_TOKEN_EXPIRE_MINUTES="30" \
  -e STORAGE_TYPE="local" \
  -e UPLOAD_DIR="/app/uploads" \
  -e LOG_LEVEL="DEBUG" \
  -v $(pwd)/docker-volumes/uploads:/app/uploads \
  -v $(pwd)/docker-volumes/logs:/app/logs \
  --restart unless-stopped \
  ccd2-app:latest
```

### 步骤 3: 监控启动过程
```bash
# 实时查看日志
docker logs -f ccd2

# 等待30秒后检查状态
sleep 30
docker ps --filter "name=ccd2"
```

### 步骤 4: 验证服务
```bash
# 检查后端进程
docker exec ccd2 pgrep -f uvicorn

# 检查Nginx进程
docker exec ccd2 pgrep nginx

# 测试API
curl http://localhost:8080/api/health
```

---

## 📋 常见错误信息和解决方案

### 错误 1: `could not connect to server: Connection refused`
**原因**: 数据库服务器不可访问  
**解决**: 检查数据库主机地址和端口,确保数据库服务器正在运行

### 错误 2: `FATAL: password authentication failed`
**原因**: 数据库密码错误  
**解决**: 检查DATABASE_URL中的用户名和密码

### 错误 3: `FATAL: database "xxx" does not exist`
**原因**: 数据库不存在  
**解决**: 创建数据库或修改DATABASE_URL中的数据库名

### 错误 4: `Error connecting to Redis`
**原因**: Redis服务器不可访问  
**解决**: 检查Redis主机地址和端口,确保Redis服务器正在运行

### 错误 5: `ModuleNotFoundError: No module named 'xxx'`
**原因**: Python依赖未安装  
**解决**: 重新构建Docker镜像

### 错误 6: `Permission denied`
**原因**: 文件或目录权限不足  
**解决**: 
```bash
docker exec ccd2 chmod 777 /app/uploads /app/logs
```

---

## 🔍 高级调试

### 启用DEBUG日志
```bash
docker run -d \
  --name ccd2 \
  -p 8080:80 \
  -e LOG_LEVEL="DEBUG" \
  ...其他参数...
  ccd2-app:latest
```

### 查看Supervisor配置
```bash
docker exec ccd2 cat /etc/supervisor/conf.d/supervisord.conf
```

### 查看Nginx配置
```bash
docker exec ccd2 cat /etc/nginx/sites-available/default
```

### 测试Nginx配置
```bash
docker exec ccd2 nginx -t
```

### 重启服务
```bash
# 重启后端
docker exec ccd2 supervisorctl restart backend

# 重启Nginx
docker exec ccd2 supervisorctl restart nginx

# 重启所有服务
docker exec ccd2 supervisorctl restart all
```

---

## 📞 获取帮助

如果以上方法都无法解决问题,请:

1. **收集诊断信息**:
   ```bash
   # 运行诊断脚本
   .\docker-diagnose.ps1 > diagnosis.txt
   
   # 或手动收集
   docker logs ccd2 > container.log
   docker exec ccd2 cat /var/log/supervisor/backend_err.log > backend_err.log
   docker exec ccd2 env > env.txt
   ```

2. **检查配置**:
   - 数据库URL是否正确
   - Redis URL是否正确
   - 网络连接是否正常
   - 防火墙设置是否正确

3. **尝试最小配置**:
   ```bash
   # 使用最简单的配置测试
   docker run -d \
     --name ccd2-test \
     -p 8080:80 \
     -e DATABASE_URL="postgresql://user:pass@host:5432/db" \
     -e REDIS_URL="redis://host:6379/0" \
     -e SECRET_KEY="test-key" \
     ccd2-app:latest
   ```

---

**最后更新**: 2025-10-18  
**适用版本**: ccd2-app:latest

