"""
文件管理Django管理界面配置
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Sum
from .models import UploadedFile, FileShare, FileAccessLog, FileCategory, FileStatus


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    """上传文件管理"""
    
    list_display = [
        'original_name', 'uploaded_by_link', 'category', 'file_size_display',
        'status', 'is_public', 'download_count', 'created_at'
    ]
    list_filter = [
        'category', 'status', 'is_public', 'created_at', 'mime_type'
    ]
    search_fields = ['original_name', 'uploaded_by__username', 'file_hash']
    readonly_fields = [
        'id', 'file_size', 'mime_type', 'file_extension', 'file_hash',
        'width', 'height', 'created_at', 'updated_at', 'last_accessed',
        'file_preview'
    ]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('基本信息', {
            'fields': ('id', 'original_name', 'file', 'file_preview')
        }),
        ('文件属性', {
            'fields': (
                'file_size', 'file_size_display', 'mime_type', 'file_extension',
                'category', 'file_hash'
            )
        }),
        ('图片属性', {
            'fields': ('width', 'height'),
            'classes': ('collapse',)
        }),
        ('上传信息', {
            'fields': ('uploaded_by', 'content_type', 'object_id')
        }),
        ('状态和权限', {
            'fields': ('status', 'is_public')
        }),
        ('统计信息', {
            'fields': ('download_count', 'last_accessed')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('元数据', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
    )
    
    def uploaded_by_link(self, obj):
        """上传者链接"""
        if obj.uploaded_by:
            url = reverse('admin:auth_user_change', args=[obj.uploaded_by.pk])
            return format_html('<a href="{}">{}</a>', url, obj.uploaded_by.username)
        return '-'
    uploaded_by_link.short_description = '上传者'
    
    def file_size_display(self, obj):
        """文件大小显示"""
        return obj.get_file_size_display()
    file_size_display.short_description = '文件大小'
    
    def file_preview(self, obj):
        """文件预览"""
        if obj.category == FileCategory.IMAGE and obj.file:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px;" />',
                obj.file.url
            )
        elif obj.file:
            return format_html(
                '<a href="{}" target="_blank">查看文件</a>',
                obj.file.url
            )
        return '无文件'
    file_preview.short_description = '文件预览'
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).select_related('uploaded_by', 'content_type')
    
    actions = ['mark_as_active', 'mark_as_deleted', 'mark_as_public', 'mark_as_private']
    
    def mark_as_active(self, request, queryset):
        """标记为正常状态"""
        updated = queryset.update(status=FileStatus.ACTIVE)
        self.message_user(request, f'成功标记 {updated} 个文件为正常状态')
    mark_as_active.short_description = '标记为正常状态'
    
    def mark_as_deleted(self, request, queryset):
        """标记为已删除"""
        updated = queryset.update(status=FileStatus.DELETED)
        self.message_user(request, f'成功标记 {updated} 个文件为已删除')
    mark_as_deleted.short_description = '标记为已删除'
    
    def mark_as_public(self, request, queryset):
        """标记为公开"""
        updated = queryset.update(is_public=True)
        self.message_user(request, f'成功标记 {updated} 个文件为公开')
    mark_as_public.short_description = '标记为公开'
    
    def mark_as_private(self, request, queryset):
        """标记为私有"""
        updated = queryset.update(is_public=False)
        self.message_user(request, f'成功标记 {updated} 个文件为私有')
    mark_as_private.short_description = '标记为私有'


@admin.register(FileShare)
class FileShareAdmin(admin.ModelAdmin):
    """文件分享管理"""
    
    list_display = [
        'file_name', 'shared_by_link', 'share_token', 'is_active',
        'download_count', 'max_downloads', 'expires_at', 'created_at'
    ]
    list_filter = [
        'is_active', 'allow_download', 'allow_preview', 'created_at'
    ]
    search_fields = ['file__original_name', 'shared_by__username', 'share_token']
    readonly_fields = [
        'id', 'share_token', 'download_count', 'created_at', 'last_accessed',
        'share_url'
    ]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('基本信息', {
            'fields': ('id', 'file', 'shared_by', 'share_token', 'share_url')
        }),
        ('分享设置', {
            'fields': ('password', 'allow_download', 'allow_preview')
        }),
        ('限制设置', {
            'fields': ('expires_at', 'max_downloads', 'download_count')
        }),
        ('状态', {
            'fields': ('is_active',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'last_accessed'),
            'classes': ('collapse',)
        }),
    )
    
    def file_name(self, obj):
        """文件名"""
        return obj.file.original_name
    file_name.short_description = '文件名'
    
    def shared_by_link(self, obj):
        """分享者链接"""
        if obj.shared_by:
            url = reverse('admin:auth_user_change', args=[obj.shared_by.pk])
            return format_html('<a href="{}">{}</a>', url, obj.shared_by.username)
        return '-'
    shared_by_link.short_description = '分享者'
    
    def share_url(self, obj):
        """分享链接"""
        if obj.share_token:
            # 这里应该是实际的分享URL
            url = f"/api/v1/files/share/{obj.share_token}/"
            return format_html('<a href="{}" target="_blank">{}</a>', url, url)
        return '无'
    share_url.short_description = '分享链接'
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).select_related('file', 'shared_by')
    
    actions = ['activate_shares', 'deactivate_shares']
    
    def activate_shares(self, request, queryset):
        """激活分享"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'成功激活 {updated} 个分享')
    activate_shares.short_description = '激活分享'
    
    def deactivate_shares(self, request, queryset):
        """停用分享"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'成功停用 {updated} 个分享')
    deactivate_shares.short_description = '停用分享'


@admin.register(FileAccessLog)
class FileAccessLogAdmin(admin.ModelAdmin):
    """文件访问日志管理"""
    
    list_display = [
        'file_name', 'user_link', 'action', 'ip_address', 'created_at'
    ]
    list_filter = ['action', 'created_at']
    search_fields = ['file__original_name', 'user__username', 'ip_address']
    readonly_fields = ['file', 'user', 'action', 'ip_address', 'user_agent', 'share', 'created_at']
    date_hierarchy = 'created_at'
    
    def file_name(self, obj):
        """文件名"""
        return obj.file.original_name
    file_name.short_description = '文件名'
    
    def user_link(self, obj):
        """用户链接"""
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.pk])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return '匿名用户'
    user_link.short_description = '用户'
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).select_related('file', 'user', 'share')
    
    def has_add_permission(self, request):
        """禁止手动添加日志"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """禁止修改日志"""
        return False


# 自定义管理界面首页统计
class FileStatsMixin:
    """文件统计混入"""
    
    def changelist_view(self, request, extra_context=None):
        """添加统计信息到列表页面"""
        extra_context = extra_context or {}
        
        # 文件统计
        file_stats = UploadedFile.objects.aggregate(
            total_files=Count('id'),
            total_size=Sum('file_size'),
            active_files=Count('id', filter=models.Q(status=FileStatus.ACTIVE)),
            deleted_files=Count('id', filter=models.Q(status=FileStatus.DELETED))
        )
        
        # 分享统计
        share_stats = FileShare.objects.aggregate(
            total_shares=Count('id'),
            active_shares=Count('id', filter=models.Q(is_active=True)),
            total_downloads=Sum('download_count')
        )
        
        extra_context['file_stats'] = file_stats
        extra_context['share_stats'] = share_stats
        
        return super().changelist_view(request, extra_context)


# 将统计混入添加到文件管理
UploadedFileAdmin.__bases__ = (FileStatsMixin,) + UploadedFileAdmin.__bases__
