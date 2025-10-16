# 快速启动指南

## 🚀 项目已搭建完成！

恭喜！客户资料收集系统的基础框架已经搭建完成。以下是快速启动和开发指南。

## 📁 项目结构

```
ccd/
├── backend/                 # FastAPI后端
│   ├── app/
│   │   ├── models/         # ✅ 数据库模型已创建
│   │   ├── core/           # ✅ 认证和权限系统已创建
│   │   ├── config.py       # ✅ 配置文件已创建
│   │   ├── database.py     # ✅ 数据库连接已配置
│   │   └── main.py         # ✅ FastAPI应用已创建
│   ├── alembic/            # ✅ 数据库迁移工具已配置
│   ├── requirements.txt    # ✅ Python依赖已列出
│   └── .env.example        # ✅ 环境变量模板已创建
│
├── frontend/                # React前端
│   ├── src/
│   │   ├── types/          # ✅ TypeScript类型定义已创建
│   │   ├── services/       # ✅ API客户端已配置
│   │   ├── App.tsx         # ✅ 主应用组件已创建
│   │   └── main.tsx        # ✅ 入口文件已创建
│   ├── package.json        # ✅ 前端依赖已列出
│   └── vite.config.ts      # ✅ Vite配置已完成
│
├── docker-compose.yml       # ✅ Docker编排文件已创建
├── README.md               # ✅ 项目文档已创建
└── .gitignore              # ✅ Git忽略文件已配置
```

## 🛠️ 开发环境准备

### 方式一：使用Docker（推荐）

这是最简单的方式，只需要安装Docker和Docker Compose。

```bash
# 1. 启动所有服务（PostgreSQL、Redis、后端、前端）
docker-compose up -d

# 2. 查看日志
docker-compose logs -f

# 3. 访问应用
# 前端: http://localhost:5173
# 后端API: http://localhost:8000
# API文档: http://localhost:8000/docs
```

### 方式二：手动安装

如果你想在本地开发环境中运行，请按以下步骤操作。

#### 1. 安装PostgreSQL和Redis

**Windows:**
- PostgreSQL: https://www.postgresql.org/download/windows/
- Redis: https://github.com/microsoftarchive/redis/releases

**macOS:**
```bash
brew install postgresql@15 redis
brew services start postgresql@15
brew services start redis
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql-15 redis-server
sudo systemctl start postgresql
sudo systemctl start redis
```

#### 2. 创建数据库

```bash
# 连接到PostgreSQL
psql -U postgres

# 在psql中执行
CREATE DATABASE ccd_db;
CREATE USER ccd_user WITH PASSWORD 'ccd_password';
GRANT ALL PRIVILEGES ON DATABASE ccd_db TO ccd_user;
\q
```

#### 3. 启动后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 复制环境变量文件
cp .env.example .env
# 编辑 .env 文件，确保数据库连接信息正确

# 运行数据库迁移
alembic upgrade head

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端将在 http://localhost:8000 启动

#### 4. 启动前端

打开新的终端窗口：

```bash
cd frontend

# 安装依赖
npm install

# 复制环境变量文件
cp .env.example .env

# 启动开发服务器
npm run dev
```

前端将在 http://localhost:5173 启动

## 📝 下一步开发任务

根据开发计划，接下来需要完成以下任务：

### 阶段1：后端核心功能（当前阶段）

1. **创建Pydantic Schemas** - 定义API的请求和响应模型
2. **实现用户认证系统** - JWT登录、注册、token验证
3. **实现权限管理** - 基于角色的访问控制
4. **开发贷款产品管理API** - 产品CRUD和资料清单配置
5. **开发客户管理API** - 客户的增删改查
6. **开发文件上传服务** - 文件上传、存储、获取
7. **开发资料完整性检查服务** - 检查客户资料是否齐全
8. **开发审计日志服务** - 记录所有操作

### 阶段2：前端核心功能

1. **搭建路由和布局** - 导航栏、侧边栏
2. **开发登录页面** - 用户登录界面
3. **开发客户列表页面** - 展示、搜索、筛选
4. **开发客户详情页面** - 资料清单、完整性进度
5. **开发文件上传组件** - 拖拽上传、压缩
6. **开发资料列表组件** - 预览、下载、删除
7. **开发产品管理页面** - 产品配置

### 阶段3：多端协同

1. **实现WebSocket服务** - 实时通信
2. **移动端适配** - 响应式布局
3. **PWA功能** - 离线支持

## 🧪 测试API

启动后端后，访问 http://localhost:8000/docs 查看自动生成的API文档。

当前可用的端点：
- `GET /` - 根路径，返回应用信息
- `GET /health` - 健康检查

## 📚 有用的命令

### 后端

```bash
# 创建新的数据库迁移
alembic revision --autogenerate -m "描述"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1

# 运行测试
pytest

# 代码格式化
black app/

# 代码检查
flake8 app/
```

### 前端

```bash
# 安装新依赖
npm install <package-name>

# 构建生产版本
npm run build

# 预览生产版本
npm run preview

# 运行测试
npm run test

# 代码检查
npm run lint
```

### Docker

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 查看日志
docker-compose logs -f [service-name]

# 重启服务
docker-compose restart [service-name]

# 重新构建并启动
docker-compose up -d --build
```

## 🔧 常见问题

### 1. 数据库连接失败

检查 `.env` 文件中的 `DATABASE_URL` 是否正确，确保PostgreSQL正在运行。

### 2. 前端无法连接后端

确保后端正在运行，检查 `frontend/.env` 中的 `VITE_API_BASE_URL` 是否正确。

### 3. 端口被占用

修改 `docker-compose.yml` 或启动命令中的端口号。

## 📖 参考文档

- [FastAPI文档](https://fastapi.tiangolo.com/)
- [React文档](https://react.dev/)
- [Ant Design文档](https://ant.design/)
- [SQLAlchemy文档](https://docs.sqlalchemy.org/)
- [Alembic文档](https://alembic.sqlalchemy.org/)

## 💡 开发建议

1. **先完成后端API** - 确保数据层和业务逻辑正确
2. **编写测试** - 为关键功能编写单元测试
3. **使用API文档** - FastAPI自动生成的文档非常有用
4. **提交代码前检查** - 运行测试和代码检查
5. **小步提交** - 每完成一个功能就提交一次

## 🎯 当前状态

✅ 项目框架已搭建完成  
✅ 数据库模型已定义  
✅ 基础配置已完成  
⏳ 等待开发API接口  
⏳ 等待开发前端页面  

---

**准备好了吗？让我们开始开发吧！** 🚀

如果需要帮助，请查看 README.md 或联系项目负责人。

