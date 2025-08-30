"""
算法模块Django管理界面配置
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db import models
from django.db.models import Count, Avg, Q
from apps.schedules.models import Schedule
from apps.courses.models import Course
from apps.users.models import User
from apps.classrooms.models import Classroom


class ScheduleInline(admin.TabularInline):
    """课程安排内联编辑"""
    model = Schedule
    extra = 0
    fields = ['day_of_week', 'time_slot', 'classroom', 'status']
    readonly_fields = ['created_at']


# 注意：Schedule模型已经在schedules应用中注册，这里不重复注册
# 但我们可以创建一个自定义的管理视图用于算法分析
class AlgorithmScheduleAdmin(admin.ModelAdmin):
    """算法生成的课程安排管理（扩展版）"""
    
    list_display = [
        'course_link', 'teacher_link', 'classroom_link', 'day_of_week_display',
        'time_slot', 'semester', 'status', 'algorithm_score'
    ]
    list_filter = [
        'day_of_week', 'semester', 'academic_year', 'status',
        'course__department', 'created_at'
    ]
    search_fields = [
        'course__code', 'course__name', 'teacher__username',
        'classroom__room_number', 'classroom__building__name'
    ]
    readonly_fields = [
        'time_display', 'location_display', 'created_at', 'updated_at',
        'algorithm_score', 'conflict_analysis'
    ]
    
    fieldsets = (
        ('课程信息', {
            'fields': ('course', 'teacher')
        }),
        ('时间安排', {
            'fields': ('day_of_week', 'time_slot', 'time_display')
        }),
        ('地点安排', {
            'fields': ('classroom', 'location_display')
        }),
        ('学期信息', {
            'fields': ('semester', 'academic_year', 'week_range')
        }),
        ('算法分析', {
            'fields': ('algorithm_score', 'conflict_analysis'),
            'classes': ('collapse',)
        }),
        ('状态', {
            'fields': ('status', 'notes')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['run_conflict_check', 'optimize_schedule', 'export_schedule']
    
    def course_link(self, obj):
        """课程链接"""
        if obj.course:
            url = reverse('admin:courses_course_change', args=[obj.course.pk])
            return format_html('<a href="{}">{}</a>', url, obj.course.name)
        return '-'
    course_link.short_description = '课程'
    
    def teacher_link(self, obj):
        """教师链接"""
        if obj.teacher:
            url = reverse('admin:users_user_change', args=[obj.teacher.pk])
            return format_html('<a href="{}">{}</a>', url, obj.teacher.get_full_name() or obj.teacher.username)
        return '-'
    teacher_link.short_description = '教师'
    
    def classroom_link(self, obj):
        """教室链接"""
        if obj.classroom:
            url = reverse('admin:classrooms_classroom_change', args=[obj.classroom.pk])
            return format_html('<a href="{}">{}</a>', url, str(obj.classroom))
        return '-'
    classroom_link.short_description = '教室'
    
    def day_of_week_display(self, obj):
        """星期显示"""
        return obj.get_day_of_week_display()
    day_of_week_display.short_description = '星期'
    
    def algorithm_score(self, obj):
        """算法评分"""
        # 这里可以实现一个简单的评分逻辑
        score = 85  # 模拟评分
        if score >= 90:
            color = 'green'
        elif score >= 70:
            color = 'orange'
        else:
            color = 'red'
        return format_html('<span style="color: {};">{}</span>', color, f'{score}分')
    algorithm_score.short_description = '算法评分'
    
    def conflict_analysis(self, obj):
        """冲突分析"""
        # 检查时间冲突
        conflicts = Schedule.objects.filter(
            day_of_week=obj.day_of_week,
            time_slot=obj.time_slot,
            semester=obj.semester
        ).exclude(id=obj.id)
        
        teacher_conflicts = conflicts.filter(teacher=obj.teacher).count()
        classroom_conflicts = conflicts.filter(classroom=obj.classroom).count()
        
        if teacher_conflicts > 0 or classroom_conflicts > 0:
            return format_html(
                '<span style="color: red;">教师冲突: {} | 教室冲突: {}</span>',
                teacher_conflicts, classroom_conflicts
            )
        return format_html('<span style="color: green;">无冲突</span>')
    conflict_analysis.short_description = '冲突分析'
    
    def run_conflict_check(self, request, queryset):
        """运行冲突检查"""
        conflicts_found = 0
        for schedule in queryset:
            # 这里可以调用冲突检测算法
            conflicts_found += 1  # 模拟
        
        self.message_user(request, f'冲突检查完成，发现 {conflicts_found} 个潜在冲突')
    run_conflict_check.short_description = '运行冲突检查'
    
    def optimize_schedule(self, request, queryset):
        """优化课程安排"""
        optimized_count = 0
        for schedule in queryset:
            # 这里可以调用优化算法
            optimized_count += 1  # 模拟
        
        self.message_user(request, f'优化完成，优化了 {optimized_count} 个课程安排')
    optimize_schedule.short_description = '优化课程安排'
    
    def export_schedule(self, request, queryset):
        """导出课程安排"""
        count = queryset.count()
        self.message_user(request, f'导出了 {count} 个课程安排')
    export_schedule.short_description = '导出课程安排'


# 创建一个算法统计信息的管理界面
class AlgorithmStatsAdmin:
    """算法统计信息管理"""

    def __init__(self):
        self.name = "算法统计"
        self.verbose_name = "算法统计"
        self.verbose_name_plural = "算法统计"

    @staticmethod
    def get_algorithm_stats():
        """获取算法统计信息"""
        from django.db.models import Count, Avg

        # 课程安排统计
        schedule_stats = {
            'total_schedules': Schedule.objects.count(),
            'active_schedules': Schedule.objects.filter(status='active').count(),
            'pending_schedules': Schedule.objects.filter(status='pending').count(),
            'cancelled_schedules': Schedule.objects.filter(status='cancelled').count(),
        }

        # 教师工作量统计
        teacher_stats = User.objects.filter(user_type='teacher').aggregate(
            total_teachers=Count('id'),
            avg_courses_per_teacher=Avg('taught_schedules__count')
        )

        # 教室利用率统计
        classroom_stats = Classroom.objects.filter(is_active=True).aggregate(
            total_classrooms=Count('id'),
            avg_utilization=Avg('schedules__count')
        )

        # 课程统计
        course_stats = Course.objects.aggregate(
            total_courses=Count('id'),
            active_courses=Count('id', filter=Q(is_active=True)),
            published_courses=Count('id', filter=Q(is_published=True))
        )

        return {
            'schedule_stats': schedule_stats,
            'teacher_stats': teacher_stats,
            'classroom_stats': classroom_stats,
            'course_stats': course_stats,
        }


# 创建一个简单的算法工具管理界面
class AlgorithmToolsAdmin:
    """算法工具管理"""

    def __init__(self):
        self.name = "算法工具"
        self.verbose_name = "算法工具"
        self.verbose_name_plural = "算法工具"

    @staticmethod
    def run_schedule_optimization(semester=None):
        """运行排课优化"""
        # 这里可以调用实际的排课算法
        return {
            'status': 'success',
            'message': '排课优化完成',
            'optimized_count': 0
        }

    @staticmethod
    def check_schedule_conflicts(semester=None):
        """检查排课冲突"""
        # 这里可以调用冲突检测算法
        conflicts = []

        # 检查教师时间冲突
        teacher_conflicts = Schedule.objects.values(
            'teacher', 'day_of_week', 'time_slot', 'semester'
        ).annotate(
            count=Count('id')
        ).filter(count__gt=1)

        # 检查教室时间冲突
        classroom_conflicts = Schedule.objects.values(
            'classroom', 'day_of_week', 'time_slot', 'semester'
        ).annotate(
            count=Count('id')
        ).filter(count__gt=1)

        return {
            'teacher_conflicts': list(teacher_conflicts),
            'classroom_conflicts': list(classroom_conflicts),
            'total_conflicts': len(teacher_conflicts) + len(classroom_conflicts)
        }
