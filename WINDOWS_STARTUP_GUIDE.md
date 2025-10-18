# Windows 一键启动指南

本指南介绍如何在 Windows 系统上使用一键启动脚本运行 CCD2 项目（不使用 Docker）。

---

## 📋 前置要求

在运行启动脚本之前，请确保已安装以下软件：

### 1. Python 3.8+
- **下载地址**: https://www.python.org/downloads/
- **安装提示**: 安装时勾选 "Add Python to PATH"

### 2. Node.js 16+
- **下载地址**: https://nodejs.org/
- **推荐版本**: LTS (长期支持版本)
- **包含**: npm 包管理器

### 3. 数据库配置
- 确保 `backend/.env` 文件存在
- 文件应包含 PostgreSQL 数据库连接信息
- 参考 `backend/.env.example` 创建配置文件

---

## 🚀 启动方式

项目提供了两种 Windows 启动脚本，功能完全相同，选择其中一种即可：

### 方式一：PowerShell 脚本（推荐）

**文件**: `start-ccd2.ps1`

**特点**:
- ✅ 彩色输出，界面美观
- ✅ 更好的错误处理
- ✅ 自动清理后台进程
- ✅ 支持 Ctrl+C 优雅退出

**使用方法**:

1. **右键点击** `start-ccd2.ps1`
2. 选择 **"使用 PowerShell 运行"**

或者在 PowerShell 中执行：
```powershell
.\start-ccd2.ps1
```

**首次运行可能需要设置执行策略**:
```powershell
# 以管理员身份运行 PowerShell，执行以下命令
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### 方式二：批处理脚本

**文件**: `start-ccd2.bat`

**特点**:
- ✅ 无需额外配置，双击即可运行
- ✅ 兼容性好，适用于所有 Windows 版本
- ✅ 后端在独立窗口运行

**使用方法**:

1. **双击** `start-ccd2.bat` 文件即可

或者在命令提示符中执行：
```cmd
start-ccd2.bat
```

---

## 📝 启动流程

两个脚本都会执行以下步骤：

### 1. 检查前置条件 ✓
- 检查 Python 是否安装
- 检查 Node.js 是否安装
- 检查 npm 是否安装
- 检查 `backend/.env` 配置文件是否存在

### 2. 准备后端环境 ✓
- 升级 pip 到最新版本
- 安装 Python 依赖包（从 `requirements.txt`）

### 3. 准备前端环境 ✓
- 检查 `node_modules` 是否存在
- 如果不存在，自动安装 npm 依赖包（首次运行）

### 4. 启动后端服务 ✓
- 在后台启动 FastAPI 服务器
- 监听端口: `8000`
- 自动重载模式（代码修改后自动重启）

### 5. 启动前端服务 ✓
- 启动 Vite 开发服务器
- 监听端口: `5173`
- 热模块替换（HMR）支持

---

## 🌐 访问地址

服务启动成功后，可以通过以下地址访问：

| 服务 | 地址 | 说明 |
|------|------|------|
| **前端应用** | http://localhost:5173 | React + Vite 前端界面 |
| **后端 API** | http://localhost:8000 | FastAPI 后端服务 |
| **API 文档** | http://localhost:8000/docs | Swagger UI 交互式文档 |
| **健康检查** | http://localhost:8000/health | 后端健康状态 |

---

## 🛑 停止服务

### PowerShell 脚本 (start-ccd2.ps1)
- 在脚本运行窗口按 **Ctrl+C**
- 脚本会自动停止前端和后端服务

### 批处理脚本 (start-ccd2.bat)
- **前端**: 关闭主窗口或按 Ctrl+C
- **后端**: 关闭标题为 "CCD2 Backend" 的窗口

---

## ❓ 常见问题

### 1. PowerShell 脚本无法运行

**错误信息**: "无法加载文件，因为在此系统上禁止运行脚本"

**解决方法**:
```powershell
# 以管理员身份运行 PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### 2. Python 未找到

