# CCD2 项目 - PostgreSQL 外部数据库配置

**项目**: 客户资料收集系统 (CCD2)  
**配置日期**: 2025-10-18  
**数据库**: PostgreSQL (外部)  
**状态**: ✅ **配置完成并启动成功**

---

## 📌 项目概述

CCD2 是一个客户资料收集系统，现已配置为使用外部 PostgreSQL 数据库，支持在本地或远程环境下运行。

### 核心特性
- ✅ 使用外部 PostgreSQL 数据库
- ✅ FastAPI 后端服务
- ✅ React + Vite 前端应用
- ✅ 一键启动脚本
- ✅ 详细的文档和指南

---

## 🚀 快速开始

### 最简单的方式（一键启动）

```bash
# 在项目根目录执行
python quick_start.py
```

此命令将：
1. 自动安装后端 Python 依赖
2. 启动 FastAPI 后端服务
3. 自动安装前端 npm 依赖
4. 启动 Vite 前端开发服务器

### 分开启动（如需单独启动某个服务）

**后端**:
```bash
python start_backend.py
```

**前端**（新终端窗口）:
```bash
python start_frontend.py
```

### 检查服务状态

```bash
python check_services.py
```

---

## 📍 访问应用

启动后，可以通过以下地址访问：

| 服务 | 地址 | 说明 |
|-----|-----|-----|
| **前端应用** | http://localhost:5173 | React 前端 |
| **后端 API** | http://localhost:8000 | FastAPI 服务器 |
| **API 文档** (Swagger) | http://localhost:8000/docs | 交互式 API 测试 |
| **API 文档** (ReDoc) | http://localhost:8000/redoc | 另一种 API 文档格式 |
| **健康检查** | http://localhost:8000/health | 后端状态检查 |

---

## 🗄️ 数据库配置

### 连接信息

```
主机地址: 115.190.29.10
端口: 5433
数据库名: ccd_db_new
用户名: flask_user
密码: flask_password
```

### 连接字符串

```
postgresql://flask_user:flask_password@115.190.29.10:5433/ccd_db_new
```

### 环境变量

数据库配置保存在 `backend/.env` 文件中：

```ini
DATABASE_URL=postgresql://flask_user:flask_password@115.190.29.10:5433/ccd_db_new
API_KEY=lxw8025031
LOG_FILE_PATH=logs/server.log
FLASK_ENV=development
DEBUG=True
STORAGE_TYPE=local
REDIS_URL=redis://localhost:6379/0
LOG_LEVEL=INFO
```

---

## 📁 项目结构

```
ccd2/
├── backend/                          # FastAPI 后端
│   ├── .env                         # 环境变量配置（PostgreSQL）
│   ├── app/
│   │   ├── config.py                # 应用配置
│   │   ├── database.py              # 数据库连接设置
│   │   ├── main.py                  # FastAPI 主应用
│   │   ├── models/                  # 数据库模型
│   │   ├── schemas/                 # 数据验证 schemas
│   │   ├── api/                     # API 路由
│   │   │   ├── auth.py              # 认证相关
│   │   │   ├── customers.py         # 客户管理
│   │   │   ├── documents.py         # 文档管理
│   │   │   ├── products.py          # 产品管理
│   │   │   └── ...
│   │   ├── core/                    # 核心功能
│   │   ├── services/                # 业务逻辑
│   │   └── utils/                   # 工具函数
│   └── requirements.txt              # Python 依赖
│
├── frontend/                         # React + Vite 前端
│   ├── src/
│   │   ├── pages/                   # 页面组件
│   │   ├── components/              # UI 组件
│   │   ├── services/api.ts          # API 请求客户端
│   │   ├── store/                   # 状态管理 (Zustand)
│   │   ├── types/                   # TypeScript 类型
│   │   ├── main.tsx                 # React 入口
│   │   └── App.tsx                  # 主应用组件
│   ├── package.json                 # npm 依赖
│   └── vite.config.ts               # Vite 配置
│
├── quick_start.py                   # 一键启动脚本
├── start_backend.py                 # 后端启动脚本
├── start_frontend.py                # 前端启动脚本
├── check_services.py                # 服务检查脚本
├── verify_configuration.py          # 配置验证脚本
│
├── QUICK_REFERENCE.md               # 快速参考卡片
├── POSTGRESQL_STARTUP_GUIDE.md      # 详细启动指南
├── PROJECT_STARTUP_SUMMARY.md       # 项目启动总结
├── COMPLETION_REPORT.md             # 完成报告
└── README_POSTGRESQL.md             # 本文件
```

