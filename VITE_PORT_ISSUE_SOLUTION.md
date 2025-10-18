# Vite 端口权限问题解决方案

## 📋 问题描述

**错误信息**:
```
error when starting dev server:
Error: listen EACCES: permission denied 0.0.0.0:5173
    at Server.setupListenHandle [as _listen2] (node:net:1918:21)
```

**问题原因**:
Vite 配置中使用了 `host: true`，这会让 Vite 监听 `0.0.0.0`（所有网络接口）。在 Windows 系统上，监听 `0.0.0.0` 可能需要管理员权限。

---

## ✅ 解决方案

### 方案一: 修改 Vite 配置（推荐）

修改 `frontend/vite.config.ts` 文件，将 `host: true` 改为 `host: 'localhost'`：

**修改前**:
```typescript
server: {
  port: 5173,
  host: true,  // 监听 0.0.0.0，需要管理员权限
  proxy: {
    // ...
  }
}
```

**修改后**:
```typescript
server: {
  port: 5173,
  host: 'localhost',  // 只监听 localhost，无需管理员权限
  proxy: {
    // ...
  }
}
```

**优点**:
- ✅ 无需管理员权限
- ✅ 适合本地开发
- ✅ 更安全

**缺点**:
- ⚠️ 无法从局域网其他设备访问

---

### 方案二: 以管理员身份运行

如果需要从局域网其他设备访问前端应用，可以保持 `host: true`，但需要以管理员身份运行启动脚本。

**Windows 操作**:
1. 右键点击 `start-ccd2.ps1` 或 `start-ccd2.bat`
2. 选择 "以管理员身份运行"

**优点**:
- ✅ 可以从局域网访问
- ✅ 适合团队协作

**缺点**:
- ⚠️ 需要管理员权限
- ⚠️ 每次都需要确认 UAC 提示

---

### 方案三: 使用特定 IP 地址

修改配置为监听特定的网络接口 IP：

```typescript
server: {
  port: 5173,
  host: '127.0.0.1',  // 或者使用本机的局域网 IP
  proxy: {
    // ...
  }
}
```

---

## 🔧 已实施的修改

### 1. 修改了 Vite 配置

**文件**: `frontend/vite.config.ts`

**修改内容**:
```typescript
// 从
host: true,

// 改为
host: 'localhost',
```

**结果**: ✅ 问题已解决

---

### 2. 创建了服务停止脚本

**文件**: `stop-services.ps1`

**功能**:
- 检查并停止占用 8000 端口的进程（后端）
- 检查并停止占用 5173 端口的进程（前端）
- 验证端口是否已释放

**使用方法**:
```powershell
.\stop-services.ps1
```

---

## 📊 测试结果

### 服务状态验证

使用 `python check_services.py` 验证：

```
============================================================
CCD2 Services Status Check
============================================================

Checking services...

✅ OK: Backend is running on http://localhost:8000
✅ OK: Frontend is running on http://localhost:5173

============================================================
✅ OK: All services are running!

Access the application at:
  Frontend: http://localhost:5173
  Backend: http://localhost:8000
  API Docs: http://localhost:8000/docs
```

**结论**: ✅ **问题已解决，服务正常运行！**

---

## 💡 其他可能的解决方案

### 1. 检查防火墙设置

如果问题仍然存在，检查 Windows 防火墙是否阻止了 Node.js：

```powershell
# 查看防火墙规则
Get-NetFirewallRule | Where-Object { $_.DisplayName -like "*Node*" }

# 添加防火墙规则（需要管理员权限）
New-NetFirewallRule -DisplayName "Node.js" -Direction Inbound -Program "C:\Program Files\nodejs\node.exe" -Action Allow
```

---

### 2. 检查端口占用

```powershell
# 检查 5173 端口
Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue

# 或使用 netstat
netstat -ano | findstr :5173
```

---

### 3. 更改端口号

如果 5173 端口有问题，可以更改为其他端口：

