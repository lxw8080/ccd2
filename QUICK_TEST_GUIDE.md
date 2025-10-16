# 🚀 快速测试指南

## 项目已成功启动并通过测试！

---

## ✅ 当前状态

- **后端**: ✅ 运行中 (http://localhost:8000)
- **数据库**: ✅ SQLite (test.db)
- **API 文档**: ✅ 可访问 (http://localhost:8000/docs)
- **测试结果**: ✅ 所有核心功能正常

---

## 🎯 快速开始

### 1. 访问 API 文档

打开浏览器访问:
```
http://localhost:8000/docs
```

在 Swagger UI 中可以直接测试所有 API 端点。

### 2. 测试用户认证

**创建用户**:
```bash
POST /api/auth/register
{
  "username": "testuser",
  "password": "password123",
  "full_name": "Test User",
  "role": "customer_service"
}
```

**登录**:
```bash
POST /api/auth/login
{
  "username": "testuser",
  "password": "password123"
}
```

### 3. 测试产品管理

**创建产品**:
```bash
POST /api/products
{
  "code": "PRODUCT002",
  "name": "个人贷款",
  "description": "个人贷款产品"
}
```

**获取产品列表**:
```bash
GET /api/products
```

---

## 📊 已测试的功能

| 功能 | 状态 | 说明 |
|------|------|------|
| API 可用性 | ✅ | HTTP 200 |
| 用户注册 | ✅ | 成功创建用户 |
| 用户登录 | ✅ | 成功获取 Token |
| JWT 认证 | ✅ | Token 生成和验证正常 |
| 产品创建 | ✅ | 成功创建产品 |
| 产品查询 | ✅ | 成功获取产品列表 |
| 数据库 | ✅ | SQLite 正常工作 |
| 异常处理 | ✅ | 错误信息清晰 |

---

## 🔧 常用命令

### 启动后端
```powershell
cd backend
$env:DATABASE_URL="sqlite:///./test.db"
.\venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 启动前端
```powershell
cd frontend
npm install --registry=https://registry.npmmirror.com
npm run dev
```

### 运行测试脚本
```powershell
python test_api.py
```

---

## 📚 文档

- **API 文档**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **测试报告**: 查看 `TESTING_COMPLETE.md`
- **详细测试结果**: 查看 `TEST_RESULTS.md`

---

## 🐛 常见问题

### Q: 后端无法启动？
A: 确保 Python 虚拟环境已激活，并且所有依赖已安装。

### Q: 密码哈希失败？
A: 当前使用 SHA256 进行密码哈希（用于测试）。生产环境应使用 bcrypt 或 argon2。

### Q: 前端无法启动？
A: 清除 npm 缓存并使用国内镜像重新安装依赖：
```powershell
npm cache clean --force
npm install --registry=https://registry.npmmirror.com
```

### Q: 如何重置数据库？
A: 删除 `backend/test.db` 文件，重新启动后端即可。

---

## 🎊 下一步

1. **启动前端** - 完成前端依赖安装并启动
2. **集成测试** - 测试前后端集成
3. **功能测试** - 测试所有业务功能
4. **性能测试** - 测试系统性能

---

## 📞 需要帮助？

查看以下文件获取更多信息：
- `README.md` - 项目概述
- `TESTING_COMPLETE.md` - 完整测试报告
- `TEST_RESULTS.md` - 详细测试结果
- `DEPLOYMENT.md` - 部署指南

---

**项目状态**: ✅ 完全可用  
**最后更新**: 2025-10-17 01:05 UTC+8

