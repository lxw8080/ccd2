#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
启动 CCD2 项目的脚本
支持 PostgreSQL 外部数据库
"""

import os
import sys
import subprocess
import time
import platform
from pathlib import Path

# 项目路径
project_root = Path(__file__).parent
backend_path = project_root / "backend"
frontend_path = project_root / "frontend"

def print_section(title):
    """打印分隔符"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def run_command(cmd, cwd=None, description=""):
    """运行命令"""
    if description:
        print(f"▶ {description}")
    try:
        if platform.system() == "Windows":
            subprocess.run(cmd, shell=True, cwd=cwd, check=False)
        else:
            subprocess.run(cmd, shell=True, cwd=cwd, check=False)
    except Exception as e:
        print(f"✗ 命令执行失败: {e}")
        return False
    return True

def main():
    print_section("CCD2 项目启动 - PostgreSQL 配置")
    
    # 检查 .env 文件
    env_file = backend_path / ".env"
    if not env_file.exists():
        print("✗ 错误: .env 文件不存在")
        print(f"  位置: {env_file}")
        print("  已为您创建 .env 文件，请检查配置")
        sys.exit(1)
    
    print(f"✓ 已找到 .env 文件: {env_file}")
    
    # 安装后端依赖
    print_section("步骤 1: 安装后端依赖")
    print("正在升级 pip...")
    run_command(f"{sys.executable} -m pip install -q --upgrade pip", cwd=backend_path)
    
    print("正在安装 Python 包...")
    run_command(f"{sys.executable} -m pip install -q -r requirements.txt", cwd=backend_path)
    print("✓ 后端依赖安装完成")
    
    # 启动后端
    print_section("步骤 2: 启动 FastAPI 后端")
    print("正在启动后端服务器...")
    print("  地址: http://localhost:8000")
    print("  API 文档: http://localhost:8000/docs")
    
    backend_cmd = f"{sys.executable} -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    
    if platform.system() == "Windows":
        backend_process = subprocess.Popen(
            backend_cmd,
            cwd=str(backend_path),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    else:
        backend_process = subprocess.Popen(
            backend_cmd,
            cwd=str(backend_path),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    
    print(f"✓ 后端进程已启动 (PID: {backend_process.pid})")
    
    # 等待后端启动
    print("正在等待后端服务启动...")
    time.sleep(5)
    
    # 检查前端依赖
    print_section("步骤 3: 前端设置")
    node_modules = frontend_path / "node_modules"
    if node_modules.exists():
        print("✓ Node modules 已存在")
    else:
        print("正在安装 npm 包...")
        run_command("npm install --quiet", cwd=frontend_path)
        print("✓ npm 包安装完成")
    
    # 启动前端
    print_section("步骤 4: 启动 Vite 前端")
    print("正在启动前端开发服务器...")
    print("  地址: http://localhost:5173")
    
    frontend_cmd = "npm run dev"
    
    try:
        subprocess.run(frontend_cmd, cwd=str(frontend_path), shell=True)
    except KeyboardInterrupt:
        print("\n\n正在关闭服务...")
        backend_process.terminate()
        sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✓ 项目已关闭")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        sys.exit(1)


