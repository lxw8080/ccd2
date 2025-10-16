#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前端功能测试脚本
"""

import requests
import time

# 配置
API_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")

def main():
    print(f"\n{Colors.BLUE}")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  🎉 前端功能测试".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    print(f"{Colors.RESET}")
    
    # 测试前端可访问性
    print_header("1. 前端可访问性测试")
    try:
        response = requests.get(FRONTEND_URL, timeout=10)
        if response.status_code == 200:
            print_success("前端页面可访问")
            print_info(f"状态码: {response.status_code}")
        else:
            print_error(f"前端返回状态码: {response.status_code}")
    except Exception as e:
        print_error(f"前端连接失败: {str(e)}")
    
    # 测试后端 API
    print_header("2. 后端 API 测试")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            print_success("后端 API 正常")
        else:
            print_error(f"后端返回状态码: {response.status_code}")
    except Exception as e:
        print_error(f"后端连接失败: {str(e)}")
    
    # 创建测试用户
    print_header("3. 创建测试用户")
    test_username = f"testuser_{int(time.time())}"
    test_password = "password123"
    
    try:
        response = requests.post(
            f"{API_URL}/api/auth/register",
            json={
                "username": test_username,
                "password": test_password,
                "full_name": "测试用户",
                "role": "admin"
            },
            timeout=5
        )
        if response.status_code in [200, 201]:
            print_success("测试用户创建成功")
            print_info(f"用户名: {test_username}")
            print_info(f"密码: {test_password}")
        else:
            print_error(f"创建失败: {response.status_code}")
    except Exception as e:
        print_error(f"创建异常: {str(e)}")
    
    # 输出测试说明
    print_header("手动测试步骤")
    print_info("1. 打开浏览器访问: http://localhost:5173")
    print_info("2. 应该看到登录页面")
    print_info(f"3. 使用以下凭据登录:")
    print_info(f"   用户名: {test_username}")
    print_info(f"   密码: {test_password}")
    print_info("4. 登录成功后应该跳转到客户列表页面")
    print_info("5. 测试以下功能:")
    print_info("   - 查看客户列表")
    print_info("   - 创建新客户")
    print_info("   - 查看客户详情")
    print_info("   - 上传文件")
    print_info("   - 查看产品列表")
    print_info("   - 批量导入")
    
    print(f"\n{Colors.GREEN}✅ 测试准备完成！请按照上述步骤进行手动测试。{Colors.RESET}\n")

if __name__ == "__main__":
    main()

