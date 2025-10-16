# 🚀 快速启动指南

## 📋 前置条件

在启动项目前，请确保已安装以下软件：

1. **Python 3.10+** - [下载](https://www.python.org/downloads/)
2. **Node.js 18+** - [下载](https://nodejs.org/)
3. **PostgreSQL 15+** - [下载](https://www.postgresql.org/download/)
4. **Redis 7+** - [下载](https://redis.io/download)

## ⚡ 快速启动 (3 步)

### 步骤 1: 启动数据库和缓存

**PostgreSQL**:
```powershell
# Windows 服务启动
net start PostgreSQL15

# 或使用 Services 应用手动启动
```

**Redis**:
```powershell
# 在新的 PowerShell 窗口中运行
redis-server
```

### 步骤 2: 启动后端

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

✅ 看到以下信息表示成功:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 步骤 3: 启动前端 (新终端)

```powershell
cd frontend
npm install  # 首次运行
npm run dev
```

✅ 看到以下信息表示成功:
```
VITE v... ready in ... ms
➜  Local:   http://localhost:5173/
```

## 🌐 访问应用

启动完成后，访问以下地址：

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端 | http://localhost:5173 | 用户界面 |
| 后端 API | http://localhost:8000 | REST API |
| API 文档 | http://localhost:8000/docs | Swagger UI |
| API 文档 | http://localhost:8000/redoc | ReDoc |

## 🔧 自动启动脚本

### Windows PowerShell

```powershell
.\start-project.ps1
```

### Windows 命令行

```cmd
start-project.bat
```

## 🆘 常见问题

### Q: 后端启动失败，提示数据库连接错误

**A**: 确保 PostgreSQL 已启动并创建了数据库：
```powershell
psql -U postgres -c "CREATE DATABASE ccd_db;"
```

### Q: 前端无法连接后端

**A**: 检查 `frontend/.env` 文件中的 API 地址配置：
```
VITE_API_BASE_URL=http://localhost:8000
```

### Q: 端口被占用

**A**: 查找并杀死占用端口的进程：
```powershell
# 查找占用 8000 端口的进程
netstat -ano | findstr :8000

# 杀死进程 (替换 PID)
taskkill /PID <PID> /F
```

### Q: npm 命令找不到

**A**: 重新安装 Node.js 或添加到 PATH：
```powershell
# 检查 Node.js 是否安装
node --version
npm --version
```

## 📚 更多信息

- 详细启动指南: 查看 `PROJECT_STARTUP_STATUS.md`
- 项目文档: 查看 `README.md`
- 开发指南: 查看 `QUICKSTART.md`
- 部署指南: 查看 `DEPLOYMENT.md`

## 🎯 首次使用

1. 启动项目后，访问 http://localhost:5173
2. 使用默认账户登录 (需要先创建)
3. 创建产品和客户
4. 上传文件并测试功能

## 💡 提示

- 后端使用 `--reload` 标志，代码修改后会自动重启
- 前端使用 Vite 热重载，修改代码后会自动刷新
- API 文档会自动生成，无需手动维护

---

**需要帮助?** 查看 `PROJECT_STARTUP_STATUS.md` 获取更详细的故障排除指南。