---

## ⚙️ 配置文件说明

### 1. backend/.env（环境变量）

此文件包含所有运行时配置，包括数据库连接字符串和 API 密钥。

**关键变量**:
- `DATABASE_URL`: PostgreSQL 连接字符串
- `API_KEY`: API 认证密钥
- `FLASK_ENV`: 运行环境 (development/production)
- `DEBUG`: 调试模式开关
- `LOG_FILE_PATH`: 日志文件位置

### 2. backend/app/config.py（应用配置）

Python Pydantic 配置类，定义应用的所有配置项。

**更新内容**:
- 默认 `DATABASE_URL` 指向外部 PostgreSQL
- `API_KEY` 设置为 `lxw8025031`
- 自动从 `.env` 文件加载环境变量

### 3. backend/app/database.py（数据库连接）

SQLAlchemy 数据库引擎和会话配置。

**连接池设置**:
- 初始连接数: 10
- 最多溢出连接数: 20
- 连接验证: 启用 (`pool_pre_ping=True`)

---

## 🔧 常用命令

### 后端相关

```bash
# 启动后端
python start_backend.py

# 手动启动（带热重载）
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 安装/更新依赖
cd backend
pip install -r requirements.txt

# 查看 API 文档
# 访问 http://localhost:8000/docs
```

### 前端相关

```bash
# 启动前端
python start_frontend.py

# 手动启动
cd frontend
npm install
npm run dev

# 构建生产版本
npm run build

# 预览构建结果
npm run preview
```

### 数据库相关

```bash
# 验证配置
python verify_configuration.py

# 检查服务状态
python check_services.py
```

---

## 🐛 常见问题

### Q1: 后端启动失败，显示数据库连接错误

**原因**: 无法连接到外部 PostgreSQL 服务器

**解决步骤**:
1. 验证网络连接
   ```bash
   ping 115.190.29.10
   ```

2. 检查 `.env` 文件
   ```bash
   type backend\.env  # Windows
   cat backend/.env   # Linux/Mac
   ```

3. 确认防火墙允许 5433 端口

4. 查看详细错误日志
   ```bash
   # 启动时输出详细信息
   python start_backend.py
   ```

5. 验证数据库凭证是否正确

### Q2: 前端无法连接到后端

**症状**: 前端显示"API 连接失败"或请求超时

**解决步骤**:
1. 检查后端是否运行
   ```bash
   # 访问健康检查端点
   # http://localhost:8000/health
   ```

2. 检查浏览器控制台错误
   ```
   F12 → Console 标签页 → 查看红色错误信息
   ```

3. 检查 CORS 配置
   - 后端已配置允许 `http://localhost:5173`
   - 如需修改，编辑 `backend/app/main.py` 中的 CORS 设置

4. 清除浏览器缓存
   ```
   Ctrl+Shift+Delete 或 Cmd+Shift+Delete
   ```

### Q3: 端口 8000 或 5173 被占用

**错误信息**:
```
Address already in use
```

**解决方案**:

Windows:
```bash
# 查找占用端口的进程
netstat -ano | findstr :8000

# 杀死进程（用上面的 PID 替换 <PID>）
taskkill /PID <PID> /F
```

Linux/Mac:
```bash
# 查找占用端口的进程
lsof -i :8000

# 杀死进程
kill -9 <PID>
```

### Q4: npm install 速度很慢

**原因**: 默认 npm 源可能很慢

**解决方案**:
```bash
# 配置国内镜像
npm config set registry https://registry.npmmirror.com

# 或使用阿里镜像
npm config set registry https://registry.aliyuncs.com/npm/

# 恢复默认源
npm config set registry https://registry.npmjs.org/
```

### Q5: Python 依赖安装失败

**原因**: pip 源可能出现问题

**解决方案**:
```bash
# 使用国内镜像
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/

# 或使用清华镜像
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 恢复默认源
pip config unset global.index-url
```