```typescript
server: {
  port: 3000,  // 使用其他端口
  host: 'localhost',
  // ...
}
```

---

## 🚀 启动项目

修改配置后，使用以下任一方式启动项目：

### 方式一: PowerShell 脚本
```powershell
.\start-ccd2.ps1
```

### 方式二: 批处理脚本
```cmd
start-ccd2.bat
```

### 方式三: Python 脚本
```bash
python quick_start.py
```

### 方式四: 手动启动

**后端**:
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**前端**（新终端）:
```bash
cd frontend
npm run dev
```

---

## 📝 配置文件对比

### 修改前的配置

```typescript
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    host: true,  // ❌ 监听 0.0.0.0，可能需要管理员权限
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

### 修改后的配置

```typescript
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    host: 'localhost',  // ✅ 只监听 localhost，无需管理员权限
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

---

## ⚠️ 注意事项

### 1. 局域网访问

修改为 `host: 'localhost'` 后，只能从本机访问前端应用。如果需要从局域网其他设备访问：

**选项 A**: 使用 `host: true` 并以管理员身份运行

**选项 B**: 使用本机的局域网 IP 地址
```typescript
host: '192.168.1.100',  // 替换为你的实际 IP
```

**选项 C**: 使用 `host: '0.0.0.0'` 并以管理员身份运行

---

### 2. 代理配置

修改 `host` 不影响代理配置，API 请求仍然会正确转发到后端。

---

### 3. 生产环境

这个配置只影响开发环境。生产环境部署时，应该使用 Nginx 或其他反向代理服务器。

---

## 🔍 故障排查

### 问题: 修改后仍然报错

**解决步骤**:

1. **清除 Vite 缓存**:
```bash
cd frontend
rm -rf node_modules/.vite
npm run dev
```

2. **重新安装依赖**:
```bash
cd frontend
rm -rf node_modules
npm install
npm run dev
```

3. **检查配置文件**:
确保 `vite.config.ts` 已正确保存

4. **重启终端**:
关闭所有终端窗口，重新打开

---

### 问题: 端口仍然被占用

**解决步骤**:

1. **使用停止脚本**:
```powershell
.\stop-services.ps1
```

2. **手动停止进程**:
```powershell
# 查找占用端口的进程
Get-NetTCPConnection -LocalPort 5173

# 停止进程
Stop-Process -Id <进程ID> -Force
```

3. **重启计算机**:
如果以上方法都不行，重启计算机可以释放所有端口

---

## ✅ 验证修复

### 1. 检查配置文件

```bash
cat frontend/vite.config.ts | grep "host:"
```

应该显示:
```typescript
host: 'localhost',
```

### 2. 启动服务

```powershell
.\start-ccd2.ps1
```

### 3. 验证服务

```bash
python check_services.py
```

应该显示:
```
✅ OK: Backend is running on http://localhost:8000
✅ OK: Frontend is running on http://localhost:5173
```

### 4. 浏览器访问

打开浏览器访问: http://localhost:5173

---

## 📚 相关文档

- [Vite 配置文档](https://vitejs.dev/config/server-options.html)
- [WINDOWS_STARTUP_GUIDE.md](./WINDOWS_STARTUP_GUIDE.md) - Windows 启动指南
- [POWERSHELL_SCRIPT_TEST_REPORT.md](./POWERSHELL_SCRIPT_TEST_REPORT.md) - PowerShell 脚本测试报告

---

## 🎉 总结

**问题**: Vite 监听 `0.0.0.0` 需要管理员权限

**解决方案**: 修改配置为 `host: 'localhost'`

**结果**: ✅ 问题已解决，服务正常运行

**访问地址**:
- 前端: http://localhost:5173
- 后端: http://localhost:8000
- API 文档: http://localhost:8000/docs

---

**修复日期**: 2025-10-18  
**状态**: ✅ 已解决  
**服务状态**: ✅ 正常运行

