#!/usr/bin/env python3
"""
API验证脚本 - 测试课程管理系统的主要API端点
功能：验证后端API是否正常工作，数据是否正确返回
"""

import requests
import json
import sys
from typing import Dict, Any, Optional
from urllib.parse import urljoin

class APITester:
    """API测试类"""
    
    def __init__(self, base_url: str = "http://localhost:18000"):
        """初始化API测试器"""
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
    
    def test_endpoint(self, name: str, method: str, endpoint: str, 
                     data: Optional[Dict] = None, 
                     headers: Optional[Dict] = None,
                     expected_status: int = 200) -> Dict[str, Any]:
        """测试单个API端点"""
        url = urljoin(self.base_url, endpoint)
        
        # 设置默认headers
        request_headers = {'Content-Type': 'application/json'}
        if headers:
            request_headers.update(headers)
        
        # 添加认证token
        if self.auth_token:
            request_headers['Authorization'] = f'Bearer {self.auth_token}'
        
        try:
            # 发送请求
            if method.upper() == 'GET':
                response = self.session.get(url, headers=request_headers, timeout=10)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, headers=request_headers, timeout=10)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, headers=request_headers, timeout=10)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, headers=request_headers, timeout=10)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            # 分析响应
            status_ok = response.status_code == expected_status
            
            try:
                response_data = response.json()
            except:
                response_data = response.text
            
            result = {
                'name': name,
                'method': method.upper(),
                'url': url,
                'status_code': response.status_code,
                'expected_status': expected_status,
                'status_ok': status_ok,
                'response_data': response_data,
                'success': status_ok
            }
            
            # 打印结果
            status_icon = "✅" if status_ok else "❌"
            print(f"{status_icon} {name}: {method.upper()} {endpoint} -> {response.status_code}")
            
            if not status_ok:
                print(f"   ⚠️  期望状态码: {expected_status}, 实际: {response.status_code}")
                if response.text:
                    print(f"   📄 响应内容: {response.text[:200]}...")
            
            return result
            
        except Exception as e:
            result = {
                'name': name,
                'method': method.upper(),
                'url': url,
                'error': str(e),
                'success': False
            }
            print(f"❌ {name}: {method.upper()} {endpoint} -> 请求失败: {e}")
            return result
    
    def authenticate(self, username: str = "test_student", password: str = "student123") -> bool:
        """用户认证"""
        print(f"🔐 尝试用户认证: {username}")
        
        auth_result = self.test_endpoint(
            name="用户登录",
            method="POST",
            endpoint="/api/v1/auth/login/",
            data={
                "username": username,
                "password": password
            },
            expected_status=200
        )
        
        if auth_result['success'] and isinstance(auth_result['response_data'], dict):
            # 先尝试直接获取access字段
            access_token = auth_result['response_data'].get('access')
            # 如果没有，尝试从udata.access获取
            if not access_token and 'data' in auth_result['response_data']:
                access_token = auth_result['response_data']['data'].get('access')
            
            if access_token:
                self.auth_token = access_token
                print(f"   ✅ 认证成功，获取Token")
                return True
        
        print(f"   ❌ 认证失败")
        return False
    
    def test_health_endpoint(self) -> None:
        """测试健康检查端点"""
        print("\n🏥 测试健康检查端点...")
        result = self.test_endpoint(
            name="健康检查",
            method="GET", 
            endpoint="/api/health/"
        )
        self.test_results.append(result)
    
    def test_auth_endpoints(self) -> None:
        """测试认证相关端点"""
        print("\n🔐 测试认证端点...")
        
        # 测试登录端点
        result = self.test_endpoint(
            name="用户登录",
            method="POST",
            endpoint="/api/v1/auth/login/",
            data={
                "username": "test_student",
                "password": "student123"
            }
        )
        self.test_results.append(result)
        
        # 如果登录成功，保存token用于后续测试
        if result['success'] and isinstance(result['response_data'], dict):
            # 先尝试直接获取access字段
            access_token = result['response_data'].get('access')
            # 如果没有，尝试从udata.access获取
            if not access_token and 'data' in result['response_data']:
                access_token = result['response_data']['data'].get('access')
            
            if access_token:
                self.auth_token = access_token
                print("   ✅ 获取认证Token用于后续 API测试")
            else:
                print("   ⚠️  登录成功但未获取到access token")
                print(f"   📄 响应数据: {result['response_data']}")
        
        # 测试获取当前用户信息（需要认证）
        if self.auth_token:
            result = self.test_endpoint(
                name="获取当前用户",
                method="GET",
                endpoint="/api/v1/auth/user/"
            )
            self.test_results.append(result)
    
    def test_user_endpoints(self) -> None:
        """测试用户管理端点"""
        print("\n👥 测试用户管理端点...")
        
        # 测试用户列表
        result = self.test_endpoint(
            name="用户列表",
            method="GET",
            endpoint="/api/v1/users/"
        )
        self.test_results.append(result)
        
        # 如果有用户数据，测试用户详情
        if result['success'] and isinstance(result['response_data'], dict):
            users_data = result['response_data'].get('results', [])
            if users_data and len(users_data) > 0:
                user_id = users_data[0]['id']
                detail_result = self.test_endpoint(
                    name="用户详情",
                    method="GET",
                    endpoint=f"/api/v1/users/{user_id}/"
                )
                self.test_results.append(detail_result)
    
    def test_course_endpoints(self) -> None:
        """测试课程管理端点"""
        print("\n📚 测试课程管理端点...")
        
        # 测试课程列表
        result = self.test_endpoint(
            name="课程列表",
            method="GET",
            endpoint="/api/v1/courses/"
        )
        self.test_results.append(result)
        
        # 如果有课程数据，测试课程详情
        if result['success'] and isinstance(result['response_data'], dict):
            courses_data = result['response_data'].get('results', [])
            if courses_data and len(courses_data) > 0:
                course_id = courses_data[0]['id']
                detail_result = self.test_endpoint(
                    name="课程详情",
                    method="GET",
                    endpoint=f"/api/v1/courses/{course_id}/"
                )
                self.test_results.append(detail_result)
                
                # 测试课程选课情况
                enrollment_result = self.test_endpoint(
                    name="课程选课情况",
                    method="GET",
                    endpoint=f"/api/v1/courses/{course_id}/enrollments/"
                )
                self.test_results.append(enrollment_result)
    
    def test_enrollment_endpoints(self) -> None:
        """测试选课管理端点"""
        print("\n📝 测试选课管理端点...")
        
        # 测试选课记录列表
        result = self.test_endpoint(
            name="选课记录列表",
            method="GET",
            endpoint="/api/v1/courses/enrollments/"
        )
        self.test_results.append(result)
        
        # 如果有选课记录，测试选课详情
        if result['success'] and isinstance(result['response_data'], dict):
            enrollments_data = result['response_data'].get('results', [])
            if enrollments_data and len(enrollments_data) > 0:
                enrollment_id = enrollments_data[0]['id']
                detail_result = self.test_endpoint(
                    name="选课记录详情",
                    method="GET",
                    endpoint=f"/api/v1/courses/enrollments/{enrollment_id}/"
                )
                self.test_results.append(detail_result)
    
    def test_student_endpoints(self) -> None:
        """测试学生相关端点"""
        print("\n👨‍🎓 测试学生相关端点...")
        
        # 测试学生仪表板
        result = self.test_endpoint(
            name="学生仪表板",
            method="GET",
            endpoint="/api/v1/students/dashboard/"
        )
        self.test_results.append(result)
        
        # 测试学生档案
        result = self.test_endpoint(
            name="学生档案",
            method="GET",
            endpoint="/api/v1/students/profile/"
        )
        self.test_results.append(result)
    
    def test_teacher_endpoints(self) -> None:
        """测试教师相关端点"""
        print("\n👨‍🏫 测试教师相关端点...")
        
        # 首先用教师账号登录
        teacher_auth_success = self.authenticate("test_teacher", "teacher123")
        
        if teacher_auth_success:
            # 测试教师仪表板
            result = self.test_endpoint(
                name="教师仪表板",
                method="GET",
                endpoint="/api/v1/teachers/dashboard/"
            )
            self.test_results.append(result)
            
            # 测试教师档案
            result = self.test_endpoint(
                name="教师档案",
                method="GET",
                endpoint="/api/v1/teachers/profile/"
            )
            self.test_results.append(result)
    
    def generate_report(self) -> None:
        """生成测试报告"""
        print("\n" + "="*60)
        print("📋 API测试报告")
        print("="*60)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r['success'])
        failed_tests = total_tests - successful_tests
        
        print(f"📊 测试统计:")
        print(f"   🧪 总测试数: {total_tests}")
        print(f"   ✅ 成功: {successful_tests}")
        print(f"   ❌ 失败: {failed_tests}")
        print(f"   📈 成功率: {(successful_tests/total_tests*100):.1f}%" if total_tests > 0 else "   📈 成功率: 0%")
        
        if failed_tests > 0:
            print(f"\n❌ 失败的测试:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   - {result['name']}: {result['method']} {result.get('url', 'N/A')}")
                    if 'error' in result:
                        print(f"     错误: {result['error']}")
                    elif 'status_code' in result:
                        print(f"     状态码: {result['status_code']} (期望: {result.get('expected_status', 200)})")
        
        print(f"\n✅ 成功的API端点:")
        for result in self.test_results:
            if result['success']:
                print(f"   - {result['name']}: {result['method']} {result.get('url', 'N/A').split('/')[-2:]} ")
        
        # 数据验证
        print(f"\n📊 数据验证结果:")
        self._validate_data_content()
    
    def _validate_data_content(self) -> None:
        """验证API返回的数据内容"""
        data_checks = []
        
        # 检查用户数据
        user_tests = [r for r in self.test_results if r['name'] == '用户列表' and r['success']]
        if user_tests:
            user_data = user_tests[0]['response_data']
            if isinstance(user_data, dict) and 'results' in user_data:
                user_count = len(user_data['results'])
                data_checks.append(f"👥 用户数据: {user_count} 条记录")
        
        # 检查课程数据
        course_tests = [r for r in self.test_results if r['name'] == '课程列表' and r['success']]
        if course_tests:
            course_data = course_tests[0]['response_data']
            if isinstance(course_data, dict) and 'results' in course_data:
                course_count = len(course_data['results'])
                data_checks.append(f"📚 课程数据: {course_count} 条记录")
        
        # 检查选课数据
        enrollment_tests = [r for r in self.test_results if r['name'] == '选课记录列表' and r['success']]
        if enrollment_tests:
            enrollment_data = enrollment_tests[0]['response_data']
            if isinstance(enrollment_data, dict) and 'results' in enrollment_data:
                enrollment_count = len(enrollment_data['results'])
                data_checks.append(f"📝 选课数据: {enrollment_count} 条记录")
        
        for check in data_checks:
            print(f"   {check}")
        
        if not data_checks:
            print("   ⚠️  未能获取有效的数据统计")


