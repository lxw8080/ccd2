# CCD2 单镜像快速部署指南

## 📦 文件清单

部署所需文件:
- ✅ `ccd2-app-all-in-one.tar` (653.32 MB) - Docker镜像文件
- ✅ `ccd2-app-all-in-one.tar.sha256` - SHA256校验文件
- ✅ `deploy-single-image.sh` - 自动部署脚本
- ✅ `SINGLE_IMAGE_DEPLOYMENT_GUIDE.md` - 完整部署文档

---

## 🚀 5分钟快速部署

### 步骤1: 传输文件到服务器

在Windows上执行:

```powershell
# 使用scp传输文件
scp ccd2-app-all-in-one.tar user@server-ip:/home/user/
scp ccd2-app-all-in-one.tar.sha256 user@server-ip:/home/user/
scp deploy-single-image.sh user@server-ip:/home/user/
```

或使用WinSCP、FileZilla等工具传输。

---

### 步骤2: 在服务器上运行部署脚本

SSH登录到Ubuntu服务器:

```bash
ssh user@server-ip
```

执行部署脚本:

```bash
# 进入文件目录
cd /home/user/

# 添加执行权限
chmod +x deploy-single-image.sh

# 运行部署脚本
./deploy-single-image.sh
```

---

### 步骤3: 按提示输入配置

脚本会提示输入以下信息:

1. **数据库URL**
   ```
   postgresql://flask_user:flask_password@115.190.29.10:5433/ccd_db_new
   ```

2. **SECRET_KEY**
   - 推荐使用自动生成(按Y)
   - 或手动输入自定义密钥

3. **日志级别**
   - 默认: INFO
   - 可选: DEBUG, WARNING, ERROR

---

### 步骤4: 等待部署完成

脚本会自动:
- ✅ 检查Docker环境
- ✅ 验证镜像文件完整性
- ✅ 加载Docker镜像
- ✅ 启动容器
- ✅ 执行健康检查

部署成功后会显示:
```
🎉 部署完成!
访问应用: http://<服务器IP>:8080
```

---

## 🔍 验证部署

### 检查容器状态

```bash
docker ps
```

应该看到名为 `ccd2` 的容器在运行。

### 查看日志

```bash
docker logs -f ccd2
```

应该看到:
```
✅ Redis connection: OK
✅ Database connection: OK
✅ Nginx entered RUNNING state
✅ Backend entered RUNNING state
```

### 测试健康检查

```bash
curl http://localhost:8080/api/health
```

应该返回:
```json
{"status":"healthy"}
```

### 访问应用

在浏览器中打开:
```
http://<服务器IP>:8080
```

---

## 📋 常用管理命令

### 查看日志
```bash
docker logs -f ccd2
```

### 停止容器
```bash
docker stop ccd2
```

### 启动容器
```bash
docker start ccd2
```

### 重启容器
```bash
docker restart ccd2
```

### 删除容器
```bash
docker stop ccd2
docker rm ccd2
```

### 查看容器详情
```bash
docker inspect ccd2
```

### 进入容器
```bash
docker exec -it ccd2 bash
```

---

## 🔧 手动部署(不使用脚本)

如果不想使用自动部署脚本,可以手动执行:

### 1. 加载镜像
```bash
docker load -i ccd2-app-all-in-one.tar
```

### 2. 启动容器
```bash
docker run -d \
    --name ccd2 \
    -p 8080:80 \
    -e DATABASE_URL="postgresql://user:pass@host:port/db" \
    -e SECRET_KEY="$(openssl rand -hex 32)" \
    -e LOG_LEVEL="INFO" \
    -e STORAGE_TYPE="local" \
    -v ccd2-uploads:/app/uploads \
    -v ccd2-logs:/app/logs \
    -v ccd2-redis-data:/var/lib/redis \
    --restart unless-stopped \
    ccd2-app:all-in-one
```

### 3. 检查状态
```bash
docker ps
docker logs ccd2
curl http://localhost:8080/api/health
```

---

## ❓ 常见问题

### Q1: 容器启动失败?

**查看日志:**
```bash
docker logs ccd2
```

**常见原因:**
- DATABASE_URL配置错误
- 端口8080已被占用
- Docker服务未启动

### Q2: 无法访问应用?

**检查防火墙:**
```bash
# Ubuntu
sudo ufw allow 8080
sudo ufw status

# 或使用iptables
sudo iptables -I INPUT -p tcp --dport 8080 -j ACCEPT
```

**检查端口监听:**
```bash
netstat -tlnp | grep 8080
```

### Q3: 数据库连接失败?

**检查数据库连接:**
```bash
# 在容器内测试
docker exec -it ccd2 bash
apt-get update && apt-get install -y postgresql-client
psql "postgresql://user:pass@host:port/db"
```

**检查网络:**
```bash
# 测试数据库主机连通性
ping 115.190.29.10
telnet 115.190.29.10 5433
```

### Q4: Redis连接失败?

Redis是内置在容器中的,如果失败:

```bash
# 进入容器检查
docker exec -it ccd2 bash

# 检查Redis进程
ps aux | grep redis

# 检查Redis日志
cat /var/log/supervisor/redis.log

# 手动测试Redis
redis-cli ping
```

### Q5: 如何更新应用?

```bash
# 1. 停止并删除旧容器
docker stop ccd2
docker rm ccd2

# 2. 删除旧镜像
docker rmi ccd2-app:all-in-one

# 3. 加载新镜像
docker load -i ccd2-app-all-in-one-new.tar

# 4. 启动新容器(使用相同命令)
docker run -d --name ccd2 ...
```

**注意:** 数据卷会保留,无需担心数据丢失。

---

## 📊 数据持久化

应用使用Docker卷存储数据:

- `ccd2-uploads` - 用户上传的文件
- `ccd2-logs` - 应用日志
- `ccd2-redis-data` - Redis数据

### 查看卷
```bash
docker volume ls | grep ccd2
```

### 备份卷
```bash
# 备份uploads
docker run --rm -v ccd2-uploads:/data -v $(pwd):/backup ubuntu tar czf /backup/uploads-backup.tar.gz /data

# 备份Redis数据
docker run --rm -v ccd2-redis-data:/data -v $(pwd):/backup ubuntu tar czf /backup/redis-backup.tar.gz /data
```

### 恢复卷
```bash
# 恢复uploads
docker run --rm -v ccd2-uploads:/data -v $(pwd):/backup ubuntu tar xzf /backup/uploads-backup.tar.gz -C /

# 恢复Redis数据
docker run --rm -v ccd2-redis-data:/data -v $(pwd):/backup ubuntu tar xzf /backup/redis-backup.tar.gz -C /
```

---

## 🎯 下一步

部署成功后,您可以:

1. **配置域名** - 使用Nginx反向代理
2. **启用HTTPS** - 使用Let's Encrypt证书
3. **设置监控** - 使用Prometheus + Grafana
4. **配置备份** - 定期备份数据库和文件
5. **优化性能** - 调整资源限制和缓存策略

详细信息请参考 `SINGLE_IMAGE_DEPLOYMENT_GUIDE.md`。

---

## 📞 技术支持

如有问题,请查看:
- 完整文档: `SINGLE_IMAGE_DEPLOYMENT_GUIDE.md`
- 容器日志: `docker logs -f ccd2`
- Supervisor日志: `docker exec ccd2 cat /var/log/supervisor/supervisord.log`

---

**部署时间**: 2025-10-18  
**镜像版本**: all-in-one  
**镜像大小**: 653.32 MB

