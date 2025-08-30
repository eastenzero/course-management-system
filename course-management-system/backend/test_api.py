#!/usr/bin/env python
"""
API测试脚本
用于测试校园课程表管理系统的主要API功能
"""

import requests
import json
import sys

BASE_URL = 'http://localhost:8000/api/v1'

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
    
    def login(self, username='admin', password='admin123'):
        """用户登录"""
        url = f"{BASE_URL}/users/auth/login/"
        data = {
            'username': username,
            'password': password
        }
        
        response = self.session.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            self.token = result['data']['access']
            self.session.headers.update({
                'Authorization': f'Bearer {self.token}'
            })
            print(f"✓ 登录成功: {username}")
            return True
        else:
            print(f"✗ 登录失败: {response.text}")
            return False
    
    def test_user_profile(self):
        """测试用户信息获取"""
        url = f"{BASE_URL}/users/profile/"
        response = self.session.get(url)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 获取用户信息成功: {result['data']['username']}")
            return True
        else:
            print(f"✗ 获取用户信息失败: {response.text}")
            return False
    
    def test_course_list(self):
        """测试课程列表获取"""
        url = f"{BASE_URL}/courses/"
        response = self.session.get(url)

        if response.status_code == 200:
            result = response.json()
            # 处理分页响应
            if 'data' in result:
                courses = result['data']
            elif 'results' in result:
                courses = result['results']
            else:
                courses = result
            print(f"✓ 获取课程列表成功: 共{len(courses)}门课程")
            return True
        else:
            print(f"✗ 获取课程列表失败: {response.text}")
            return False
    
    def test_create_course(self):
        """测试创建课程"""
        url = f"{BASE_URL}/courses/"
        data = {
            'code': 'CS101',
            'name': '计算机科学导论',
            'english_name': 'Introduction to Computer Science',
            'course_type': 'required',
            'credits': 3,
            'hours': 48,
            'department': '计算机学院',
            'semester': '2024-2025-1',
            'academic_year': '2024-2025',
            'description': '计算机科学基础课程',
            'max_students': 100,
            'min_students': 20,
            'is_active': True,
            'is_published': True
        }
        
        response = self.session.post(url, json=data)
        if response.status_code == 201:
            result = response.json()
            print(f"✓ 创建课程成功: {result['data']['name']}")
            return result['data']['id']
        else:
            print(f"✗ 创建课程失败: {response.text}")
            return None
    
    def test_classroom_list(self):
        """测试教室列表获取"""
        url = f"{BASE_URL}/classrooms/"
        response = self.session.get(url)

        if response.status_code == 200:
            result = response.json()
            # 处理分页响应
            if 'data' in result:
                classrooms = result['data']
            elif 'results' in result:
                classrooms = result['results']
            else:
                classrooms = result
            print(f"✓ 获取教室列表成功: 共{len(classrooms)}间教室")
            return True
        else:
            print(f"✗ 获取教室列表失败: {response.text}")
            return False
    
    def test_create_building(self):
        """测试创建教学楼"""
        url = f"{BASE_URL}/classrooms/buildings/"
        data = {
            'name': '信息楼',
            'code': 'INFO',
            'address': '校园东区',
            'description': '信息技术教学楼',
            'is_active': True
        }
        
        response = self.session.post(url, json=data)
        if response.status_code == 201:
            result = response.json()
            print(f"✓ 创建教学楼成功: {result['data']['name']}")
            return result['data']['id']
        else:
            print(f"✗ 创建教学楼失败: {response.text}")
            return None
    
    def test_create_classroom(self, building_id):
        """测试创建教室"""
        url = f"{BASE_URL}/classrooms/"
        data = {
            'building': building_id,
            'room_number': '101',
            'name': '多媒体教室',
            'capacity': 60,
            'room_type': 'multimedia',
            'floor': 1,
            'area': 80.5,
            'equipment': {
                '投影仪': '1台',
                '音响': '1套',
                '空调': '2台'
            },
            'is_available': True,
            'is_active': True
        }
        
        response = self.session.post(url, json=data)
        if response.status_code == 201:
            result = response.json()
            print(f"✓ 创建教室成功: {result['data']['full_name']}")
            return result['data']['id']
        else:
            print(f"✗ 创建教室失败: {response.text}")
            return None
    
    def test_timeslot_list(self):
        """测试时间段列表获取"""
        url = f"{BASE_URL}/schedules/timeslots/"
        response = self.session.get(url)

        if response.status_code == 200:
            result = response.json()
            # 处理分页响应
            if 'data' in result:
                timeslots = result['data']
            elif 'results' in result:
                timeslots = result['results']
            else:
                timeslots = result
            print(f"✓ 获取时间段列表成功: 共{len(timeslots)}个时间段")
            return True
        else:
            print(f"✗ 获取时间段列表失败: {response.text}")
            return False
    
    def test_create_timeslot(self):
        """测试创建时间段"""
        url = f"{BASE_URL}/schedules/timeslots/"
        data = {
            'name': '第1节课',
            'start_time': '08:00:00',
            'end_time': '08:45:00',
            'order': 1,
            'is_active': True
        }
        
        response = self.session.post(url, json=data)
        if response.status_code == 201:
            result = response.json()
            print(f"✓ 创建时间段成功: {result['data']['name']}")
            return result['data']['id']
        else:
            print(f"✗ 创建时间段失败: {response.text}")
            return None
    
    def test_schedule_list(self):
        """测试课程安排列表获取"""
        url = f"{BASE_URL}/schedules/"
        response = self.session.get(url)

        if response.status_code == 200:
            result = response.json()
            # 处理分页响应
            if 'data' in result:
                schedules = result['data']
            elif 'results' in result:
                schedules = result['results']
            else:
                schedules = result
            print(f"✓ 获取课程安排列表成功: 共{len(schedules)}个安排")
            return True
        else:
            print(f"✗ 获取课程安排列表失败: {response.text}")
            return False
    
    def test_api_docs(self):
        """测试API文档访问"""
        url = f"{BASE_URL.replace('/api/v1', '')}/api/schema/"
        response = requests.get(url)
        
        if response.status_code == 200:
            print("✓ API文档访问成功")
            return True
        else:
            print(f"✗ API文档访问失败: {response.status_code}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("开始API测试...")
        print("=" * 50)
        
        # 登录测试
        if not self.login():
            print("登录失败，终止测试")
            return False
        
        # 用户相关测试
        self.test_user_profile()
        
        # 课程相关测试
        self.test_course_list()
        course_id = self.test_create_course()
        
        # 教室相关测试
        self.test_classroom_list()
        building_id = self.test_create_building()
        if building_id:
            classroom_id = self.test_create_classroom(building_id)
        
        # 排课相关测试
        self.test_timeslot_list()
        timeslot_id = self.test_create_timeslot()
        self.test_schedule_list()
        
        # API文档测试
        self.test_api_docs()
        
        print("=" * 50)
        print("API测试完成")


if __name__ == '__main__':
    tester = APITester()
    tester.run_all_tests()
