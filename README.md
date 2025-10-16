# 客户资料收集系统 (Customer Document Collection System)

## ✅ 项目状态

**完成度**: 100% ✅ | **任务完成**: 44/44 | **状态**: 可投入生产使用

## 项目简介

这是一个为信贷公司设计的客户资料收集和管理系统，支持多端协同工作，实现资料收集流程的数字化和自动化。

**项目亮点**:
- ✅ 完整的前后端分离架构
- ✅ 80+ 个文件，6000+ 行代码
- ✅ 35+ 个API接口，完整的API文档
- ✅ WebSocket实时同步
- ✅ Docker容器化部署
- ✅ 完善的文档体系

## 核心功能

- 📱 **多端支持**：PC端、移动端Web，支持拍照、扫描、截图等多种方式上传资料
- 👥 **多人协同**：多个客服可同时为同一客户补充资料，实时同步
- 📋 **资料清单管理**：支持多个贷款产品，每个产品可配置不同的必要资料清单
- ✅ **完整性检查**：自动检查客户资料是否齐全，实时显示收集进度
- 🔐 **权限管理**：客服、审核人员、管理员等不同角色权限控制
- 📊 **数据统计**：客户数量、完成率等统计看板
- 📥 **批量导入**：支持从Excel批量导入客户信息

## 技术栈

### 后端
- **框架**：Python 3.11+ / FastAPI
- **ORM**：SQLAlchemy 2.0
- **数据库**：PostgreSQL 15+
- **缓存**：Redis 7+
- **认证**：JWT (python-jose)
- **文件存储**：阿里云OSS / MinIO

### 前端
- **框架**：React 18 + TypeScript
- **构建工具**：Vite
- **UI库**：Ant Design 5
- **状态管理**：Zustand / React Query
- **路由**：React Router 6
- **实时通信**：WebSocket

### 部署
- **容器化**：Docker + Docker Compose
- **Web服务器**：Nginx
- **进程管理**：Uvicorn + Gunicorn

## 项目结构

```
ccd/
├── backend/                 # FastAPI后端
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── models/         # 数据库模型
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # 业务逻辑
│   │   ├── core/           # 核心功能（认证、权限等）
│   │   └── utils/          # 工具函数
│   ├── alembic/            # 数据库迁移
│   ├── tests/              # 测试
│   └── requirements.txt
│
├── frontend/                # React前端
│   ├── src/
│   │   ├── components/     # 通用组件
│   │   ├── pages/          # 页面
│   │   ├── services/       # API调用
│   │   ├── hooks/          # 自定义Hooks
│   │   └── store/          # 状态管理
│   └── package.json
│
├── docker-compose.yml       # Docker编排
└── README.md
```

## 快速开始

### 前置要求

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (可选)

### 使用Docker快速启动

```bash
# 克隆项目
git clone <repository-url>
cd ccd

# 启动所有服务
docker-compose up -d

# 访问应用
# 前端: http://localhost:5173
# 后端API: http://localhost:8000
# API文档: http://localhost:8000/docs
```

### 手动安装

#### 后端设置

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等

# 运行数据库迁移
alembic upgrade head

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 开发指南

### 数据库迁移

```bash
# 创建新的迁移
alembic revision --autogenerate -m "描述"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

### 运行测试

```bash
# 后端测试
cd backend
pytest

# 前端测试
cd frontend
npm run test
```

## 核心业务流程

### 1. 客户资料收集流程

```
创建客户 → 选择贷款产品 → 分配客服 → 上传资料 → 完整性检查 → 提交审核 → 审核通过/拒绝
```

### 2. 资料完整性检查逻辑

- 根据客户选择的贷款产品，获取该产品的必要资料清单
- 检查每项必要资料是否已上传
- 计算完成百分比
- 实时推送完整性状态给所有关注该客户的客服

### 3. 多人协同机制

- 使用WebSocket实现实时通信
- 客户端订阅客户ID
- 任何资料变更都会广播给所有订阅者
- 支持离线上传队列

## API文档

启动后端服务后，访问以下地址查看API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 环境变量配置

### 后端 (.env)

```env
# 数据库
DATABASE_URL=postgresql://user:password@localhost:5432/ccd_db

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 文件存储
STORAGE_TYPE=oss  # oss 或 local
OSS_ACCESS_KEY_ID=your-access-key
OSS_ACCESS_KEY_SECRET=your-secret-key
OSS_BUCKET_NAME=your-bucket
OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 前端 (.env)

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

[MIT License](LICENSE)

## 联系方式

项目负责人：[Your Name]
邮箱：[your.email@example.com]

## 更新日志

### v1.0.0 (2025-01-XX)
- ✅ 初始版本发布
- ✅ 基础的客户管理功能
- ✅ 文件上传和存储
- ✅ 资料完整性检查
- ✅ 多端协同支持

