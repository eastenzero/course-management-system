"""
通知系统模型
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

User = get_user_model()


class NotificationType(models.TextChoices):
    """通知类型"""
    COURSE_ENROLLMENT = 'course_enrollment', '课程选课'
    GRADE_PUBLISHED = 'grade_published', '成绩发布'
    ASSIGNMENT_DUE = 'assignment_due', '作业截止'
    SCHEDULE_CHANGE = 'schedule_change', '课程表变更'
    SYSTEM_ANNOUNCEMENT = 'system_announcement', '系统公告'
    COURSE_REMINDER = 'course_reminder', '课程提醒'
    EXAM_NOTIFICATION = 'exam_notification', '考试通知'


class NotificationPriority(models.TextChoices):
    """通知优先级"""
    LOW = 'low', '低'
    NORMAL = 'normal', '普通'
    HIGH = 'high', '高'
    URGENT = 'urgent', '紧急'


class NotificationChannel(models.TextChoices):
    """通知渠道"""
    WEBSOCKET = 'websocket', 'WebSocket'
    EMAIL = 'email', '邮件'
    SMS = 'sms', '短信'
    PUSH = 'push', '推送'


class Notification(models.Model):
    """通知模型"""
    
    # 接收者
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='接收者'
    )
    
    # 发送者（可选）
    sender = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_notifications',
        verbose_name='发送者'
    )
    
    # 通知内容
    title = models.CharField(max_length=200, verbose_name='标题')
    message = models.TextField(verbose_name='消息内容')
    
    # 通知类型和优先级
    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM_ANNOUNCEMENT,
        verbose_name='通知类型'
    )
    
    priority = models.CharField(
        max_length=20,
        choices=NotificationPriority.choices,
        default=NotificationPriority.NORMAL,
        verbose_name='优先级'
    )
    
    # 关联对象（通用外键）
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='内容类型'
    )
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name='对象ID')
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # 状态字段
    is_read = models.BooleanField(default=False, verbose_name='是否已读')
    is_sent = models.BooleanField(default=False, verbose_name='是否已发送')
    
    # 时间字段
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    read_at = models.DateTimeField(null=True, blank=True, verbose_name='阅读时间')
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name='发送时间')
    
    # 额外数据（JSON格式）
    extra_data = models.JSONField(default=dict, blank=True, verbose_name='额外数据')
    
    class Meta:
        db_table = 'notifications'
        verbose_name = '通知'
        verbose_name_plural = '通知'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username}"
    
    def mark_as_read(self):
        """标记为已读"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    def mark_as_sent(self):
        """标记为已发送"""
        if not self.is_sent:
            self.is_sent = True
            self.sent_at = timezone.now()
            self.save(update_fields=['is_sent', 'sent_at'])


class NotificationPreference(models.Model):
    """用户通知偏好设置"""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_preference',
        verbose_name='用户'
    )
    
    # 各类型通知的渠道偏好
    course_enrollment_channels = models.JSONField(
        default=list,
        verbose_name='选课通知渠道'
    )
    grade_published_channels = models.JSONField(
        default=list,
        verbose_name='成绩发布通知渠道'
    )
    assignment_due_channels = models.JSONField(
        default=list,
        verbose_name='作业截止通知渠道'
    )
    schedule_change_channels = models.JSONField(
        default=list,
        verbose_name='课程表变更通知渠道'
    )
    system_announcement_channels = models.JSONField(
        default=list,
        verbose_name='系统公告通知渠道'
    )
    
    # 全局设置
    enable_email_notifications = models.BooleanField(
        default=True,
        verbose_name='启用邮件通知'
    )
    enable_websocket_notifications = models.BooleanField(
        default=True,
        verbose_name='启用实时通知'
    )
    
    # 免打扰时间
    quiet_hours_start = models.TimeField(
        null=True,
        blank=True,
        verbose_name='免打扰开始时间'
    )
    quiet_hours_end = models.TimeField(
        null=True,
        blank=True,
        verbose_name='免打扰结束时间'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'notification_preferences'
        verbose_name = '通知偏好'
        verbose_name_plural = '通知偏好'
    
    def __str__(self):
        return f"{self.user.username}的通知偏好"
    
    def get_channels_for_type(self, notification_type: str) -> list:
        """获取指定类型通知的渠道列表"""
        channel_map = {
            NotificationType.COURSE_ENROLLMENT: self.course_enrollment_channels,
            NotificationType.GRADE_PUBLISHED: self.grade_published_channels,
            NotificationType.ASSIGNMENT_DUE: self.assignment_due_channels,
            NotificationType.SCHEDULE_CHANGE: self.schedule_change_channels,
            NotificationType.SYSTEM_ANNOUNCEMENT: self.system_announcement_channels,
        }
        return channel_map.get(notification_type, [NotificationChannel.WEBSOCKET])


class NotificationTemplate(models.Model):
    """通知模板"""
    
    name = models.CharField(max_length=100, unique=True, verbose_name='模板名称')
    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
        verbose_name='通知类型'
    )
    
    # 模板内容
    title_template = models.CharField(max_length=200, verbose_name='标题模板')
    message_template = models.TextField(verbose_name='消息模板')
    email_subject_template = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='邮件主题模板'
    )
    email_body_template = models.TextField(blank=True, verbose_name='邮件正文模板')
    
    # 模板变量说明
    variables = models.JSONField(
        default=dict,
        help_text='模板变量说明，格式：{"variable_name": "description"}',
        verbose_name='模板变量'
    )
    
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'notification_templates'
        verbose_name = '通知模板'
        verbose_name_plural = '通知模板'
    
    def __str__(self):
        return self.name
    
    def render(self, context: dict) -> dict:
        """渲染模板"""
        from django.template import Template, Context
        
        title = Template(self.title_template).render(Context(context))
        message = Template(self.message_template).render(Context(context))
        
        result = {
            'title': title,
            'message': message,
        }
        
        if self.email_subject_template:
            result['email_subject'] = Template(self.email_subject_template).render(Context(context))
        
        if self.email_body_template:
            result['email_body'] = Template(self.email_body_template).render(Context(context))
        
        return result
