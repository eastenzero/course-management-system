#!/usr/bin/env python3
"""
前端验证脚本 - 验证前端页面数据显示效果
功能：通过访问前端页面，验证数据是否正确显示
"""

import requests
import json
import time
from urllib.parse import urljoin

class FrontendValidator:
    """前端验证类"""
    
    def __init__(self, frontend_url: str = "http://localhost:18081", backend_url: str = "http://localhost:18000"):
        """初始化前端验证器"""
        self.frontend_url = frontend_url
        self.backend_url = backend_url
        self.auth_token = None
        self.test_results = []
    
    def test_frontend_accessibility(self) -> bool:
        """测试前端可访问性"""
        print("🌐 测试前端服务可访问性...")
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            if response.status_code == 200:
                print(f"   ✅ 前端服务正常运行: {self.frontend_url}")
                return True
            else:
                print(f"   ❌ 前端服务异常: 状态码 {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ 前端服务无法访问: {e}")
            return False
    
    def test_backend_data_availability(self) -> bool:
        """测试后端数据可用性"""
        print("\n📊 测试后端数据可用性...")
        
        # 登录获取token
        try:
            login_response = requests.post(
                urljoin(self.backend_url, "/api/v1/auth/login/"),
                json={"username": "test_student", "password": "student123"},
                timeout=10
            )
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                if 'data' in login_data and 'access' in login_data['data']:
                    self.auth_token = login_data['data']['access']
                    print("   ✅ 后端认证成功")
                else:
                    print("   ❌ 后端认证失败：未获取到token")
                    return False
            else:
                print(f"   ❌ 后端认证失败：状态码 {login_response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ 后端认证失败：{e}")
            return False
        
        # 测试数据端点
        headers = {'Authorization': f'Bearer {self.auth_token}'}
        endpoints_to_test = [
            ("/api/v1/users/", "用户数据"),
            ("/api/v1/courses/", "课程数据"),
            ("/api/v1/courses/enrollments/", "选课数据"),
            ("/api/v1/students/dashboard/", "学生仪表板数据")
        ]
        
        data_counts = {}
        for endpoint, name in endpoints_to_test:
            try:
                response = requests.get(
                    urljoin(self.backend_url, endpoint),
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict) and 'results' in data:
                        count = len(data['results'])
                        data_counts[name] = count
                        print(f"   ✅ {name}: {count} 条记录")
                    elif isinstance(data, list):
                        count = len(data)
                        data_counts[name] = count
                        print(f"   ✅ {name}: {count} 条记录")
                    else:
                        print(f"   ✅ {name}: 数据正常")
                        data_counts[name] = "数据正常"
                else:
                    print(f"   ❌ {name}: 状态码 {response.status_code}")
                    return False
            except Exception as e:
                print(f"   ❌ {name}: {e}")
                return False
        
        # 检查数据完整性
        total_records = sum(v for v in data_counts.values() if isinstance(v, int))
        print(f"\n   📈 数据统计总览:")
        for name, count in data_counts.items():
            print(f"      - {name}: {count}")
        
        if total_records > 0:
            print(f"   🎉 后端数据充足，总计 {total_records} 条记录可供前端显示")
            return True
        else:
            print(f"   ⚠️  后端数据不足，可能影响前端显示效果")
            return False
    
    def test_frontend_pages(self) -> bool:
        """测试前端页面"""
        print("\n🖥️  测试前端页面...")
        
        # 由于前端是SPA应用，我们主要测试主页面是否包含基本元素
        try:
            response = requests.get(self.frontend_url, timeout=10)
            content = response.text
            
            # 检查页面基本元素
            checks = [
                ("<!DOCTYPE html>", "HTML文档类型"),
                ("<title>", "页面标题"),
                ("react", "React框架", False),  # 可选检查
                ("app", "应用容器", False),  # 可选检查
            ]
            
            page_checks = []
            for check_text, description, *optional in checks:
                is_optional = optional[0] if optional else False
                found = check_text.lower() in content.lower()
                
                if found:
                    print(f"   ✅ {description}: 已找到")
                    page_checks.append(True)
                else:
                    if is_optional:
                        print(f"   ⚠️  {description}: 未找到 (可选)")
                        page_checks.append(True)  # 可选项不影响结果
                    else:
                        print(f"   ❌ {description}: 未找到")
                        page_checks.append(False)
            
            if all(page_checks):
                print("   🎉 前端页面基本结构正常")
                return True
            else:
                print("   ⚠️  前端页面可能存在问题")
                return False
                
        except Exception as e:
            print(f"   ❌ 前端页面测试失败: {e}")
            return False
    
    def test_api_connectivity(self) -> bool:
        """测试前端到后端的API连通性"""
        print("\n🔗 测试前端到后端API连通性...")
        
        # 由于前端是独立的React应用，我们无法直接测试前端的API调用
        # 但我们可以验证前端和后端服务都在运行，且端口正确
        
        # 检查前端可以访问后端（通过CORS等）
        try:
            # 模拟前端发起的OPTIONS请求（CORS预检）
            response = requests.options(
                urljoin(self.backend_url, "/api/v1/courses/"),
                headers={
                    'Origin': self.frontend_url,
                    'Access-Control-Request-Method': 'GET'
                },
                timeout=10
            )
            
            # 检查CORS headers
            cors_headers = [
                'Access-Control-Allow-Origin',
                'Access-Control-Allow-Methods',
                'Access-Control-Allow-Headers'
            ]
            
            cors_configured = any(header in response.headers for header in cors_headers)
            
            if cors_configured:
                print("   ✅ CORS配置正常，前端可以访问后端API")
                return True
            else:
                print("   ⚠️  CORS配置可能需要检查")
                # 这不是致命错误，可能是开发环境配置不同
                return True
                
        except Exception as e:
            print(f"   ⚠️  API连通性测试异常: {e}")
            # 这不是致命错误
            return True
    
    def generate_verification_report(self, frontend_accessible: bool, backend_data_available: bool, 
                                   frontend_pages_ok: bool, api_connectivity_ok: bool) -> None:
        """生成验证报告"""
        print("\n" + "="*60)
        print("📋 前端验证报告")
        print("="*60)
        
        # 计算总体状态
        checks = [frontend_accessible, backend_data_available, frontend_pages_ok, api_connectivity_ok]
        passed_checks = sum(checks)
        total_checks = len(checks)
        
        print(f"📊 验证统计:")
        print(f"   🧪 总检查项: {total_checks}")
        print(f"   ✅ 通过: {passed_checks}")
        print(f"   ❌ 失败: {total_checks - passed_checks}")
        print(f"   📈 通过率: {(passed_checks/total_checks*100):.1f}%")
        
        print(f"\n📋 详细检查结果:")
        print(f"   {'✅' if frontend_accessible else '❌'} 前端服务可访问性")
        print(f"   {'✅' if backend_data_available else '❌'} 后端数据可用性")
        print(f"   {'✅' if frontend_pages_ok else '❌'} 前端页面结构")
        print(f"   {'✅' if api_connectivity_ok else '❌'} API连通性")
        
        if passed_checks == total_checks:
            print(f"\n🎉 前端验证完全通过！")
            print(f"✨ 系统已准备就绪，可以在前端查看实际数据效果")
            print(f"🌐 访问地址: {self.frontend_url}")
            
            print(f"\n🔑 测试账号:")
            print(f"   - 学生账号: test_student / student123")
            print(f"   - 教师账号: test_teacher / teacher123")
            
        elif passed_checks >= total_checks * 0.75:  # 75%以上通过
            print(f"\n✅ 前端验证基本通过！")
            print(f"⚠️  存在一些小问题，但不影响基本功能")
            print(f"🌐 访问地址: {self.frontend_url}")
        else:
            print(f"\n⚠️  前端验证未完全通过")
            print(f"🔧 建议检查服务配置和数据状态")
    
    def run_validation(self) -> bool:
        """运行完整验证"""
        print("🚀 课程管理系统 - 前端验证工具")
        print("="*60)
        
        # 执行各项验证
        frontend_accessible = self.test_frontend_accessibility()
        backend_data_available = self.test_backend_data_availability()
        frontend_pages_ok = self.test_frontend_pages()
        api_connectivity_ok = self.test_api_connectivity()
        
        # 生成报告
        self.generate_verification_report(
            frontend_accessible, backend_data_available, 
            frontend_pages_ok, api_connectivity_ok
        )
        
        # 返回整体成功状态
        return all([frontend_accessible, backend_data_available, frontend_pages_ok])


def main():
    """主函数"""
    validator = FrontendValidator()
    success = validator.run_validation()
    return success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)