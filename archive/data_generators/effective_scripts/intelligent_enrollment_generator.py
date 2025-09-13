#!/usr/bin/env python
"""
智能选课数据生成器 - 为学生生成合理的选课记录
基于课程容量、学生专业匹配、先修关系等约束生成高质量选课数据
"""

import os
import sys
import django
import random
import json
from datetime import datetime, time, date
from typing import List, Dict, Any, Set, Tuple, Optional
from dataclasses import dataclass
from faker import Faker
import math
from collections import defaultdict

# Django环境设置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.courses.models import Course, Enrollment
from apps.classrooms.models import Building, Classroom
from apps.schedules.models import Schedule, TimeSlot
from django.db import transaction
from django.utils import timezone

User = get_user_model()
fake = Faker('zh_CN')

@dataclass
class EnrollmentGenerationConfig:
    """选课生成配置"""
    target_enrollments: int = 5607049  # 目标选课记录数
    batch_size: int = 5000
    
    # 选课约束参数
    avg_courses_per_student: int = 7    # 每名学生平均选课数
    min_courses_per_student: int = 5    # 最少选课数
    max_courses_per_student: int = 9    # 最多选课数
    
    # 课程类型权重
    course_type_weights: Dict[str, float] = None
    
    def __post_init__(self):
        if self.course_type_weights is None:
            self.course_type_weights = {
                'public': 0.8,      # 公共课选课概率高
                'required': 0.85,   # 必修课选课概率高
                'elective': 0.3,    # 选修课选课概率适中
                'professional': 0.4  # 专业课选课概率适中
            }

