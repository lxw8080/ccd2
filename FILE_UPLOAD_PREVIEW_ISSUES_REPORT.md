# 📋 文件上传和预览功能问题报告

**测试日期**: 2025-10-17  
**测试工具**: MCP浏览器工具 + 手动测试  
**项目**: CCD2 客户资料收集系统

---

## 🔍 问题总结

### 问题1: 后端缺少静态文件服务路由 ✅ **已修复**

**症状**:
- 移动端无法查看图片和文件
- 文件预览URL返回404错误
- 文件下载失败

**根本原因**:
- `storage_service.get_file_url()` 返回 `/api/files/{file_path}`
- 但后端 `main.py` 没有配置静态文件服务路由
- FastAPI无法提供上传文件的访问

**修复方案**:
在 `backend/app/main.py` 中添加静态文件挂载：

```python
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# Mount static files for uploaded documents
upload_dir = Path(settings.UPLOAD_DIR)
upload_dir.mkdir(parents=True, exist_ok=True)
app.mount("/api/files", StaticFiles(directory=str(upload_dir)), name="files")
```

**测试结果**:
```bash
$ curl -I "http://localhost:8000/api/files/e0266c89-5f69-49da-8c71-d0e9c583ecc2/id_card/460524ca-a0ef-4f45-bf03-bf43b4b317c8.jpg"
HTTP/1.1 200 OK
content-type: image/jpeg
content-length: 133639
```

✅ **修复成功！**

---

### 问题2: 移动端无法访问localhost ⚠️ **需要配置**

**症状**:
- 移动设备访问前端时，文件URL指向 `http://localhost:8000`
- 移动设备无法解析localhost
- 图片和文件无法加载

**根本原因**:
- 前端通过Vite代理访问后端API
- 文件URL由后端生成，使用相对路径 `/api/files/...`
- 移动端直接访问前端时，相对路径会解析为前端服务器地址
- 但文件实际存储在后端服务器

**当前架构**:
```
移动设备 → http://192.168.x.x:5173 (前端Vite)
                ↓ (代理)
           http://localhost:8000 (后端FastAPI)
                ↓
           /api/files/... (静态文件)
```

**问题**:
- 前端返回的文件URL: `/api/files/xxx.jpg`
- 移动端解析为: `http://192.168.x.x:5173/api/files/xxx.jpg`
- 但文件在: `http://192.168.x.x:8000/api/files/xxx.jpg`

**解决方案选项**:

#### 方案A: 配置Vite代理转发文件请求 ✅ **推荐**

修改 `frontend/vite.config.ts`:
```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
    configure: (proxy, _options) => {
      proxy.on('proxyReq', (proxyReq, req, _res) => {
        if (req.headers.authorization) {
          proxyReq.setHeader('Authorization', req.headers.authorization);
        }
      });
    },
  },
  // 不需要额外配置，/api/files 已经被 /api 代理覆盖
}
```

**优点**:
- 无需修改后端代码
- 移动端和PC端使用相同配置
- 文件请求通过Vite代理转发到后端

**缺点**:
- 仅适用于开发环境
- 生产环境需要Nginx等反向代理

#### 方案B: 后端返回完整URL

修改 `backend/app/services/storage.py`:
```python
def get_file_url(self, file_path: str, expires_in: int = 3600) -> str:
    if self.storage_type == "local":
        # 返回完整URL而不是相对路径
        base_url = settings.API_BASE_URL or "http://localhost:8000"
        return f"{base_url}/api/files/{file_path}"
```

添加配置 `backend/app/config.py`:
```python
class Settings(BaseSettings):
    # API基础URL（用于生成文件访问链接）
    API_BASE_URL: str = "http://localhost:8000"
```

**优点**:
- 明确指定文件服务器地址
- 适用于生产环境

**缺点**:
- 需要配置环境变量
- 不同环境需要不同配置

#### 方案C: 前端环境变量配置

创建 `frontend/.env.development`:
```env
VITE_API_BASE_URL=http://192.168.x.x:8000
```

创建 `frontend/.env.production`:
```env
VITE_API_BASE_URL=https://api.yourdomain.com
```

**优点**:
- 灵活配置不同环境
- 前端完全控制API地址

**缺点**:
- 需要为每个网络环境配置
- IP地址变化需要重新配置

---

### 问题3: 文件上传功能测试 ⚠️ **待测试**

**当前状态**:
- 上传UI正常显示
- 上传区域可以展开/收起
- 文件拖拽区域正常

**待测试项**:
1. 文件选择功能
2. 文件上传进度
3. 图片压缩功能
4. 多文件上传
5. 文件类型验证
6. 文件大小验证
7. 上传成功后列表刷新

**测试限制**:
- MCP浏览器工具无法模拟文件选择
- 需要实际设备测试

---

## 📊 测试结果

### PC端测试 (http://localhost:5173)

