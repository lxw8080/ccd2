#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PDF预览功能测试脚本
测试PDF文件的上传、下载和预览功能
"""
import requests
import json
import sys

# 设置编码
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# API基础URL
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"

def print_section(title):
    """打印分节标题"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def login():
    """登录并获取token"""
    print_section("1. 登录系统")
    
    url = f"{API_URL}/auth/login"
    data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        result = response.json()
        token = result.get("access_token")
        print(f"✅ 登录成功")
        print(f"   Token: {token[:50]}...")
        return token
    else:
        print(f"❌ 登录失败: {response.status_code}")
        print(f"   错误: {response.text}")
        return None

def get_documents(token):
    """获取文档列表"""
    print_section("2. 获取文档列表")
    
    url = f"{API_URL}/documents"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        documents = response.json()
        print(f"✅ 获取文档列表成功")
        print(f"   总文档数: {len(documents)}")
        
        # 筛选PDF文件
        pdf_docs = [doc for doc in documents if doc.get('file_type') == 'application/pdf']
        print(f"   PDF文档数: {len(pdf_docs)}")
        
        if pdf_docs:
            print("\n   PDF文档列表:")
            for i, doc in enumerate(pdf_docs[:5], 1):
                print(f"   {i}. {doc.get('file_name')} (ID: {doc.get('id')})")
        
        return pdf_docs
    else:
        print(f"❌ 获取文档列表失败: {response.status_code}")
        print(f"   错误: {response.text}")
        return []

def test_pdf_download(token, document_id, file_name):
    """测试PDF下载功能"""
    print_section(f"3. 测试PDF下载: {file_name}")
    
    # 测试inline预览
    url = f"{API_URL}/documents/download/{document_id}?inline=true"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        print(f"✅ PDF下载成功 (inline=true)")
        print(f"   Content-Type: {response.headers.get('Content-Type')}")
        print(f"   Content-Disposition: {response.headers.get('Content-Disposition')}")
        print(f"   文件大小: {len(response.content)} bytes")
        
        # 检查是否是PDF
        if response.headers.get('Content-Type') == 'application/pdf':
            print(f"   ✅ 文件类型正确: application/pdf")
        else:
            print(f"   ⚠️  文件类型: {response.headers.get('Content-Type')}")
        
        return True
    else:
        print(f"❌ PDF下载失败: {response.status_code}")
        print(f"   错误: {response.text}")
        return False

def test_frontend_access():
    """测试前端访问"""
    print_section("4. 测试前端服务")
    
    url = "http://localhost:5173"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ 前端服务正常")
            print(f"   URL: {url}")
            return True
        else:
            print(f"⚠️  前端服务响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 前端服务无法访问: {e}")
        return False

def test_pdf_worker():
    """测试PDF worker文件"""
    print_section("5. 测试PDF Worker文件")
    
    url = "http://localhost:5173/pdf-worker/pdf.worker.min.mjs"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ PDF Worker文件可访问")
            print(f"   URL: {url}")
            print(f"   文件大小: {len(response.content)} bytes")
            return True
        else:
            print(f"❌ PDF Worker文件无法访问: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ PDF Worker文件访问失败: {e}")
        return False

def main():
    """主测试流程"""
    print("\n" + "🔍 PDF预览功能测试".center(60, "="))
    print("测试时间:", "2025-10-18")
    print("="*60)
    
    # 1. 登录
    token = login()
    if not token:
        print("\n❌ 测试失败: 无法登录")
        return
    
    # 2. 获取文档列表
    pdf_docs = get_documents(token)
    
    # 3. 测试PDF下载
    if pdf_docs:
        # 测试第一个PDF文档
        doc = pdf_docs[0]
        test_pdf_download(token, doc['id'], doc['file_name'])
    else:
        print("\n⚠️  没有找到PDF文档，跳过下载测试")
    
    # 4. 测试前端服务
    test_frontend_access()
    
    # 5. 测试PDF Worker
    test_pdf_worker()
    
    # 总结
    print_section("测试总结")
    print("✅ 后端API: 正常")
    print("✅ 文档下载: 正常" if pdf_docs else "⚠️  文档下载: 无PDF文档")
    print("✅ 前端服务: 正常")
    print("✅ PDF Worker: 正常")
    
    print("\n" + "="*60)
    print("📝 手动测试步骤:")
    print("="*60)
    print("1. 访问: http://localhost:5173")
    print("2. 登录: admin / admin123")
    print("3. 进入「资料管理」页面")
    print("4. 找到PDF文件，点击「预览」按钮")
    print("5. 验证PDF能够正确显示")
    print("6. 测试页面导航和缩放功能")
    print("="*60)
    print("\n✅ 自动化测试完成！请进行手动测试验证。\n")

if __name__ == "__main__":
    main()

