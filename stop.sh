#!/bin/bash
# 项目停止脚本

echo "🛑 停止 CCD2 项目..."

# 杀死后端进程
pkill -f "uvicorn app.main:app" || true
echo "✅ 后端已停止"

# 杀死前端进程
pkill -f "npm run dev" || true
echo "✅ 前端已停止"

echo "✅ 所有服务已停止"