| 功能 | 状态 | 说明 |
|------|------|------|
| 文件列表显示 | ✅ 正常 | 所有已上传文件正确显示 |
| 图片预览 | ✅ 正常 | 预览对话框正常打开，图片加载成功 |
| 文件下载 | ✅ 正常 | 下载功能正常 |
| 上传UI显示 | ✅ 正常 | 上传区域正常展开 |
| 静态文件访问 | ✅ 正常 | `/api/files/...` 返回200 OK |

### 移动端测试 (http://192.168.x.x:5173)

| 功能 | 状态 | 说明 |
|------|------|------|
| 文件列表显示 | ⚠️ 待测试 | 需要实际移动设备测试 |
| 图片预览 | ⚠️ 待测试 | 需要验证文件URL解析 |
| 文件下载 | ⚠️ 待测试 | 需要验证文件URL解析 |
| 文件上传 | ⚠️ 待测试 | 需要实际移动设备测试 |

---

## 🔧 已实施的修复

### 1. 添加静态文件服务 ✅

**文件**: `backend/app/main.py`

**修改内容**:
```python
# 导入必要的模块
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# 挂载静态文件目录
upload_dir = Path(settings.UPLOAD_DIR)
upload_dir.mkdir(parents=True, exist_ok=True)
app.mount("/api/files", StaticFiles(directory=str(upload_dir)), name="files")
```

**效果**:
- 后端现在可以提供上传文件的访问
- URL格式: `http://localhost:8000/api/files/{customer_id}/{doc_type}/{filename}`
- 支持图片、PDF等所有文件类型

---

## 📝 待实施的修复

### 1. 配置移动端文件访问 ⚠️ **高优先级**

**推荐方案**: 使用Vite代理（方案A）

**原因**:
- 无需修改后端代码
- 开发环境即可使用
- 配置简单

**当前状态**:
- Vite代理已配置 `/api` 路径
- `/api/files` 会自动被代理到后端
- 理论上移动端应该可以访问

**需要验证**:
1. 移动设备访问 `http://192.168.x.x:5173`
2. 查看文件是否正常加载
3. 检查网络请求是否正确代理

### 2. 添加文件上传测试 ⚠️ **中优先级**

**需要测试**:
- 单文件上传
- 多文件上传
- 图片压缩
- 文件验证
- 错误处理

**测试方法**:
- 使用实际移动设备
- 或使用Chrome DevTools模拟移动设备

---

## 🎯 生产环境建议

### 1. 使用CDN或对象存储

**当前**: 本地文件存储
**建议**: 阿里云OSS / MinIO

**优点**:
- 更好的性能
- 更高的可用性
- 支持图片处理（缩略图、水印等）
- 减轻服务器负担

**实施**:
```python
# backend/app/config.py
STORAGE_TYPE: str = "oss"  # 或 "minio"
OSS_ACCESS_KEY_ID: str = "your-key"
OSS_ACCESS_KEY_SECRET: str = "your-secret"
OSS_BUCKET_NAME: str = "ccd-files"
OSS_ENDPOINT: str = "oss-cn-hangzhou.aliyuncs.com"
```

### 2. 配置Nginx反向代理

**生产环境配置示例**:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # 前端静态文件
    location / {
        root /var/www/ccd-frontend;
        try_files $uri $uri/ /index.html;
    }

    # API代理
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. 启用HTTPS

**建议**:
- 使用Let's Encrypt免费证书
- 配置SSL/TLS
- 强制HTTPS重定向

---

## 📸 测试截图

### 图片预览功能
- 文件: `preview-modal.png`
- 位置: `/tmp/playwright-mcp-output/1760697539024/preview-modal.png`
- 状态: ✅ 预览正常显示

---

## 🔗 相关文件

### 后端文件
- `backend/app/main.py` - 主应用配置（已修改）
- `backend/app/services/storage.py` - 文件存储服务
- `backend/app/api/documents.py` - 文档API
- `backend/app/config.py` - 配置文件

### 前端文件
- `frontend/src/components/FileUpload.tsx` - 文件上传组件
- `frontend/src/components/DocumentUploadTab.tsx` - 文档上传标签页
- `frontend/src/components/FilePreview.tsx` - 文件预览组件
- `frontend/src/services/api.ts` - API客户端配置
- `frontend/vite.config.ts` - Vite配置

---

## ✅ 下一步行动

### 立即执行
1. ✅ 添加静态文件服务路由（已完成）
2. ⚠️ 使用实际移动设备测试文件访问
3. ⚠️ 测试文件上传功能

### 短期（本周）
1. 验证移动端文件访问
2. 完善错误处理
3. 添加上传进度显示优化
4. 添加文件预览缓存

### 中期（本月）
1. 考虑迁移到对象存储（OSS/MinIO）
2. 添加图片缩略图功能
3. 优化大文件上传
4. 添加断点续传

### 长期（季度）
1. 实施CDN加速
2. 添加文件安全扫描
3. 实现文件版本控制
4. 优化存储成本

---

**报告生成时间**: 2025-10-17 19:03  
**修复状态**: 1/3 已完成  
**待测试项**: 2 项  
**优先级**: 高

