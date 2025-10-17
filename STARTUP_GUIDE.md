# 🚀 项目启动指南

## ⚡ 快速启动 (第一次)

### 步骤 1: 安装依赖

#### 后端
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 前端
```bash
cd frontend
npm install
```

### 步骤 2: 启动服务

#### 方法 A: 使用启动脚本 (推荐)
```bash
# 从项目根目录
./start.sh
```

#### 方法 B: 手动启动

**后端** (新终端窗口):
```bash
cd backend
source venv/bin/activate
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**前端** (新终端窗口):
```bash
cd frontend
npm run dev
```

### 步骤 3: 访问应用

打开浏览器访问:
```
http://localhost:5173
```

---

## 🔐 登录信息

### 管理员账户
- **用户名**: admin
- **密码**: admin123

### 测试账户
- **用户名**: test
- **密码**: test123

---

## 🌐 服务地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端应用 | http://localhost:5173 | 主应用界面 |
| 后端 API | http://localhost:8000 | REST API 端点 |
| Swagger 文档 | http://localhost:8000/docs | 交互式 API 文档 |
| ReDoc 文档 | http://localhost:8000/redoc | 静态 API 文档 |

---

## 🛑 停止服务

### 方法 A: 使用停止脚本
```bash
./stop.sh
```

### 方法 B: 手动停止
- 在运行服务的终端窗口按 `Ctrl+C`

---

## 📝 配置说明

### 后端配置 (backend/.env)

```env
# 应用
DEBUG=True
DATABASE_URL=sqlite:///:memory:

# 数据库: 使用内存数据库 (开发用)
# 如需持久化, 改为: sqlite:///./ccd_db.sqlite

# Redis (可选)
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```

---

## 💾 数据库

### 当前配置
- **类型**: SQLite (内存数据库)
- **优点**: 无需安装和配置外部数据库
- **注意**: 应用重启后数据会丢失

### 改用文件数据库 (持久化)
在 `.env` 中修改:
```env
DATABASE_URL=sqlite:///./ccd_db.sqlite
```

### 改用 PostgreSQL
```env
DATABASE_URL=postgresql://user:password@localhost:5432/ccd_db
```

---

## 🔥 热重载功能

### 前端
- Vite 已启用热重载
- 修改代码后浏览器自动刷新
- 无需手动重启

### 后端
- FastAPI --reload 已启用
- 修改代码后服务器自动重启
- 无需手动重启

---

## 📦 依赖更新

### 后端
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

### 前端
```bash
cd frontend
npm update
```

---

## 🆘 常见问题

### Q: 无法访问前端
**A**: 
- 确保访问地址是 http://localhost:5173
- 查看终端是否有错误信息
- 检查 npm 服务是否运行: `lsof -i :5173`

### Q: 无法连接后端 API
**A**:
- 检查后端是否运行: `lsof -i :8000`
- 查看后端日志是否有错误
- 确保 CORS 配置正确

### Q: 端口已被占用
**A**:
```bash
# 查看占用端口的进程
lsof -i :8000    # 后端
lsof -i :5173    # 前端

# 杀死进程 (替换 PID)
kill -9 <PID>
```

### Q: npm 找不到
**A**:
```bash
# 检查 Node.js 是否安装
node --version
npm --version

# 如果未安装, 从 https://nodejs.org 下载
```

### Q: Python 虚拟环境问题
**A**:
```bash
# 删除旧的虚拟环境
rm -rf backend/venv

# 重新创建
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📚 更多资源

- 项目文档: [README.md](README.md)
- 启动状态: [PROJECT_STARTUP_SUCCESS.md](PROJECT_STARTUP_SUCCESS.md)
- API 文档: http://localhost:8000/docs
- 前端源码: `frontend/src/`
- 后端源码: `backend/app/`

---

## 🎯 首次使用建议

1. 启动项目
2. 用 admin 账户登录
3. 创建一个贷款产品 (如 "个人贷款")
4. 创建一个客户
5. 上传客户资料文件
6. 查看完整性检查结果
7. 探索其他功能

---

**项目已准备就绪！** 🎉

有任何问题？查看日志或 API 文档。

