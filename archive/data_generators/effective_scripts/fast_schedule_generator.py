#!/usr/bin/env python
"""
快速排课数据生成器 - 简化版本，专注于生成大量有效的排课记录
"""

# 设置环境变量，禁用有问题的模块
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'course_management.settings'
os.environ['DISABLE_MAGIC'] = '1'  # 禁用magic模块

import sys
import django
import random
import time
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
from apps.courses.models import Course
from apps.classrooms.models import Classroom
from apps.schedules.models import Schedule, TimeSlot
from django.db import transaction
from django.utils import timezone

User = get_user_model()

class FastScheduleGenerator:
    """快速排课生成器"""
    
    def __init__(self):
        self.batch_size = 2000
        self.target_schedules = 100000  # 目标排课数量
        
    def generate_schedules(self):
        """快速生成排课数据"""
        print("📅 快速排课数据生成器启动")
        print("=" * 50)
        
        # 加载数据
        print("📊 加载基础数据...")
        courses = list(Course.objects.filter(is_active=True, is_published=True))
        teachers = list(User.objects.filter(user_type='teacher', is_active=True))
        classrooms = list(Classroom.objects.filter(is_available=True, is_active=True))
        time_slots = list(TimeSlot.objects.filter(is_active=True))
        
        print(f"✅ 数据加载完成：")
        print(f"   课程: {len(courses):,} 门")
        print(f"   教师: {len(teachers):,} 名")
        print(f"   教室: {len(classrooms):,} 间")
        print(f"   时间段: {len(time_slots)} 个")
        
        if not courses or not teachers or not classrooms or not time_slots:
            print("❌ 基础数据不足，无法生成排课")
            return 0
        
        # 工作日（周一到周五）
        weekdays = [1, 2, 3, 4, 5]
        
        created_count = 0
        start_time = time.time()
        
        print(f"📅 开始生成 {self.target_schedules:,} 条排课记录...")
        
        for batch_start in range(0, self.target_schedules, self.batch_size):
            batch_end = min(batch_start + self.batch_size, self.target_schedules)
            batch_schedules = []
            
            for i in range(batch_start, batch_end):
                # 随机选择组合
                course = random.choice(courses)
                teacher = random.choice(teachers)
                classroom = random.choice(classrooms)
                day = random.choice(weekdays)
                time_slot = random.choice(time_slots)
                
                # 简单的容量检查
                if classroom.capacity < course.max_students * 0.5:  # 允许50%的容量利用率
                    continue
                
                # 创建排课记录
                schedule = Schedule(
                    course=course,
                    teacher=teacher,
                    classroom=classroom,
                    day_of_week=day,
                    time_slot=time_slot,
                    week_range="1-16周",
                    semester=course.semester,
                    academic_year=course.academic_year,
                    status='active',
                    notes=f"快速生成排课记录"
                )
                batch_schedules.append(schedule)
            
            # 批量保存
            if batch_schedules:
                try:
                    with transaction.atomic():
                        Schedule.objects.bulk_create(batch_schedules, ignore_conflicts=True)
                    created_count += len(batch_schedules)
                    
                    # 显示进度
                    if batch_start % (self.batch_size * 5) == 0:
                        elapsed_time = time.time() - start_time
                        speed = created_count / elapsed_time if elapsed_time > 0 else 0
                        progress = (created_count / self.target_schedules) * 100
                        print(f"   进度: {progress:.1f}% ({created_count:,}/{self.target_schedules:,}) "
                              f"速度: {speed:.0f} 条/秒")
                
                except Exception as e:
                    print(f"   批量保存失败: {e}")
                    continue
        
        elapsed_time = time.time() - start_time
        print(f"\n✅ 排课生成完成: {created_count:,} 条，耗时 {elapsed_time:.2f} 秒")
        
        return created_count

def main():
    """主函数"""
    print("📅 快速排课数据生成器")
    
    # 检查当前排课数量
    current_schedules = Schedule.objects.count()
    print(f"📊 当前排课记录: {current_schedules:,} 条")
    
    generator = FastScheduleGenerator()
    
    try:
        start_time = time.time()
        created_count = generator.generate_schedules()
        total_time = time.time() - start_time
        
        print("\n" + "=" * 50)
        print("🎉 快速排课数据生成完成！")
        print(f"⏱️  总用时: {total_time:.2f} 秒")
        print(f"📅 新增排课: {created_count:,} 条")
        print(f"📊 排课总数: {Schedule.objects.count():,} 条")
        
        if created_count > 0:
            print(f"🚀 生成速度: {created_count/total_time:.0f} 条/秒")
            print("\n📋 下一步：运行选课数据生成器")
            print("   python fast_enrollment_generator.py")
        
    except Exception as e:
        print(f"❌ 生成过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()