class IntelligentEnrollmentGenerator:
    """智能选课生成器"""
    
    def __init__(self, config: EnrollmentGenerationConfig):
        self.config = config
        self.fake = Faker('zh_CN')
        
        # 缓存数据
        self.students = []
        self.courses = []
        self.schedules = []
        
        # 分析数据
        self.course_by_type = defaultdict(list)
        self.course_by_department = defaultdict(list)
        self.student_by_department = defaultdict(list)
        self.course_capacities = {}
        self.course_enrollments = defaultdict(int)  # 当前选课人数
    
    def load_data(self):
        """加载基础数据并进行分析"""
        print("📊 加载基础数据...")
        
        # 加载学生
        self.students = list(User.objects.filter(user_type='student', is_active=True))
        
        # 加载课程
        self.courses = list(Course.objects.filter(is_active=True, is_published=True))
        
        # 加载排课信息
        self.schedules = list(Schedule.objects.filter(status='active')
                             .select_related('course', 'teacher', 'classroom'))
        
        print(f"✅ 数据加载完成：")
        print(f"   学生: {len(self.students)} 名")
        print(f"   课程: {len(self.courses)} 门")
        print(f"   排课: {len(self.schedules)} 条")
        
        # 分析数据
        self._analyze_data()
    
    def _analyze_data(self):
        """分析数据，建立索引"""
        print("🔍 分析数据结构...")
        
        # 按课程类型分类
        for course in self.courses:
            self.course_by_type[course.course_type].append(course)
            self.course_by_department[course.department].append(course)
            self.course_capacities[course.id] = course.max_students
        
        # 按学生院系分类（从用户名或其他字段推断）
        for student in self.students:
            # 从学号或其他字段推断院系（简化处理）
            dept = self._infer_student_department(student)
            self.student_by_department[dept].append(student)
        
        print(f"✅ 数据分析完成：")
        print(f"   课程类型: {list(self.course_by_type.keys())}")
        print(f"   涉及院系: {len(self.course_by_department)} 个")
        print(f"   学生分布: {len(self.student_by_department)} 个院系")
    
    def _infer_student_department(self, student: User) -> str:
        """推断学生所属院系（简化版）"""
        # 根据学号、用户名等推断院系
        username = student.username
        if hasattr(student, 'department') and student.department:
            return student.department
        
        # 根据用户名前缀推断（简化处理）
        if 'cs' in username.lower() or 'comp' in username.lower():
            return "计算机学院"
        elif 'math' in username.lower():
            return "数学学院"
        elif 'phys' in username.lower():
            return "物理学院"
        elif 'chem' in username.lower():
            return "化学学院"
        elif 'bio' in username.lower():
            return "生物学院"
        elif 'eng' in username.lower():
            return "外国语学院"
        elif 'econ' in username.lower():
            return "经济管理学院"
        else:
            # 随机分配到一个院系
            departments = ["计算机学院", "数学学院", "物理学院", "化学学院", "生物学院", 
                          "外国语学院", "经济管理学院", "文学院", "艺术学院", "体育学院"]
            return random.choice(departments)
    
    def generate_enrollments(self) -> List[Dict]:
        """生成选课数据"""
        print(f"📝 开始生成选课数据...")
        
        enrollments = []
        processed_students = 0
        
        for student in self.students:
            if processed_students % 10000 == 0:
                print(f"\r处理学生进度: {processed_students}/{len(self.students)} "
                      f"({processed_students/len(self.students)*100:.1f}%) "
                      f"已生成选课: {len(enrollments)}", end="")
            
            # 为该学生生成选课记录
            student_enrollments = self._generate_student_enrollments(student)
            enrollments.extend(student_enrollments)
            
            processed_students += 1
            
            # 控制总数
            if len(enrollments) >= self.config.target_enrollments:
                break
        
        print(f"\n✅ 选课生成完成：总计 {len(enrollments)} 条记录")
        return enrollments
    
    def _generate_student_enrollments(self, student: User) -> List[Dict]:
        """为单个学生生成选课记录"""
        enrollments = []
        student_dept = self._infer_student_department(student)
        
        # 确定该学生的选课数量
        num_courses = random.randint(
            self.config.min_courses_per_student, 
            self.config.max_courses_per_student
        )
        
        selected_courses = set()
        
        # 1. 优先选择公共课（每个学生都要选）
        public_courses = self._select_public_courses(student, selected_courses)
        enrollments.extend(public_courses)
        selected_courses.update(course['course'].id for course in public_courses)
        
        # 2. 选择本院系的必修课和专业课
        dept_courses = self._select_department_courses(student, student_dept, selected_courses)
        enrollments.extend(dept_courses)
        selected_courses.update(course['course'].id for course in dept_courses)
        
        # 3. 选择选修课（跨院系）
        if len(enrollments) < num_courses:
            elective_courses = self._select_elective_courses(
                student, selected_courses, num_courses - len(enrollments)
            )
            enrollments.extend(elective_courses)
        
        return enrollments
    
    def _select_public_courses(self, student: User, selected_courses: Set[int]) -> List[Dict]:
        """选择公共课"""
        enrollments = []
        public_courses = self.course_by_type.get('public', [])
        
        # 公共课选择概率高
        for course in public_courses:
            if course.id in selected_courses:
                continue
            
            if random.random() < self.config.course_type_weights['public']:
                if self._can_enroll(course):
                    enrollment = self._create_enrollment_record(student, course)
                    enrollments.append(enrollment)
                    self.course_enrollments[course.id] += 1
        
        return enrollments
    
    def _select_department_courses(self, student: User, dept: str, 
                                  selected_courses: Set[int]) -> List[Dict]:
        """选择本院系课程"""
        enrollments = []
        dept_courses = self.course_by_department.get(dept, [])
        
        # 按课程类型分别处理
        for course in dept_courses:
            if course.id in selected_courses:
                continue
            
            selection_prob = self.config.course_type_weights.get(course.course_type, 0.3)
            
            if random.random() < selection_prob:
                if self._can_enroll(course):
                    enrollment = self._create_enrollment_record(student, course)
                    enrollments.append(enrollment)
                    selected_courses.add(course.id)
                    self.course_enrollments[course.id] += 1
        
        return enrollments
    
    def _select_elective_courses(self, student: User, selected_courses: Set[int], 
                               num_needed: int) -> List[Dict]:
        """选择选修课"""
        enrollments = []
        elective_courses = self.course_by_type.get('elective', [])
        
        # 随机选择选修课
        available_courses = [c for c in elective_courses if c.id not in selected_courses]
        random.shuffle(available_courses)
        
        for course in available_courses[:num_needed * 2]:  # 多选一些备选
            if len(enrollments) >= num_needed:
                break
            
            if self._can_enroll(course):
                enrollment = self._create_enrollment_record(student, course)
                enrollments.append(enrollment)
                self.course_enrollments[course.id] += 1
        
        return enrollments
    
    def _can_enroll(self, course: Course) -> bool:
        """检查是否可以选课"""
        # 检查容量限制
        current_count = self.course_enrollments[course.id]
        if current_count >= course.max_students:
            return False
        
        # 检查是否有排课（简化检查）
        has_schedule = any(s.course_id == course.id for s in self.schedules)
        if not has_schedule:
            return False
        
        return True
    
    def _create_enrollment_record(self, student: User, course: Course) -> Dict:
        """创建选课记录"""
        # 选择选课状态
        status_choices = ['enrolled', 'enrolled', 'enrolled', 'waitlisted']  # 大部分成功选课
        status = random.choice(status_choices)
        
        enrollment = {
            'student': student,
            'course': course,
            'status': status,
            'enrollment_date': timezone.now(),
            'grade': None,  # 初始没有成绩
            'is_active': True
        }
        
        return enrollment

