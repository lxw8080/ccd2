#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的前端服务器
用于提供前端测试页面
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

PORT = 5173
FRONTEND_DIR = Path(__file__).parent / "frontend"

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)
    
    def end_headers(self):
        # 添加 CORS 头
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_GET(self):
        # 如果请求的是根路径，返回 test.html
        if self.path == '/':
            self.path = '/test.html'
        return super().do_GET()

def main():
    os.chdir(FRONTEND_DIR)
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"🚀 前端服务器启动成功！")
        print(f"📍 访问地址: http://localhost:{PORT}")
        print(f"📁 服务目录: {FRONTEND_DIR}")
        print(f"📝 测试页面: http://localhost:{PORT}/test.html")
        print(f"\n按 Ctrl+C 停止服务器")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 服务器已停止")
            sys.exit(0)

if __name__ == "__main__":
    main()

