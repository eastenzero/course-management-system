from django.contrib import admin
from .models import Course, Enrollment


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """课程管理"""

    list_display = [
        'code', 'name', 'course_type', 'credits', 'hours',
        'department', 'semester', 'max_students', 'current_enrollment',
        'is_active', 'is_published'
    ]
    list_filter = [
        'course_type', 'department', 'semester', 'academic_year',
        'is_active', 'is_published', 'created_at'
    ]
    search_fields = ['code', 'name', 'english_name', 'department']
    filter_horizontal = ['prerequisites', 'teachers']
    readonly_fields = ['current_enrollment', 'created_at', 'updated_at']

    fieldsets = (
        ('基本信息', {
            'fields': ('code', 'name', 'english_name', 'course_type')
        }),
        ('课程属性', {
            'fields': ('credits', 'hours', 'department', 'semester', 'academic_year')
        }),
        ('课程描述', {
            'fields': ('description', 'objectives'),
            'classes': ('collapse',)
        }),
        ('关联信息', {
            'fields': ('prerequisites', 'teachers')
        }),
        ('选课设置', {
            'fields': ('max_students', 'min_students', 'current_enrollment')
        }),
        ('状态', {
            'fields': ('is_active', 'is_published')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def current_enrollment(self, obj):
        """当前选课人数"""
        return obj.current_enrollment
    current_enrollment.short_description = '当前选课人数'


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    """选课记录管理"""

    list_display = [
        'student', 'course', 'status', 'score', 'grade',
        'enrolled_at', 'is_active'
    ]
    list_filter = [
        'status', 'course__department', 'course__semester',
        'enrolled_at', 'is_active'
    ]
    search_fields = [
        'student__username', 'student__first_name', 'student__last_name',
        'course__code', 'course__name'
    ]
    readonly_fields = ['enrolled_at']

    fieldsets = (
        ('基本信息', {
            'fields': ('student', 'course', 'status')
        }),
        ('成绩信息', {
            'fields': ('score', 'grade')
        }),
        ('时间信息', {
            'fields': ('enrolled_at', 'dropped_at', 'is_active')
        }),
    )
