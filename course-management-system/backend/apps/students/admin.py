from django.contrib import admin
from .models import StudentProfile, StudentCourseProgress


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'major', 'class_name', 'admission_year',
        'gpa', 'completed_credits', 'enrollment_status'
    ]
    list_filter = [
        'admission_year', 'major', 'enrollment_status', 'created_at'
    ]
    search_fields = [
        'user__username', 'user__first_name', 'user__last_name',
        'user__student_id', 'major', 'class_name'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'admission_year', 'major', 'class_name')
        }),
        ('学业信息', {
            'fields': ('gpa', 'total_credits', 'completed_credits', 'enrollment_status')
        }),
        ('联系信息', {
            'fields': ('emergency_contact', 'emergency_phone')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(StudentCourseProgress)
class StudentCourseProgressAdmin(admin.ModelAdmin):
    list_display = [
        'student', 'course', 'attendance_rate', 'assignment_completion'
    ]
    list_filter = [
        'course__department', 'course__semester', 'created_at'
    ]
    search_fields = [
        'student__username', 'student__first_name', 'student__last_name',
        'course__name', 'course__code'
    ]
    readonly_fields = ['created_at', 'updated_at']
