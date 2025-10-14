from django.contrib import admin
from .models import TeacherProfile, TeacherCourseAssignment, TeacherNotice


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'title', 'research_area', 'office_location',
        'teaching_experience', 'is_active_teacher'
    ]
    list_filter = [
        'title', 'is_active_teacher', 'teaching_experience', 'created_at'
    ]
    search_fields = [
        'user__username', 'user__first_name', 'user__last_name',
        'user__employee_id', 'research_area', 'office_location'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'title', 'research_area')
        }),
        ('办公信息', {
            'fields': ('office_location', 'office_hours', 'office_phone')
        }),
        ('教学信息', {
            'fields': ('teaching_experience', 'education_background', 'is_active_teacher')
        }),
        ('其他信息', {
            'fields': ('personal_website',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TeacherCourseAssignment)
class TeacherCourseAssignmentAdmin(admin.ModelAdmin):
    list_display = [
        'teacher', 'course', 'role', 'workload_hours', 'assigned_at', 'is_active'
    ]
    list_filter = [
        'role', 'is_active', 'assigned_at', 'course__department'
    ]
    search_fields = [
        'teacher__username', 'teacher__first_name', 'teacher__last_name',
        'course__name', 'course__code'
    ]
    readonly_fields = ['assigned_at']


@admin.register(TeacherNotice)
class TeacherNoticeAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'teacher', 'course', 'notice_type', 'priority',
        'is_published', 'published_at', 'created_at'
    ]
    list_filter = [
        'notice_type', 'priority', 'is_published', 'created_at',
        'course__department'
    ]
    search_fields = [
        'title', 'content', 'teacher__username', 'course__name'
    ]
    readonly_fields = ['published_at', 'created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('teacher', 'course', 'title', 'content')
        }),
        ('分类信息', {
            'fields': ('notice_type', 'priority')
        }),
        ('发布状态', {
            'fields': ('is_published', 'published_at')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
