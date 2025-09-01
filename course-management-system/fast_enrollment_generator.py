#!/usr/bin/env python
"""
快速选课数据生成器 - 优化版本，快速为学生生成选课记录
"""

# 设置环境变量，禁用有问题的模块
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'course_management.settings'
os.environ['DISABLE_MAGIC'] = '1'  # 禁用magic模块

import sys
import django
import random
from datetime import datetime
from typing import List, Dict, Any

# 添加backend目录到Python路径
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.append(backend_path)

# 修改magic模块导入问题
import builtins
original_import = builtins.__import__

def patched_import(name, *args, **kwargs):
    if name == 'magic':
        # 创建一个虚拟magic模块
        class FakeMagic:
            def from_buffer(self, buffer, mime=False):
                return 'application/octet-stream'
        
        class MockMagic:
            Magic = FakeMagic
            
        return MockMagic()
    return original_import(name, *args, **kwargs)

builtins.__import__ = patched_import

try:
    django.setup()
except Exception as e:
    print(f"警告: Django初始化问题: {e}")
    print("尝试继续运行...")

from django.contrib.auth import get_user_model
from apps.courses.models import Course, Enrollment
from django.db import transaction
from django.utils import timezone

User = get_user_model()

class FastEnrollmentGenerator:
    """快速选课生成器"""
    
    def __init__(self):
        self.batch_size = 10000
        self.target_avg_courses = 7
        
    def generate_enrollments(self):
        """快速生成选课数据"""
        print("🚀 启动快速选课数据生成...")
        
        # 获取所有学生和课程
        students = list(User.objects.filter(user_type='student', is_active=True))
        courses = list(Course.objects.filter(is_active=True, is_published=True))
        
        print(f"📊 加载数据：{len(students)} 名学生，{len(courses)} 门课程")
        
        # 按类型分组课程
        public_courses = [c for c in courses if c.course_type == 'public']
        required_courses = [c for c in courses if c.course_type == 'required']
        elective_courses = [c for c in courses if c.course_type == 'elective']
        professional_courses = [c for c in courses if c.course_type == 'professional']
        
        print(f"📚 课程分类：公共课 {len(public_courses)}，必修课 {len(required_courses)}，选修课 {len(elective_courses)}，专业课 {len(professional_courses)}")
        
        total_enrollments = 0
        
        # 分批处理学生
        for i in range(0, len(students), self.batch_size):
            batch_students = students[i:i + self.batch_size]
            batch_enrollments = []
            
            print(f"\r处理进度: {i+1}-{min(i+self.batch_size, len(students))}/{len(students)} "
                  f"({(i+1)/len(students)*100:.1f}%)", end="")
            
            for student in batch_students:
                # 为每个学生生成选课
                student_enrollments = self._generate_student_courses(
                    student, public_courses, required_courses, 
                    elective_courses, professional_courses
                )
                batch_enrollments.extend(student_enrollments)
            
            # 批量保存
            if batch_enrollments:
                try:
                    with transaction.atomic():
                        Enrollment.objects.bulk_create(batch_enrollments, ignore_conflicts=True)
                    total_enrollments += len(batch_enrollments)
                except Exception as e:
                    print(f"\n⚠️ 批量保存失败: {e}")
                    continue
        
        print(f"\n✅ 选课数据生成完成：总计 {total_enrollments:,} 条记录")
        return total_enrollments
    
    def _generate_student_courses(self, student, public_courses, required_courses, 
                                 elective_courses, professional_courses):
        """为单个学生生成选课"""
        enrollments = []
        
        # 1. 必选公共课（每个学生都选部分公共课）
        selected_public = random.sample(public_courses, min(3, len(public_courses)))
        for course in selected_public:
            enrollments.append(self._create_enrollment(student, course))
        
        # 2. 必修课（随机选择）
        num_required = random.randint(2, min(4, len(required_courses)))
        selected_required = random.sample(required_courses, num_required)
        for course in selected_required:
            enrollments.append(self._create_enrollment(student, course))
        
        # 3. 选修课和专业课（补充到目标数量）
        remaining = self.target_avg_courses - len(enrollments)
        if remaining > 0:
            all_remaining = elective_courses + professional_courses
            if all_remaining:
                additional = random.sample(all_remaining, min(remaining, len(all_remaining)))
                for course in additional:
                    enrollments.append(self._create_enrollment(student, course))
        
        return enrollments
    
    def _create_enrollment(self, student, course):
        """创建选课记录"""
        return Enrollment(
            student=student,
            course=course,
            status='enrolled',
            enrolled_at=timezone.now(),
            is_active=True
        )

def main():
    """主函数"""
    print("🚀 快速选课数据生成器启动")
    print("=" * 50)
    
    start_time = datetime.now()
    generator = FastEnrollmentGenerator()
    
    try:
        total_created = generator.generate_enrollments()
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        print("\n" + "=" * 50)
        print("🎉 快速选课数据生成完成！")
        print(f"⏱️ 总用时: {duration}")
        print(f"📝 生成选课记录: {total_created:,} 条")
        print(f"📊 当前选课总数: {Enrollment.objects.count():,} 条")
        
    except Exception as e:
        print(f"❌ 生成过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()