#!/usr/bin/env python3
"""
导入排课结果到数据库脚本
用于将排课算法生成的结果导入到数据库中
"""

import os
import sys
import json
import django
from pathlib import Path

# 添加项目路径（基于脚本位置，提升跨平台兼容性）
BASE_DIR = Path(__file__).resolve().parent  # app/backend
sys.path.insert(0, str(BASE_DIR))

# 配置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
django.setup()

from django.db import transaction
from apps.schedules.models import Schedule, TimeSlot
from apps.courses.models import Course
from apps.classrooms.models import Classroom
from apps.users.models import User


def parse_week_range(week_range_str):
    """解析周次范围字符串"""
    # 简单处理，返回默认值
    return "1-16"


def import_scheduling_results(json_file_path):
    """导入排课结果到数据库"""
    print(f"📥 开始导入排课结果从 {json_file_path}...")
    
    try:
        # 读取排课结果
        with open(json_file_path, 'r', encoding='utf-8') as f:
            scheduling_result = json.load(f)
        
        # 获取已分配的槽位
        assigned_slots = scheduling_result.get('assigned_slots', {})
        
        if not assigned_slots:
            print("❌ 没有找到排课数据")
            return False
        
        print(f"📊 找到 {len(assigned_slots)} 个课程的排课数据")
        
        # 开始事务
        with transaction.atomic():
            # 先删除现有的2024-1学期排课数据
            deleted_count = Schedule.objects.filter(
                semester="2024-1",
                academic_year="2023-2024"
            ).delete()[0]
            
            if deleted_count > 0:
                print(f"🗑️  删除了 {deleted_count} 条旧的排课数据")
            
            # 导入新的排课数据
            created_count = 0
            conflict_count = 0
            
            # 跟踪教师时间安排以避免冲突
            teacher_schedule_map = {}
            # 跟踪教室时间安排以避免冲突
            classroom_schedule_map = {}
            
            for constraint_key, slots in assigned_slots.items():
                # 解析约束键 (格式: "课程代码-教师用户名")
                try:
                    course_code, teacher_username = constraint_key.split('-')
                except ValueError:
                    print(f"⚠️  跳过无效约束键: {constraint_key}")
                    continue
                
                # 查找课程
                try:
                    course = Course.objects.get(
                        code=course_code,
                        semester="2024-1",
                        academic_year="2023-2024"
                    )
                except Course.DoesNotExist:
                    print(f"⚠️  未找到课程: {course_code}")
                    continue
                
                # 查找教师
                try:
                    teacher = User.objects.get(
                        username=teacher_username,
                        user_type="teacher"
                    )
                except User.DoesNotExist:
                    print(f"⚠️  未找到教师: {teacher_username}")
                    continue
                
                # 为每个时间槽创建排课记录
                for slot in slots:
                    day_of_week = slot['day_of_week']
                    time_slot_name = slot['time_slot']
                    classroom_name = slot['classroom']
                    
                    # 查找时间段
                    try:
                        time_slot = TimeSlot.objects.get(name=time_slot_name)
                    except TimeSlot.DoesNotExist:
                        print(f"⚠️  未找到时间段: {time_slot_name}")
                        continue
                    
                    # 查找教室 (格式: "楼名-房间号")
                    try:
                        building_code, room_number = classroom_name.split('-', 1)
                        classroom = Classroom.objects.get(
                            building__code=building_code,
                            room_number=room_number
                        )
                    except (ValueError, Classroom.DoesNotExist):
                        print(f"⚠️  未找到教室: {classroom_name}")
                        continue
                    
                    # 检查教师时间冲突
                    teacher_key = (teacher.id, day_of_week, time_slot.id)
                    if teacher_key in teacher_schedule_map:
                        print(f"⚠️  教师时间冲突: {teacher_username} 在星期{day_of_week} {time_slot_name} 已有安排")
                        conflict_count += 1
                        continue
                    
                    # 检查教室时间冲突
                    classroom_key = (classroom.id, day_of_week, time_slot.id)
                    if classroom_key in classroom_schedule_map:
                        print(f"⚠️  教室时间冲突: {classroom_name} 在星期{day_of_week} {time_slot_name} 已有安排")
                        conflict_count += 1
                        continue
                    
                    # 创建排课记录
                    try:
                        Schedule.objects.create(
                            course=course,
                            teacher=teacher,
                            classroom=classroom,
                            time_slot=time_slot,
                            day_of_week=day_of_week,
                            week_range=parse_week_range("1-16"),  # 默认周次范围
                            semester="2024-1",
                            academic_year="2023-2024",
                            status="active"
                        )
                        
                        # 记录安排以避免冲突
                        teacher_schedule_map[teacher_key] = True
                        classroom_schedule_map[classroom_key] = True
                        
                        created_count += 1
                    except Exception as e:
                        print(f"⚠️  创建排课记录失败: {e}")
                        conflict_count += 1
                        continue
            
            print(f"✅ 成功导入 {created_count} 条排课记录")
            if conflict_count > 0:
                print(f"⚠️  跳过了 {conflict_count} 条有冲突的记录")
            return True
            
    except FileNotFoundError:
        print(f"❌ 文件未找到: {json_file_path}")
        return False
    except Exception as e:
        print(f"❌ 导入排课结果时发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("💾 开始导入排课结果到数据库...")
    print("=" * 50)
    
    # 默认使用贪心算法的结果
    json_file = "scheduling_result_greedy.json"
    
    # 如果提供了参数，则使用指定的文件
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    
    success = import_scheduling_results(json_file)
    
    if success:
        print()
        print("=" * 50)
        print("🎉 排课结果导入完成!")
        
        # 显示统计信息
        total_schedules = Schedule.objects.filter(
            semester="2024-1",
            academic_year="2023-2024"
        ).count()
        
        print(f"📊 数据库中的排课记录总数: {total_schedules}")
        
    else:
        print()
        print("=" * 50)
        print("❌ 排课结果导入失败!")
        sys.exit(1)


if __name__ == "__main__":
    main()