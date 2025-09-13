#!/usr/bin/env python3
"""
校园课程管理系统 - 系统健康检查和启动脚本
检测前端、后端、数据库的连接性，并提供系统启动功能
"""

import sys
import subprocess
import socket
import time
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import urllib.request
import urllib.error

class Colors:
    """终端颜色定义"""
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    NC = '\033[0m'  # No Color

def print_colored(message: str, color: str = Colors.WHITE) -> None:
    """打印彩色文本"""
    print(f"{color}{message}{Colors.NC}")

def run_command(command: str, capture_output: bool = True, timeout: int = 30) -> Tuple[bool, str, str]:
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            command,
            capture_output=capture_output,
            text=True,
            timeout=timeout,
            shell=True,
            encoding='utf-8',
            errors='ignore'
        )
        stdout = result.stdout.strip() if result.stdout else ""
        stderr = result.stderr.strip() if result.stderr else ""
        return result.returncode == 0, stdout, stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def test_port(host: str = "localhost", port: int = 80, timeout: int = 3) -> bool:
    """测试端口连接"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def test_http_endpoint(url: str, timeout: int = 10) -> bool:
    """测试HTTP端点"""
    try:
        request = urllib.request.Request(url)
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.getcode() == 200
    except Exception:
        return False

def check_prerequisites() -> bool:
    """检查系统先决条件"""
    print_colored("🔍 检查系统先决条件...", Colors.BLUE)
    all_good = True
    
    # 检查 Docker
    success, output, _ = run_command("docker --version")
    if success:
        print_colored(f"  ✅ Docker: {output}", Colors.GREEN)
        
        # 检查 Docker Compose
        success_compose, output_compose, _ = run_command("docker-compose --version")
        if success_compose:
            print_colored(f"  ✅ Docker Compose: {output_compose}", Colors.GREEN)
        else:
            print_colored("  ❌ Docker Compose 未安装", Colors.RED)
            all_good = False
    else:
        print_colored("  ❌ Docker 未安装", Colors.RED)
        all_good = False
    
    # 检查 Node.js (用于前端开发)
    success, output, _ = run_command("node --version")
    if success:
        print_colored(f"  ✅ Node.js: {output}", Colors.GREEN)
    else:
        print_colored("  ⚠️  Node.js 未安装 (仅影响开发模式)", Colors.YELLOW)
    
    # 检查 Python (用于后端开发)
    success, output, _ = run_command("python --version")
    if success:
        print_colored(f"  ✅ Python: {output}", Colors.GREEN)
    else:
        print_colored("  ⚠️  Python 未安装 (仅影响开发模式)", Colors.YELLOW)
    
    return all_good

def check_docker_services() -> bool:
    """检查 Docker 服务状态"""
    print_colored("🐳 检查 Docker 服务状态...", Colors.BLUE)
    
    try:
        success, output, error = run_command("docker-compose ps --format json")
        if success and output:
            try:
                # 尝试解析JSON输出
                services = []
                for line in output.strip().split('\n'):
                    if line.strip():
                        services.append(json.loads(line))
                
                if services:
                    for service in services:
                        status_icon = "✅" if service.get("State") == "running" else "❌"
                        color = Colors.GREEN if service.get("State") == "running" else Colors.RED
                        print_colored(f"  {status_icon} {service.get('Service', 'Unknown')}: {service.get('State', 'Unknown')}", color)
                    return True
                else:
                    print_colored("  ❌ 没有运行的服务", Colors.RED)
                    return False
            except json.JSONDecodeError:
                # 如果JSON解析失败，尝试简单的ps命令
                success, output, _ = run_command("docker-compose ps")
                if success and "Up" in output:
                    print_colored("  ✅ Docker 服务正在运行", Colors.GREEN)
                    return True
                else:
                    print_colored("  ❌ Docker 服务未运行", Colors.RED)
                    return False
        else:
            print_colored(f"  ❌ 无法获取服务状态: {error}", Colors.RED)
            return False
    except Exception as e:
        print_colored(f"  ❌ 检查服务状态时出错: {e}", Colors.RED)
        return False

def check_database_connection() -> bool:
    """检查数据库连接"""
    print_colored("🗄️  检查数据库连接...", Colors.BLUE)
    
    # 检查 PostgreSQL 端口
    if test_port(port=5432):
        print_colored("  ✅ PostgreSQL 端口 5432 可访问", Colors.GREEN)
        
        # 尝试通过 Docker 检查数据库连接
        success, output, error = run_command("docker-compose exec -T db pg_isready -U postgres")
        if success:
            print_colored("  ✅ PostgreSQL 数据库连接正常", Colors.GREEN)
            return True
        else:
            print_colored(f"  ❌ PostgreSQL 数据库连接失败: {error}", Colors.RED)
            return False
    else:
        print_colored("  ❌ PostgreSQL 端口 5432 不可访问", Colors.RED)
        return False

def check_redis_connection() -> bool:
    """检查 Redis 连接"""
    print_colored("🔴 检查 Redis 连接...", Colors.BLUE)
    
    # 检查 Redis 端口
    if test_port(port=6379):
        print_colored("  ✅ Redis 端口 6379 可访问", Colors.GREEN)
        
        # 尝试通过 Docker 检查 Redis 连接
        success, output, error = run_command("docker-compose exec -T redis redis-cli ping")
        if success and "PONG" in output:
            print_colored("  ✅ Redis 连接正常", Colors.GREEN)
            return True
        else:
            print_colored(f"  ❌ Redis 连接失败: {error}", Colors.RED)
            return False
    else:
        print_colored("  ❌ Redis 端口 6379 不可访问", Colors.RED)
        return False

def check_backend_health() -> bool:
    """检查后端服务"""
    print_colored("🔧 检查后端服务...", Colors.BLUE)
    
    # 检查后端端口
    if test_port(port=8000):
        print_colored("  ✅ 后端端口 8000 可访问", Colors.GREEN)
        
        # 检查健康检查端点
        if test_http_endpoint("http://localhost:8000/api/health/"):
            print_colored("  ✅ 后端健康检查通过", Colors.GREEN)
            return True
        else:
            print_colored("  ❌ 后端健康检查失败", Colors.RED)
            return False
    else:
        print_colored("  ❌ 后端端口 8000 不可访问", Colors.RED)
        return False

def check_frontend_health() -> bool:
    """检查前端服务"""
    print_colored("🎨 检查前端服务...", Colors.BLUE)
    
    # 检查前端端口 (Docker 模式)
    if test_port(port=8081):
        print_colored("  ✅ 前端端口 8081 可访问", Colors.GREEN)
        
        # 检查前端页面
        if test_http_endpoint("http://localhost:8081"):
            print_colored("  ✅ 前端页面可访问", Colors.GREEN)
            return True
        else:
            print_colored("  ❌ 前端页面不可访问", Colors.RED)
            return False
    # 检查开发模式端口
    elif test_port(port=3000):
        print_colored("  ✅ 前端开发端口 3000 可访问", Colors.GREEN)
        
        if test_http_endpoint("http://localhost:3000"):
            print_colored("  ✅ 前端开发页面可访问", Colors.GREEN)
            return True
        else:
            print_colored("  ❌ 前端开发页面不可访问", Colors.RED)
            return False
    else:
        print_colored("  ❌ 前端服务不可访问 (端口 8081 或 3000)", Colors.RED)
        return False

def start_system(mode: str = "docker") -> None:
    """启动系统"""
    print_colored(f"🚀 启动系统 ({mode} 模式)...", Colors.BLUE)
    
    if mode == "docker":
        print_colored("📦 启动 Docker 服务...", Colors.YELLOW)
        success, output, error = run_command("docker-compose up -d")
        if not success:
            print_colored(f"  ❌ 启动失败: {error}", Colors.RED)
            return
        
        print_colored("⏳ 等待服务启动...", Colors.YELLOW)
        time.sleep(15)
        
        print_colored("🗄️  运行数据库迁移...", Colors.YELLOW)
        success, output, error = run_command("docker-compose exec -T backend python manage.py migrate")
        if not success:
            print_colored(f"  ⚠️  数据库迁移可能失败: {error}", Colors.YELLOW)
        
        print_colored("👤 创建测试用户...", Colors.YELLOW)
        create_user_script = """
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123', user_type='admin')
    print('✅ 管理员账号已创建: admin/admin123')
