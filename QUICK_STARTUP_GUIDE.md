# 🚀 快速启动指南

## 📌 项目已完全配置并运行中

### ✅ 当前状态
- ✅ 前端: http://localhost:5173 (运行中)
- ✅ 后端: http://localhost:8000 (运行中)
- ✅ 数据库: 115.190.29.10:5433 (已连接)
- ✅ API 文档: http://localhost:8000/docs (可用)

---

## 🔐 登录凭证

### 管理员账户
```
用户名: admin
密码: admin123
```

### 测试账户
```
用户名: test
密码: test123
```

---

## 🌐 访问应用

### 1. 打开前端
访问: **http://localhost:5173**

### 2. 查看 API 文档
访问: **http://localhost:8000/docs**

### 3. 测试 API
```bash
# 登录
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 获取用户信息
curl -X GET "http://localhost:8000/api/users/me" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📁 项目结构

```
ccd2/
├── frontend/              # React 前端
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
├── backend/               # FastAPI 后端
│   ├── app/
│   ├── requirements.txt
│   ├── .env              # 环境变量配置
│   ├── create_db.py      # 创建数据库脚本
│   └── init_db.py        # 初始化数据库脚本
└── docker-compose.yml    # Docker 配置
```

---

## 🛠️ 常用命令

### 启动后端
```bash
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 启动前端
```bash
cd frontend
npm run dev
```

### 创建数据库
```bash
cd backend
python3 create_db.py
```

### 初始化数据库
```bash
cd backend
python3 init_db.py
```

---

## 📊 数据库信息

### 连接字符串
```
postgresql://flask_user:flask_password@115.190.29.10:5433/ccd_db_new
```

### 已创建的表
- users - 用户表
- customers - 客户表
- loan_products - 贷款产品表
- customer_documents - 客户文档表
- document_types - 文档类型表
- audit_logs - 审计日志表
- import_records - 导入记录表

---

## 🔄 工作流程

### 1. 用户登录
- 访问前端: http://localhost:5173
- 输入用户名和密码
- 获取 JWT Token

### 2. 创建贷款产品
- 登录后进入产品管理
- 创建新的贷款产品
- 配置产品参数

### 3. 添加客户
- 进入客户管理
- 添加新客户信息
- 分配给相应的员工

### 4. 上传文档
- 为客户上传相关文档
- 系统自动验证文档完整性
- 生成审计日志

### 5. 查看报表
- 查看客户统计
- 查看文档完整性报告
- 导出数据

---

## 🐛 常见问题

### Q: 无法连接到数据库？
A: 检查网络连接和数据库服务器状态

### Q: 前端无法访问？
A: 确保 npm run dev 已启动，检查端口 5173

### Q: API 返回 401 错误？
A: 检查 JWT Token 是否有效，重新登录

### Q: 数据库表不存在？
A: 运行 `python3 init_db.py` 初始化数据库

---

## 📞 技术支持

### 后端日志
```bash
tail -f backend/logs/server.log
```

### 前端控制台
打开浏览器开发者工具 (F12) 查看控制台

### API 文档
访问 http://localhost:8000/docs 查看完整 API 文档

---

## ✨ 功能特性

- ✅ 用户认证和授权
- ✅ 客户信息管理
- ✅ 贷款产品管理
- ✅ 文档上传和验证
- ✅ 审计日志记录
- ✅ 数据导入导出
- ✅ 权限管理
- ✅ WebSocket 实时通知

---

**项目已准备就绪，开始使用吧！** 🎉

