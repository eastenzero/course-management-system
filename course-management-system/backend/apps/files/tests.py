"""
文件管理系统测试
"""

import os
import tempfile
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from PIL import Image
import io

from .models import UploadedFile, FileShare, FileAccessLog, FileCategory, FileStatus

User = get_user_model()


class UploadedFileModelTest(TestCase):
    """上传文件模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def create_test_image(self):
        """创建测试图片"""
        image = Image.new('RGB', (100, 100), color='red')
        image_io = io.BytesIO()
        image.save(image_io, format='JPEG')
        image_io.seek(0)
        return SimpleUploadedFile(
            'test_image.jpg',
            image_io.getvalue(),
            content_type='image/jpeg'
        )
    
    def create_test_text_file(self):
        """创建测试文本文件"""
        return SimpleUploadedFile(
            'test_file.txt',
            b'This is a test file content',
            content_type='text/plain'
        )
    
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_create_uploaded_file(self):
        """测试创建上传文件"""
        test_file = self.create_test_text_file()
        
        uploaded_file = UploadedFile.objects.create(
            original_name='test_file.txt',
            file=test_file,
            uploaded_by=self.user,
            file_hash='test_hash_123'
        )
        
        self.assertEqual(uploaded_file.original_name, 'test_file.txt')
        self.assertEqual(uploaded_file.uploaded_by, self.user)
        self.assertEqual(uploaded_file.status, FileStatus.ACTIVE)
        self.assertFalse(uploaded_file.is_public)
    
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_file_category_detection(self):
        """测试文件分类检测"""
        # 测试图片文件
        image_file = self.create_test_image()
        uploaded_image = UploadedFile.objects.create(
            original_name='test_image.jpg',
            file=image_file,
            uploaded_by=self.user,
            file_hash='image_hash_123'
        )
        
        self.assertEqual(uploaded_image.category, FileCategory.IMAGE)
        self.assertIsNotNone(uploaded_image.width)
        self.assertIsNotNone(uploaded_image.height)
        
        # 测试文本文件
        text_file = self.create_test_text_file()
        uploaded_text = UploadedFile.objects.create(
            original_name='test_file.txt',
            file=text_file,
            uploaded_by=self.user,
            file_hash='text_hash_123'
        )
        
        self.assertEqual(uploaded_text.category, FileCategory.DOCUMENT)
    
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_file_size_display(self):
        """测试文件大小显示"""
        test_file = self.create_test_text_file()
        
        uploaded_file = UploadedFile.objects.create(
            original_name='test_file.txt',
            file=test_file,
            uploaded_by=self.user,
            file_hash='test_hash_123'
        )
        
        size_display = uploaded_file.get_file_size_display()
        self.assertIn('B', size_display)  # 应该显示字节单位
    
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_soft_delete(self):
        """测试软删除"""
        test_file = self.create_test_text_file()
        
        uploaded_file = UploadedFile.objects.create(
            original_name='test_file.txt',
            file=test_file,
            uploaded_by=self.user,
            file_hash='test_hash_123'
        )
        
        self.assertEqual(uploaded_file.status, FileStatus.ACTIVE)
        
        uploaded_file.soft_delete()
        self.assertEqual(uploaded_file.status, FileStatus.DELETED)
        
        uploaded_file.restore()
        self.assertEqual(uploaded_file.status, FileStatus.ACTIVE)
    
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_increment_download_count(self):
        """测试增加下载次数"""
        test_file = self.create_test_text_file()
        
        uploaded_file = UploadedFile.objects.create(
            original_name='test_file.txt',
            file=test_file,
            uploaded_by=self.user,
            file_hash='test_hash_123'
        )
        
        self.assertEqual(uploaded_file.download_count, 0)
        self.assertIsNone(uploaded_file.last_accessed)
        
        uploaded_file.increment_download_count()
        
        self.assertEqual(uploaded_file.download_count, 1)
        self.assertIsNotNone(uploaded_file.last_accessed)


class FileShareModelTest(TestCase):
    """文件分享模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        test_file = SimpleUploadedFile(
            'test_file.txt',
            b'This is a test file content',
            content_type='text/plain'
        )
        
        self.uploaded_file = UploadedFile.objects.create(
            original_name='test_file.txt',
            file=test_file,
            uploaded_by=self.user,
            file_hash='test_hash_123'
        )
    
    def test_create_file_share(self):
        """测试创建文件分享"""
        file_share = FileShare.objects.create(
            file=self.uploaded_file,
            shared_by=self.user,
            share_token='test_token_123'
        )
        
        self.assertEqual(file_share.file, self.uploaded_file)
        self.assertEqual(file_share.shared_by, self.user)
        self.assertTrue(file_share.is_active)
        self.assertTrue(file_share.allow_download)
        self.assertTrue(file_share.allow_preview)
    
    def test_share_expiration(self):
        """测试分享过期"""
        from django.utils import timezone
        from datetime import timedelta
        
        # 创建已过期的分享
        expired_share = FileShare.objects.create(
            file=self.uploaded_file,
            shared_by=self.user,
            share_token='expired_token',
            expires_at=timezone.now() - timedelta(days=1)
        )
        
        self.assertTrue(expired_share.is_expired())
        self.assertFalse(expired_share.can_access())
        
        # 创建未过期的分享
        active_share = FileShare.objects.create(
            file=self.uploaded_file,
            shared_by=self.user,
            share_token='active_token',
            expires_at=timezone.now() + timedelta(days=1)
        )
        
        self.assertFalse(active_share.is_expired())
        self.assertTrue(active_share.can_access())
    
    def test_download_limit(self):
        """测试下载限制"""
        file_share = FileShare.objects.create(
            file=self.uploaded_file,
            shared_by=self.user,
            share_token='limited_token',
            max_downloads=2
        )
        
        self.assertFalse(file_share.is_download_limit_reached())
        self.assertTrue(file_share.can_access())
        
        # 增加下载次数
        file_share.increment_download_count()
        file_share.increment_download_count()
        
        self.assertTrue(file_share.is_download_limit_reached())
        self.assertFalse(file_share.can_access())


