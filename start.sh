#!/bin/bash
# 项目启动脚本

echo "🚀 启动 CCD2 项目..."
echo ""

# 获取项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# 启动后端
echo "📦 启动后端服务..."
cd backend
source venv/bin/activate
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo "✅ 后端启动完成 (PID: $BACKEND_PID)"

# 等待后端启动
sleep 3

# 启动前端
echo "📱 启动前端服务..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!
echo "✅ 前端启动完成 (PID: $FRONTEND_PID)"

echo ""
echo "🌐 服务已启动："
echo "   前端: http://localhost:5173"
echo "   后端: http://localhost:8000"
echo "   API文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo ""

# 等待进程
wait $BACKEND_PID $FRONTEND_PID
