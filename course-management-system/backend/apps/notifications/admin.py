"""
通知系统Django管理界面配置
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Notification, NotificationPreference, NotificationTemplate


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """通知管理"""
    
    list_display = [
        'id', 'title', 'recipient_link', 'sender_link', 'notification_type',
        'priority', 'is_read', 'is_sent', 'created_at'
    ]
    list_filter = [
        'notification_type', 'priority', 'is_read', 'is_sent', 'created_at'
    ]
    search_fields = ['title', 'message', 'recipient__username', 'sender__username']
    readonly_fields = ['created_at', 'read_at', 'sent_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('基本信息', {
            'fields': ('recipient', 'sender', 'title', 'message')
        }),
        ('分类和优先级', {
            'fields': ('notification_type', 'priority')
        }),
        ('状态', {
            'fields': ('is_read', 'is_sent', 'created_at', 'read_at', 'sent_at')
        }),
        ('关联对象', {
            'fields': ('content_type', 'object_id'),
            'classes': ('collapse',)
        }),
        ('额外数据', {
            'fields': ('extra_data',),
            'classes': ('collapse',)
        }),
    )
    
    def recipient_link(self, obj):
        """接收者链接"""
        if obj.recipient:
            url = reverse('admin:auth_user_change', args=[obj.recipient.pk])
            return format_html('<a href="{}">{}</a>', url, obj.recipient.username)
        return '-'
    recipient_link.short_description = '接收者'
    
    def sender_link(self, obj):
        """发送者链接"""
        if obj.sender:
            url = reverse('admin:auth_user_change', args=[obj.sender.pk])
            return format_html('<a href="{}">{}</a>', url, obj.sender.username)
        return '系统'
    sender_link.short_description = '发送者'
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).select_related('recipient', 'sender', 'content_type')
    
    actions = ['mark_as_read', 'mark_as_unread', 'mark_as_sent']
    
    def mark_as_read(self, request, queryset):
        """批量标记为已读"""
        from django.utils import timezone
        updated = queryset.filter(is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )
        self.message_user(request, f'成功标记 {updated} 条通知为已读')
    mark_as_read.short_description = '标记为已读'
    
    def mark_as_unread(self, request, queryset):
        """批量标记为未读"""
        updated = queryset.filter(is_read=True).update(
            is_read=False,
            read_at=None
        )
        self.message_user(request, f'成功标记 {updated} 条通知为未读')
    mark_as_unread.short_description = '标记为未读'
    
    def mark_as_sent(self, request, queryset):
        """批量标记为已发送"""
        from django.utils import timezone
        updated = queryset.filter(is_sent=False).update(
            is_sent=True,
            sent_at=timezone.now()
        )
        self.message_user(request, f'成功标记 {updated} 条通知为已发送')
    mark_as_sent.short_description = '标记为已发送'


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    """通知偏好管理"""
    
    list_display = [
        'user_link', 'enable_email_notifications', 'enable_websocket_notifications',
        'quiet_hours_display', 'created_at'
    ]
    list_filter = ['enable_email_notifications', 'enable_websocket_notifications', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('用户', {
            'fields': ('user',)
        }),
        ('全局设置', {
            'fields': ('enable_email_notifications', 'enable_websocket_notifications')
        }),
        ('通知渠道偏好', {
            'fields': (
                'course_enrollment_channels', 'grade_published_channels',
                'assignment_due_channels', 'schedule_change_channels',
                'system_announcement_channels'
            )
        }),
        ('免打扰时间', {
            'fields': ('quiet_hours_start', 'quiet_hours_end')
        }),
        ('时间戳', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_link(self, obj):
        """用户链接"""
        url = reverse('admin:auth_user_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = '用户'
    
    def quiet_hours_display(self, obj):
        """免打扰时间显示"""
        if obj.quiet_hours_start and obj.quiet_hours_end:
            return f"{obj.quiet_hours_start} - {obj.quiet_hours_end}"
        return '未设置'
    quiet_hours_display.short_description = '免打扰时间'


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    """通知模板管理"""
    
    list_display = [
        'name', 'notification_type', 'is_active', 'created_at', 'updated_at'
    ]
    list_filter = ['notification_type', 'is_active', 'created_at']
    search_fields = ['name', 'title_template', 'message_template']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'notification_type', 'is_active')
        }),
        ('模板内容', {
            'fields': ('title_template', 'message_template')
        }),
        ('邮件模板', {
            'fields': ('email_subject_template', 'email_body_template'),
            'classes': ('collapse',)
        }),
        ('模板变量', {
            'fields': ('variables',),
            'description': '模板中可用的变量说明，JSON格式'
        }),
        ('时间戳', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        """自定义表单"""
        form = super().get_form(request, obj, **kwargs)
        
        # 为模板字段添加帮助文本
        if 'title_template' in form.base_fields:
            form.base_fields['title_template'].help_text = '支持Django模板语法，如：{{ user.username }}'
        
        if 'message_template' in form.base_fields:
            form.base_fields['message_template'].help_text = '支持Django模板语法，如：{{ course.name }}'
        
        return form
    
    actions = ['activate_templates', 'deactivate_templates']
    
    def activate_templates(self, request, queryset):
        """批量激活模板"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'成功激活 {updated} 个模板')
    activate_templates.short_description = '激活选中的模板'
    
    def deactivate_templates(self, request, queryset):
        """批量停用模板"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'成功停用 {updated} 个模板')
    deactivate_templates.short_description = '停用选中的模板'


# 自定义管理界面标题
admin.site.site_header = '课程管理系统 - 管理后台'
admin.site.site_title = '课程管理系统'
admin.site.index_title = '欢迎使用课程管理系统管理后台'