if not User.objects.filter(username='teacher1').exists():
    User.objects.create_user('teacher1', 'teacher1@example.com', 'teacher123', user_type='teacher', first_name='张', last_name='老师')
    print('✅ 教师账号已创建: teacher1/teacher123')
if not User.objects.filter(username='student1').exists():
    User.objects.create_user('student1', 'student1@example.com', 'student123', user_type='student', first_name='李', last_name='同学')
    print('✅ 学生账号已创建: student1/student123')
"""
        
        # 将脚本写入临时文件并执行
        temp_script = Path("temp_create_users.py")
        temp_script.write_text(create_user_script)
        
        try:
            success, output, error = run_command(f"docker-compose exec -T backend python manage.py shell < {temp_script}")
            if output:
                print_colored(f"  {output}", Colors.GREEN)
        finally:
            if temp_script.exists():
                temp_script.unlink()
    else:
        print_colored("⚠️  开发模式启动需要手动操作", Colors.YELLOW)
        print_colored("  1. 启动后端: cd backend && python manage.py runserver", Colors.WHITE)
        print_colored("  2. 启动前端: cd frontend && npm run dev", Colors.WHITE)

def show_system_info() -> None:
    """显示系统信息"""
    print_colored("📋 系统访问信息:", Colors.BLUE)
    print_colored("  🌐 前端应用: http://localhost:8081", Colors.GREEN)
    print_colored("  🔧 后端API: http://localhost:8000", Colors.GREEN)
    print_colored("  📚 API文档: http://localhost:8000/api/docs/", Colors.GREEN)
    print_colored("  👨‍💼 管理后台: http://localhost:8000/admin", Colors.GREEN)
    print()
    print_colored("👤 测试账号:", Colors.BLUE)
    print_colored("  管理员: admin / admin123", Colors.GREEN)
    print_colored("  教师: teacher1 / teacher123", Colors.GREEN)
    print_colored("  学生: student1 / student123", Colors.GREEN)
    print()
    print_colored("🔧 常用命令:", Colors.BLUE)
    print_colored("  查看服务状态: docker-compose ps", Colors.WHITE)
    print_colored("  查看日志: docker-compose logs -f", Colors.WHITE)
    print_colored("  停止服务: docker-compose down", Colors.WHITE)
    print_colored("  重启服务: docker-compose restart", Colors.WHITE)

def main() -> int:
    """主函数"""
    parser = argparse.ArgumentParser(description="校园课程管理系统 - 系统健康检查")
    parser.add_argument("action", choices=["check", "start"], default="check", nargs="?",
                       help="执行的操作 (check: 仅检查, start: 启动并检查)")
    parser.add_argument("--mode", choices=["docker", "dev"], default="docker",
                       help="运行模式 (docker: Docker模式, dev: 开发模式)")
    
    args = parser.parse_args()
    
    print_colored("=" * 60, Colors.BLUE)
    print_colored("🏫 校园课程管理系统 - 系统健康检查", Colors.BLUE)
    print_colored("=" * 60, Colors.BLUE)
    
    # 检查先决条件
    if not check_prerequisites():
        print_colored("❌ 先决条件检查失败，请安装必要的软件", Colors.RED)
        return 1
    
    if args.action == "start":
        start_system(args.mode)
        time.sleep(5)
    
    # 执行健康检查
    print_colored("\n🔍 开始系统健康检查...", Colors.BLUE)
    
    checks = [
        ("Docker服务", check_docker_services),
        ("数据库连接", check_database_connection),
        ("Redis连接", check_redis_connection),
        ("后端服务", check_backend_health),
        ("前端服务", check_frontend_health),
    ]
    
    results = []
    for name, check_func in checks:
        print()
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print_colored(f"  ❌ 检查 {name} 时出错: {e}", Colors.RED)
            results.append((name, False))
    
    # 显示总结
    print_colored(f"\n{'=' * 60}", Colors.BLUE)
    print_colored("📊 健康检查结果总结", Colors.BLUE)
    print_colored("=" * 60, Colors.BLUE)
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        status = "✅ 正常" if result else "❌ 异常"
        color = Colors.GREEN if result else Colors.RED
        print_colored(f"{name:<15} {status}", color)
        if result:
            passed += 1
    
    print_colored(f"\n总计: {passed}/{total} 项检查通过", Colors.WHITE)
    
    if passed == total:
        print_colored("\n🎉 所有系统组件运行正常！", Colors.GREEN)
        show_system_info()
        return 0
    else:
        print_colored(f"\n⚠️  有 {total - passed} 项检查失败，请检查相关服务", Colors.YELLOW)
        if args.action != "start":
            print_colored("\n💡 尝试运行: python system-health-check.py start", Colors.BLUE)
        return 1

if __name__ == "__main__":
    sys.exit(main())