---

## 📊 技术栈

### 后端
| 组件 | 版本 | 说明 |
|-----|------|-----|
| Python | 3.8+ | 编程语言 |
| FastAPI | 0.109.0 | Web 框架 |
| Uvicorn | 0.27.0 | ASGI 服务器 |
| SQLAlchemy | 2.0.25 | ORM |
| Alembic | 1.13.1 | 数据库迁移 |
| Pydantic | 2.5.3 | 数据验证 |
| psycopg2 | 2.9.9 | PostgreSQL 驱动 |

### 前端
| 组件 | 版本 | 说明 |
|-----|------|-----|
| Node.js | 14.0+ | JavaScript 运行时 |
| React | 18.2.0 | UI 框架 |
| Vite | 5.0.11 | 构建工具 |
| TypeScript | 5.3.3 | 类型脚本 |
| Axios | 1.6.5 | HTTP 客户端 |
| Zustand | 4.4.7 | 状态管理 |
| Ant Design | 5.12.8 | UI 组件库 |

### 数据库
| 组件 | 版本 |
|-----|------|
| PostgreSQL | 10.0+ |
| 连接池 | SQLAlchemy |

---

## 📝 文档导航

| 文档 | 内容 | 用途 |
|-----|-----|-----|
| **QUICK_REFERENCE.md** | 快速参考卡片 | 快速查询常用命令和配置 |
| **POSTGRESQL_STARTUP_GUIDE.md** | 详细启动指南 | 详细的启动步骤和配置说明 |
| **PROJECT_STARTUP_SUMMARY.md** | 项目启动总结 | 项目概览和技术栈信息 |
| **COMPLETION_REPORT.md** | 完成报告 | 任务完成情况和验证清单 |
| **README_POSTGRESQL.md** | 本文件 | 综合说明文档 |

---

## ✅ 启动检查清单

在启动项目前，请确保以下条件满足：

- [ ] 网络连接正常
- [ ] 可以 ping 通 115.190.29.10
- [ ] 防火墙允许 5433 端口
- [ ] Python 3.8+ 已安装
- [ ] Node.js 14.0+ 已安装
- [ ] npm 6.0+ 已安装
- [ ] `backend/.env` 文件存在
- [ ] 已运行 `python verify_configuration.py` 验证配置

---

## 🎯 使用场景

### 开发环境
```bash
# 适合本地开发
python quick_start.py

# 或分开启动便于调试
python start_backend.py  # Terminal 1
python start_frontend.py # Terminal 2
```

### 测试环境
```bash
# 在有限资源的测试机上分开启动
python start_backend.py &
sleep 5
python start_frontend.py
```

### 集成环境
- 后端可独立部署到服务器
- 前端可编译为静态文件部署到 CDN
- 通过环境变量灵活配置数据库连接

---

## 🔐 安全建议

### 生产环境配置

1. **更改默认凭证**
   - 修改 `.env` 中的 `API_KEY`
   - 更新数据库密码

2. **启用 HTTPS**
   - 配置 SSL 证书
   - 更新 CORS 允许的源

3. **环境变量管理**
   - 不要提交 `.env` 到 Git
   - 使用密钥管理服务（如 AWS Secrets Manager）

4. **日志和监控**
   - 启用审计日志
   - 配置监控告警

---

## 📞 支持和反馈

如遇到问题，请按照以下步骤排查：

1. 检查网络连接
2. 验证配置文件 (`verify_configuration.py`)
3. 查看错误日志 (`backend/logs/server.log`)
4. 参考文档中的故障排查部分

---

## 📚 相关资源

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [React 官方文档](https://react.dev/)
- [Vite 官方文档](https://vitejs.dev/)
- [PostgreSQL 官方文档](https://www.postgresql.org/docs/)
- [SQLAlchemy 官方文档](https://docs.sqlalchemy.org/)

---

## 更新历史

| 日期 | 变更 | 版本 |
|-----|-----|-----|
| 2025-10-18 | PostgreSQL 配置完成并启动 | 1.0.0 |

---

**项目状态**: ✅ **已就绪**

现在您可以通过运行 `python quick_start.py` 启动项目！

祝您使用愉快！🚀


