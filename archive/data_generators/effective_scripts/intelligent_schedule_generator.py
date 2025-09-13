#!/usr/bin/env python
"""
智能排课数据生成器 - 基于排课算法约束管理机制的排课方案生成
严格遵循硬约束和软约束，生成高质量的排课数据
"""

# 设置环境变量，禁用有问题的模块
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'course_management.settings'
os.environ['DISABLE_MAGIC'] = '1'  # 禁用magic模块

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
from apps.classrooms.models import Building, Classroom
from apps.schedules.models import Schedule, TimeSlot
from django.db import transaction
from django.utils import timezone

User = get_user_model()
fake = Faker('zh_CN')

@dataclass
class ScheduleGenerationConfig:
    """排课生成配置"""
    target_schedules: int = 180000
    batch_size: int = 2000
    
    # 约束参数（参考排课算法）
    classroom_utilization_rate: float = 0.75  # 教室利用率目标
    teacher_max_weekly_hours: int = 20  # 教师最大周学时
    teacher_max_daily_hours: int = 8   # 教师最大日学时
    max_consecutive_classes: int = 3   # 最大连续课程数
    
    # 时间分布权重（参考软约束）
    time_preference_weights: Dict[str, float] = None
    
    def __post_init__(self):
        if self.time_preference_weights is None:
            self.time_preference_weights = {
                'morning': 0.4,    # 上午时段权重
                'afternoon': 0.45, # 下午时段权重
                'evening': 0.15    # 晚上时段权重
            }

