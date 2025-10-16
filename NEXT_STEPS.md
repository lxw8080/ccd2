# 📋 下一步开发指南

## 当前状态

✅ **已完成**: 项目基础架构、后端API系统、前端核心页面  
⏳ **进行中**: 多端协同和实时同步  
📊 **完成度**: 约75%

---

## 🎯 立即可以开始的工作

### 1. 测试现有功能

在开始新功能开发前，建议先测试已完成的功能：

```bash
# 1. 启动项目
docker-compose up -d

# 2. 创建管理员账户
docker-compose exec backend python -c "
from app.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

db = SessionLocal()
admin = User(
    username='admin',
    password_hash=get_password_hash('admin123'),
    full_name='系统管理员',
    role='admin',
    is_active=True
)
db.add(admin)
db.commit()
print('管理员创建成功')
"

# 3. 访问前端
# http://localhost:5173
# 登录: admin / admin123

# 4. 测试功能
# - 创建贷款产品
# - 创建客户
# - 查看客户列表
# - 查看客户详情
```

### 2. 完善前端组件

#### 2.1 文件上传组件 (高优先级)

**文件**: `frontend/src/components/FileUpload.tsx`

**功能需求**:
- 拖拽上传
- 图片压缩（使用browser-image-compression）
- 上传进度显示
- 文件类型验证
- 文件大小限制

**参考代码**:
```typescript
import { Upload, message } from 'antd'
import { InboxOutlined } from '@ant-design/icons'
import imageCompression from 'browser-image-compression'
import { api } from '../services/api'

const FileUpload: React.FC<{
  customerId: string
  documentTypeId: string
  onSuccess: () => void
}> = ({ customerId, documentTypeId, onSuccess }) => {
  const handleUpload = async (file: File) => {
    // 1. 如果是图片，先压缩
    let uploadFile = file
    if (file.type.startsWith('image/')) {
      uploadFile = await imageCompression(file, {
        maxSizeMB: 1,
        maxWidthOrHeight: 1920
      })
    }

    // 2. 上传文件
    const formData = new FormData()
    formData.append('file', uploadFile)
    formData.append('customer_id', customerId)
    formData.append('document_type_id', documentTypeId)

    const response = await api.post('/documents/upload', formData)
    message.success('上传成功')
    onSuccess()
  }

  return (
    <Upload.Dragger
      beforeUpload={handleUpload}
      showUploadList={false}
    >
      <p className="ant-upload-drag-icon">
        <InboxOutlined />
      </p>
      <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
    </Upload.Dragger>
  )
}
```

#### 2.2 资料列表组件

**文件**: `frontend/src/components/DocumentList.tsx`

**功能需求**:
- 展示已上传文件列表
- 文件预览（图片、PDF）
- 文件下载
- 文件删除
- 审核状态显示

#### 2.3 完善客户详情页

**文件**: `frontend/src/pages/CustomerDetail.tsx`

**需要添加**:
- 集成FileUpload组件
- 集成DocumentList组件
- 添加资料上传功能
- 添加资料删除功能

---

## 🚀 下一阶段功能开发

### 阶段4: 多端协同和实时同步

#### 4.1 WebSocket后端实现

**文件**: `backend/app/api/websocket.py`

```python
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, customer_id: str):
        await websocket.accept()
        if customer_id not in self.active_connections:
            self.active_connections[customer_id] = set()
        self.active_connections[customer_id].add(websocket)

    def disconnect(self, websocket: WebSocket, customer_id: str):
        self.active_connections[customer_id].remove(websocket)

    async def broadcast(self, customer_id: str, message: dict):
        if customer_id in self.active_connections:
            for connection in self.active_connections[customer_id]:
                await connection.send_json(message)

manager = ConnectionManager()

@router.websocket("/ws/{customer_id}")
async def websocket_endpoint(websocket: WebSocket, customer_id: str):
    await manager.connect(websocket, customer_id)
    try:
        while True:
            data = await websocket.receive_text()
            # 处理消息
    except WebSocketDisconnect:
        manager.disconnect(websocket, customer_id)
```

#### 4.2 WebSocket前端实现

**文件**: `frontend/src/services/websocket.ts`

```typescript
class WebSocketService {
  private ws: WebSocket | null = null
  private listeners: Map<string, Set<Function>> = new Map()

  connect(customerId: string) {
    this.ws = new WebSocket(`ws://localhost:8000/api/ws/${customerId}`)
    
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      this.emit(data.type, data.payload)
    }

    this.ws.onclose = () => {
      // 重连逻辑
      setTimeout(() => this.connect(customerId), 3000)
    }
  }

  on(eventType: string, callback: Function) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set())
    }
    this.listeners.get(eventType)!.add(callback)
  }

  private emit(eventType: string, data: any) {
    const callbacks = this.listeners.get(eventType)
    if (callbacks) {
      callbacks.forEach(cb => cb(data))
    }
  }
}

