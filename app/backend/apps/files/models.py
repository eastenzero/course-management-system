"""
文件管理模型
"""

import os
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from PIL import Image
import magic

User = get_user_model()


def upload_to(instance, filename):
    """生成文件上传路径"""
    # 按年月分目录
    date_path = timezone.now().strftime('%Y/%m')
    # 生成唯一文件名
    ext = filename.split('.')[-1] if '.' in filename else ''
    unique_filename = f"{uuid.uuid4().hex}.{ext}" if ext else str(uuid.uuid4().hex)
    return f"uploads/{date_path}/{unique_filename}"


class FileCategory(models.TextChoices):
    """文件分类"""
    DOCUMENT = 'document', '文档'
    IMAGE = 'image', '图片'
    VIDEO = 'video', '视频'
    AUDIO = 'audio', '音频'
    ARCHIVE = 'archive', '压缩包'
    OTHER = 'other', '其他'


class FileStatus(models.TextChoices):
    """文件状态"""
    UPLOADING = 'uploading', '上传中'
    ACTIVE = 'active', '正常'
    DELETED = 'deleted', '已删除'
    QUARANTINED = 'quarantined', '隔离'


class UploadedFile(models.Model):
    """上传文件模型"""
    
    # 基本信息
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_name = models.CharField(max_length=255, verbose_name='原始文件名')
    file = models.FileField(upload_to=upload_to, verbose_name='文件')
    
    # 文件属性
    file_size = models.PositiveBigIntegerField(verbose_name='文件大小(字节)')
    mime_type = models.CharField(max_length=100, verbose_name='MIME类型')
    file_extension = models.CharField(max_length=10, verbose_name='文件扩展名')
    category = models.CharField(
        max_length=20,
        choices=FileCategory.choices,
        default=FileCategory.OTHER,
        verbose_name='文件分类'
    )
    
    # 图片特有属性
    width = models.PositiveIntegerField(null=True, blank=True, verbose_name='图片宽度')
    height = models.PositiveIntegerField(null=True, blank=True, verbose_name='图片高度')
    
    # 文件哈希值（用于去重）
    file_hash = models.CharField(max_length=64, db_index=True, verbose_name='文件哈希')
    
    # 上传者信息
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='uploaded_files',
        verbose_name='上传者'
    )
    
    # 关联对象（通用外键）
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='关联内容类型'
    )
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name='关联对象ID')
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # 状态和权限
    status = models.CharField(
        max_length=20,
        choices=FileStatus.choices,
        default=FileStatus.ACTIVE,
        verbose_name='文件状态'
    )
    is_public = models.BooleanField(default=False, verbose_name='是否公开')
    
    # 时间字段
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    # 访问统计
    download_count = models.PositiveIntegerField(default=0, verbose_name='下载次数')
    last_accessed = models.DateTimeField(null=True, blank=True, verbose_name='最后访问时间')
    
    # 元数据
    metadata = models.JSONField(default=dict, blank=True, verbose_name='文件元数据')
    
    class Meta:
        db_table = 'uploaded_files'
        verbose_name = '上传文件'
        verbose_name_plural = '上传文件'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['uploaded_by', 'status']),
            models.Index(fields=['category']),
            models.Index(fields=['file_hash']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.original_name
    
    def save(self, *args, **kwargs):
        """保存时自动设置文件属性"""
        if self.file and not self.file_size:
            self.file_size = self.file.size
            
        if self.file and not self.mime_type:
            # 检测MIME类型
            try:
                self.mime_type = magic.from_buffer(self.file.read(1024), mime=True)
                self.file.seek(0)  # 重置文件指针
            except:
                self.mime_type = 'application/octet-stream'
        
        if not self.file_extension and self.original_name:
            self.file_extension = os.path.splitext(self.original_name)[1].lower()
        
        # 设置文件分类
        if not self.category or self.category == FileCategory.OTHER:
            self.category = self._detect_category()
        
        # 处理图片
        if self.category == FileCategory.IMAGE and self.file:
            self._process_image()
        
        super().save(*args, **kwargs)
    
    def _detect_category(self) -> str:
        """检测文件分类"""
        if self.mime_type:
            if self.mime_type.startswith('image/'):
                return FileCategory.IMAGE
            elif self.mime_type.startswith('video/'):
                return FileCategory.VIDEO
            elif self.mime_type.startswith('audio/'):
                return FileCategory.AUDIO
            elif self.mime_type in ['application/zip', 'application/x-rar', 'application/x-7z-compressed']:
                return FileCategory.ARCHIVE
            elif self.mime_type in ['application/pdf', 'application/msword', 'text/plain']:
                return FileCategory.DOCUMENT
        
        # 根据扩展名判断
        ext = self.file_extension.lower()
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
            return FileCategory.IMAGE
        elif ext in ['.mp4', '.avi', '.mov', '.wmv', '.flv']:
            return FileCategory.VIDEO
        elif ext in ['.mp3', '.wav', '.flac', '.aac']:
            return FileCategory.AUDIO
        elif ext in ['.zip', '.rar', '.7z', '.tar', '.gz']:
            return FileCategory.ARCHIVE
        elif ext in ['.pdf', '.doc', '.docx', '.txt', '.rtf']:
            return FileCategory.DOCUMENT
        
        return FileCategory.OTHER
    
    def _process_image(self):
        """处理图片文件"""
        try:
            with Image.open(self.file) as img:
                self.width, self.height = img.size
                
                # 保存图片元数据
                self.metadata.update({
                    'format': img.format,
                    'mode': img.mode,
                    'has_transparency': img.mode in ('RGBA', 'LA') or 'transparency' in img.info
                })
        except Exception as e:
            print(f"Error processing image: {e}")
    
    def get_file_url(self):
        """获取文件URL"""
        if self.file:
            return self.file.url
        return None
    
    def get_file_size_display(self):
        """获取友好的文件大小显示"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def increment_download_count(self):
        """增加下载次数"""
        self.download_count += 1
        self.last_accessed = timezone.now()
        self.save(update_fields=['download_count', 'last_accessed'])
    
    def soft_delete(self):
        """软删除文件"""
        self.status = FileStatus.DELETED
        self.save(update_fields=['status'])
    
    def restore(self):
        """恢复文件"""
        self.status = FileStatus.ACTIVE
        self.save(update_fields=['status'])


class FileShare(models.Model):
    """文件分享模型"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.ForeignKey(
        UploadedFile,
        on_delete=models.CASCADE,
        related_name='shares',
        verbose_name='文件'
    )
    
    # 分享者
    shared_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shared_files',
        verbose_name='分享者'
    )
    
    # 分享设置
    share_token = models.CharField(max_length=32, unique=True, verbose_name='分享令牌')
    password = models.CharField(max_length=20, blank=True, verbose_name='访问密码')
    
    # 权限设置
    allow_download = models.BooleanField(default=True, verbose_name='允许下载')
    allow_preview = models.BooleanField(default=True, verbose_name='允许预览')
    
    # 时间限制
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name='过期时间')
    
    # 访问限制
    max_downloads = models.PositiveIntegerField(null=True, blank=True, verbose_name='最大下载次数')
    download_count = models.PositiveIntegerField(default=0, verbose_name='已下载次数')
    
    # 状态
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    
    # 时间字段
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    last_accessed = models.DateTimeField(null=True, blank=True, verbose_name='最后访问时间')
    
    class Meta:
        db_table = 'file_shares'
        verbose_name = '文件分享'
        verbose_name_plural = '文件分享'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.file.original_name} - {self.share_token}"
    
    def is_expired(self):
        """检查是否过期"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def is_download_limit_reached(self):
        """检查是否达到下载限制"""
        if self.max_downloads:
            return self.download_count >= self.max_downloads
        return False
    
    def can_access(self):
        """检查是否可以访问"""
        return (
            self.is_active and
            not self.is_expired() and
            not self.is_download_limit_reached()
        )
    
    def increment_download_count(self):
        """增加下载次数"""
        self.download_count += 1
        self.last_accessed = timezone.now()
        self.save(update_fields=['download_count', 'last_accessed'])


class FileAccessLog(models.Model):
    """文件访问日志"""
    
    file = models.ForeignKey(
        UploadedFile,
        on_delete=models.CASCADE,
        related_name='access_logs',
        verbose_name='文件'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='访问用户'
    )
    
    # 访问信息
    action = models.CharField(max_length=20, verbose_name='操作类型')  # view, download, upload
    ip_address = models.GenericIPAddressField(verbose_name='IP地址')
    user_agent = models.TextField(blank=True, verbose_name='用户代理')
    
    # 分享访问
    share = models.ForeignKey(
        FileShare,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='分享记录'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='访问时间')
    
    class Meta:
        db_table = 'file_access_logs'
        verbose_name = '文件访问日志'
        verbose_name_plural = '文件访问日志'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['file', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.file.original_name} - {self.action} - {self.created_at}"
