# 项目启动指南

## 当前状态

Docker Desktop 正在启动中。请按照以下步骤操作：

---

## 方案 A: 使用 Docker Compose（推荐）

### 步骤 1: 确保 Docker Desktop 已启动

1. 打开 **任务管理器** (Ctrl + Shift + Esc)
2. 查找 "Docker Desktop" 进程
3. 如果没有运行，手动启动：
   - 点击 **开始菜单**
   - 搜索 "Docker Desktop"
   - 点击启动
4. 等待 Docker Desktop 完全启动（通常需要 1-2 分钟）
   - 右下角系统托盘会显示 Docker 图标
   - 图标稳定后表示已就绪

### 步骤 2: 启动项目

打开 PowerShell 或 CMD，进入项目目录：

```powershell
cd c:\Users\16094\Desktop\ccd

# 启动所有服务
docker-compose up -d

# 查看启动状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 步骤 3: 初始化数据

```powershell
# 等待后端容器完全启动（约 30 秒）
Start-Sleep -Seconds 30

# 运行数据迁移脚本
docker-compose exec backend python scripts/migrate_data.py
```

### 步骤 4: 访问应用

- **前端**: http://localhost:5173
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

### 步骤 5: 登录

- **用户名**: admin
- **密码**: admin123

---

## 方案 B: 手动启动（如果 Docker 有问题）

### 前置要求

- Python 3.10+
- Node.js 16+
- PostgreSQL 15+
- Redis 7+

### 启动后端

```powershell
cd backend

# 创建虚拟环境
python -m venv venv
.\venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 启动前端（新终端）

```powershell
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

---

## 常见问题

### Q1: Docker Desktop 无法启动

**解决方案**:
1. 检查 Windows 是否启用了 Hyper-V
   - 打开 **控制面板** → **程序** → **启用或关闭 Windows 功能**
   - 勾选 **Hyper-V**
   - 重启电脑

2. 如果仍然无法启动，使用方案 B（手动启动）

### Q2: 端口被占用

**解决方案**:
```powershell
# 查找占用端口的进程
netstat -ano | findstr :5432
netstat -ano | findstr :6379
netstat -ano | findstr :8000
netstat -ano | findstr :5173

# 杀死进程（替换 PID）
taskkill /PID <PID> /F
```

### Q3: 容器启动失败

**解决方案**:
```powershell
# 查看详细日志
docker-compose logs backend
docker-compose logs postgres
docker-compose logs redis

# 重新构建
docker-compose down
docker-compose up -d --build
```

### Q4: 无法连接到数据库

**解决方案**:
```powershell
# 检查数据库是否运行
docker-compose ps postgres

# 测试连接
docker-compose exec postgres psql -U ccd_user -d ccd_db
```

### Q5: 前端无法访问后端

**解决方案**:
1. 检查后端是否运行: http://localhost:8000/docs
2. 检查 CORS 配置（backend/.env）
3. 检查防火墙设置

---

## 停止项目

```powershell
# 停止所有服务
docker-compose down

# 停止并删除数据
docker-compose down -v
```

---

## 查看日志

```powershell
# 查看所有日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
docker-compose logs -f redis
```

---

## 重启服务

```powershell
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart backend
docker-compose restart frontend
```

---

## 下一步

1. ✅ 启动项目
2. ✅ 访问 http://localhost:5173
3. ✅ 使用 admin/admin123 登录
4. ✅ 创建贷款产品
5. ✅ 创建客户
6. ✅ 上传资料文件

---

## 需要帮助？

查看以下文档：
- **QUICKSTART.md** - 详细的启动指南
- **README.md** - 项目介绍
- **DEPLOYMENT.md** - 部署指南

祝你使用愉快！🚀

