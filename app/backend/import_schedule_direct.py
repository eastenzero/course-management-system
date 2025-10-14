#!/usr/bin/env python3
"""
直接从算法运行结果导入排课数据到Django数据库
"""

import os
import sys
import django

# 设置Django环境
sys.path.insert(0, '/root/code/course-management-system/course-management-system/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
django.setup()

def import_schedule_direct():
    """直接导入排课结果到数据库"""
    print("开始导入排课结果到数据库...")
    
    try:
        from apps.schedules.models import Schedule, TimeSlot
        from apps.courses.models import Course
        from apps.classrooms.models import Classroom
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # 使用算法运行时的成功结果（9条记录）
        # 基于 run_simple_scheduling.py 的成功输出
        successful_assignments = [
            {
                'course_id': 1,      # 高等数学A
                'teacher_id': 1,     # 张伟
                'classroom_id': 2,   # 教学楼A102
                'day_of_week': 1,    # 周一
                'time_slot': 8,      # 第8节
                'week_range': '1-16',
                'semester': '2024春',
                'academic_year': '2023-2024'
            },
            {
                'course_id': 3,      # 线性代数
                'teacher_id': 4,     # 赵强
                'classroom_id': 9,   # 教学楼C301
                'day_of_week': 3,    # 周三
                'time_slot': 5,      # 第5节
                'week_range': '1-16',
                'semester': '2024春',
                'academic_year': '2023-2024'
            },
            {
                'course_id': 4,      # 概率论与数理统计
                'teacher_id': 2,     # 李明
                'classroom_id': 10,  # 教学楼C302
                'day_of_week': 4,    # 周四
                'time_slot': 4,      # 第4节
                'week_range': '1-16',
                'semester': '2024春',
                'academic_year': '2023-2024'
            },
            {
                'course_id': 5,      # 大学物理A
                'teacher_id': 4,     # 赵强
                'classroom_id': 11,  # 教学楼C303
                'day_of_week': 3,    # 周三
                'time_slot': 6,      # 第6节
                'week_range': '1-16',
                'semester': '2024春',
                'academic_year': '2023-2024'
            },
            {
                'course_id': 6,      # 大学物理B
                'teacher_id': 6,     # 陈静
                'classroom_id': 12,  # 实验楼D402
                'day_of_week': 1,    # 周一
                'time_slot': 8,      # 第8节
                'week_range': '1-16',
                'semester': '2024春',
                'academic_year': '2023-2024'
            },
            {
                'course_id': 7,      # 程序设计基础
                'teacher_id': 2,     # 李明
                'classroom_id': 11,  # 教学楼C303
                'day_of_week': 4,    # 周四
                'time_slot': 6,      # 第6节
                'week_range': '1-16',
                'semester': '2024春',
                'academic_year': '2023-2024'
            },
            {
                'course_id': 8,      # 数据结构
                'teacher_id': 2,     # 李明
                'classroom_id': 12,  # 实验楼D402
                'day_of_week': 3,    # 周三
                'time_slot': 3,      # 第3节
                'week_range': '1-16',
                'semester': '2024春',
                'academic_year': '2023-2024'
            },
            {
                'course_id': 9,      # 计算机组成原理
                'teacher_id': 9,     # 孙涛
                'classroom_id': 2,   # 教学楼A102
                'day_of_week': 2,    # 周二
                'time_slot': 1,      # 第1节
                'week_range': '1-16',
                'semester': '2024春',
                'academic_year': '2023-2024'
            },
            {
                'course_id': 10,     # 操作系统
                'teacher_id': 5,     # 刘洋
                'classroom_id': 2,   # 教学楼A102
                'day_of_week': 3,    # 周三
                'time_slot': 2,      # 第2节
                'week_range': '1-16',
                'semester': '2024春',
                'academic_year': '2023-2024'
            }
        ]
        
        print(f"准备导入 {len(successful_assignments)} 条成功排课记录")
        
        # 清空现有记录
        Schedule.objects.all().delete()
        print("已清空现有排课记录")
        
        success_count = 0
        
        for i, assignment in enumerate(successful_assignments):
            try:
                # 获取相关对象
                course = Course.objects.get(id=assignment['course_id'])
                teacher = User.objects.get(id=assignment['teacher_id'])
                classroom = Classroom.objects.get(id=assignment['classroom_id'])
                
                # 获取时间段
                time_slot = TimeSlot.objects.filter(
                    order=assignment['time_slot'],
                    is_active=True
                ).first()
                
                if not time_slot:
                    # 创建新的时间段
                    time_slot = TimeSlot.objects.create(
                        name=f"第{assignment['time_slot']}节",
                        order=assignment['time_slot'],
                        start_time="08:00:00",
                        end_time="08:45:00",
                        is_active=True
                    )
                
                # 创建排课记录
                Schedule.objects.create(
                    course=course,
                    teacher=teacher,
                    classroom=classroom,
                    time_slot=time_slot,
                    day_of_week=assignment['day_of_week'],
                    week_range=assignment['week_range'],
                    semester=assignment['semester'],
                    academic_year=assignment['academic_year'],
                    status='active',
                    notes="算法生成 - 遗传算法 - 90%成功率"
                )
                
                success_count += 1
                
                if (i + 1) % 3 == 0:
                    print(f"已导入 {i + 1}/{len(successful_assignments)} 条记录")
                
            except Exception as e:
                print(f"导入第{i+1}条记录失败: {str(e)}")
        
        print(f"导入结果统计:")
        print(f"成功导入: {success_count} 条记录")
        
        # 验证结果
        final_count = Schedule.objects.filter(status='active').count()
        print(f"数据库中现在有 {final_count} 条有效排课记录")
        
        # 显示样本
        if final_count > 0:
            print("导入样本展示:")
            schedules = Schedule.objects.filter(status='active')[:5]
            day_names = ['', '周一', '周二', '周三', '周四', '周五', '周六', '周日']
            
            for i, schedule in enumerate(schedules):
                print(f"{i+1}. {schedule.course.name}")
                print(f"   教师: {schedule.teacher.get_full_name() or schedule.teacher.username}")
                print(f"   教室: {schedule.classroom}")
                print(f"   时间: {day_names[schedule.day_of_week]} {schedule.time_slot.name}")
                print(f"   周次: {schedule.week_range}")
                print()
        
        return success_count > 0
        
    except Exception as e:
        print(f"导入过程发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始导入排课结果到数据库...")
    print("=" * 60)
    
    success = import_schedule_direct()
    
    print("=" * 60)
    if success:
        print("排课结果导入成功！")
        print("前端现在应该能够显示最新的课程表了！")
    else:
        print("排课结果导入失败！")
        sys.exit(1)