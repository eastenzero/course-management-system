"""
数据分析异步任务
用于处理统计数据计算、报表生成等耗时操作
"""

from celery import shared_task
from django.utils import timezone
from django.db.models import Count, Avg, Q
from datetime import datetime, timedelta

from .models import CourseStatistics, ClassroomUtilization, TeacherWorkload, SystemReport
from apps.courses.models import Course, Enrollment
from apps.classrooms.models import Classroom
from apps.schedules.models import Schedule, TimeSlot
from apps.users.models import User
from utils.cache import CacheManager


@shared_task
def update_course_statistics(semester=None):
    """更新课程统计数据"""
    if not semester:
        # 获取当前学期
        semester = get_current_semester()
    
    courses = Course.objects.filter(semester=semester)
    
    for course in courses:
        # 获取或创建统计记录
        stats, created = CourseStatistics.objects.get_or_create(
            course=course,
            semester=semester,
            defaults={
                'total_enrolled': 0,
                'total_dropped': 0,
                'current_enrolled': 0,
            }
        )
        
        # 计算选课统计
        enrollments = Enrollment.objects.filter(course=course)
        stats.total_enrolled = enrollments.count()
        stats.total_dropped = enrollments.filter(status='dropped').count()
        stats.current_enrolled = enrollments.filter(is_active=True, status='enrolled').count()
        
        # 计算成绩统计
        completed_enrollments = enrollments.filter(status='completed', score__isnull=False)
        if completed_enrollments.exists():
            stats.average_score = completed_enrollments.aggregate(
                avg_score=Avg('score')
            )['avg_score']
            
            # 计算及格率（60分及以上）
            pass_count = completed_enrollments.filter(score__gte=60).count()
            stats.pass_rate = (pass_count / completed_enrollments.count()) * 100
            
            # 计算优秀率（85分及以上）
            excellent_count = completed_enrollments.filter(score__gte=85).count()
            stats.excellent_rate = (excellent_count / completed_enrollments.count()) * 100
        
        stats.save()
    
    # 清除相关缓存
    CacheManager.clear_schedule_cache(semester)
    
    return f"Updated statistics for {courses.count()} courses in semester {semester}"


@shared_task
def update_classroom_utilization(semester=None, week_number=None):
    """更新教室利用率统计"""
    if not semester:
        semester = get_current_semester()
    
    if not week_number:
        # 获取当前周次
        week_number = get_current_week_number()
    
    classrooms = Classroom.objects.filter(is_active=True)
    time_slots = TimeSlot.objects.filter(is_active=True)
    
    # 计算一周的总时间段数
    total_time_slots_per_week = time_slots.count() * 7
    
    for classroom in classrooms:
        # 获取或创建利用率记录
        utilization, created = ClassroomUtilization.objects.get_or_create(
            classroom=classroom,
            semester=semester,
            week_number=week_number,
            defaults={
                'total_time_slots': total_time_slots_per_week,
                'occupied_time_slots': 0,
                'utilization_rate': 0,
            }
        )
        
        # 计算占用的时间段数
        occupied_count = Schedule.objects.filter(
            classroom=classroom,
            semester=semester,
            status='active'
        ).count()
        
        utilization.total_time_slots = total_time_slots_per_week
        utilization.occupied_time_slots = occupied_count
        utilization.utilization_rate = (occupied_count / total_time_slots_per_week * 100) if total_time_slots_per_week > 0 else 0
        utilization.save()
    
    return f"Updated classroom utilization for {classrooms.count()} classrooms"


@shared_task
def update_teacher_workload(semester=None):
    """更新教师工作量统计"""
    if not semester:
        semester = get_current_semester()
    
    teachers = User.objects.filter(user_type='teacher')
    
    for teacher in teachers:
        # 获取或创建工作量记录
        workload, created = TeacherWorkload.objects.get_or_create(
            teacher=teacher,
            semester=semester,
            defaults={
                'total_courses': 0,
                'total_hours': 0,
                'total_students': 0,
                'required_courses': 0,
                'elective_courses': 0,
            }
        )
        
        # 获取教师的课程
        teacher_courses = Course.objects.filter(
            teachers=teacher,
            semester=semester
        )
        
        workload.total_courses = teacher_courses.count()
        workload.total_hours = sum(course.hours for course in teacher_courses)
        
        # 计算总学生数
        total_students = 0
        for course in teacher_courses:
            total_students += course.current_enrollment
        workload.total_students = total_students
        
        # 按课程类型统计
        workload.required_courses = teacher_courses.filter(course_type='required').count()
        workload.elective_courses = teacher_courses.filter(course_type='elective').count()
        
        workload.save()
    
    return f"Updated workload for {teachers.count()} teachers"


