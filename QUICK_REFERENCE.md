# CCD2 项目快速参考

## 🚀 快速启动

### 一键启动（推荐）
```bash
python quick_start.py
```

### 分开启动
```bash
# Terminal 1: 后端
python start_backend.py

# Terminal 2: 前端
python start_frontend.py
```

---

## 📍 访问地址

| 服务 | 地址 |
|-----|-----|
| **前端** | http://localhost:5173 |
| **后端** | http://localhost:8000 |
| **API 文档** | http://localhost:8000/docs |
| **健康检查** | http://localhost:8000/health |

---

## 🗄️ 数据库配置

```
地址: 115.190.29.10:5433
数据库: ccd_db_new
用户: flask_user
密码: flask_password
```

---

## ⚙️ 关键配置文件

| 文件 | 说明 |
|-----|-----|
| `backend/.env` | 数据库连接和环境变量 |
| `backend/app/config.py` | 应用配置 |
| `backend/app/database.py` | 数据库连接 |
| `frontend/package.json` | 前端依赖 |

---

## 🔧 常用命令

### 后端
```bash
# 启动
python start_backend.py

# 手动启动
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 安装依赖
cd backend
pip install -r requirements.txt
```

### 前端
```bash
# 启动
python start_frontend.py

# 手动启动
cd frontend
npm install
npm run dev

# 构建
npm run build
```

### 检查状态
```bash
python check_services.py
```

---

## 🐛 常见问题

### 后端无法启动
- 检查网络: `ping 115.190.29.10`
- 检查 .env: `backend/.env` 是否存在
- 查看日志: `backend/logs/server.log`

### 前端无法加载
- 确认后端运行: http://localhost:8000/health
- 重装依赖: `cd frontend && npm install`
- 清除缓存: `Ctrl+Shift+Delete` (浏览器)

### 端口被占用
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>
```

---

## 📊 技术栈

| 层 | 技术 | 版本 |
|----|------|------|
| 前端 | React + Vite | 18.2.0 + 5.0.11 |
| 后端 | FastAPI | 0.109.0 |
| 数据库 | PostgreSQL | 10.0+ |
| ORM | SQLAlchemy | 2.0.25 |

---

## 📚 文档

| 文件 | 内容 |
|-----|-----|
| `POSTGRESQL_STARTUP_GUIDE.md` | 详细启动指南 |
| `PROJECT_STARTUP_SUMMARY.md` | 项目总结 |
| `COMPLETION_REPORT.md` | 完成报告 |

---

## 🔑 关键参数

| 参数 | 值 |
|-----|-----|
| API_KEY | lxw8025031 |
| 后端端口 | 8000 |
| 前端端口 | 5173 |
| 日志文件 | logs/server.log |
| 最大文件大小 | 20MB |
| Token 过期时间 | 30 分钟 |

---

## 📝 环境变量 (.env)

```ini
DATABASE_URL=postgresql://flask_user:flask_password@115.190.29.10:5433/ccd_db_new
API_KEY=lxw8025031
LOG_FILE_PATH=logs/server.log
FLASK_ENV=development
DEBUG=True
```

---

## ✅ 启动检查清单

- [ ] 检查网络连接
- [ ] 验证 `backend/.env` 文件存在
- [ ] 安装 Python 依赖
- [ ] 安装 Node.js 依赖
- [ ] 启动后端服务
- [ ] 启动前端服务
- [ ] 访问 http://localhost:5173
- [ ] 检查 API 文档: http://localhost:8000/docs

---

## 🎯 下一步

1. 运行: `python quick_start.py`
2. 访问: http://localhost:5173
3. 登录系统
4. 开始使用

---

**最后更新**: 2025-10-18  
**状态**: ✅ 项目运行中


