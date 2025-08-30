"""
通知系统序列化器
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Notification, NotificationPreference, NotificationTemplate,
    NotificationType, NotificationChannel, NotificationPriority
)

User = get_user_model()


class NotificationSerializer(serializers.ModelSerializer):
    """通知序列化器"""
    
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    sender_full_name = serializers.SerializerMethodField()
    time_since_created = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'notification_type', 'priority',
            'is_read', 'is_sent', 'created_at', 'read_at', 'sent_at',
            'sender_name', 'sender_full_name', 'time_since_created',
            'extra_data'
        ]
        read_only_fields = [
            'id', 'created_at', 'read_at', 'sent_at', 'sender_name',
            'sender_full_name', 'time_since_created'
        ]
    
    def get_sender_full_name(self, obj):
        """获取发送者全名"""
        if obj.sender:
            return f"{obj.sender.first_name} {obj.sender.last_name}".strip() or obj.sender.username
        return "系统"
    
    def get_time_since_created(self, obj):
        """获取创建时间的相对时间"""
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff < timedelta(minutes=1):
            return "刚刚"
        elif diff < timedelta(hours=1):
            return f"{diff.seconds // 60}分钟前"
        elif diff < timedelta(days=1):
            return f"{diff.seconds // 3600}小时前"
        elif diff < timedelta(days=7):
            return f"{diff.days}天前"
        else:
            return obj.created_at.strftime("%Y-%m-%d")


class NotificationListSerializer(serializers.ModelSerializer):
    """通知列表序列化器（简化版）"""
    
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    time_since_created = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'notification_type', 'priority',
            'is_read', 'created_at', 'sender_name', 'time_since_created'
        ]
    
    def get_time_since_created(self, obj):
        """获取创建时间的相对时间"""
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff < timedelta(minutes=1):
            return "刚刚"
        elif diff < timedelta(hours=1):
            return f"{diff.seconds // 60}分钟前"
        elif diff < timedelta(days=1):
            return f"{diff.seconds // 3600}小时前"
        elif diff < timedelta(days=7):
            return f"{diff.days}天前"
        else:
            return obj.created_at.strftime("%Y-%m-%d")


class NotificationMarkReadSerializer(serializers.Serializer):
    """标记通知为已读的序列化器"""
    
    notification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
        help_text="要标记为已读的通知ID列表"
    )


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """通知偏好序列化器"""
    
    class Meta:
        model = NotificationPreference
        fields = [
            'course_enrollment_channels', 'grade_published_channels',
            'assignment_due_channels', 'schedule_change_channels',
            'system_announcement_channels', 'enable_email_notifications',
            'enable_websocket_notifications', 'quiet_hours_start',
            'quiet_hours_end'
        ]
    
    def validate_course_enrollment_channels(self, value):
        """验证选课通知渠道"""
        valid_channels = [choice[0] for choice in NotificationChannel.choices]
        for channel in value:
            if channel not in valid_channels:
                raise serializers.ValidationError(f"无效的通知渠道: {channel}")
        return value
    
    def validate_grade_published_channels(self, value):
        """验证成绩发布通知渠道"""
        valid_channels = [choice[0] for choice in NotificationChannel.choices]
        for channel in value:
            if channel not in valid_channels:
                raise serializers.ValidationError(f"无效的通知渠道: {channel}")
        return value
    
    def validate_assignment_due_channels(self, value):
        """验证作业截止通知渠道"""
        valid_channels = [choice[0] for choice in NotificationChannel.choices]
        for channel in value:
            if channel not in valid_channels:
                raise serializers.ValidationError(f"无效的通知渠道: {channel}")
        return value
    
    def validate_schedule_change_channels(self, value):
        """验证课程表变更通知渠道"""
        valid_channels = [choice[0] for choice in NotificationChannel.choices]
        for channel in value:
            if channel not in valid_channels:
                raise serializers.ValidationError(f"无效的通知渠道: {channel}")
        return value
    
    def validate_system_announcement_channels(self, value):
        """验证系统公告通知渠道"""
        valid_channels = [choice[0] for choice in NotificationChannel.choices]
        for channel in value:
            if channel not in valid_channels:
                raise serializers.ValidationError(f"无效的通知渠道: {channel}")
        return value


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """通知模板序列化器"""
    
    class Meta:
        model = NotificationTemplate
        fields = [
            'id', 'name', 'notification_type', 'title_template',
            'message_template', 'email_subject_template',
            'email_body_template', 'variables', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CreateNotificationSerializer(serializers.Serializer):
    """创建通知的序列化器"""
    
    recipient_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="接收者用户ID列表"
    )
    title = serializers.CharField(max_length=200, help_text="通知标题")
    message = serializers.CharField(help_text="通知内容")
    notification_type = serializers.ChoiceField(
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM_ANNOUNCEMENT,
        help_text="通知类型"
    )
    priority = serializers.ChoiceField(
        choices=NotificationPriority.choices,
        default=NotificationPriority.NORMAL,
        help_text="优先级"
    )
    channels = serializers.ListField(
        child=serializers.ChoiceField(choices=NotificationChannel.choices),
        required=False,
        help_text="发送渠道列表（可选）"
    )
    extra_data = serializers.JSONField(
        required=False,
        default=dict,
        help_text="额外数据"
    )
    
    def validate_recipient_ids(self, value):
        """验证接收者ID"""
        if not value:
            raise serializers.ValidationError("接收者列表不能为空")
        
        # 检查用户是否存在
        existing_users = User.objects.filter(id__in=value).values_list('id', flat=True)
        missing_ids = set(value) - set(existing_users)
        
        if missing_ids:
            raise serializers.ValidationError(f"以下用户ID不存在: {list(missing_ids)}")
        
        return value
