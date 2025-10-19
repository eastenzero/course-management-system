"""
排课结果可视化模块
提供排课结果的可视化功能
"""

import json
from typing import Dict, List, Any
from collections import defaultdict

from .models import Schedule, TimeSlot
from apps.courses.models import Course
from apps.classrooms.models import Classroom
from apps.users.models import User


class ScheduleVisualizer:
    """排课结果可视化器"""
    
    def __init__(self, semester: str, academic_year: str):
        self.semester = semester
        self.academic_year = academic_year
        
    def generate_schedule_table(self, user_type: str = 'general', user_id: int = None) -> Dict[str, Any]:
        """
        生成课程表
        
        Args:
            user_type: 用户类型 ('student', 'teacher', 'classroom', 'general')
            user_id: 用户ID（可选）
            
        Returns:
            课程表数据
        """
        # 获取所有时间段
        time_slots = TimeSlot.objects.filter(is_active=True).order_by('order')
        
        # 构建课程表结构
        schedule_table = {
            'metadata': {
                'semester': self.semester,
                'academic_year': self.academic_year,
                'generated_at': str(timezone.now()) if 'timezone' in globals() else str(datetime.now())
            },
            'time_slots': [
                {
                    'id': ts.id,
                    'name': ts.name,
                    'start_time': ts.start_time.strftime('%H:%M'),
                    'end_time': ts.end_time.strftime('%H:%M'),
                    'order': ts.order
                }
                for ts in time_slots
            ],
            'days': {
                1: {'name': '周一', 'courses': {}},
                2: {'name': '周二', 'courses': {}},
                3: {'name': '周三', 'courses': {}},
                4: {'name': '周四', 'courses': {}},
                5: {'name': '周五', 'courses': {}},
                6: {'name': '周六', 'courses': {}},
                7: {'name': '周日', 'courses': {}}
            }
        }
        
        # 初始化课程表结构
        for day_num in schedule_table['days']:
            for time_slot in time_slots:
                schedule_table['days'][day_num]['courses'][time_slot.id] = None
        
        # 获取排课数据
        schedules = Schedule.objects.filter(
            semester=self.semester,
            academic_year=self.academic_year,
            status='active'
        ).select_related('course', 'teacher', 'classroom', 'time_slot')
        
        # 根据用户类型过滤数据
        if user_type == 'student' and user_id:
            # 学生课程表：查询学生选课的课程安排
            from apps.courses.models import Enrollment
            enrolled_courses = Enrollment.objects.filter(
                student_id=user_id,
                is_active=True,
                status='enrolled'
            ).values_list('course_id', flat=True)
            schedules = schedules.filter(course_id__in=enrolled_courses)
        elif user_type == 'teacher' and user_id:
            # 教师课程表：查询教师的课程安排
            schedules = schedules.filter(teacher_id=user_id)
        elif user_type == 'classroom' and user_id:
            # 教室课程表：查询教室的使用安排
            schedules = schedules.filter(classroom_id=user_id)
        
        # 填充课程表数据
        for schedule in schedules:
            day = schedule.day_of_week
            time_slot_id = schedule.time_slot.id
            
            if day in schedule_table['days'] and time_slot_id in schedule_table['days'][day]['courses']:
                schedule_table['days'][day]['courses'][time_slot_id] = {
                    'id': schedule.id,
                    'course': {
                        'id': schedule.course.id,
                        'code': schedule.course.code,
                        'name': schedule.course.name,
                        'credits': schedule.course.credits,
                        'type': schedule.course.course_type
                    },
                    'teacher': {
                        'id': schedule.teacher.id,
                        'name': schedule.teacher.get_full_name() or schedule.teacher.username
                    },
                    'classroom': {
                        'id': schedule.classroom.id,
                        'name': str(schedule.classroom),
                        'capacity': schedule.classroom.capacity
                    },
                    'time': {
                        'slot': schedule.time_slot.name,
                        'start_time': schedule.time_slot.start_time.strftime('%H:%M'),
                        'end_time': schedule.time_slot.end_time.strftime('%H:%M')
                    },
                    'week_range': schedule.week_range,
                    'notes': schedule.notes
                }
        
        return schedule_table
    
    def generate_statistics_chart(self) -> Dict[str, Any]:
        """
        生成统计图表数据
        
        Returns:
            统计图表数据
        """
        # 获取排课数据
        schedules = Schedule.objects.filter(
            semester=self.semester,
            academic_year=self.academic_year,
            status='active'
        ).select_related('course', 'teacher', 'classroom', 'time_slot')
        
        # 按星期分布统计
        day_distribution = defaultdict(int)
        day_names = {1: '周一', 2: '周二', 3: '周三', 4: '周四', 5: '周五', 6: '周六', 7: '周日'}
        
        # 按时间段分布统计
        time_slot_distribution = defaultdict(int)
        
        # 按课程类型统计
        course_type_distribution = defaultdict(int)
        
        # 教师工作量统计
        teacher_workload = defaultdict(int)
        
        # 教室利用率统计
        classroom_usage = defaultdict(int)
        
        for schedule in schedules:
            # 星期分布
            day_distribution[day_names[schedule.day_of_week]] += 1
            
            # 时间段分布
            time_slot_distribution[schedule.time_slot.name] += 1
            
            # 课程类型分布
            course_type_distribution[schedule.course.course_type] += 1
            
            # 教师工作量
            teacher_workload[schedule.teacher.get_full_name() or schedule.teacher.username] += 1
            
            # 教室利用率
            classroom_usage[str(schedule.classroom)] += 1
        
        return {
            'day_distribution': dict(day_distribution),
            'time_slot_distribution': dict(time_slot_distribution),
            'course_type_distribution': dict(course_type_distribution),
            'teacher_workload': dict(teacher_workload),
            'classroom_usage': dict(classroom_usage)
        }
    
    def generate_conflict_report(self) -> Dict[str, Any]:
        """
        生成冲突报告
        
        Returns:
            冲突报告数据
        """
        # 获取所有排课
        schedules = Schedule.objects.filter(
            semester=self.semester,
            academic_year=self.academic_year,
            status='active'
        ).select_related('course', 'teacher', 'classroom', 'time_slot')
        
        conflicts = []
        
        # 检查教师时间冲突
        teacher_schedule_map = defaultdict(list)
        # 检查教室时间冲突
        classroom_schedule_map = defaultdict(list)
        
        for schedule in schedules:
            # 教师时间键
            teacher_key = (schedule.teacher.id, schedule.day_of_week, schedule.time_slot.id)
            # 教室时间键
            classroom_key = (schedule.classroom.id, schedule.day_of_week, schedule.time_slot.id)
            
            # 检查教师冲突
            if teacher_key in teacher_schedule_map:
                for existing_schedule in teacher_schedule_map[teacher_key]:
                    conflicts.append({
                        'type': 'teacher_conflict',
                        'description': f'教师 {schedule.teacher.get_full_name() or schedule.teacher.username} '
                                     f'在 {schedule.get_day_of_week_display()} {schedule.time_slot.name} '
                                     f'有时间冲突',
                        'schedules': [
                            {
                                'id': existing_schedule.id,
                                'course': existing_schedule.course.name,
                                'classroom': str(existing_schedule.classroom)
                            },
                            {
                                'id': schedule.id,
                                'course': schedule.course.name,
                                'classroom': str(schedule.classroom)
                            }
                        ]
                    })
            
            # 检查教室冲突
            if classroom_key in classroom_schedule_map:
                for existing_schedule in classroom_schedule_map[classroom_key]:
                    conflicts.append({
                        'type': 'classroom_conflict',
                        'description': f'教室 {schedule.classroom} '
                                     f'在 {schedule.get_day_of_week_display()} {schedule.time_slot.name} '
                                     f'有时间冲突',
                        'schedules': [
                            {
                                'id': existing_schedule.id,
                                'course': existing_schedule.course.name,
                                'teacher': existing_schedule.teacher.get_full_name() or existing_schedule.teacher.username
                            },
                            {
                                'id': schedule.id,
                                'course': schedule.course.name,
                                'teacher': schedule.teacher.get_full_name() or schedule.teacher.username
                            }
                        ]
                    })
            
            # 记录当前排课
            teacher_schedule_map[teacher_key].append(schedule)
            classroom_schedule_map[classroom_key].append(schedule)
        
        return {
            'total_conflicts': len(conflicts),
            'conflicts': conflicts
        }


def generate_visualization_data(semester: str, academic_year: str, 
                              visualization_type: str = 'schedule_table',
                              user_type: str = 'general', 
                              user_id: int = None) -> Dict[str, Any]:
    """
    生成可视化数据
    
    Args:
        semester: 学期
        academic_year: 学年
        visualization_type: 可视化类型 ('schedule_table', 'statistics', 'conflicts')
        user_type: 用户类型
        user_id: 用户ID
        
    Returns:
        可视化数据
    """
    visualizer = ScheduleVisualizer(semester, academic_year)
    
    if visualization_type == 'schedule_table':
        return visualizer.generate_schedule_table(user_type, user_id)
    elif visualization_type == 'statistics':
        return visualizer.generate_statistics_chart()
    elif visualization_type == 'conflicts':
        return visualizer.generate_conflict_report()
    else:
        # 默认返回课程表
        return visualizer.generate_schedule_table(user_type, user_id)