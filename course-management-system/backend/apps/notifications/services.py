"""
通知服务
"""

import logging
from typing import List, Dict, Any, Optional
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import (
    Notification, NotificationPreference, NotificationTemplate,
    NotificationType, NotificationChannel, NotificationPriority
)

logger = logging.getLogger(__name__)
User = get_user_model()


class NotificationService:
    """通知服务类"""
    
    def __init__(self):
        self.channel_layer = get_channel_layer()
    
    def create_notification(
        self,
        recipient: User,
        title: str,
        message: str,
        notification_type: str = NotificationType.SYSTEM_ANNOUNCEMENT,
        priority: str = NotificationPriority.NORMAL,
        sender: Optional[User] = None,
        content_object: Any = None,
        extra_data: Optional[Dict] = None,
        channels: Optional[List[str]] = None
    ) -> Notification:
        """创建通知"""
        
        # 创建通知记录
        notification = Notification.objects.create(
            recipient=recipient,
            sender=sender,
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            content_object=content_object,
            extra_data=extra_data or {}
        )
        
        # 获取用户通知偏好
        if channels is None:
            channels = self._get_user_preferred_channels(recipient, notification_type)
        
        # 发送通知到各个渠道
        self._send_to_channels(notification, channels)
        
        return notification
    
    def create_bulk_notifications(
        self,
        recipients: List[User],
        title: str,
        message: str,
        notification_type: str = NotificationType.SYSTEM_ANNOUNCEMENT,
        priority: str = NotificationPriority.NORMAL,
        sender: Optional[User] = None,
        content_object: Any = None,
        extra_data: Optional[Dict] = None
    ) -> List[Notification]:
        """批量创建通知"""
        
        notifications = []
        for recipient in recipients:
            notification = self.create_notification(
                recipient=recipient,
                title=title,
                message=message,
                notification_type=notification_type,
                priority=priority,
                sender=sender,
                content_object=content_object,
                extra_data=extra_data
            )
            notifications.append(notification)
        
        return notifications
    
    def create_from_template(
        self,
        recipient: User,
        template_name: str,
        context: Dict[str, Any],
        notification_type: str = NotificationType.SYSTEM_ANNOUNCEMENT,
        priority: str = NotificationPriority.NORMAL,
        sender: Optional[User] = None,
        content_object: Any = None,
        channels: Optional[List[str]] = None
    ) -> Optional[Notification]:
        """使用模板创建通知"""
        
        try:
            template = NotificationTemplate.objects.get(
                name=template_name,
                is_active=True
            )
            
            rendered = template.render(context)
            
            return self.create_notification(
                recipient=recipient,
                title=rendered['title'],
                message=rendered['message'],
                notification_type=notification_type,
                priority=priority,
                sender=sender,
                content_object=content_object,
                extra_data={'template_name': template_name, 'context': context},
                channels=channels
            )
            
        except NotificationTemplate.DoesNotExist:
            logger.error(f"Notification template '{template_name}' not found")
            return None
    
    def _get_user_preferred_channels(self, user: User, notification_type: str) -> List[str]:
        """获取用户偏好的通知渠道"""
        try:
            preference = user.notification_preference
            channels = preference.get_channels_for_type(notification_type)
            
            # 如果没有设置偏好，使用默认渠道
            if not channels:
                channels = [NotificationChannel.WEBSOCKET]
            
            return channels
            
        except NotificationPreference.DoesNotExist:
            # 创建默认偏好设置
            NotificationPreference.objects.create(
                user=user,
                course_enrollment_channels=[NotificationChannel.WEBSOCKET, NotificationChannel.EMAIL],
                grade_published_channels=[NotificationChannel.WEBSOCKET, NotificationChannel.EMAIL],
                assignment_due_channels=[NotificationChannel.WEBSOCKET],
                schedule_change_channels=[NotificationChannel.WEBSOCKET, NotificationChannel.EMAIL],
                system_announcement_channels=[NotificationChannel.WEBSOCKET]
            )
            return [NotificationChannel.WEBSOCKET]
    
    def _send_to_channels(self, notification: Notification, channels: List[str]):
        """发送通知到指定渠道"""
        for channel in channels:
            try:
                if channel == NotificationChannel.WEBSOCKET:
                    self._send_websocket_notification(notification)
                elif channel == NotificationChannel.EMAIL:
                    self._send_email_notification(notification)
                # 其他渠道可以在这里添加
                
            except Exception as e:
                logger.error(f"Failed to send notification via {channel}: {e}")
    
    def _send_websocket_notification(self, notification: Notification):
        """发送WebSocket通知"""
        if not self.channel_layer:
            logger.warning("Channel layer not available for WebSocket notifications")
            return
        
        group_name = f"notifications_{notification.recipient.id}"
        
        notification_data = {
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'notification_type': notification.notification_type,
            'priority': notification.priority,
            'created_at': notification.created_at.isoformat(),
            'extra_data': notification.extra_data,
        }
        
        async_to_sync(self.channel_layer.group_send)(
            group_name,
            {
                'type': 'notification_message',
                'notification': notification_data
            }
        )
        
        logger.info(f"WebSocket notification sent to user {notification.recipient.username}")
    
    def _send_email_notification(self, notification: Notification):
        """发送邮件通知"""
        if not settings.EMAIL_HOST_USER:
            logger.warning("Email not configured, skipping email notification")
            return
        
        try:
            # 检查用户是否启用了邮件通知
            preference = getattr(notification.recipient, 'notification_preference', None)
            if preference and not preference.enable_email_notifications:
                return
            
            # 获取邮件模板
            template_name = settings.NOTIFICATION_SETTINGS['EMAIL_TEMPLATES'].get(
                notification.notification_type,
                'notifications/default.html'
            )
            
            context = {
                'notification': notification,
                'user': notification.recipient,
                'site_name': 'Course Management System',
                'site_url': getattr(settings, 'SITE_URL', 'http://localhost:3000'),
            }
            
            # 渲染邮件内容
            try:
                html_content = render_to_string(template_name, context)
                subject = f"[课程管理系统] {notification.title}"
                
                send_mail(
                    subject=subject,
                    message=notification.message,  # 纯文本版本
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[notification.recipient.email],
                    html_message=html_content,
                    fail_silently=False
                )
                
                notification.mark_as_sent()
                logger.info(f"Email notification sent to {notification.recipient.email}")
                
            except Exception as e:
                logger.error(f"Failed to render email template {template_name}: {e}")
                # 发送简单的纯文本邮件
                send_mail(
                    subject=f"[课程管理系统] {notification.title}",
                    message=notification.message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[notification.recipient.email],
                    fail_silently=False
                )
                
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
    
    def send_system_announcement(self, title: str, message: str, priority: str = NotificationPriority.NORMAL):
        """发送系统公告"""
        if not self.channel_layer:
            return
        
        announcement_data = {
            'title': title,
            'message': message,
            'priority': priority,
            'timestamp': timezone.now().isoformat()
        }
        
        async_to_sync(self.channel_layer.group_send)(
            "system_notifications",
            {
                'type': 'system_announcement',
                'announcement': announcement_data
            }
        )
        
        logger.info(f"System announcement sent: {title}")
    
    def send_course_notification(
        self,
        course_id: int,
        notification_type: str,
        data: Dict[str, Any]
    ):
        """发送课程相关通知"""
        if not self.channel_layer:
            return
        
        group_name = f"course_notifications_{course_id}"
        
        async_to_sync(self.channel_layer.group_send)(
            group_name,
            {
                'type': notification_type,
                notification_type.split('_')[0]: data
            }
        )
        
        logger.info(f"Course notification sent to course {course_id}: {notification_type}")


# 全局通知服务实例
notification_service = NotificationService()


# 便捷函数
def send_notification(
    recipient: User,
    title: str,
    message: str,
    notification_type: str = NotificationType.SYSTEM_ANNOUNCEMENT,
    **kwargs
) -> Notification:
    """发送通知的便捷函数"""
    return notification_service.create_notification(
        recipient=recipient,
        title=title,
        message=message,
        notification_type=notification_type,
        **kwargs
    )


def send_bulk_notification(
    recipients: List[User],
    title: str,
    message: str,
    notification_type: str = NotificationType.SYSTEM_ANNOUNCEMENT,
    **kwargs
) -> List[Notification]:
    """批量发送通知的便捷函数"""
    return notification_service.create_bulk_notifications(
        recipients=recipients,
        title=title,
        message=message,
        notification_type=notification_type,
        **kwargs
    )


def send_template_notification(
    recipient: User,
    template_name: str,
    context: Dict[str, Any],
    **kwargs
) -> Optional[Notification]:
    """使用模板发送通知的便捷函数"""
    return notification_service.create_from_template(
        recipient=recipient,
        template_name=template_name,
        context=context,
        **kwargs
    )
