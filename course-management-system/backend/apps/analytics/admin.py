from django.contrib import admin
from .models import CourseStatistics, ClassroomUtilization, TeacherWorkload, SystemReport


@admin.register(CourseStatistics)
class CourseStatisticsAdmin(admin.ModelAdmin):
    """课程统计管理"""

    list_display = [
        'course', 'semester', 'current_enrolled', 'average_score',
        'pass_rate', 'excellent_rate', 'last_updated'
    ]
    list_filter = ['semester', 'last_updated']
    search_fields = ['course__code', 'course__name']
    readonly_fields = ['last_updated', 'created_at']

    fieldsets = (
        ('基本信息', {
            'fields': ('course', 'semester')
        }),
        ('选课统计', {
            'fields': ('total_enrolled', 'total_dropped', 'current_enrolled')
        }),
        ('成绩统计', {
            'fields': ('average_score', 'pass_rate', 'excellent_rate')
        }),
        ('其他统计', {
            'fields': ('classroom_utilization',)
        }),
        ('时间信息', {
            'fields': ('last_updated', 'created_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ClassroomUtilization)
class ClassroomUtilizationAdmin(admin.ModelAdmin):
    """教室利用率管理"""

    list_display = [
        'classroom', 'semester', 'week_number', 'total_time_slots',
        'occupied_time_slots', 'utilization_rate', 'updated_at'
    ]
    list_filter = ['semester', 'week_number', 'classroom__building']
    search_fields = ['classroom__room_number', 'classroom__building__name']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('基本信息', {
            'fields': ('classroom', 'semester', 'week_number')
        }),
        ('利用率统计', {
            'fields': ('total_time_slots', 'occupied_time_slots', 'utilization_rate')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TeacherWorkload)
class TeacherWorkloadAdmin(admin.ModelAdmin):
    """教师工作量管理"""

    list_display = [
        'teacher', 'semester', 'total_courses', 'total_hours',
        'total_students', 'updated_at'
    ]
    list_filter = ['semester', 'updated_at']
    search_fields = ['teacher__username', 'teacher__first_name', 'teacher__last_name']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('基本信息', {
            'fields': ('teacher', 'semester')
        }),
        ('工作量统计', {
            'fields': ('total_courses', 'total_hours', 'total_students')
        }),
        ('课程类型分布', {
            'fields': ('required_courses', 'elective_courses')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SystemReport)
class SystemReportAdmin(admin.ModelAdmin):
    """系统报表管理"""

    list_display = [
        'name', 'report_type', 'semester', 'generated_by',
        'generated_at', 'is_public'
    ]
    list_filter = ['report_type', 'semester', 'is_public', 'generated_at']
    search_fields = ['name', 'generated_by__username']
    readonly_fields = ['generated_at']

    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'report_type', 'semester')
        }),
        ('报表数据', {
            'fields': ('data',),
            'classes': ('collapse',)
        }),
        ('生成信息', {
            'fields': ('generated_by', 'generated_at', 'is_public')
        }),
    )
