from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserPreference


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """自定义用户管理"""

    list_display = [
        'username', 'email', 'first_name', 'last_name',
        'user_type', 'display_id', 'department', 'is_active', 'date_joined'
    ]
    list_filter = ['user_type', 'department', 'is_active', 'date_joined']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'employee_id', 'student_id']
    ordering = ['-date_joined']

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'avatar')
        }),
        (_('School info'), {
            'fields': ('user_type', 'employee_id', 'student_id', 'department')
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        (_('School info'), {
            'fields': ('user_type', 'employee_id', 'student_id', 'department')
        }),
    )

    def display_id(self, obj):
        """显示学号或工号"""
        return obj.display_id
    display_id.short_description = '学号/工号'


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    """用户偏好设置管理"""

    list_display = [
        'user', 'theme', 'language', 'page_size', 'profile_visibility',
        'auto_logout', 'session_timeout', 'updated_at'
    ]
    list_filter = [
        'theme', 'language', 'profile_visibility', 'session_timeout',
        'show_email', 'show_phone', 'created_at'
    ]
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('用户', {
            'fields': ('user',)
        }),
        ('界面设置', {
            'fields': ('theme', 'language', 'page_size', 'date_format')
        }),
        ('隐私设置', {
            'fields': ('profile_visibility', 'show_email', 'show_phone')
        }),
        ('安全设置', {
            'fields': ('auto_logout', 'session_timeout')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).select_related('user')