class ConstraintManager:
    """约束管理器 - 实现排课算法的硬约束和软约束检查"""
    
    def __init__(self):
        # 已分配的排课记录（用于冲突检查）
        self.teacher_schedules = defaultdict(set)  # teacher_id -> set of (day, time_slot)
        self.classroom_schedules = defaultdict(set)  # classroom_id -> set of (day, time_slot)
        self.teacher_weekly_hours = defaultdict(int)  # teacher_id -> weekly_hours
        self.teacher_daily_hours = defaultdict(lambda: defaultdict(int))  # teacher_id -> day -> hours
        
    def check_hard_constraints(self, course: Course, teacher: User, classroom: Classroom,
                              day: int, time_slot: TimeSlot) -> Tuple[bool, List[str]]:
        """检查硬约束（必须满足）"""
        violations = []
        
        # 1. 教师时间冲突检查
        teacher_key = (day, time_slot.id)
        if teacher_key in self.teacher_schedules[teacher.id]:
            violations.append(f"教师{teacher.get_full_name()}在周{day}第{time_slot.order}节已有课程")
        
        # 2. 教室时间冲突检查
        classroom_key = (day, time_slot.id)
        if classroom_key in self.classroom_schedules[classroom.id]:
            violations.append(f"教室{classroom.full_name}在周{day}第{time_slot.order}节已被占用")
        
        # 3. 教室容量检查
        if classroom.capacity < course.max_students:
            violations.append(f"教室容量{classroom.capacity}小于课程需求{course.max_students}")
        
        # 4. 教室类型匹配检查（简化版）
        if course.name.__contains__('实验') and classroom.room_type not in ['lab', 'computer']:
            violations.append(f"实验课程需要实验室或机房")
        elif course.name.__contains__('计算机') and classroom.room_type != 'computer':
            if classroom.room_type not in ['multimedia', 'lab']:
                violations.append(f"计算机课程需要机房或多媒体教室")
        
        # 5. 教师工作量检查
        course_hours = course.hours / 16  # 每周学时 = 总学时 / 16周
        if self.teacher_weekly_hours[teacher.id] + course_hours > 20:
            violations.append(f"教师{teacher.get_full_name()}周学时超限")
        
        if self.teacher_daily_hours[teacher.id][day] + course_hours > 8:
            violations.append(f"教师{teacher.get_full_name()}日学时超限")
        
        return len(violations) == 0, violations
    
    def calculate_soft_score(self, course: Course, teacher: User, classroom: Classroom,
                           day: int, time_slot: TimeSlot) -> float:
        """计算软约束评分（0-100分，越高越好）"""
        score = 0.0
        
        # 1. 时间偏好评分（25%权重）
        period_score = self._get_time_preference_score(time_slot)
        score += period_score * 0.25
        
        # 2. 工作量均衡评分（20%权重）
        workload_score = self._get_workload_balance_score(teacher, course)
        score += workload_score * 0.20
        
        # 3. 教室利用率评分（15%权重）
        utilization_score = self._get_classroom_utilization_score(classroom, course)
        score += utilization_score * 0.15
        
        # 4. 时间分布评分（15%权重）
        distribution_score = self._get_time_distribution_score(teacher, day, time_slot)
        score += distribution_score * 0.15
        
        # 5. 每日均衡评分（10%权重）
        daily_balance_score = self._get_daily_balance_score(teacher, day)
        score += daily_balance_score * 0.10
        
        # 6. 连续性惩罚评分（10%权重）
        continuity_score = self._get_continuity_score(teacher, day, time_slot)
        score += continuity_score * 0.10
        
        # 7. 教室类型匹配评分（5%权重）
        room_match_score = self._get_room_type_match_score(course, classroom)
        score += room_match_score * 0.05
        
        return score
    
    def add_assignment(self, course: Course, teacher: User, classroom: Classroom,
                      day: int, time_slot: TimeSlot):
        """添加排课分配（更新约束状态）"""
        self.teacher_schedules[teacher.id].add((day, time_slot.id))
        self.classroom_schedules[classroom.id].add((day, time_slot.id))
        
        course_weekly_hours = course.hours / 16
        self.teacher_weekly_hours[teacher.id] += course_weekly_hours
        self.teacher_daily_hours[teacher.id][day] += course_weekly_hours
    
    def _get_time_preference_score(self, time_slot: TimeSlot) -> float:
        """获取时间偏好评分"""
        hour = time_slot.start_time.hour
        if hour < 12:  # 上午
            return 85.0
        elif hour < 18:  # 下午
            return 90.0
        else:  # 晚上
            return 60.0
    
    def _get_workload_balance_score(self, teacher: User, course: Course) -> float:
        """获取工作量均衡评分"""
        current_hours = self.teacher_weekly_hours[teacher.id]
        course_hours = course.hours / 16
        new_total = current_hours + course_hours
        
        # 理想工作量为12-16学时
        if 12 <= new_total <= 16:
            return 100.0
        elif new_total < 12:
            return 80.0 + (new_total / 12) * 20
        else:
            return max(0, 100 - (new_total - 16) * 10)
    
    def _get_classroom_utilization_score(self, classroom: Classroom, course: Course) -> float:
        """获取教室利用率评分"""
        utilization = course.max_students / classroom.capacity
        if 0.7 <= utilization <= 0.9:
            return 100.0
        elif utilization < 0.7:
            return utilization * 100 / 0.7
        else:
            return max(0, 100 - (utilization - 0.9) * 200)
    
    def _get_time_distribution_score(self, teacher: User, day: int, time_slot: TimeSlot) -> float:
        """获取时间分布评分"""
        daily_count = len([k for k in self.teacher_schedules[teacher.id] if k[0] == day])
        if daily_count <= 2:
            return 100.0
        else:
            return max(0, 100 - (daily_count - 2) * 25)
    
    def _get_daily_balance_score(self, teacher: User, day: int) -> float:
        """获取每日均衡评分"""
        daily_hours = self.teacher_daily_hours[teacher.id][day]
        if daily_hours <= 4:
            return 100.0
        else:
            return max(0, 100 - (daily_hours - 4) * 20)
    
    def _get_continuity_score(self, teacher: User, day: int, time_slot: TimeSlot) -> float:
        """获取连续性评分"""
        # 检查前后时段是否有课
        adjacent_slots = 0
        for existing_day, existing_slot_id in self.teacher_schedules[teacher.id]:
            if existing_day == day:
                if abs(existing_slot_id - time_slot.id) == 1:
                    adjacent_slots += 1
        
        if adjacent_slots == 0:
            return 100.0
        elif adjacent_slots == 1:
            return 80.0
        else:
            return max(0, 100 - adjacent_slots * 30)
    
    def _get_room_type_match_score(self, course: Course, classroom: Classroom) -> float:
        """获取教室类型匹配评分"""
        course_name = course.name.lower()
        
        if '实验' in course_name:
            return 100.0 if classroom.room_type in ['lab', 'computer'] else 50.0
        elif '计算机' in course_name or '编程' in course_name:
            return 100.0 if classroom.room_type == 'computer' else 70.0
        elif '设计' in course_name or '艺术' in course_name:
            return 100.0 if classroom.room_type in ['studio', 'multimedia'] else 60.0
        else:
            return 100.0 if classroom.room_type in ['lecture', 'multimedia'] else 80.0