export default new WebSocketService()
```

#### 4.3 移动端响应式优化

**需要优化的页面**:
- CustomerList.tsx - 表格改为卡片布局
- CustomerDetail.tsx - 优化移动端布局
- Layout.tsx - 添加移动端菜单

**使用Ant Design的响应式工具**:
```typescript
import { Grid } from 'antd'
const { useBreakpoint } = Grid

const screens = useBreakpoint()
const isMobile = !screens.md
```

---

## 📦 批量导入功能

### 后端实现

**文件**: `backend/app/api/import_export.py`

```python
from fastapi import UploadFile
import pandas as pd

@router.post("/customers/import")
async def import_customers(
    file: UploadFile,
    db: Session = Depends(get_db)
):
    # 1. 读取Excel
    df = pd.read_excel(file.file)
    
    # 2. 验证数据
    errors = []
    success_count = 0
    
    for index, row in df.iterrows():
        try:
            customer = Customer(
                customer_no=row['客户编号'],
                name=row['客户姓名'],
                phone=row['手机号'],
                # ...
            )
            db.add(customer)
            success_count += 1
        except Exception as e:
            errors.append(f"第{index+2}行: {str(e)}")
    
    db.commit()
    
    return {
        "success_count": success_count,
        "error_count": len(errors),
        "errors": errors
    }
```

### 前端实现

**文件**: `frontend/src/pages/BatchImport.tsx`

```typescript
const BatchImport: React.FC = () => {
  const [uploading, setUploading] = useState(false)

  const handleUpload = async (file: File) => {
    setUploading(true)
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await api.post('/customers/import', formData)
      message.success(`成功导入 ${response.data.success_count} 条记录`)
      if (response.data.errors.length > 0) {
        // 显示错误详情
      }
    } catch (error) {
      message.error('导入失败')
    } finally {
      setUploading(false)
    }
  }

  return (
    <Upload beforeUpload={handleUpload}>
      <Button icon={<UploadOutlined />} loading={uploading}>
        选择Excel文件
      </Button>
    </Upload>
  )
}
```

---

## 🔧 性能优化建议

### 1. 数据库索引

```sql
-- 为常用查询字段添加索引
CREATE INDEX idx_customer_no ON customers(customer_no);
CREATE INDEX idx_customer_phone ON customers(phone);
CREATE INDEX idx_customer_status ON customers(status);
CREATE INDEX idx_document_customer ON customer_documents(customer_id);
CREATE INDEX idx_document_type ON customer_documents(document_type_id);
```

### 2. Redis缓存

```python
# 缓存产品列表
@router.get("/products")
async def get_products(redis: Redis = Depends(get_redis)):
    # 先从缓存获取
    cached = await redis.get("products:list")
    if cached:
        return json.loads(cached)
    
    # 从数据库查询
    products = db.query(LoanProduct).all()
    
    # 写入缓存
    await redis.setex("products:list", 3600, json.dumps(products))
    
    return products
```

### 3. 前端优化

```typescript
// 使用React.memo避免不必要的重渲染
const CustomerCard = React.memo(({ customer }) => {
  // ...
})

// 使用useMemo缓存计算结果
const filteredCustomers = useMemo(() => {
  return customers.filter(c => c.status === 'active')
}, [customers])

// 使用虚拟滚动处理大列表
import { List } from 'react-virtualized'
```

---

## 🧪 测试建议

### 1. 后端单元测试

**文件**: `backend/tests/test_auth.py`

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login():
    response = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
```

### 2. 前端组件测试

**文件**: `frontend/src/components/__tests__/Login.test.tsx`

```typescript
import { render, screen, fireEvent } from '@testing-library/react'
import Login from '../Login'

test('renders login form', () => {
  render(<Login />)
  expect(screen.getByPlaceholderText('用户名')).toBeInTheDocument()
  expect(screen.getByPlaceholderText('密码')).toBeInTheDocument()
})
```

---

## 📝 开发优先级

### 本周建议
1. ✅ 测试现有功能
2. 🔥 完成文件上传组件
3. 🔥 完成资料列表组件
4. 🔥 完善客户详情页

### 下周建议
5. WebSocket实时同步
6. 移动端响应式优化
7. 批量导入功能

### 后续建议
8. 数据统计看板
9. 性能优化
10. 单元测试
11. 部署上线

---

## 💡 开发提示

1. **使用API文档**: http://localhost:8000/docs
2. **查看数据库**: 使用pgAdmin或DBeaver连接PostgreSQL
3. **调试技巧**: 使用FastAPI的自动重载和React的热更新
4. **代码规范**: 遵循PEP8（Python）和ESLint（TypeScript）
5. **Git提交**: 每完成一个功能就提交一次

---

## 📞 需要帮助？

如果在开发过程中遇到问题：

1. 查看 `QUICKSTART.md` - 快速启动指南
2. 查看 `COMPLETION_REPORT.md` - 已完成功能说明
3. 查看 `FINAL_SUMMARY.md` - 项目总体概览
4. 查看API文档 - http://localhost:8000/docs

---

**祝开发顺利！** 🚀