def main():
    """主函数"""
    print("🚀 课程管理系统 - API验证工具")
    print("="*60)
    
    # 初始化API测试器
    tester = APITester()
    
    # 执行测试
    try:
        # 1. 健康检查
        tester.test_health_endpoint()
        
        # 2. 认证端点测试
        tester.test_auth_endpoints()
        
        # 3. 用户管理端点测试
        tester.test_user_endpoints()
        
        # 4. 课程管理端点测试
        tester.test_course_endpoints()
        
        # 5. 选课管理端点测试
        tester.test_enrollment_endpoints()
        
        # 6. 学生端点测试
        tester.test_student_endpoints()
        
        # 7. 教师端点测试
        tester.test_teacher_endpoints()
        
        # 8. 生成报告
        tester.generate_report()
        
        # 返回成功状态
        successful_tests = sum(1 for r in tester.test_results if r['success'])
        total_tests = len(tester.test_results)
        
        if successful_tests >= total_tests * 0.8:  # 80%以上成功率认为通过
            print(f"\n🎉 API验证通过！成功率: {successful_tests/total_tests*100:.1f}%")
            return True
        else:
            print(f"\n⚠️  API验证未完全通过，成功率: {successful_tests/total_tests*100:.1f}%")
            return False
            
    except Exception as e:
        print(f"\n❌ API验证过程中发生错误: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)