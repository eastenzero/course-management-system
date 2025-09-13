#!/usr/bin/env python
"""
智能排课数据生成器 - 专为算法验证设计
目标：生成高质量、具有真实约束的测试数据，充分体现排课算法的优势
"""

import os
import sys
import django
import random
import json
from datetime import datetime, date, timedelta
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

# 设置Django环境
# 添加backend路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from apps.courses.models import Course, Enrollment

User = get_user_model()


@dataclass
class TeacherProfile:
    """教师画像建模"""
    id: int
    name: str
    department: str
    title: str
    specialties: List[str]
    qualified_courses: List[str]
    max_weekly_hours: int
    preferred_time_slots: List[Tuple[int, int]]
    
    def can_teach_course(self, course_name: str) -> bool:
        return course_name in self.qualified_courses


class SmartDataGenerator:
    """智能数据生成器 - 基于真实场景建模"""
    
    def __init__(self, scale: str = 'medium'):
        self.scale = scale
        self.teacher_profiles = []
        self.course_catalog = []
        
        # 规模配置
        self.scale_config = {
            'small': {'teachers': 50, 'students': 500, 'courses': 100},
            'medium': {'teachers': 200, 'students': 2000, 'courses': 300},
            'large': {'teachers': 500, 'students': 5000, 'courses': 800}
        }
        
        self.config = self.scale_config[scale]
        
        # 大学结构
        self.departments = {
            'computer_science': {'name': '计算机学院', 'teacher_count': 120},
            'mathematics': {'name': '数学学院', 'teacher_count': 80},
            'physics': {'name': '物理学院', 'teacher_count': 60},
            'economics': {'name': '经济学院', 'teacher_count': 90}
        }
        
        # 课程层次
        self.course_hierarchy = {
            'foundation': {
                'courses': ['高等数学A1', '高等数学A2', '线性代数', '概率论与数理统计', '大学英语1', '大学英语2'],
                'prerequisites': {},
                'semester': [1, 2]
            },
            'professional_core': {
                'courses': ['程序设计基础', '数据结构', '算法分析', '操作系统', '计算机网络', '数据库原理'],
                'prerequisites': {'数据结构': ['程序设计基础'], '算法分析': ['数据结构']},
                'semester': [3, 4, 5]
            },
            'professional_elective': {
                'courses': ['人工智能', '机器学习', 'Web开发', '移动应用开发', '云计算', '大数据技术'],
                'prerequisites': {'机器学习': ['概率论与数理统计', '线性代数']},
                'semester': [6, 7, 8]
            }
        }
        
        # 预编译密码
        self.student_password = make_password('student123')
        self.teacher_password = make_password('teacher123')
    
    def generate_realistic_teacher_profiles(self) -> List[TeacherProfile]:
        """生成真实的教师画像"""
        print("📝 生成教师画像...")
        
        profiles = []
        teacher_id = 1
        
        for dept_code, dept_info in self.departments.items():
            dept_teacher_count = int(self.config['teachers'] * dept_info['teacher_count'] / 350)
            
            for i in range(dept_teacher_count):
                # 职称分布
                title = random.choices(['教授', '副教授', '讲师', '助教'], weights=[0.15, 0.25, 0.35, 0.25])[0]
                
                # 根据职称确定能力
                if title in ['教授', '副教授']:
                    specialty_count = random.randint(2, 4)
                    max_hours = random.randint(12, 18)
                else:
                    specialty_count = random.randint(1, 2)
                    max_hours = random.randint(16, 24)
                
                # 生成专业领域
                all_courses = []
                for level_info in self.course_hierarchy.values():
                    all_courses.extend(level_info['courses'])
                
                specialties = random.sample(all_courses, min(specialty_count, len(all_courses)))
                qualified_courses = specialties.copy()
                
                # 生成时间偏好
                preferred_slots = []
                for _ in range(random.randint(3, 6)):
                    day = random.randint(1, 5)
                    slot = random.randint(1, 8)
                    preferred_slots.append((day, slot))
                
                profile = TeacherProfile(
                    id=teacher_id,
                    name=f"{dept_info['name']}教师{i+1:03d}",
                    department=dept_info['name'],
                    title=title,
                    specialties=specialties,
                    qualified_courses=qualified_courses,
                    max_weekly_hours=max_hours,
                    preferred_time_slots=preferred_slots
                )
                
                profiles.append(profile)
                teacher_id += 1
        
        self.teacher_profiles = profiles
        print(f"   ✅ 生成 {len(profiles)} 个教师画像")
        return profiles
    
    def generate_realistic_course_catalog(self) -> List[Dict]:
        """生成真实的课程目录"""
        print("📚 生成课程目录...")
        
        catalog = []
        course_id = 1
        
        for level_name, level_info in self.course_hierarchy.items():
            for course_name in level_info['courses']:
                # 课程属性设置
                if level_name == 'foundation':
                    credits = random.choice([3, 4, 5])
                    max_students = random.randint(120, 200)
                    course_type = 'required'
                elif level_name == 'professional_core':
                    credits = random.choice([3, 4])
                    max_students = random.randint(60, 100)
                    course_type = 'professional'
                else:
                    credits = random.choice([2, 3])
                    max_students = random.randint(30, 60)
                    course_type = 'elective'
                
                course = {
                    'id': course_id,
                    'name': course_name,
                    'code': f"SMART{course_id:03d}",
                    'credits': credits,
                    'max_students': max_students,
                    'course_type': course_type,
                    'level': level_name,
                    'prerequisites': level_info['prerequisites'].get(course_name, []),
                    'semester': random.choice(level_info['semester']),
                    'academic_year': '2024-2025',
                    'department': random.choice(list(self.departments.values()))['name'],
                    'is_active': True,
                    'is_published': True,
                }
                
                catalog.append(course)
                course_id += 1
        
        self.course_catalog = catalog
        print(f"   ✅ 生成 {len(catalog)} 门课程")
        return catalog
    
    def generate_database_records(self) -> Dict:
        """生成数据库记录"""
        print("💾 生成数据库记录...")
        
        users = self._create_user_records()
        courses = self._create_course_records()
        enrollments = self._create_enrollment_records(users, courses)
        
        return {
            'users': users,
            'courses': courses,
            'enrollments': enrollments,
            'summary': {
                'total_users': len(users),
                'total_courses': len(courses),
                'total_enrollments': len(enrollments),
                'teachers': len([u for u in users if u['user_type'] == 'teacher']),
                'students': len([u for u in users if u['user_type'] == 'student'])
            }
        }
    
    def _create_user_records(self) -> List[Dict]:
        """创建用户记录"""
        users = []
        user_id = 1
        
        # 创建教师用户
        for profile in self.teacher_profiles:
            user = {
                'id': user_id,
                'username': f"teacher_{user_id:04d}",
                'email': f"teacher_{user_id:04d}@university.edu",
                'first_name': profile.name[:1],
                'last_name': profile.name[1:],
                'user_type': 'teacher',
                'department': profile.department,
                'employee_id': f"T{user_id:06d}",
                'phone': self._generate_phone(),
                'password': self.teacher_password,
                'is_active': True,
                'date_joined': timezone.now() - timedelta(days=random.randint(30, 1095)),
                'profile_data': {
                    'title': profile.title,
                    'specialties': profile.specialties,
                    'max_weekly_hours': profile.max_weekly_hours
                }
            }
            users.append(user)
            user_id += 1
        
        # 创建学生用户
        student_count = self.config['students']
        for i in range(student_count):
            dept = random.choice(list(self.departments.values()))
            
            user = {
                'id': user_id,
                'username': f"student_{user_id:06d}",
                'email': f"student_{user_id:06d}@university.edu",
                'first_name': self._generate_chinese_name()[:1],
                'last_name': self._generate_chinese_name()[1:],
                'user_type': 'student',
                'department': dept['name'],
                'student_id': f"S{user_id:08d}",
                'phone': self._generate_phone(),
                'password': self.student_password,
                'is_active': True,
                'date_joined': timezone.now() - timedelta(days=random.randint(0, 365)),
                'profile_data': {
                    'grade': random.choice([1, 2, 3, 4])
                }
            }
            users.append(user)
            user_id += 1
        
        return users
    
    def _create_course_records(self) -> List[Dict]:
        """创建课程记录"""
        return self.course_catalog.copy()
    
    def _create_enrollment_records(self, users: List[Dict], courses: List[Dict]) -> List[Dict]:
        """创建选课记录"""
        enrollments = []
        enrollment_id = 1
        
        students = [u for u in users if u['user_type'] == 'student']
        
        for student in students:
            grade = student['profile_data']['grade']
            
            # 根据年级选择合适的课程
            suitable_courses = []
            for course in courses:
                if self._is_suitable_for_grade(course, grade):
                    suitable_courses.append(course)
            
            # 随机选择课程
            course_count = random.randint(4, 8)
            selected_courses = random.sample(
                suitable_courses, 
                min(course_count, len(suitable_courses))
            )
            
            for course in selected_courses:
                enrollment = {
                    'id': enrollment_id,
                    'student_id': student['id'],
                    'course_id': course['id'],
                    'semester': course['semester'],
                    'academic_year': course['academic_year'],
                    'enrollment_date': timezone.now() - timedelta(days=random.randint(0, 60)),
                    'status': 'enrolled'
                }
                enrollments.append(enrollment)
                enrollment_id += 1
        
        return enrollments
    
    def _is_suitable_for_grade(self, course: Dict, grade: int) -> bool:
        """判断课程是否适合某个年级"""
        course_level = course['level']
        
        if grade <= 2:
            return course_level == 'foundation'
        elif grade == 3:
            return course_level == 'professional_core'
        else:
            return course_level in ['professional_core', 'professional_elective']
    
    def _generate_chinese_name(self) -> str:
        """生成中文姓名"""
        surnames = ['王', '李', '张', '刘', '陈', '杨', '赵', '黄', '周', '吴']
        given_names = ['伟', '芳', '娜', '敏', '静', '丽', '强', '磊', '军', '洋']
        
        surname = random.choice(surnames)
        given = random.choice(given_names)
        return surname + given
    
    def _generate_phone(self) -> str:
        """生成手机号"""
        prefixes = ['130', '131', '132', '133', '134', '135', '136', '137', '138', '139']
        prefix = random.choice(prefixes)
        suffix = ''.join([str(random.randint(0, 9)) for _ in range(8)])
        return prefix + suffix
    
    def save_to_database(self, data: Dict) -> bool:
        """保存数据到数据库"""
        print("💾 保存数据到数据库...")
        
        try:
            with transaction.atomic():
                # 清理旧数据
                print("   清理旧测试数据...")
                User.objects.filter(username__startswith='smart_').delete()
                Course.objects.filter(code__startswith='SMART_').delete()
                
                # 保存用户
                print("   保存用户数据...")
                users_to_create = []
                for user_data in data['users']:
                    user = User(
                        username=f"smart_{user_data['username']}",
                        email=user_data['email'],
                        first_name=user_data['first_name'],
                        last_name=user_data['last_name'],
                        user_type=user_data['user_type'],
                        department=user_data['department'],
                        phone=user_data['phone'],
                        password=user_data['password'],
                        is_active=user_data['is_active'],
                        date_joined=user_data['date_joined']
                    )
                    
                    if user_data['user_type'] == 'teacher':
                        user.employee_id = user_data['employee_id']
                    else:
                        user.student_id = user_data['student_id']
                    
                    users_to_create.append(user)
                
                User.objects.bulk_create(users_to_create, batch_size=1000)
                print(f"   ✅ 保存用户: {len(users_to_create)} 条")
                
                # 保存课程
                print("   保存课程数据...")
                courses_to_create = []
                for course_data in data['courses']:
                    course = Course(
                        name=course_data['name'],
                        code=f"SMART_{course_data['code']}",
                        credits=course_data['credits'],
                        max_students=course_data['max_students'],
                        course_type=course_data['course_type'],
                        semester=course_data['semester'],
                        academic_year=course_data['academic_year'],
                        department=course_data['department'],
                        is_active=course_data['is_active'],
                        is_published=course_data['is_published']
                    )
                    courses_to_create.append(course)
                
                Course.objects.bulk_create(courses_to_create, batch_size=500)
                print(f"   ✅ 保存课程: {len(courses_to_create)} 条")
                
                print("   ✅ 数据保存完成")
                return True
                
        except Exception as e:
            print(f"   ❌ 数据保存失败: {e}")
            return False


