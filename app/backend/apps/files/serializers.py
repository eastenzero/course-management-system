"""
文件管理序列化器
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UploadedFile, FileShare, FileAccessLog

User = get_user_model()


class UploadedFileSerializer(serializers.ModelSerializer):
    """上传文件序列化器"""
    
    file_url = serializers.SerializerMethodField()
    file_size_display = serializers.SerializerMethodField()
    uploaded_by_name = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()
    can_share = serializers.SerializerMethodField()
    
    class Meta:
        model = UploadedFile
        fields = [
            'id', 'original_name', 'file', 'file_url', 'file_size', 'file_size_display',
            'mime_type', 'file_extension', 'category', 'width', 'height',
            'file_hash', 'uploaded_by', 'uploaded_by_name', 'status', 'is_public',
            'created_at', 'updated_at', 'download_count', 'last_accessed',
            'metadata', 'can_delete', 'can_share'
        ]
        read_only_fields = [
            'id', 'file_size', 'mime_type', 'file_extension', 'category',
            'width', 'height', 'file_hash', 'uploaded_by', 'created_at',
            'updated_at', 'download_count', 'last_accessed'
        ]
    
    def get_file_url(self, obj):
        """获取文件URL"""
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return obj.get_file_url()
    
    def get_file_size_display(self, obj):
        """获取友好的文件大小显示"""
        return obj.get_file_size_display()
    
    def get_uploaded_by_name(self, obj):
        """获取上传者姓名"""
        if obj.uploaded_by:
            return f"{obj.uploaded_by.first_name} {obj.uploaded_by.last_name}".strip() or obj.uploaded_by.username
        return None
    
    def get_can_delete(self, obj):
        """检查是否可以删除"""
        request = self.context.get('request')
        if not request or not request.user:
            return False
        
        # 文件所有者或管理员可以删除
        return (
            obj.uploaded_by == request.user or
            request.user.user_type == 'admin'
        )
    
    def get_can_share(self, obj):
        """检查是否可以分享"""
        request = self.context.get('request')
        if not request or not request.user:
            return False
        
        # 文件所有者或管理员可以分享
        return (
            obj.uploaded_by == request.user or
            request.user.user_type == 'admin'
        )


class FileUploadSerializer(serializers.ModelSerializer):
    """文件上传序列化器"""
    
    file = serializers.FileField()
    
    class Meta:
        model = UploadedFile
        fields = ['file', 'original_name', 'is_public', 'content_type', 'object_id']
    
    def validate_file(self, value):
        """验证文件"""
        # 文件大小限制（100MB）
        max_size = 100 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError(f'文件大小不能超过 {max_size // (1024*1024)} MB')
        
        # 文件类型限制
        allowed_extensions = [
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp',  # 图片
            '.pdf', '.doc', '.docx', '.txt', '.rtf',  # 文档
            '.mp4', '.avi', '.mov', '.wmv',  # 视频
            '.mp3', '.wav', '.flac',  # 音频
            '.zip', '.rar', '.7z',  # 压缩包
            '.xlsx', '.xls', '.pptx', '.ppt'  # Office文档
        ]
        
        file_extension = '.' + value.name.split('.')[-1].lower() if '.' in value.name else ''
        if file_extension not in allowed_extensions:
            raise serializers.ValidationError(f'不支持的文件类型: {file_extension}')
        
        return value
    
    def create(self, validated_data):
        """创建文件记录"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['uploaded_by'] = request.user
        
        # 设置原始文件名
        if not validated_data.get('original_name'):
            validated_data['original_name'] = validated_data['file'].name
        
        return super().create(validated_data)


class FileShareSerializer(serializers.ModelSerializer):
    """文件分享序列化器"""
    
    file_info = UploadedFileSerializer(source='file', read_only=True)
    shared_by_name = serializers.SerializerMethodField()
    share_url = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    is_download_limit_reached = serializers.SerializerMethodField()
    can_access = serializers.SerializerMethodField()
    
    class Meta:
        model = FileShare
        fields = [
            'id', 'file', 'file_info', 'shared_by', 'shared_by_name',
            'share_token', 'password', 'allow_download', 'allow_preview',
            'expires_at', 'max_downloads', 'download_count', 'is_active',
            'created_at', 'last_accessed', 'share_url', 'is_expired',
            'is_download_limit_reached', 'can_access'
        ]
        read_only_fields = [
            'id', 'shared_by', 'share_token', 'download_count',
            'created_at', 'last_accessed'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def get_shared_by_name(self, obj):
        """获取分享者姓名"""
        if obj.shared_by:
            return f"{obj.shared_by.first_name} {obj.shared_by.last_name}".strip() or obj.shared_by.username
        return None
    
    def get_share_url(self, obj):
        """获取分享URL"""
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/api/files/share/{obj.share_token}/')
        return f'/api/files/share/{obj.share_token}/'
    
    def get_is_expired(self, obj):
        """检查是否过期"""
        return obj.is_expired()
    
    def get_is_download_limit_reached(self, obj):
        """检查是否达到下载限制"""
        return obj.is_download_limit_reached()
    
    def get_can_access(self, obj):
        """检查是否可以访问"""
        return obj.can_access()


class FileAccessLogSerializer(serializers.ModelSerializer):
    """文件访问日志序列化器"""
    
    file_name = serializers.CharField(source='file.original_name', read_only=True)
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = FileAccessLog
        fields = [
            'id', 'file', 'file_name', 'user', 'user_name', 'action',
            'ip_address', 'user_agent', 'share', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_user_name(self, obj):
        """获取用户姓名"""
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username
        return '匿名用户'


class FileStatsSerializer(serializers.Serializer):
    """文件统计序列化器"""
    
    total_files = serializers.IntegerField()
    total_size = serializers.IntegerField()
    total_size_display = serializers.CharField()
    files_by_category = serializers.DictField()
    files_by_month = serializers.DictField()
    top_downloaded = serializers.ListField()
    recent_uploads = serializers.ListField()


class BulkFileOperationSerializer(serializers.Serializer):
    """批量文件操作序列化器"""
    
    file_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        max_length=100
    )
    action = serializers.ChoiceField(choices=['delete', 'restore', 'make_public', 'make_private'])
    
    def validate_file_ids(self, value):
        """验证文件ID列表"""
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError('用户未认证')
        
        # 检查文件是否存在且用户有权限操作
        files = UploadedFile.objects.filter(id__in=value)
        if files.count() != len(value):
            raise serializers.ValidationError('部分文件不存在')
        
        # 检查权限
        for file in files:
            if file.uploaded_by != request.user and request.user.user_type != 'admin':
                raise serializers.ValidationError(f'您没有权限操作文件: {file.original_name}')
        
        return value