@shared_task
def generate_system_report(report_type, semester, user_id):
    """生成系统报表"""
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return "User not found"
    
    report_data = {}
    
    if report_type == 'enrollment':
        # 选课统计报表
        courses = Course.objects.filter(semester=semester)
        report_data = {
            'total_courses': courses.count(),
            'total_enrollments': Enrollment.objects.filter(
                course__semester=semester, is_active=True
            ).count(),
            'enrollment_by_department': list(
                courses.values('department').annotate(
                    enrollment_count=Count('enrollments', filter=Q(enrollments__is_active=True))
                )
            ),
            'enrollment_by_course_type': list(
                courses.values('course_type').annotate(
                    enrollment_count=Count('enrollments', filter=Q(enrollments__is_active=True))
                )
            ),
        }
    
    elif report_type == 'classroom':
        # 教室利用率报表
        classrooms = Classroom.objects.filter(is_active=True)
        utilization_data = ClassroomUtilization.objects.filter(semester=semester)
        
        report_data = {
            'total_classrooms': classrooms.count(),
            'average_utilization': utilization_data.aggregate(
                avg_rate=Avg('utilization_rate')
            )['avg_rate'] or 0,
            'utilization_by_building': list(
                utilization_data.values('classroom__building__name').annotate(
                    avg_utilization=Avg('utilization_rate')
                )
            ),
        }
    
    elif report_type == 'teacher':
        # 教师工作量报表
        workload_data = TeacherWorkload.objects.filter(semester=semester)
        
        report_data = {
            'total_teachers': workload_data.count(),
            'average_courses_per_teacher': workload_data.aggregate(
                avg_courses=Avg('total_courses')
            )['avg_courses'] or 0,
            'average_hours_per_teacher': workload_data.aggregate(
                avg_hours=Avg('total_hours')
            )['avg_hours'] or 0,
            'workload_distribution': list(
                workload_data.values('total_courses').annotate(
                    teacher_count=Count('teacher')
                ).order_by('total_courses')
            ),
        }
    
    # 创建报表记录
    report = SystemReport.objects.create(
        name=f"{dict(SystemReport.REPORT_TYPE_CHOICES)[report_type]} - {semester}",
        report_type=report_type,
        semester=semester,
        data=report_data,
        generated_by=user
    )
    
    return f"Generated report: {report.name}"


@shared_task
def cleanup_old_cache():
    """清理过期缓存"""
    # 这里可以添加清理逻辑
    # 由于Django缓存框架会自动处理过期，这里主要是清理一些特定的缓存
    
    # 清理统计缓存（每天清理一次）
    CacheManager.delete_pattern(CacheManager.STATISTICS_PREFIX + '*')
    
    return "Cache cleanup completed"


def get_current_semester():
    """获取当前学期"""
    now = timezone.now()
    year = now.year
    month = now.month
    
    # 简单的学期判断逻辑
    if month >= 9 or month <= 1:
        # 秋季学期
        if month >= 9:
            return f"{year}-{year+1}-1"
        else:
            return f"{year-1}-{year}-1"
    else:
        # 春季学期
        return f"{year-1}-{year}-2"


def get_current_week_number():
    """获取当前周次"""
    # 简单的周次计算，实际应用中可能需要更复杂的逻辑
    now = timezone.now()
    # 假设学期从9月1日开始
    semester_start = datetime(now.year if now.month >= 9 else now.year - 1, 9, 1)
    if now < semester_start:
        semester_start = datetime(now.year - 1, 9, 1)
    
    delta = now - semester_start
    week_number = delta.days // 7 + 1
    return min(week_number, 20)  # 最多20周