class IntelligentScheduleGenerator:
    """智能排课生成器"""
    
    def __init__(self, config: ScheduleGenerationConfig):
        self.config = config
        self.constraint_manager = ConstraintManager()
        
        # 缓存数据
        self.courses = []
        self.teachers = []
        self.classrooms = []
        self.time_slots = []
        
    def load_data(self):
        """加载基础数据"""
        print("📊 加载基础数据...")
        
        # 加载课程（包含教师关联）
        self.courses = list(Course.objects.filter(is_active=True, is_published=True)
                           .prefetch_related('teachers'))
        
        # 加载教师
        self.teachers = list(User.objects.filter(user_type='teacher', is_active=True))
        
        # 加载教室
        self.classrooms = list(Classroom.objects.filter(is_available=True, is_active=True)
                              .select_related('building'))
        
        # 加载时间段
        self.time_slots = list(TimeSlot.objects.filter(is_active=True).order_by('order'))
        
        print(f"✅ 数据加载完成：")
        print(f"   课程: {len(self.courses)} 门")
        print(f"   教师: {len(self.teachers)} 名")
        print(f"   教室: {len(self.classrooms)} 间")
        print(f"   时间段: {len(self.time_slots)} 个")
    
    def generate_schedules(self) -> List[Dict]:
        """生成排课数据"""
        print(f"📅 开始生成排课数据...")
        
        schedules = []
        failed_assignments = 0
        max_attempts = self.config.target_schedules * 2  # 允许失败
        
        # 工作日（周一到周五）
        weekdays = [1, 2, 3, 4, 5]
        
        for attempt in range(max_attempts):
            if len(schedules) >= self.config.target_schedules:
                break
            
            if attempt % 1000 == 0:
                print(f"\r生成进度: {len(schedules)}/{self.config.target_schedules} "
                      f"({len(schedules)/self.config.target_schedules*100:.1f}%) "
                      f"失败: {failed_assignments}", end="")
            
            # 随机选择课程
            course = random.choice(self.courses)
            
            # 选择该课程的教师
            course_teachers = list(course.teachers.all())
            if not course_teachers:
                # 如果课程没有分配教师，随机分配一个
                teacher = random.choice(self.teachers)
            else:
                teacher = random.choice(course_teachers)
            
            # 随机选择时间
            day = random.choice(weekdays)
            time_slot = random.choice(self.time_slots)
            
            # 选择最佳教室
            best_classroom = self._select_best_classroom(course, teacher, day, time_slot)
            
            if best_classroom is None:
                failed_assignments += 1
                continue
            
            # 检查硬约束
            is_valid, violations = self.constraint_manager.check_hard_constraints(
                course, teacher, best_classroom, day, time_slot
            )
            
            if not is_valid:
                failed_assignments += 1
                continue
            
            # 计算软约束评分
            soft_score = self.constraint_manager.calculate_soft_score(
                course, teacher, best_classroom, day, time_slot
            )
            
            # 接受阈值（可以调整来控制质量）
            acceptance_threshold = 60.0
            if soft_score < acceptance_threshold:
                failed_assignments += 1
                continue
            
            # 创建排课记录
            schedule = {
                'course': course,
                'teacher': teacher,
                'classroom': best_classroom,
                'day_of_week': day,
                'time_slot': time_slot,
                'semester': course.semester,
                'academic_year': course.academic_year,
                'soft_score': soft_score
            }
            
            schedules.append(schedule)
            
            # 更新约束状态
            self.constraint_manager.add_assignment(course, teacher, best_classroom, day, time_slot)
        
        print(f"\n✅ 排课生成完成：成功 {len(schedules)} 条，失败 {failed_assignments} 条")
        return schedules
    
    def _select_best_classroom(self, course: Course, teacher: User, 
                              day: int, time_slot: TimeSlot) -> Optional[Classroom]:
        """为课程选择最佳教室"""
        candidate_classrooms = []
        
        for classroom in self.classrooms:
            # 快速硬约束检查
            if classroom.capacity < course.max_students:
                continue
            
            classroom_key = (day, time_slot.id)
            if classroom_key in self.constraint_manager.classroom_schedules[classroom.id]:
                continue
            
            # 计算适配分数
            match_score = self._calculate_classroom_match_score(course, classroom)
            candidate_classrooms.append((classroom, match_score))
        
        if not candidate_classrooms:
            return None
        
        # 选择评分最高的教室
        candidate_classrooms.sort(key=lambda x: x[1], reverse=True)
        return candidate_classrooms[0][0]
    
    def _calculate_classroom_match_score(self, course: Course, classroom: Classroom) -> float:
        """计算教室匹配分数"""
        score = 0.0
        
        # 容量匹配（40%权重）
        utilization = course.max_students / classroom.capacity
        if 0.7 <= utilization <= 0.9:
            capacity_score = 100.0
        elif utilization < 0.7:
            capacity_score = utilization * 100 / 0.7
        else:
            capacity_score = max(0, 100 - (utilization - 0.9) * 200)
        
        score += capacity_score * 0.4
        
        # 类型匹配（30%权重）
        type_score = self.constraint_manager._get_room_type_match_score(course, classroom)
        score += type_score * 0.3
        
        # 设备匹配（20%权重）
        equipment_score = self._get_equipment_match_score(course, classroom)
        score += equipment_score * 0.2
        
        # 位置便利性（10%权重）
        location_score = 80.0  # 简化处理
        score += location_score * 0.1
        
        return score
    
    def _get_equipment_match_score(self, course: Course, classroom: Classroom) -> float:
        """获取设备匹配评分"""
        required_equipment = set()
        
        course_name = course.name.lower()
        if '计算机' in course_name or '编程' in course_name:
            required_equipment.update(['电脑', '网络'])
        if '多媒体' in course_name or '视频' in course_name:
            required_equipment.update(['投影仪', '音响'])
        if '实验' in course_name:
            required_equipment.update(['实验台', '通风系统'])
        
        if not required_equipment:
            return 100.0  # 无特殊要求
        
        available_equipment = set(classroom.equipment.keys())
        match_count = len(required_equipment & available_equipment)
        
        return (match_count / len(required_equipment)) * 100

