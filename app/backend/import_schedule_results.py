#!/usr/bin/env python3
"""
将算法生成的排课结果导入到Django数据库中
"""

import os
import sys
import django
import json
from datetime import datetime

# 设置Django环境
sys.path.insert(0, '/root/code/course-management-system/course-management-system/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
django.setup()

def import_schedule_results():
    """导入排课结果到数据库"""
    print("🚀 开始导入排课结果到数据库...")
    
    try:
        from apps.schedules.models import Schedule, TimeSlot
        from apps.courses.models import Course
        from apps.classrooms.models import Classroom
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # 加载算法生成的排课结果
        try:
            with open('/root/code/course-management-system/course-management-system/algorithms/genetic_scheduling_result.json', 'r', encoding='utf-8') as f:
                result_data = json.load(f)
        except FileNotFoundError:
            print("❌ 未找到算法排课结果文件")
            return False
        
        # 检查是否已经有排课记录
        existing_count = Schedule.objects.filter(status='active').count()
        if existing_count > 0:
            print(f"⚠️  发现已有 {existing_count} 条排课记录")
            response = input("是否清空现有记录并重新导入？(y/n): ")
            if response.lower() == 'y':
                Schedule.objects.all().delete()
                print("✅ 已清空现有排课记录")
            else:
                print("❌ 取消导入操作")
                return False
        
        assignments = result_data.get('assignments', [])
        if not assignments:
            print("❌ 排课结果中没有分配数据")
            return False
        
        print(f"📊 准备导入 {len(assignments)} 条排课记录")
        
        success_count = 0
        failed_count = 0
        failed_reasons = []
        
        for i, assignment in enumerate(assignments):
            try:
                # 获取相关对象
                course = Course.objects.get(id=assignment['course_id'])
                teacher = User.objects.get(id=assignment['teacher_id'])
                classroom = Classroom.objects.get(id=assignment['classroom_id'])
                
                # 查找合适的时间段
                time_slot = TimeSlot.objects.filter(
                    order=assignment['time_slot'],
                    is_active=True
                ).first()
                
                if not time_slot:
                    # 如果没有找到对应的时间段，创建一个新的
                    time_slot = TimeSlot.objects.create(
                        name=f"第{assignment['time_slot']}节",
                        order=assignment['time_slot'],
                        start_time=f"{8 + (assignment['time_slot']-1)//2:02d}:{30 if (assignment['time_slot']-1)%2 else 0:02d}:00",
                        end_time=f"{8 + assignment['time_slot']//2:02d}:{30 if assignment['time_slot']%2 else 0:02d}:00",
                        is_active=True
                    )
                
                # 创建排课记录
                schedule = Schedule.objects.create(
                    course=course,
                    teacher=teacher,
                    classroom=classroom,
                    time_slot=time_slot,
                    day_of_week=assignment['day_of_week'],
                    week_range=assignment.get('week_range', '1-16'),
                    semester=assignment.get('semester', '2024春'),
                    academic_year=assignment.get('academic_year', '2023-2024'),
                    status='active',
                    notes=f"算法生成 - 遗传算法 - 适应度:{result_data.get('fitness_score', 0):.2f}"
                )
                
                success_count += 1
                
                if (i + 1) % 10 == 0:
                    print(f"   ✓ 已导入 {i + 1}/{len(assignments)} 条记录")
                
            except Course.DoesNotExist:
                failed_count += 1
                failed_reasons.append(f"课程ID {assignment['course_id']} 不存在")
            except User.DoesNotExist:
                failed_count += 1
                failed_reasons.append(f"教师ID {assignment['teacher_id']} 不存在")
            except Classroom.DoesNotExist:
                failed_count += 1
                failed_reasons.append(f"教室ID {assignment['classroom_id']} 不存在")
            except Exception as e:
                failed_count += 1
                failed_reasons.append(f"导入第{i+1}条记录时出错: {str(e)}")
        
        # 显示导入结果
        print(f\"\\n📈 导入结果统计:\")
        print(f\"✅ 成功导入: {success_count} 条记录\")
        print(f\"❌ 失败导入: {failed_count} 条记录\")
        
        if failed_count > 0:
            print(f\"\\n🔍 失败原因:\")
            for reason in failed_reasons[:10]:  # 显示前10个错误
                print(f\"   - {reason}\")
            if len(failed_reasons) > 10:
                print(f\"   ... 还有 {len(failed_reasons) - 10} 个错误\")
        
        # 验证导入结果
        final_count = Schedule.objects.filter(status='active').count()
        print(f\"\\n✅ 数据库中现在有 {final_count} 条有效排课记录\")
        
        # 显示样本
        if final_count > 0:
            print(f\"\\n📋 导入样本展示:\")
            schedules = Schedule.objects.filter(status='active')[:3]
            day_names = ['', '周一', '周二', '周三', '周四', '周五', '周六', '周日']
            
            for i, schedule in enumerate(schedules):
                print(f\"{i+1}. {schedule.course.name}\")
                print(f\"   教师: {schedule.teacher.get_full_name() or schedule.teacher.username}\")
                print(f\"   教室: {schedule.classroom}\")
                print(f\"   时间: {day_names[schedule.day_of_week]} {schedule.time_slot.name}\")
                print(f\"   周次: {schedule.week_range}\")
                print()
        
        return success_count == len(assignments)
        
    except Exception as e:
        print(f\"❌ 导入过程发生错误: {str(e)}\")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 开始导入排课结果到数据库...")
    print("=" * 60)
    
    success = import_schedule_results()
    
    print("=" * 60)
    if success:
        print("🎉 排课结果导入成功！\")
        print("✅ 前端现在应该能够显示最新的课程表了！\")
    else:
        print("❌ 排课结果导入失败！\")
        sys.exit(1)