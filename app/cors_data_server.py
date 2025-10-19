#!/usr/bin/env python3
"""
支持CORS的数据服务服务器
解决前端跨域访问问题
"""

import http.server
import socketserver
import json
import os
from urllib.parse import urlparse

# 基于脚本位置的路径，提升跨平台兼容性
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
APP_ROOT = BASE_DIR
FRONTEND_PUBLIC_DIR = os.path.join(APP_ROOT, 'frontend', 'public')
SCHEDULES_JSON = os.path.join(FRONTEND_PUBLIC_DIR, 'data', 'schedules.json')

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # 添加CORS头
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        # 处理预检请求
        self.send_response(200)
        self.end_headers()
    
    def do_GET(self):
        # 处理GET请求
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        print(f"📡 收到请求: {path}")
        
        # 特殊处理数据文件请求
        if path == '/data/schedules.json':
            try:
                file_path = SCHEDULES_JSON
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
                    print(f"✅ 成功返回数据: {len(data.get('schedules', []))} 条记录")
                else:
                    self.send_error(404, "数据文件未找到")
            except Exception as e:
                print(f"❌ 处理请求失败: {e}")
                self.send_error(500, f"服务器错误: {e}")
        else:
            # 其他文件使用默认处理
            super().do_GET()

def start_cors_server():
    """启动支持CORS的HTTP服务器"""
    port = 8080
    directory = FRONTEND_PUBLIC_DIR
    
    # 切换到数据目录
    os.chdir(directory)
    
    # 创建服务器
    handler = CORSHTTPRequestHandler
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"🚀 CORS数据服务已启动")
        print(f"📁 工作目录: {directory}")
        print(f"🌐 访问地址: http://localhost:{port}")
        print(f"📊 数据端点: http://localhost:{port}/data/schedules.json")
        print(f"🔧 CORS支持: 已启用")
        print("=" * 50)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 服务器已停止")

if __name__ == "__main__":
    start_cors_server()