class ScheduleDatabase:
    """排课数据库操作管理器"""
    
    def __init__(self, config: ScheduleGenerationConfig):
        self.config = config
    
    def save_schedules(self, schedules: List[Dict]) -> int:
        """保存排课数据到数据库"""
        print("💾 保存排课数据到数据库...")
        
        created_count = 0
        batch = []
        total_schedules = len(schedules)
        
        for i, schedule_data in enumerate(schedules):
            if i % 200 == 0:
                print(f"\r保存排课进度: {i+1}/{total_schedules} "
                      f"({(i+1)/total_schedules*100:.1f}%)", end="")
            
            try:
                # 检查是否已存在相同的排课
                existing = Schedule.objects.filter(
                    course=schedule_data['course'],
                    teacher=schedule_data['teacher'],
                    classroom=schedule_data['classroom'],
                    day_of_week=schedule_data['day_of_week'],
                    time_slot=schedule_data['time_slot'],
                    semester=schedule_data['semester']
                ).exists()
                
                if existing:
                    continue
                
                schedule = Schedule(
                    course=schedule_data['course'],
                    teacher=schedule_data['teacher'],
                    classroom=schedule_data['classroom'],
                    day_of_week=schedule_data['day_of_week'],
                    time_slot=schedule_data['time_slot'],
                    week_range="1-16周",  # 默认周次范围
                    semester=schedule_data['semester'],
                    academic_year=schedule_data['academic_year'],
                    status='active',  # 默认状态
                    notes=f"软约束得分: {schedule_data['soft_score']:.1f}"
                )
                
                batch.append(schedule)
                created_count += 1
                
                # 批量保存
                if len(batch) >= self.config.batch_size:
                    Schedule.objects.bulk_create(batch, ignore_conflicts=True)
                    batch = []
                    
            except Exception as e:
                print(f"\n⚠️  跳过排课记录: {e}")
                continue
        
        # 保存剩余记录
        if batch:
            Schedule.objects.bulk_create(batch, ignore_conflicts=True)
        
        print(f"\n✅ 排课保存完成：新增 {created_count} 条记录")
        return created_count

