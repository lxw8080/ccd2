# 📡 Webhook 使用指南

## 概述

Webhook 系统允许您在特定事件发生时接收实时通知，实现与外部系统的集成。

---

## 🎯 支持的事件

### 客户事件
- `customer.created` - 客户创建
- `customer.updated` - 客户更新
- `customer.deleted` - 客户删除
- `customer.status_changed` - 客户状态变更

### 文档事件
- `document.uploaded` - 文档上传
- `document.approved` - 文档审核通过
- `document.rejected` - 文档审核拒绝
- `document.deleted` - 文档删除

### 产品事件
- `product.created` - 产品创建
- `product.updated` - 产品更新
- `product.deleted` - 产品删除

---

## 📝 Webhook 负载格式

所有 Webhook 请求都使用 POST 方法，Content-Type 为 `application/json`。

### 负载结构

```json
{
  "event": "customer.created",
  "data": {
    "id": "123",
    "name": "张三",
    "customer_no": "C001",
    "phone": "13800138000"
  },
  "timestamp": "2025-10-17T10:30:00.000Z",
  "metadata": {
    "user_id": "admin",
    "ip_address": "192.168.1.1"
  }
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `event` | string | 事件类型 |
| `data` | object | 事件相关数据 |
| `timestamp` | string | 事件发生时间 (ISO 8601) |
| `metadata` | object | 元数据（可选） |

---

## 🔐 安全性

### 签名验证

如果您在注册 Webhook 时提供了密钥，系统会在请求头中添加签名：

```
X-Webhook-Signature: sha256=<signature>
```

### 验证签名（Python 示例）

```python
import hmac
import hashlib
import json

def verify_webhook_signature(payload: str, signature: str, secret: str) -> bool:
    """验证 Webhook 签名"""
    expected_signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # 移除 "sha256=" 前缀
    if signature.startswith("sha256="):
        signature = signature[7:]
    
    return hmac.compare_digest(expected_signature, signature)

# 使用示例
@app.post("/webhook")
async def handle_webhook(request: Request):
    payload = await request.body()
    signature = request.headers.get("X-Webhook-Signature", "")
    
    if not verify_webhook_signature(payload.decode(), signature, "your-secret-key"):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # 处理 webhook
    data = json.loads(payload)
    print(f"Received event: {data['event']}")
    
    return {"status": "ok"}
```

### 验证签名（Node.js 示例）

```javascript
const crypto = require('crypto');

function verifyWebhookSignature(payload, signature, secret) {
  const expectedSignature = crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex');
  
  // 移除 "sha256=" 前缀
  if (signature.startsWith('sha256=')) {
    signature = signature.substring(7);
  }
  
  return crypto.timingSafeEqual(
    Buffer.from(expectedSignature),
    Buffer.from(signature)
  );
}

// Express 示例
app.post('/webhook', express.raw({ type: 'application/json' }), (req, res) => {
  const signature = req.headers['x-webhook-signature'] || '';
  
  if (!verifyWebhookSignature(req.body.toString(), signature, 'your-secret-key')) {
    return res.status(401).json({ error: 'Invalid signature' });
  }
  
  const data = JSON.parse(req.body);
  console.log(`Received event: ${data.event}`);
  
  res.json({ status: 'ok' });
});
```

---

## 🚀 使用方法

### 1. 注册 Webhook

在后端代码中注册 Webhook 订阅：

```python
from app.core.webhooks import register_webhook, WebhookEvent

# 注册单个事件
register_webhook(
    url="https://your-domain.com/webhook",
    events=[WebhookEvent.CUSTOMER_CREATED],
    secret="your-secret-key"
)

# 注册多个事件
register_webhook(
    url="https://your-domain.com/webhook",
    events=[
        WebhookEvent.CUSTOMER_CREATED,
        WebhookEvent.CUSTOMER_UPDATED,
        WebhookEvent.DOCUMENT_APPROVED,
    ],
    secret="your-secret-key",
    headers={
        "Authorization": "Bearer your-api-token"
    }
)
```

### 2. 触发 Webhook

在业务代码中触发 Webhook：

```python
from app.core.webhooks import trigger_webhook, WebhookEvent