def main():
    """主函数"""
    print("🎯 智能排课数据生成器 - 专为算法验证设计")
    print("=" * 60)
    
    # 选择数据规模
    scale = input("请选择数据规模 (small/medium/large) [medium]: ").strip() or 'medium'
    
    if scale not in ['small', 'medium', 'large']:
        print("❌ 无效的数据规模，使用默认值 'medium'")
        scale = 'medium'
    
    # 创建生成器
    generator = SmartDataGenerator(scale=scale)
    
    # 生成数据
    print(f"\n🚀 开始生成 {scale} 规模的智能测试数据...")
    
    # 生成教师画像
    generator.generate_realistic_teacher_profiles()
    
    # 生成课程目录
    generator.generate_realistic_course_catalog()
    
    # 生成数据库记录
    data = generator.generate_database_records()
    
    # 保存到数据库
    success = generator.save_to_database(data)
    
    if success:
        print("\n📊 数据生成完成！")
        print(f"总用户数: {data['summary']['total_users']:,}")
        print(f"教师数量: {data['summary']['teachers']:,}")
        print(f"学生数量: {data['summary']['students']:,}")
        print(f"课程数量: {data['summary']['total_courses']:,}")
        print(f"选课记录: {data['summary']['total_enrollments']:,}")
        
        print("\n🎯 建议下一步:")
        print("1. 运行智能排课算法测试这些数据")
        print("2. 观察算法在真实约束下的表现")
        print("3. 验证生成的课程表是否合理")
        print("4. 分析不同场景下的优化效果")
    else:
        print("\n❌ 数据生成失败，请检查数据库连接和权限")


if __name__ == '__main__':
    main()