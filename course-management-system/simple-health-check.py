#!/usr/bin/env python3
"""
校园课程管理系统 - 简化版健康检查脚本
专为 Windows 环境优化，无外部依赖
"""

import sys
import subprocess
import socket
import time
import argparse
from pathlib import Path

class Colors:
    """终端颜色定义"""
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    WHITE = '\033[1;37m'
    NC = '\033[0m'

def print_colored(message: str, color: str = Colors.WHITE) -> None:
    """打印彩色文本"""
    print(f"{color}{message}{Colors.NC}")

def run_simple_command(command: str) -> bool:
    """运行简单命令并返回是否成功"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        return result.returncode == 0
    except Exception:
        return False

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

def test_http_simple(url: str) -> bool:
    """简单的HTTP测试"""
    try:
        import urllib.request
        with urllib.request.urlopen(url, timeout=5) as response:
            return response.getcode() == 200
    except Exception:
        return False

def check_prerequisites() -> bool:
    """检查系统先决条件"""
    print_colored("🔍 检查系统先决条件...", Colors.BLUE)
    all_good = True
    
    # 检查 Docker
    if run_simple_command("docker --version"):
        print_colored("  ✅ Docker 已安装", Colors.GREEN)
        
        # 检查 Docker Compose
        if run_simple_command("docker-compose --version"):
            print_colored("  ✅ Docker Compose 已安装", Colors.GREEN)
        else:
            print_colored("  ❌ Docker Compose 未安装", Colors.RED)
            all_good = False
    else:
        print_colored("  ❌ Docker 未安装", Colors.RED)
        all_good = False
    
    return all_good

def check_docker_services() -> bool:
    """检查 Docker 服务状态"""
    print_colored("🐳 检查 Docker 服务状态...", Colors.BLUE)
    
    if run_simple_command("docker-compose ps"):
        print_colored("  ✅ Docker 服务正在运行", Colors.GREEN)
        return True
    else:
        print_colored("  ❌ Docker 服务未运行", Colors.RED)
        return False

def check_database_connection() -> bool:
    """检查数据库连接"""
    print_colored("🗄️  检查数据库连接...", Colors.BLUE)
    
    if test_port(port=5432):
        print_colored("  ✅ PostgreSQL 端口 5432 可访问", Colors.GREEN)
        
        if run_simple_command("docker-compose exec -T db pg_isready -U postgres"):
            print_colored("  ✅ PostgreSQL 数据库连接正常", Colors.GREEN)
            return True
        else:
            print_colored("  ❌ PostgreSQL 数据库连接失败", Colors.RED)
            return False
    else:
        print_colored("  ❌ PostgreSQL 端口 5432 不可访问", Colors.RED)
        return False

def check_redis_connection() -> bool:
    """检查 Redis 连接"""
    print_colored("🔴 检查 Redis 连接...", Colors.BLUE)
    
    if test_port(port=6379):
        print_colored("  ✅ Redis 端口 6379 可访问", Colors.GREEN)
        
        if run_simple_command("docker-compose exec -T redis redis-cli ping"):
            print_colored("  ✅ Redis 连接正常", Colors.GREEN)
            return True
        else:
            print_colored("  ❌ Redis 连接失败", Colors.RED)
            return False
    else:
        print_colored("  ❌ Redis 端口 6379 不可访问", Colors.RED)
        return False

def check_backend_health() -> bool:
    """检查后端服务"""
    print_colored("🔧 检查后端服务...", Colors.BLUE)
    
    if test_port(port=8000):
        print_colored("  ✅ 后端端口 8000 可访问", Colors.GREEN)
        
        if test_http_simple("http://localhost:8000/api/health/"):
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
    
    if test_port(port=8081):
        print_colored("  ✅ 前端端口 8081 可访问", Colors.GREEN)
        
        if test_http_simple("http://localhost:8081"):
            print_colored("  ✅ 前端页面可访问", Colors.GREEN)
            return True
        else:
            print_colored("  ❌ 前端页面不可访问", Colors.RED)
            return False
    elif test_port(port=3000):
        print_colored("  ✅ 前端开发端口 3000 可访问", Colors.GREEN)
        
        if test_http_simple("http://localhost:3000"):
            print_colored("  ✅ 前端开发页面可访问", Colors.GREEN)
            return True
        else:
            print_colored("  ❌ 前端开发页面不可访问", Colors.RED)
            return False
    else:
        print_colored("  ❌ 前端服务不可访问 (端口 8081 或 3000)", Colors.RED)
        return False

def start_system() -> None:
    """启动系统"""
    print_colored("🚀 启动系统...", Colors.BLUE)
    
    print_colored("📦 启动 Docker 服务...", Colors.YELLOW)
    if not run_simple_command("docker-compose up -d"):
        print_colored("  ❌ 启动失败", Colors.RED)
        return
    
    print_colored("⏳ 等待服务启动...", Colors.YELLOW)
    time.sleep(15)
    
    print_colored("🗄️  运行数据库迁移...", Colors.YELLOW)
    run_simple_command("docker-compose exec -T backend python manage.py migrate")
    
    print_colored("👤 创建测试用户...", Colors.YELLOW)
    create_user_cmd = '''docker-compose exec -T backend python manage.py shell -c "
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
"'''
    run_simple_command(create_user_cmd)

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
    parser = argparse.ArgumentParser(description="校园课程管理系统 - 简化版健康检查")
    parser.add_argument("action", choices=["check", "start"], default="check", nargs="?",
                       help="执行的操作 (check: 仅检查, start: 启动并检查)")
    
    args = parser.parse_args()
    
    print_colored("=" * 60, Colors.BLUE)
    print_colored("🏫 校园课程管理系统 - 简化版健康检查", Colors.BLUE)
    print_colored("=" * 60, Colors.BLUE)
    
    # 检查先决条件
    if not check_prerequisites():
        print_colored("❌ 先决条件检查失败，请安装必要的软件", Colors.RED)
        return 1
    
    if args.action == "start":
        start_system()
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
            print_colored("\n💡 尝试运行: python simple-health-check.py start", Colors.BLUE)
        return 1

if __name__ == "__main__":
    sys.exit(main())