def main():
    """主函数"""
    print("📅 智能排课数据生成器启动")
    print("=" * 60)
    
    # 检查当前数据状况
    current_courses = Course.objects.filter(is_active=True).count()
    current_teachers = User.objects.filter(user_type='teacher', is_active=True).count()
    current_classrooms = Classroom.objects.filter(is_available=True).count()
    current_schedules = Schedule.objects.count()
    current_time_slots = TimeSlot.objects.filter(is_active=True).count()
    
    print(f"📊 当前数据状况：")
    print(f"   活跃课程: {current_courses:,}")
    print(f"   活跃教师: {current_teachers:,}")
    print(f"   可用教室: {current_classrooms:,}")
    print(f"   现有排课: {current_schedules:,}")
    print(f"   时间段: {current_time_slots:,}")
    print()
    
    if current_courses < 1000:
        print("❌ 错误：课程数量不足，请先运行课程数据生成器")
        return
    
    if current_classrooms < 1000:
        print("❌ 错误：教室数量不足，请先运行教室数据生成器")
        return
    
    if current_time_slots == 0:
        print("❌ 错误：没有时间段数据，请先运行教室数据生成器")
        return
    
    # 初始化配置
    config = ScheduleGenerationConfig()
    generator = IntelligentScheduleGenerator(config)
    db_manager = ScheduleDatabase(config)
    
    start_time = datetime.now()
    
    try:
        # 加载数据
        generator.load_data()
        
        # 生成排课数据
        print("\n📅 开始生成排课数据（基于约束算法）...")
        schedules = generator.generate_schedules()
        
        if not schedules:
            print("❌ 未能生成任何有效的排课数据")
            return
        
        # 保存到数据库
        created_count = db_manager.save_schedules(schedules)
        
        # 计算用时
        end_time = datetime.now()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print("🎉 排课数据生成完成！")
        print(f"⏱️  总用时: {duration}")
        print(f"📅 新增排课: {created_count} 条")
        print(f"📊 排课总数: {Schedule.objects.count()} 条")
        print()
        print("📈 约束满足统计：")
        print(f"   硬约束满足率: 100%（必须满足）")
        print(f"   软约束平均分: {sum(s['soft_score'] for s in schedules)/len(schedules):.1f}")
        print()
        print("📋 下一步：运行选课数据生成器")
        print("   python intelligent_enrollment_generator.py")
        
    except Exception as e:
        print(f"❌ 生成过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()