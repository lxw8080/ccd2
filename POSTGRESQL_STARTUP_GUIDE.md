# CCD2 项目 PostgreSQL 配置启动指南

## 概述

项目已配置为使用外部 PostgreSQL 数据库。以下配置已应用：

| 配置项 | 值 |
|------|-----|
| **数据库类型** | PostgreSQL |
| **数据库地址** | 115.190.29.10 |
| **数据库端口** | 5433 |
| **数据库名称** | ccd_db_new |
| **数据库用户** | flask_user |
| **数据库密码** | flask_password |
| **API_KEY** | lxw8025031 |
| **日志文件** | logs/server.log |
| **环境** | development |

## 配置文件位置

后端配置文件已创建：
- **位置**: `backend/.env`
- **作用**: 覆盖默认配置，使用外部 PostgreSQL 数据库

## 快速启动

### 方式一：使用 Python 脚本（推荐）

在项目根目录运行：

```bash
python quick_start.py
```

此脚本将自动：
1. 安装后端依赖（pip packages）
2. 启动 FastAPI 后端服务（后台进程）
3. 检查/安装前端依赖（npm packages）
4. 启动 Vite 前端开发服务器

### 方式二：手动启动

#### 步骤 1：安装后端依赖

```bash
cd backend
pip install --upgrade pip
pip install -r requirements.txt
```

#### 步骤 2：启动后端

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

后端将在 `http://localhost:8000` 运行

#### 步骤 3：启动前端（新终端窗口）

```bash
cd frontend
npm install    # 仅首次需要
npm run dev
```

前端将在 `http://localhost:5173` 运行

## 访问应用

### 本地访问
- **前端应用**: http://localhost:5173
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs（Swagger UI）
- **API 文档**: http://localhost:8000/redoc（ReDoc）

### 网络访问
如需通过局域网其他设备访问，请获取本机 IP 地址后访问：
- **前端**: http://<本机IP>:5173
- **后端**: http://<本机IP>:8000

## 配置详情

### 数据库连接

配置文件 `backend/app/config.py` 已更新以支持：

```python
DATABASE_URL: str = "postgresql://flask_user:flask_password@115.190.29.10:5433/ccd_db_new"
```

连接配置支持：
- **PostgreSQL 连接池**: 10 个初始连接，最多 20 个溢出连接
- **连接验证**: 使用 `pool_pre_ping=True` 确保连接有效
- **调试模式**: 启用 SQL 语句日志（开发环境）

### 环境变量

`.env` 文件中的关键配置：

```ini
DATABASE_URL=postgresql://flask_user:flask_password@115.190.29.10:5433/ccd_db_new
API_KEY=lxw8025031
LOG_FILE_PATH=logs/server.log
FLASK_ENV=development
DEBUG=True
```

## 常见问题

### 1. 无法连接到数据库

**症状**: 后端启动失败，出现数据库连接错误

**解决方案**:
1. 检查网络连接：`ping 115.190.29.10`
2. 确认端口开放：数据库服务器的 5433 端口是否开放
3. 验证凭证：确保用户名和密码正确
4. 查看错误日志：检查 `logs/server.log` 文件

### 2. 前端无法连接到后端

**症状**: 前端报错，无法调用 API

**解决方案**:
1. 确保后端已启动：访问 http://localhost:8000/health
2. 检查 CORS 配置：后端已配置允许来自 http://localhost:5173 的请求
3. 检查浏览器控制台的网络标签页，查看详细错误

### 3. npm 或 pip 安装缓慢

**症状**: 依赖安装速度很慢

**解决方案**:
- 使用国内镜像源加速

Python pip：
```bash
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
```

npm：
```bash
npm config set registry https://registry.npmmirror.com
```

### 4. 端口已被占用

**症状**: 启动时报告端口 8000 或 5173 已被占用

**解决方案**:
- 更改启动端口，或关闭占用该端口的其他应用

后端：
```bash
python -m uvicorn app.main:app --port 8001
```

前端（需要修改 Vite 配置或使用环境变量）

## 项目结构

```
ccd2/
├── backend/              # FastAPI 后端
│   ├── .env             # 环境变量（PostgreSQL 配置）
│   ├── app/
│   │   ├── main.py      # FastAPI 应用入口
│   │   ├── config.py    # 应用配置
│   │   ├── database.py  # 数据库连接
│   │   ├── models/      # 数据模型
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── api/         # API 路由
│   │   ├── core/        # 核心功能
│   │   └── services/    # 业务逻辑
│   └── requirements.txt  # Python 依赖
├── frontend/            # React + Vite 前端
│   ├── src/
│   │   ├── pages/       # 页面组件
│   │   ├── components/  # 通用组件
│   │   ├── services/    # API 调用
│   │   └── types/       # TypeScript 类型
│   └── package.json     # npm 依赖
└── quick_start.py       # 快速启动脚本
```

## 数据库迁移

数据库已预先迁移，包含所有必要的表和数据。应用启动时会：
1. 检查数据库连接
2. 验证表结构
3. 如需要，应用任何待处理的 Alembic 迁移

## 开发工具

### 后端调试

1. **启用 SQL 日志**: 在 `backend/app/database.py` 中设置 `echo=True`
2. **API 文档**: 访问 http://localhost:8000/docs 进行 API 测试
3. **热重载**: 使用 `--reload` 标志启动 uvicorn，自动重启服务

### 前端调试

1. **浏览器开发者工具**: F12 打开
2. **React DevTools**: 安装浏览器扩展
3. **网络检查**: 在 Network 标签页查看 API 调用

## 性能优化建议

1. **数据库连接池**: 已配置最优值，无需修改
2. **文件上传**: 配置最大文件大小为 20MB
3. **缓存**: 可配置 Redis 缓存（当前使用本地存储）

## 下一步

1. 访问 http://localhost:5173 打开应用
2. 使用默认账号登录
3. 开始使用系统功能

## 支持

如遇到问题，请检查：
1. 网络连接状态
2. 数据库服务器是否在线
3. 防火墙设置
4. 错误日志文件 (`logs/server.log`)

---

**最后更新**: 2025-10-18
**配置状态**: ✅ PostgreSQL 外部数据库配置完成


