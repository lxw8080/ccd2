# 🚀 快速参考指南

## 项目启动

### 前端启动
```bash
cd frontend
npm run dev
```
访问: http://localhost:5173

### 后端启动
```bash
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
访问: http://localhost:8000/docs

---

## 📱 响应式设计

### 断点
- **移动端**: < 768px (screens.md = false)
- **桌面端**: >= 768px (screens.md = true)

### 使用方法
```typescript
import { Grid } from 'antd'
const { useBreakpoint } = Grid

const screens = useBreakpoint()
const isMobile = !screens.md

// 条件渲染
{isMobile ? <MobileView /> : <DesktopView />}
```

---

## 🎨 添加新菜单

### 1. 编辑菜单配置
**文件**: `frontend/src/config/menuConfig.tsx`

```typescript
{
  key: 'new-feature',
  path: '/new-feature',
  label: '新功能',
  icon: StarOutlined,
  roles: ['admin', 'customer_service'],
}
```

### 2. 添加路由
**文件**: `frontend/src/config/routeConfig.tsx`

```typescript
{
  path: '/new-feature',
  element: LazyLoad(NewFeature),
  roles: ['admin', 'customer_service'],
}
```

### 3. 创建组件
**文件**: `frontend/src/pages/NewFeature.tsx`

```typescript
const NewFeature: React.FC = () => {
  return <div>新功能页面</div>
}

export default NewFeature
```

---

## 🔐 权限控制

### 角色
- `admin` - 管理员（所有权限）
- `customer_service` - 客服（客户管理、文档上传）
- `reviewer` - 审核员（文档审核）

### 检查权限
```typescript
// 前端
const hasPermission = hasRoutePermission(route, user.role)

// 后端
from app.core.permissions import check_permission
has_perm = check_permission(user.role, "customer.create")
```

---

## 📡 Webhook 使用

### 注册 Webhook
```python
from app.core.webhooks import register_webhook, WebhookEvent

register_webhook(
    url="https://example.com/webhook",
    events=[WebhookEvent.CUSTOMER_CREATED],
    secret="your-secret-key"
)
```

### 触发 Webhook
```python
from app.core.webhooks import trigger_webhook, WebhookEvent

await trigger_webhook(
    WebhookEvent.CUSTOMER_CREATED,
    {"id": customer.id, "name": customer.name}
)
```

### 接收 Webhook
```python
@app.post("/webhook")
async def handle_webhook(request: Request):
    # 验证签名
    # 处理事件
    return {"status": "ok"}
```

---

## 🗄️ 数据库

### 连接信息
- **主机**: 115.190.29.10
- **端口**: 5433
- **数据库**: ccd_db_new
- **用户**: flask_user

### 初始账户
| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | admin |
| test | test123 | customer_service |

---

## 🛠️ 常用命令

### 安装依赖
```bash
# 前端
cd frontend && npm install

# 后端
cd backend && pip install -r requirements.txt
```

### 数据库初始化
```bash
cd backend
python3 init_db.py
```

### 运行测试
```bash
# 前端
npm run test

# 后端
pytest
```

---

## 📂 项目结构

```
ccd2/
├── frontend/               # 前端项目
│   ├── src/
│   │   ├── components/    # 组件
│   │   ├── pages/         # 页面
│   │   ├── config/        # 配置文件
│   │   ├── store/         # 状态管理
│   │   └── utils/         # 工具函数
│   └── package.json
│
├── backend/               # 后端项目
│   ├── app/
│   │   ├── api/          # API 路由
│   │   ├── core/         # 核心功能
│   │   ├── models/       # 数据模型
│   │   └── main.py       # 入口文件
│   └── requirements.txt
│
└── docs/                 # 文档
```

---

## 🔍 调试技巧

### 前端调试
1. 打开浏览器开发者工具 (F12)
2. 查看 Console 标签页的错误信息
3. 使用 React DevTools 检查组件状态

### 后端调试
1. 查看终端输出的日志
2. 访问 http://localhost:8000/docs 测试 API
3. 检查 `logs/server.log` 文件

---

## 📚 重要文件

| 文件 | 说明 |
|------|------|
| `ARCHITECTURE_IMPROVEMENTS.md` | 架构改进文档 |
| `WEBHOOK_USAGE_GUIDE.md` | Webhook 使用指南 |
| `PROJECT_IMPROVEMENTS_SUMMARY.md` | 项目改进总结 |
| `QUICK_REFERENCE.md` | 本文件 |

---

## 🆘 常见问题

### Q: 前端启动失败？
A: 检查 Node.js 版本 (需要 >= 16)，运行 `npm install`

### Q: 后端启动失败？
A: 检查 Python 版本 (需要 >= 3.9)，运行 `pip install -r requirements.txt`

### Q: 数据库连接失败？
A: 检查 `.env` 文件中的数据库配置

### Q: 移动端菜单不显示？
A: 检查浏览器窗口宽度是否 < 768px

---

## 📞 获取帮助

- 查看文档: `docs/` 目录
- API 文档: http://localhost:8000/docs
- 项目仓库: (添加您的仓库链接)

---

**最后更新**: 2025-10-17