# 客户创建事件
async def create_customer(customer_data):
    # 创建客户
    customer = Customer(**customer_data)
    db.add(customer)
    db.commit()
    
    # 触发 webhook
    await trigger_webhook(
        WebhookEvent.CUSTOMER_CREATED,
        {
            "id": customer.id,
            "name": customer.name,
            "customer_no": customer.customer_no,
            "phone": customer.phone,
        },
        metadata={
            "user_id": current_user.id,
            "action": "create"
        }
    )
    
    return customer
```

### 3. 接收 Webhook

创建一个端点来接收 Webhook 通知：

```python
from fastapi import FastAPI, Request, HTTPException
import hmac
import hashlib

app = FastAPI()

@app.post("/webhook")
async def handle_webhook(request: Request):
    # 获取请求体
    body = await request.body()
    payload = body.decode()
    
    # 验证签名
    signature = request.headers.get("X-Webhook-Signature", "")
    if not verify_signature(payload, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # 解析数据
    import json
    data = json.loads(payload)
    
    # 根据事件类型处理
    event = data["event"]
    event_data = data["data"]
    
    if event == "customer.created":
        print(f"New customer created: {event_data['name']}")
        # 执行您的业务逻辑
    
    elif event == "document.approved":
        print(f"Document approved: {event_data['file_name']}")
        # 执行您的业务逻辑
    
    return {"status": "ok"}
```

---

## 📊 事件数据示例

### customer.created

```json
{
  "event": "customer.created",
  "data": {
    "id": "123",
    "customer_no": "C001",
    "name": "张三",
    "phone": "13800138000",
    "product_id": "1",
    "status": "collecting"
  },
  "timestamp": "2025-10-17T10:30:00.000Z"
}
```

### document.approved

```json
{
  "event": "document.approved",
  "data": {
    "id": "456",
    "customer_id": "123",
    "file_name": "身份证.jpg",
    "file_type": "image/jpeg",
    "status": "approved",
    "review_note": "审核通过"
  },
  "timestamp": "2025-10-17T10:35:00.000Z"
}
```

### customer.status_changed

```json
{
  "event": "customer.status_changed",
  "data": {
    "id": "123",
    "customer_no": "C001",
    "old_status": "collecting",
    "new_status": "completed"
  },
  "timestamp": "2025-10-17T10:40:00.000Z"
}
```

---

## ⚙️ 配置

### 从配置文件加载

您可以在应用启动时从配置文件加载 Webhook 订阅：

```python
# backend/app/main.py
from app.core.webhooks import init_webhooks

@app.on_event("startup")
async def startup_event():
    init_webhooks()
```

### 配置文件示例 (webhooks.json)

```json
{
  "webhooks": [
    {
      "url": "https://example.com/webhook",
      "events": ["customer.created", "customer.updated"],
      "secret": "your-secret-key",
      "headers": {
        "Authorization": "Bearer token"
      }
    }
  ]
}
```

---

## 🔍 调试

### 测试 Webhook

使用 [webhook.site](https://webhook.site) 或 [RequestBin](https://requestbin.com) 来测试 Webhook：

```python
register_webhook(
    url="https://webhook.site/your-unique-url",
    events=[WebhookEvent.CUSTOMER_CREATED]
)
```

### 日志

Webhook 系统会记录所有发送的请求和错误：

```
INFO: Triggering 2 webhooks for event customer.created
INFO: Webhook sent successfully to https://example.com/webhook
ERROR: Error sending webhook to https://example.com/webhook: Connection timeout
```

---

## 🛡️ 最佳实践

1. **使用 HTTPS**: 始终使用 HTTPS URL 来接收 Webhook
2. **验证签名**: 始终验证 Webhook 签名以确保安全性
3. **幂等性**: 设计您的 Webhook 处理器为幂等的，因为可能会收到重复的事件
4. **快速响应**: Webhook 处理器应该快速响应（< 5秒），将耗时操作放到后台队列
5. **错误处理**: 妥善处理错误，返回适当的 HTTP 状态码
6. **日志记录**: 记录所有接收到的 Webhook 以便调试

---

## 📚 相关资源

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Webhook 最佳实践](https://webhooks.fyi/)
- [HMAC 签名验证](https://en.wikipedia.org/wiki/HMAC)

---

**最后更新**: 2025-10-17

