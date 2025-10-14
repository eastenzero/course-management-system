"""
WebSocket消费者
"""

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from .models import Notification

logger = logging.getLogger(__name__)
User = get_user_model()


class NotificationConsumer(AsyncWebsocketConsumer):
    """通知WebSocket消费者"""
    
    async def connect(self):
        """WebSocket连接"""
        self.user = self.scope["user"]
        
        # 检查用户是否已认证
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return
        
        # 加入用户专属的通知组
        self.notification_group_name = f"notifications_{self.user.id}"
        
        await self.channel_layer.group_add(
            self.notification_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # 发送连接成功消息
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': '通知连接已建立'
        }))
        
        # 发送未读通知数量
        unread_count = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            'type': 'unread_count',
            'count': unread_count
        }))
        
        logger.info(f"User {self.user.username} connected to notifications")
    
    async def disconnect(self, close_code):
        """WebSocket断开连接"""
        if hasattr(self, 'notification_group_name'):
            await self.channel_layer.group_discard(
                self.notification_group_name,
                self.channel_name
            )
        
        logger.info(f"User {getattr(self.user, 'username', 'unknown')} disconnected from notifications")
    
    async def receive(self, text_data):
        """接收WebSocket消息"""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            if message_type == 'mark_as_read':
                await self.handle_mark_as_read(text_data_json)
            elif message_type == 'get_notifications':
                await self.handle_get_notifications(text_data_json)
            elif message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': text_data_json.get('timestamp')
                }))
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'未知的消息类型: {message_type}'
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': '无效的JSON格式'
            }))
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': '处理消息时发生错误'
            }))
    
    async def handle_mark_as_read(self, data):
        """处理标记为已读的请求"""
        notification_id = data.get('notification_id')
        if notification_id:
            success = await self.mark_notification_as_read(notification_id)
            if success:
                # 发送更新后的未读数量
                unread_count = await self.get_unread_count()
                await self.send(text_data=json.dumps({
                    'type': 'notification_read',
                    'notification_id': notification_id,
                    'unread_count': unread_count
                }))
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': '标记通知为已读失败'
                }))
    
    async def handle_get_notifications(self, data):
        """处理获取通知列表的请求"""
        page = data.get('page', 1)
        page_size = data.get('page_size', 20)
        
        notifications = await self.get_user_notifications(page, page_size)
        await self.send(text_data=json.dumps({
            'type': 'notifications_list',
            'notifications': notifications,
            'page': page
        }))
    
    # 组消息处理器
    async def notification_message(self, event):
        """处理通知消息"""
        await self.send(text_data=json.dumps({
            'type': 'new_notification',
            'notification': event['notification']
        }))
    
    async def notification_update(self, event):
        """处理通知更新"""
        await self.send(text_data=json.dumps({
            'type': 'notification_update',
            'update': event['update']
        }))
    
    # 数据库操作方法
    @database_sync_to_async
    def get_unread_count(self):
        """获取未读通知数量"""
        return Notification.objects.filter(
            recipient=self.user,
            is_read=False
        ).count()
    
    @database_sync_to_async
    def mark_notification_as_read(self, notification_id):
        """标记通知为已读"""
        try:
            notification = Notification.objects.get(
                id=notification_id,
                recipient=self.user
            )
            notification.mark_as_read()
            return True
        except Notification.DoesNotExist:
            return False
    
    @database_sync_to_async
    def get_user_notifications(self, page=1, page_size=20):
        """获取用户通知列表"""
        offset = (page - 1) * page_size
        notifications = Notification.objects.filter(
            recipient=self.user
        ).order_by('-created_at')[offset:offset + page_size]
        
        return [
            {
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'notification_type': notification.notification_type,
                'priority': notification.priority,
                'is_read': notification.is_read,
                'created_at': notification.created_at.isoformat(),
                'read_at': notification.read_at.isoformat() if notification.read_at else None,
                'extra_data': notification.extra_data,
            }
            for notification in notifications
        ]


class SystemNotificationConsumer(AsyncWebsocketConsumer):
    """系统通知消费者（广播）"""
    
    async def connect(self):
        """连接到系统通知频道"""
        self.user = self.scope["user"]
        
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return
        
        # 加入系统通知组
        await self.channel_layer.group_add(
            "system_notifications",
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"User {self.user.username} connected to system notifications")
    
    async def disconnect(self, close_code):
        """断开系统通知连接"""
        await self.channel_layer.group_discard(
            "system_notifications",
            self.channel_name
        )
        logger.info(f"User {getattr(self.user, 'username', 'unknown')} disconnected from system notifications")
    
    async def system_announcement(self, event):
        """处理系统公告"""
        await self.send(text_data=json.dumps({
            'type': 'system_announcement',
            'announcement': event['announcement']
        }))
    
    async def system_maintenance(self, event):
        """处理系统维护通知"""
        await self.send(text_data=json.dumps({
            'type': 'system_maintenance',
            'maintenance': event['maintenance']
        }))


class CourseNotificationConsumer(AsyncWebsocketConsumer):
    """课程通知消费者"""
    
    async def connect(self):
        """连接到课程通知频道"""
        self.user = self.scope["user"]
        self.course_id = self.scope['url_route']['kwargs']['course_id']
        
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return
        
        # 验证用户是否有权限接收该课程的通知
        has_permission = await self.check_course_permission()
        if not has_permission:
            await self.close()
            return
        
        # 加入课程通知组
        self.course_group_name = f"course_notifications_{self.course_id}"
        await self.channel_layer.group_add(
            self.course_group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"User {self.user.username} connected to course {self.course_id} notifications")
    
    async def disconnect(self, close_code):
        """断开课程通知连接"""
        if hasattr(self, 'course_group_name'):
            await self.channel_layer.group_discard(
                self.course_group_name,
                self.channel_name
            )
        logger.info(f"User {getattr(self.user, 'username', 'unknown')} disconnected from course notifications")
    
    async def course_update(self, event):
        """处理课程更新通知"""
        await self.send(text_data=json.dumps({
            'type': 'course_update',
            'update': event['update']
        }))
    
    async def grade_published(self, event):
        """处理成绩发布通知"""
        await self.send(text_data=json.dumps({
            'type': 'grade_published',
            'grade': event['grade']
        }))
    
    async def schedule_change(self, event):
        """处理课程表变更通知"""
        await self.send(text_data=json.dumps({
            'type': 'schedule_change',
            'change': event['change']
        }))
    
    @database_sync_to_async
    def check_course_permission(self):
        """检查用户是否有权限接收课程通知"""
        from apps.courses.models import Course, Enrollment
        
        try:
            course = Course.objects.get(id=self.course_id)
            
            # 检查用户是否是该课程的学生或教师
            if self.user.user_type == 'student':
                return Enrollment.objects.filter(
                    course=course,
                    student=self.user,
                    is_active=True
                ).exists()
            elif self.user.user_type == 'teacher':
                return course.teachers.filter(id=self.user.id).exists()
            elif self.user.user_type == 'admin':
                return True
            
            return False
        except Course.DoesNotExist:
            return False
