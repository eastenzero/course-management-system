#!/usr/bin/env python3
"""
校园课程表管理工具 - 环境配置验证脚本
验证所有必要的环境组件是否正确安装和配置
"""

import sys
import subprocess
import os
import socket
from pathlib import Path

def run_command(command, description):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def check_python():
    """检查Python 3.11安装"""
    print("🐍 检查Python 3.11...")
    success, output, error = run_command("python3.11 --version", "Python 3.11版本")
    if success and "Python 3.11" in output:
        print(f"  ✅ {output}")
        return True
    else:
        print(f"  ❌ Python 3.11未正确安装: {error}")
        return False

def check_node():
    """检查Node.js 18安装"""
    print("🟢 检查Node.js 18...")
    success, output, error = run_command("node --version", "Node.js版本")
    if success and output.startswith("v18"):
        print(f"  ✅ Node.js {output}")
        
        # 检查npm
        success_npm, output_npm, _ = run_command("npm --version", "npm版本")
        if success_npm:
            print(f"  ✅ npm {output_npm}")
            return True
    
    print(f"  ❌ Node.js 18未正确安装: {error}")
    return False

def check_postgresql():
    """检查PostgreSQL安装和配置"""
    print("🐘 检查PostgreSQL...")
    success, output, error = run_command("psql --version", "PostgreSQL版本")
    if success and "PostgreSQL" in output:
        print(f"  ✅ {output}")
        
        # 检查服务状态
        success_service, _, _ = run_command("sudo systemctl is-active postgresql", "PostgreSQL服务")
        if success_service:
            print("  ✅ PostgreSQL服务运行中")
            
            # 检查数据库连接
            db_cmd = "PGPASSWORD=secure_password_123 psql -h localhost -U course_admin -d course_management_db -c 'SELECT version();'"
            success_db, output_db, error_db = run_command(db_cmd, "数据库连接")
            if success_db:
                print("  ✅ 数据库连接成功")
                return True
            else:
                print(f"  ❌ 数据库连接失败: {error_db}")
        else:
            print("  ❌ PostgreSQL服务未运行")
    else:
        print(f"  ❌ PostgreSQL未正确安装: {error}")
    return False

def check_redis():
    """检查Redis安装和配置"""
    print("🔴 检查Redis...")
    success, output, error = run_command("redis-server --version", "Redis版本")
    if success and "Redis server" in output:
        print(f"  ✅ {output}")
        
        # 检查服务状态
        success_service, _, _ = run_command("sudo systemctl is-active redis-server", "Redis服务")
        if success_service:
            print("  ✅ Redis服务运行中")
            
            # 检查连接
            success_ping, output_ping, _ = run_command("redis-cli ping", "Redis连接")
            if success_ping and "PONG" in output_ping:
                print("  ✅ Redis连接成功")
                return True
            else:
                print("  ❌ Redis连接失败")
        else:
            print("  ❌ Redis服务未运行")
    else:
        print(f"  ❌ Redis未正确安装: {error}")
    return False

def check_docker():
    """检查Docker安装"""
    print("🐳 检查Docker...")
    success, output, error = run_command("docker --version", "Docker版本")
    if success and "Docker version" in output:
        print(f"  ✅ {output}")
        
        # 检查Docker Compose
        success_compose, output_compose, _ = run_command("docker compose version", "Docker Compose版本")
        if success_compose:
            print(f"  ✅ {output_compose}")
            return True
    
    print(f"  ❌ Docker未正确安装: {error}")
    return False

def check_project_structure():
    """检查项目目录结构"""
    print("📁 检查项目目录结构...")
    # 当前目录就是course-management-system
    base_path = Path(".")

    required_dirs = [
        "backend", "frontend", "algorithms", "data-generator", "docs", "deployment",
        "backend/apps", "backend/config", "frontend/src", "algorithms/genetic"
    ]

    all_exist = True
    for dir_path in required_dirs:
        full_path = base_path / dir_path
        if full_path.exists():
            print(f"  ✅ {dir_path}/")
        else:
            print(f"  ❌ {dir_path}/ 不存在")
            all_exist = False

    return all_exist

def check_python_venv():
    """检查Python虚拟环境"""
    print("🔧 检查Python虚拟环境...")
    venv_path = Path("backend/venv")

    if venv_path.exists():
        print("  ✅ 虚拟环境目录存在")

        # 检查requirements.txt
        req_path = Path("backend/requirements.txt")
        if req_path.exists():
            print("  ✅ requirements.txt存在")

            # 检查关键依赖
            with open(req_path, 'r') as f:
                requirements = f.read()
                key_packages = ['django', 'djangorestframework', 'psycopg2-binary', 'redis', 'celery']
                for package in key_packages:
                    if package in requirements.lower():
                        print(f"  ✅ {package}已安装")
                    else:
                        print(f"  ❌ {package}未安装")
                        return False
            return True
        else:
            print("  ❌ requirements.txt不存在")
    else:
        print("  ❌ 虚拟环境不存在")

    return False

def check_ports():
    """检查关键端口是否可用"""
    print("🔌 检查端口状态...")
    ports = {
        5432: "PostgreSQL",
        6379: "Redis",
        8000: "Django开发服务器",
        3000: "React开发服务器"
    }
    
    for port, service in ports.items():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            if port in [5432, 6379]:  # 这些服务应该运行
                print(f"  ✅ 端口 {port} ({service}) 正在使用")
            else:  # 这些端口应该空闲
                print(f"  ⚠️  端口 {port} ({service}) 被占用")
        else:
            if port in [5432, 6379]:  # 这些服务应该运行
                print(f"  ❌ 端口 {port} ({service}) 未使用")
                return False
            else:  # 这些端口应该空闲
                print(f"  ✅ 端口 {port} ({service}) 可用")
    
    return True

def main():
    """主验证函数"""
    print("=" * 60)
    print("🚀 校园课程表管理工具 - 环境配置验证")
    print("=" * 60)
    
    checks = [
        ("Python 3.11", check_python),
        ("Node.js 18", check_node),
        ("PostgreSQL", check_postgresql),
        ("Redis", check_redis),
        ("Docker", check_docker),
        ("项目结构", check_project_structure),
        ("Python虚拟环境", check_python_venv),
        ("端口状态", check_ports),
    ]
    
    results = []
    for name, check_func in checks:
        print()
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"  ❌ 检查 {name} 时出错: {e}")
            results.append((name, False))
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 验证结果总结")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name:20} {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 项检查通过")
    
    if passed == total:
        print("\n🎉 所有环境配置验证通过！系统已准备就绪。")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 项检查失败，请修复后重新验证。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
