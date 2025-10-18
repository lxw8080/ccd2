# PDF预览功能快速指南

## 🎯 功能概述

PDF预览功能已升级为使用专业的PDF.js渲染引擎，提供跨平台、本地化的PDF查看体验。

---

## ✨ 主要特性

### 📄 PDF查看器功能
- ✅ **页面导航**: 上一页/下一页按钮，支持键盘快捷键
- ✅ **缩放控制**: 50% - 300% 自由缩放
- ✅ **页码显示**: 实时显示当前页/总页数
- ✅ **文本支持**: 可选择和复制PDF中的文本
- ✅ **表单支持**: 支持PDF表单和超链接

### 🌍 跨平台兼容
- ✅ Windows / macOS / Linux
- ✅ Chrome / Firefox / Safari / Edge
- ✅ iOS / Android 移动端

### 🇨🇳 中国大陆优化
- ✅ 所有资源完全本地化
- ✅ 无需访问外部CDN
- ✅ 支持离线环境

---

## 🚀 使用方法

### 1. 访问系统
```
URL: http://localhost:5173
用户名: admin
密码: admin123
```

### 2. 查看PDF文件

#### 方式一：资料管理页面
1. 点击左侧菜单「资料管理」
2. 找到PDF文件
3. 点击「预览」按钮
4. PDF将在弹窗中打开

#### 方式二：客户详情页面
1. 进入「客户列表」
2. 点击客户姓名进入详情
3. 在「资料上传」标签页中
4. 找到PDF文件，点击「预览」

### 3. 使用PDF查看器

#### 页面导航
- **上一页**: 点击「上一页」按钮或按键盘 ← 键
- **下一页**: 点击「下一页」按钮或按键盘 → 键
- **页码**: 顶部显示「第 X / 总页数 页」

#### 缩放控制
- **放大**: 点击「放大」按钮（最大300%）
- **缩小**: 点击「缩小」按钮（最小50%）
- **比例**: 中间显示当前缩放比例

#### 其他操作
- **文本选择**: 直接用鼠标选择PDF中的文本
- **复制文本**: 选中后右键复制或 Ctrl+C
- **下载**: 点击底部「下载」按钮
- **关闭**: 点击「关闭」按钮或按 ESC 键

---

## 🔧 技术架构

### 核心技术
- **react-pdf**: React PDF查看器组件库
- **pdfjs-dist**: Mozilla PDF.js核心渲染引擎
- **本地Worker**: PDF.js worker文件本地部署

### 文件结构
```
frontend/
├── public/
│   └── pdf-worker/
│       └── pdf.worker.min.mjs      # PDF.js worker (1.0 MB)
├── src/
│   ├── components/
│   │   ├── PDFViewer.tsx           # PDF查看器组件
│   │   └── FilePreview.tsx         # 文件预览组件
│   └── config/
│       └── pdfConfig.ts            # PDF.js配置
```

---

## 🐛 故障排查

### 问题：PDF无法加载

**可能原因**:
1. PDF文件损坏
2. 网络连接问题
3. Worker文件加载失败

**解决方案**:
1. 检查浏览器控制台错误信息
2. 尝试下载PDF文件验证完整性
3. 刷新页面重试
4. 清除浏览器缓存

### 问题：Worker加载失败

**检查步骤**:
1. 访问 http://localhost:5173/pdf-worker/pdf.worker.min.mjs
2. 应该能下载到约1MB的文件
3. 如果404，检查 `frontend/public/pdf-worker/` 目录

**修复方法**:
```bash
# 重新复制worker文件
cd frontend
Copy-Item "node_modules/pdfjs-dist/build/pdf.worker.min.mjs" `
          "public/pdf-worker/pdf.worker.min.mjs" -Force
```

### 问题：PDF显示模糊

**解决方案**:
- 使用缩放功能放大查看
- 默认缩放为100%，可放大至300%

---

## 📊 性能优化

### 已实现的优化
- ✅ Canvas渲染，性能优异
- ✅ 按需加载页面
- ✅ Worker多线程处理
- ✅ 文件缓存机制

### 建议的优化
- 📝 添加PDF缓存策略
- 📝 实现虚拟滚动（大文件）
- 📝 添加预加载机制

---

## 🔐 安全说明

### 文件访问控制
- ✅ 需要登录认证
- ✅ JWT Token验证
- ✅ 用户权限检查

### 数据传输
- ✅ HTTPS支持（生产环境）
- ✅ 文件内容加密传输
- ✅ CORS安全配置

---

## 📝 开发说明

### 添加新功能

如需添加PDF相关功能，编辑 `PDFViewer.tsx`:

```typescript
// 示例：添加打印功能
const handlePrint = () => {
  window.print()
}

// 在控制栏添加按钮
<Button onClick={handlePrint}>打印</Button>
```

### 更新PDF.js版本

```bash
# 1. 更新npm包
npm update react-pdf pdfjs-dist

# 2. 更新worker文件
Copy-Item "node_modules/pdfjs-dist/build/pdf.worker.min.mjs" `
          "public/pdf-worker/pdf.worker.min.mjs" -Force

# 3. 测试验证
npm run dev
```

---

## 📚 相关文档

- **详细报告**: `PDF_PREVIEW_FIX_REPORT.md`
- **测试脚本**: `test_pdf_preview.py`
- **React-PDF文档**: https://github.com/wojtekmaj/react-pdf
- **PDF.js文档**: https://mozilla.github.io/pdf.js/

---

## ✅ 验证清单

使用前请确认：

- [ ] 前端服务运行正常 (http://localhost:5173)
- [ ] 后端服务运行正常 (http://localhost:8000)
- [ ] Worker文件可访问 (http://localhost:5173/pdf-worker/pdf.worker.min.mjs)
- [ ] 能够登录系统
- [ ] 能够访问资料管理页面
- [ ] PDF文件能够正常预览
- [ ] 页面导航功能正常
- [ ] 缩放功能正常

---

**最后更新**: 2025-10-18  
**版本**: 1.0  
**状态**: ✅ 已完成并测试