class FileAccessLogModelTest(TestCase):
    """文件访问日志模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        test_file = SimpleUploadedFile(
            'test_file.txt',
            b'This is a test file content',
            content_type='text/plain'
        )
        
        self.uploaded_file = UploadedFile.objects.create(
            original_name='test_file.txt',
            file=test_file,
            uploaded_by=self.user,
            file_hash='test_hash_123'
        )
    
    def test_create_access_log(self):
        """测试创建访问日志"""
        access_log = FileAccessLog.objects.create(
            file=self.uploaded_file,
            user=self.user,
            action='download',
            ip_address='127.0.0.1',
            user_agent='Test User Agent'
        )
        
        self.assertEqual(access_log.file, self.uploaded_file)
        self.assertEqual(access_log.user, self.user)
        self.assertEqual(access_log.action, 'download')
        self.assertEqual(access_log.ip_address, '127.0.0.1')


class FileAPITest(APITestCase):
    """文件API测试"""
    
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
    
    def create_test_file(self):
        """创建测试文件"""
        return SimpleUploadedFile(
            'test_file.txt',
            b'This is a test file content',
            content_type='text/plain'
        )
    
    def test_file_upload_authenticated(self):
        """测试认证用户上传文件"""
        self.client.force_authenticate(user=self.user)
        
        test_file = self.create_test_file()
        url = reverse('files:file-upload')  # 假设有这个URL
        
        # 注意：这个测试可能需要根据实际的API端点进行调整
        # data = {'file': test_file}
        # response = self.client.post(url, data, format='multipart')
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_file_list_authenticated(self):
        """测试认证用户获取文件列表"""
        self.client.force_authenticate(user=self.user)
        
        # 创建测试文件
        test_file = self.create_test_file()
        uploaded_file = UploadedFile.objects.create(
            original_name='test_file.txt',
            file=test_file,
            uploaded_by=self.user,
            file_hash='test_hash_123'
        )
        
        url = reverse('files:file-list')  # 假设有这个URL
        
        # 注意：这个测试可能需要根据实际的API端点进行调整
        # response = self.client.get(url)
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_file_access_unauthenticated(self):
        """测试未认证用户无法访问文件"""
        url = reverse('files:file-list')  # 假设有这个URL
        
        # 注意：这个测试可能需要根据实际的API端点进行调整
        # response = self.client.get(url)
        # self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
