from django.contrib import admin
from .models import TimeSlot, Schedule


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    """时间段管理"""

    list_display = ['order', 'name', 'start_time', 'end_time', 'duration_minutes', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    readonly_fields = ['duration_minutes', 'created_at', 'updated_at']
    ordering = ['order']

    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'order')
        }),
        ('时间设置', {
            'fields': ('start_time', 'end_time', 'duration_minutes')
        }),
        ('状态', {
            'fields': ('is_active',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    """课程安排管理"""

    list_display = [
        'course', 'teacher', 'classroom', 'day_of_week', 'time_slot',
        'semester', 'status', 'time_display'
    ]
    list_filter = [
        'day_of_week', 'semester', 'academic_year', 'status',
        'course__department', 'created_at'
    ]
    search_fields = [
        'course__code', 'course__name', 'teacher__username',
        'classroom__room_number', 'classroom__building__name'
    ]
    readonly_fields = ['time_display', 'location_display', 'created_at', 'updated_at']

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
        ('状态', {
            'fields': ('status', 'notes')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def time_display(self, obj):
        """时间显示"""
        return obj.time_display
    time_display.short_description = '时间'

    def location_display(self, obj):
        """地点显示"""
        return obj.location_display
    location_display.short_description = '地点'
