#!/usr/bin/env python3
"""
直接运行排课算法进行测试
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
django.setup()

from apps.schedules.algorithms import create_auto_schedule
from apps.courses.models import Course

def test_algorithm_direct():
    print('🚀 直接运行排课算法 - 小范围测试')
    print('='*50)
    
    # 测试参数
    semester = '2024春'
    academic_year = '2023-2024'
    test_course_ids = [66, 67, 71, 73, 49]  # 之前选定的5门课程
    
    print(f'📅 学期: {semester}')
    print(f'📚 学年: {academic_year}')
    print(f'🎯 测试课程ID: {test_course_ids}')
    
    # 显示测试课程信息
    test_courses = Course.objects.filter(id__in=test_course_ids)
    print(f'📋 测试课程:')
    for course in test_courses:
        teachers = course.teachers.all()
        enroll_count = course.enrollments.filter(is_active=True, status='enrolled').count()
        print(f'  - {course.name} ({course.code})')
        print(f'    教师: {", ".join([t.username for t in teachers])}')
        print(f'    选课: {enroll_count}/{course.max_students} 人')
        print(f'    学分: {course.credits} | 类型: {course.course_type}')
    print()
    
    try:
        # 直接调用算法函数
        print('⏳ 正在运行排课算法...')
        result = create_auto_schedule(semester, academic_year, test_course_ids)
        
        print(f'✅ 算法运行完成！')
        print(f'📊 算法性能报告:')
        print(f'  总约束数量: {result["total_constraints"]}')
        print(f'  成功分配: {result["successful_assignments"]}')
        print(f'  失败分配: {len(result["failed_assignments"])}')
        print(f'  成功率: {result["success_rate"]:.1f}%')
        
        # 显示失败详情
        if result['failed_assignments']:
            print(f'\n❌ 失败分配详情:')
            for i, failed in enumerate(result['failed_assignments'][:3]):
                constraint = failed['constraint']
                print(f'  {i+1}. {constraint.course.name} ({constraint.course.code})')
                print(f'     教师: {constraint.teacher.username}')
                print(f'     原因: {failed["reason"]}')
                print(f'     需要: {failed["required_slots"]} 时段，实际: {failed["assigned_slots"]} 时段')
        
        # 显示优化建议
        suggestions = result.get('suggestions', [])
        if suggestions:
            print(f'\n💡 算法优化建议:')
            for suggestion in suggestions[:3]:
                print(f'  - {suggestion.get("message", "")}')
        
        # 获取算法实例来创建Schedule对象
        algorithm_instance = result['algorithm_instance']
        schedules_to_create = algorithm_instance.create_schedules()
        
        print(f'\n📋 生成的排课方案:')
        print(f'  生成排课记录: {len(schedules_to_create)} 条')
        
        if schedules_to_create:
            print(f'\n🎯 排课方案预览:')
            for i, schedule in enumerate(schedules_to_create[:3]):
                print(f'  {i+1}. {schedule.course.name}')
                print(f'     教师: {schedule.teacher.username}')
                print(f'     教室: {schedule.classroom.room_number}')
                print(f'     时间: 周{schedule.day_of_week} {schedule.time_slot.name}')
                print(f'     周次: {schedule.week_range}')
        
        print(f'\n🎉 小范围算法测试完成！')
        print(f'📈 建议: {"继续大规模排课" if result["success_rate"] >= 70 else "需要调优参数"}')
        
        return result
        
    except Exception as e:
        print(f'❌ 算法运行失败: {e}')
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_algorithm_direct()