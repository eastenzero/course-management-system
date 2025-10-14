"""
通知系统测试
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Notification, NotificationPreference, NotificationTemplate, NotificationType
from .services import notification_service

User = get_user_model()


class NotificationModelTest(TestCase):
    """通知模型测试"""
    
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
    
    def test_create_notification(self):
        """测试创建通知"""
        notification = Notification.objects.create(
            recipient=self.user1,
            sender=self.user2,
            title='测试通知',
            message='这是一条测试通知',
            notification_type=NotificationType.SYSTEM_ANNOUNCEMENT
        )
        
        self.assertEqual(notification.recipient, self.user1)
        self.assertEqual(notification.sender, self.user2)
        self.assertEqual(notification.title, '测试通知')
        self.assertFalse(notification.is_read)
        self.assertFalse(notification.is_sent)
    
    def test_mark_as_read(self):
        """测试标记为已读"""
        notification = Notification.objects.create(
            recipient=self.user1,
            title='测试通知',
            message='测试消息'
        )
        
        self.assertFalse(notification.is_read)
        self.assertIsNone(notification.read_at)
        
        notification.mark_as_read()
        
        self.assertTrue(notification.is_read)
        self.assertIsNotNone(notification.read_at)
    
    def test_notification_str(self):
        """测试通知字符串表示"""
        notification = Notification.objects.create(
            recipient=self.user1,
            title='测试通知',
            message='测试消息'
        )
        
        expected = f"测试通知 - {self.user1.username}"
        self.assertEqual(str(notification), expected)


class NotificationPreferenceModelTest(TestCase):
    """通知偏好模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_preference(self):
        """测试创建通知偏好"""
        preference = NotificationPreference.objects.create(
            user=self.user,
            enable_email_notifications=True,
            enable_websocket_notifications=True
        )
        
        self.assertEqual(preference.user, self.user)
        self.assertTrue(preference.enable_email_notifications)
        self.assertTrue(preference.enable_websocket_notifications)
    
    def test_get_channels_for_type(self):
        """测试获取通知类型的渠道"""
        preference = NotificationPreference.objects.create(
            user=self.user,
            course_enrollment_channels=['websocket', 'email']
        )
        
        channels = preference.get_channels_for_type(NotificationType.COURSE_ENROLLMENT)
        self.assertEqual(channels, ['websocket', 'email'])


class NotificationServiceTest(TestCase):
    """通知服务测试"""
    
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
    
    def test_create_notification(self):
        """测试创建通知"""
        notification = notification_service.create_notification(
            recipient=self.user1,
            title='测试通知',
            message='测试消息',
            sender=self.user2
        )
        
        self.assertIsInstance(notification, Notification)
        self.assertEqual(notification.recipient, self.user1)
        self.assertEqual(notification.sender, self.user2)
        self.assertEqual(notification.title, '测试通知')
    
    def test_create_bulk_notifications(self):
        """测试批量创建通知"""
        recipients = [self.user1, self.user2]
        notifications = notification_service.create_bulk_notifications(
            recipients=recipients,
            title='批量通知',
            message='批量消息'
        )
        
        self.assertEqual(len(notifications), 2)
        self.assertEqual(notifications[0].recipient, self.user1)
        self.assertEqual(notifications[1].recipient, self.user2)


class NotificationAPITest(APITestCase):
    """通知API测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        # 创建测试通知
        self.notification = Notification.objects.create(
            recipient=self.user,
            title='测试通知',
            message='测试消息'
        )
    
    def test_notification_list_authenticated(self):
        """测试认证用户获取通知列表"""
        self.client.force_authenticate(user=self.user)
        url = reverse('notifications:notification-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_notification_list_unauthenticated(self):
        """测试未认证用户无法获取通知列表"""
        url = reverse('notifications:notification-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_notification_detail(self):
        """测试获取通知详情"""
        self.client.force_authenticate(user=self.user)
        url = reverse('notifications:notification-detail', kwargs={'pk': self.notification.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], '测试通知')
        
        # 检查是否自动标记为已读
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)
    
    def test_mark_notifications_read(self):
        """测试标记通知为已读"""
        self.client.force_authenticate(user=self.user)
        url = reverse('notifications:mark-read')
        data = {'notification_ids': [self.notification.pk]}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['updated_count'], 1)
        
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)
    
    def test_unread_count(self):
        """测试获取未读通知数量"""
        self.client.force_authenticate(user=self.user)
        url = reverse('notifications:unread-count')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread_count'], 1)
    
    def test_notification_preferences(self):
        """测试通知偏好设置"""
        self.client.force_authenticate(user=self.user)
        url = reverse('notifications:preferences')
        
        # 获取偏好设置
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 更新偏好设置
        data = {
            'enable_email_notifications': False,
            'enable_websocket_notifications': True
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['enable_email_notifications'])
    
    def test_create_notification_admin_only(self):
        """测试只有管理员可以创建通知"""
        # 普通用户无法创建通知
        self.client.force_authenticate(user=self.user)
        url = reverse('notifications:create-notification')
        data = {
            'recipient_ids': [self.user.pk],
            'title': '管理员通知',
            'message': '管理员消息'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # 管理员可以创建通知
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