**错误信息**: "未检测到 Python！"

**解决方法**:
1. 下载并安装 Python: https://www.python.org/downloads/
2. 安装时勾选 "Add Python to PATH"
3. 重启命令行窗口

**验证安装**:
```cmd
python --version
```

---

### 3. Node.js 未找到

**错误信息**: "未检测到 Node.js！"

**解决方法**:
1. 下载并安装 Node.js: https://nodejs.org/
2. 选择 LTS 版本
3. 重启命令行窗口

**验证安装**:
```cmd
node --version
npm --version
```

---

### 4. 缺少 backend/.env 文件

**错误信息**: "未找到 backend\.env 配置文件！"

**解决方法**:
1. 复制 `backend/.env.example` 为 `backend/.env`
2. 编辑 `.env` 文件，填入正确的数据库连接信息

**示例配置**:
```ini
DATABASE_URL=postgresql://flask_user:flask_password@115.190.29.10:5433/ccd_db_new
API_KEY=lxw8025031
LOG_FILE_PATH=logs/server.log
FLASK_ENV=development
DEBUG=True
```

---

### 5. 端口被占用

**错误信息**: "Address already in use" 或 "端口已被占用"

**解决方法**:

**检查端口占用**:
```powershell
# 检查 8000 端口（后端）
netstat -ano | findstr :8000

# 检查 5173 端口（前端）
netstat -ano | findstr :5173
```

**停止占用端口的进程**:
```powershell
# 找到进程 ID (PID)，然后终止
taskkill /PID <进程ID> /F
```

---

### 6. 依赖安装失败

**Python 依赖安装失败**:
```cmd
cd backend
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

**npm 依赖安装失败**:
```cmd
cd frontend
npm cache clean --force
npm install
```

---

## 🔧 手动启动（备选方案）

如果启动脚本遇到问题，可以手动启动服务：

### 启动后端
```cmd
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 启动前端（新窗口）
```cmd
cd frontend
npm install
npm run dev
```

---

## 📚 其他启动方式

除了 Windows 一键启动脚本，项目还提供以下启动方式：

### Python 跨平台脚本
```bash
# 一键启动（推荐）
python quick_start.py

# 分开启动
python start_backend.py  # 终端 1
python start_frontend.py # 终端 2
```

### Linux/macOS Shell 脚本
```bash
./start.sh
```

### Docker 容器化部署
```bash
docker-compose up -d
```

详细信息请参考：
- `README.md` - 项目主文档
- `README_POSTGRESQL.md` - PostgreSQL 配置指南
- `QUICK_REFERENCE.md` - 快速参考

---

## 💡 开发提示

### 开发模式特性
- ✅ **后端自动重载**: 修改 Python 代码后自动重启
- ✅ **前端热更新**: 修改前端代码后浏览器自动刷新
- ✅ **详细日志**: 开发模式下显示详细的调试信息

### 推荐开发工具
- **后端**: VS Code + Python 扩展
- **前端**: VS Code + Volar 扩展
- **API 测试**: Postman 或浏览器访问 http://localhost:8000/docs

### 日志文件位置
- **后端日志**: `backend/logs/server.log`
- **前端日志**: 控制台输出

---

## ✅ 验证服务状态

启动后，可以使用以下方法验证服务是否正常运行：

### 1. 浏览器访问
- 前端: http://localhost:5173
- API 文档: http://localhost:8000/docs

### 2. 使用检查脚本
```bash
python check_services.py
```

### 3. 手动检查
```powershell
# 检查后端
curl http://localhost:8000/health

# 检查前端
curl http://localhost:5173
```

---

## 📞 获取帮助

如果遇到问题：

1. 查看本文档的"常见问题"部分
2. 检查 `backend/logs/server.log` 日志文件
3. 参考项目主文档 `README.md`
4. 查看 API 文档 http://localhost:8000/docs

---

**祝您使用愉快！** 🎉

