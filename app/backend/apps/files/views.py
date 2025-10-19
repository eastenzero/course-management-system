"""
文件管理视图
"""

import hashlib
import secrets
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.db.models import Count, Sum, Q
from django.utils import timezone
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.openapi import OpenApiTypes

from .models import UploadedFile, FileShare, FileAccessLog, FileCategory, FileStatus
from .serializers import (
    UploadedFileSerializer, FileUploadSerializer, FileShareSerializer,
    FileAccessLogSerializer, FileStatsSerializer, BulkFileOperationSerializer
)
from .utils import get_client_ip, calculate_file_hash


class FileListCreateView(generics.ListCreateAPIView):
    """文件列表和上传视图"""
    
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'status', 'is_public']
    search_fields = ['original_name', 'mime_type']
    ordering_fields = ['created_at', 'file_size', 'download_count']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return FileUploadSerializer
        return UploadedFileSerializer
    
    def get_queryset(self):
        """根据用户权限返回文件列表"""
        user = self.request.user
        
        if user.user_type == 'admin':
            # 管理员可以看到所有文件
            return UploadedFile.objects.all()
        else:
            # 普通用户只能看到自己上传的文件和公开文件
            return UploadedFile.objects.filter(
                Q(uploaded_by=user) | Q(is_public=True),
                status=FileStatus.ACTIVE
            )
    
    @extend_schema(
        tags=['文件管理'],
        summary='上传文件',
        description='上传文件到服务器'
    )
    def post(self, request, *args, **kwargs):
        """上传文件"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 计算文件哈希
        file_obj = serializer.validated_data['file']
        file_hash = calculate_file_hash(file_obj)
        
        # 检查是否已存在相同文件
        existing_file = UploadedFile.objects.filter(
            file_hash=file_hash,
            uploaded_by=request.user
        ).first()
        
        if existing_file:
            return Response({
                'message': '文件已存在',
                'data': UploadedFileSerializer(existing_file, context={'request': request}).data
            }, status=status.HTTP_200_OK)
        
        # 保存文件
        serializer.validated_data['file_hash'] = file_hash
        file_instance = serializer.save()
        
        # 记录访问日志
        FileAccessLog.objects.create(
            file=file_instance,
            user=request.user,
            action='upload',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({
            'message': '文件上传成功',
            'data': UploadedFileSerializer(file_instance, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)


class FileDetailView(generics.RetrieveUpdateDestroyAPIView):
    """文件详情视图"""
    
    serializer_class = UploadedFileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'admin':
            return UploadedFile.objects.all()
        return UploadedFile.objects.filter(
            Q(uploaded_by=user) | Q(is_public=True),
            status=FileStatus.ACTIVE
        )
    
    def get_object(self):
        """获取文件对象并记录访问"""
        obj = super().get_object()
        
        # 记录访问日志
        FileAccessLog.objects.create(
            file=obj,
            user=self.request.user,
            action='view',
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        
        return obj
    
    def destroy(self, request, *args, **kwargs):
        """软删除文件"""
        instance = self.get_object()
        
        # 检查权限
        if instance.uploaded_by != request.user and request.user.user_type != 'admin':
            return Response({
                'error': '您没有权限删除此文件'
            }, status=status.HTTP_403_FORBIDDEN)
        
        instance.soft_delete()
        
        return Response({
            'message': '文件删除成功'
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_file(request, file_id):
    """下载文件"""
    try:
        file_obj = get_object_or_404(UploadedFile, id=file_id, status=FileStatus.ACTIVE)
        
        # 检查权限
        if not file_obj.is_public and file_obj.uploaded_by != request.user and request.user.user_type != 'admin':
            return Response({
                'error': '您没有权限下载此文件'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 增加下载次数
        file_obj.increment_download_count()
        
        # 记录访问日志
        FileAccessLog.objects.create(
            file=file_obj,
            user=request.user,
            action='download',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # 返回文件
        response = HttpResponse(file_obj.file.read(), content_type=file_obj.mime_type)
        response['Content-Disposition'] = f'attachment; filename="{file_obj.original_name}"'
        response['Content-Length'] = file_obj.file_size
        
        return response
        
    except Exception as e:
        return Response({
            'error': f'下载失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FileShareListCreateView(generics.ListCreateAPIView):
    """文件分享列表和创建视图"""
    
    serializer_class = FileShareSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """获取用户的分享记录"""
        return FileShare.objects.filter(shared_by=self.request.user)
    
    def perform_create(self, serializer):
        """创建分享记录"""
        # 生成分享令牌
        share_token = secrets.token_urlsafe(16)
        serializer.save(
            shared_by=self.request.user,
            share_token=share_token
        )


@api_view(['GET', 'POST'])
@permission_classes([permissions.AllowAny])
def access_shared_file(request, share_token):
    """访问分享文件"""
    try:
        share = get_object_or_404(FileShare, share_token=share_token)
        
        # 检查分享是否可访问
        if not share.can_access():
            return Response({
                'error': '分享链接已失效'
            }, status=status.HTTP_410_GONE)
        
        if request.method == 'GET':
            # 检查密码
            password = request.query_params.get('password')
            if share.password and password != share.password:
                return Response({
                    'error': '密码错误',
                    'requires_password': True
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # 返回文件信息
            serializer = FileShareSerializer(share, context={'request': request})
            return Response({
                'message': '获取分享文件信息成功',
                'data': serializer.data
            })
        
        elif request.method == 'POST':
            # 下载文件
            action = request.data.get('action', 'download')
            password = request.data.get('password')
            
            # 验证密码
            if share.password and password != share.password:
                return Response({
                    'error': '密码错误'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            if action == 'download' and not share.allow_download:
                return Response({
                    'error': '不允许下载'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # 增加下载次数
            share.increment_download_count()
            
            # 记录访问日志
            FileAccessLog.objects.create(
                file=share.file,
                user=request.user if request.user.is_authenticated else None,
                action=action,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                share=share
            )
            
            if action == 'download':
                # 返回文件
                response = HttpResponse(share.file.file.read(), content_type=share.file.mime_type)
                response['Content-Disposition'] = f'attachment; filename="{share.file.original_name}"'
                response['Content-Length'] = share.file.file_size
                return response
            
            return Response({'message': '操作成功'})
            
    except Exception as e:
        return Response({
            'error': f'访问失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def file_statistics(request):
    """获取文件统计信息"""
    user = request.user
    
    # 基础查询
    if user.user_type == 'admin':
        files_query = UploadedFile.objects.filter(status=FileStatus.ACTIVE)
    else:
        files_query = UploadedFile.objects.filter(
            uploaded_by=user,
            status=FileStatus.ACTIVE
        )
    
    # 总体统计
    total_files = files_query.count()
    total_size = files_query.aggregate(total=Sum('file_size'))['total'] or 0
    
    # 按分类统计
    files_by_category = {}
    for category in FileCategory.choices:
        count = files_query.filter(category=category[0]).count()
        files_by_category[category[1]] = count
    
    # 按月份统计
    from django.db.models.functions import TruncMonth
    files_by_month = files_query.annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    # 热门下载
    top_downloaded = files_query.order_by('-download_count')[:10]
    
    # 最近上传
    recent_uploads = files_query.order_by('-created_at')[:10]
    
    stats_data = {
        'total_files': total_files,
        'total_size': total_size,
        'total_size_display': _format_file_size(total_size),
        'files_by_category': files_by_category,
        'files_by_month': {
            item['month'].strftime('%Y-%m'): item['count']
            for item in files_by_month
        },
        'top_downloaded': UploadedFileSerializer(
            top_downloaded, many=True, context={'request': request}
        ).data,
        'recent_uploads': UploadedFileSerializer(
            recent_uploads, many=True, context={'request': request}
        ).data
    }
    
    return Response({
        'message': '获取统计信息成功',
        'data': stats_data
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def bulk_file_operation(request):
    """批量文件操作"""
    serializer = BulkFileOperationSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    
    file_ids = serializer.validated_data['file_ids']
    action = serializer.validated_data['action']
    
    files = UploadedFile.objects.filter(id__in=file_ids)
    updated_count = 0
    
    for file_obj in files:
        if action == 'delete':
            file_obj.soft_delete()
            updated_count += 1
        elif action == 'restore':
            file_obj.restore()
            updated_count += 1
        elif action == 'make_public':
            file_obj.is_public = True
            file_obj.save(update_fields=['is_public'])
            updated_count += 1
        elif action == 'make_private':
            file_obj.is_public = False
            file_obj.save(update_fields=['is_public'])
            updated_count += 1
    
    return Response({
        'message': f'批量操作成功，处理了 {updated_count} 个文件',
        'updated_count': updated_count
    })


def _format_file_size(size_bytes):
    """格式化文件大小"""
    if size_bytes == 0:
        return "0 B"
    
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"
