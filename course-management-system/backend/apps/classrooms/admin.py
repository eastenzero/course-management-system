from django.contrib import admin
from .models import Building, Classroom


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    """教学楼管理"""

    list_display = ['code', 'name', 'address', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['code', 'name', 'address']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('基本信息', {
            'fields': ('code', 'name', 'address', 'description')
        }),
        ('状态', {
            'fields': ('is_active',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    """教室管理"""

    list_display = [
        'building', 'room_number', 'name', 'room_type', 'capacity',
        'floor', 'is_available', 'is_active'
    ]
    list_filter = [
        'building', 'room_type', 'floor', 'is_available', 'is_active',
        'created_at'
    ]
    search_fields = ['room_number', 'name', 'building__name', 'building__code']
    readonly_fields = ['full_name', 'equipment_list', 'created_at', 'updated_at']

    fieldsets = (
        ('基本信息', {
            'fields': ('building', 'room_number', 'name', 'full_name')
        }),
        ('教室属性', {
            'fields': ('room_type', 'capacity', 'floor', 'area')
        }),
        ('设备信息', {
            'fields': ('equipment', 'equipment_list'),
            'classes': ('collapse',)
        }),
        ('位置描述', {
            'fields': ('location_description',),
            'classes': ('collapse',)
        }),
        ('状态', {
            'fields': ('is_available', 'is_active')
        }),
        ('维护信息', {
            'fields': ('maintenance_notes', 'last_maintenance'),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def full_name(self, obj):
        """完整名称"""
        return obj.full_name
    full_name.short_description = '完整名称'

    def equipment_list(self, obj):
        """设备列表"""
        return '; '.join(obj.equipment_list) if obj.equipment_list else '无'
    equipment_list.short_description = '设备列表'