class EnrollmentDatabase:
    """选课数据库操作管理器"""
    
    def __init__(self, config: EnrollmentGenerationConfig):
        self.config = config
    
    def save_enrollments(self, enrollments: List[Dict]) -> int:
        """保存选课数据到数据库"""
        print("💾 保存选课数据到数据库...")
        
        created_count = 0
        batch = []
        total_enrollments = len(enrollments)
        
        for i, enrollment_data in enumerate(enrollments):
            if i % 1000 == 0:
                print(f"\r保存选课进度: {i+1}/{total_enrollments} "
                      f"({(i+1)/total_enrollments*100:.1f}%)", end="")
            
            try:
                # 检查是否已存在相同的选课记录
                existing = Enrollment.objects.filter(
                    student=enrollment_data['student'],
                    course=enrollment_data['course']
                ).exists()
                
                if existing:
                    continue
                
                enrollment = Enrollment(
                    student=enrollment_data['student'],
                    course=enrollment_data['course'],
                    status=enrollment_data['status'],
                    enrollment_date=enrollment_data['enrollment_date'],
                    grade=enrollment_data['grade'],
                    is_active=enrollment_data['is_active']
                )
                
                batch.append(enrollment)
                created_count += 1
                
                # 批量保存
                if len(batch) >= self.config.batch_size:
                    Enrollment.objects.bulk_create(batch, ignore_conflicts=True)
                    batch = []
                    
            except Exception as e:
                print(f"\n⚠️  跳过选课记录: {e}")
                continue
        
        # 保存剩余记录
        if batch:
            Enrollment.objects.bulk_create(batch, ignore_conflicts=True)
        
        print(f"\n✅ 选课保存完成：新增 {created_count} 条记录")
        return created_count

def generate_enrollment_statistics(enrollments: List[Dict]) -> Dict:
    """生成选课统计信息"""
    stats = {
        'total_enrollments': len(enrollments),
        'students_enrolled': len(set(e['student'].id for e in enrollments)),
        'courses_with_enrollments': len(set(e['course'].id for e in enrollments)),
        'status_distribution': defaultdict(int),
        'course_type_distribution': defaultdict(int),
        'department_distribution': defaultdict(int)
    }
    
    for enrollment in enrollments:
        stats['status_distribution'][enrollment['status']] += 1
        stats['course_type_distribution'][enrollment['course'].course_type] += 1
        stats['department_distribution'][enrollment['course'].department] += 1
    
    return stats

def main():
    """主函数"""
    print("📝 智能选课数据生成器启动")
    print("=" * 60)
    
    # 检查当前数据状况
    current_students = User.objects.filter(user_type='student', is_active=True).count()
    current_courses = Course.objects.filter(is_active=True).count()
    current_schedules = Schedule.objects.filter(status='active').count()
    current_enrollments = Enrollment.objects.count()
    
    print(f"📊 当前数据状况：")
    print(f"   活跃学生: {current_students:,}")
    print(f"   活跃课程: {current_courses:,}")
    print(f"   活跃排课: {current_schedules:,}")
    print(f"   现有选课: {current_enrollments:,}")
    print()
    
    if current_students < 100000:
        print("❌ 错误：学生数量不足，请确保有足够的学生数据")
        return
    
    if current_courses < 1000:
        print("❌ 错误：课程数量不足，请先运行课程数据生成器")
        return
    
    if current_schedules < 10000:
        print("❌ 错误：排课数量不足，请先运行排课数据生成器")
        return
    
    # 初始化配置
    config = EnrollmentGenerationConfig()
    generator = IntelligentEnrollmentGenerator(config)
    db_manager = EnrollmentDatabase(config)
    
    start_time = datetime.now()
    
    try:
        # 加载数据
        generator.load_data()
        
        # 生成选课数据
        print("\n📝 开始生成选课数据...")
        enrollments = generator.generate_enrollments()
        
        if not enrollments:
            print("❌ 未能生成任何选课数据")
            return
        
        # 生成统计信息
        stats = generate_enrollment_statistics(enrollments)
        
        # 保存到数据库
        created_count = db_manager.save_enrollments(enrollments)
        
        # 计算用时
        end_time = datetime.now()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print("🎉 选课数据生成完成！")
        print(f"⏱️  总用时: {duration}")
        print(f"📝 新增选课: {created_count} 条")
        print(f"📊 选课总数: {Enrollment.objects.count()} 条")
        print()
        print("📈 选课统计：")
        print(f"   参与选课学生: {stats['students_enrolled']:,} 名")
        print(f"   有选课的课程: {stats['courses_with_enrollments']:,} 门")
        print(f"   平均每生选课: {stats['total_enrollments']/stats['students_enrolled']:.1f} 门")
        
        print("\n📋 选课状态分布：")
        for status, count in stats['status_distribution'].items():
            print(f"   {status}: {count:,} ({count/stats['total_enrollments']*100:.1f}%)")
        
        print("\n📚 课程类型分布：")
        for course_type, count in stats['course_type_distribution'].items():
            print(f"   {course_type}: {count:,} ({count/stats['total_enrollments']*100:.1f}%)")
        
        print("\n🎯 数据生成任务全部完成！")
        print("   ✅ 教室数据: 已完成")
        print("   ✅ 课程数据: 已完成") 
        print("   ✅ 排课数据: 已完成")
        print("   ✅ 选课数据: 已完成")
        
    except Exception as e:
        print(f"❌ 生成过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()