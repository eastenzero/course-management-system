"""
通知系统视图
"""

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import Notification, NotificationPreference, NotificationTemplate
from .serializers import (
    NotificationSerializer, NotificationListSerializer,
    NotificationMarkReadSerializer, NotificationPreferenceSerializer,
    NotificationTemplateSerializer, CreateNotificationSerializer
)
from .services import notification_service

User = get_user_model()


class NotificationPagination(PageNumberPagination):
    """通知分页器"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class NotificationListView(generics.ListAPIView):
    """通知列表视图"""
    
    serializer_class = NotificationListSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = NotificationPagination
    
    def get_queryset(self):
        """获取当前用户的通知列表"""
        user = self.request.user
        queryset = Notification.objects.filter(recipient=user)
        
        # 过滤参数
        is_read = self.request.query_params.get('is_read')
        notification_type = self.request.query_params.get('type')
        priority = self.request.query_params.get('priority')
        
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
        
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        if priority:
            queryset = queryset.filter(priority=priority)
        
        return queryset.select_related('sender').order_by('-created_at')
    
    @extend_schema(
        summary="获取通知列表",
        description="获取当前用户的通知列表，支持分页和过滤",
        parameters=[
            OpenApiParameter(
                name='is_read',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='是否已读过滤'
            ),
            OpenApiParameter(
                name='type',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='通知类型过滤'
            ),
            OpenApiParameter(
                name='priority',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='优先级过滤'
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class NotificationDetailView(generics.RetrieveAPIView):
    """通知详情视图"""
    
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """只能查看自己的通知"""
        return Notification.objects.filter(recipient=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        """获取通知详情并标记为已读"""
        instance = self.get_object()
        
        # 自动标记为已读
        if not instance.is_read:
            instance.mark_as_read()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @extend_schema(
        summary="获取通知详情",
        description="获取指定通知的详细信息，会自动标记为已读"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(
    summary="标记通知为已读",
    description="批量标记通知为已读状态",
    request=NotificationMarkReadSerializer,
    responses={200: {"description": "标记成功"}}
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notifications_read(request):
    """标记通知为已读"""
    serializer = NotificationMarkReadSerializer(data=request.data)
    
    if serializer.is_valid():
        notification_ids = serializer.validated_data['notification_ids']
        
        # 只能标记自己的通知
        notifications = Notification.objects.filter(
            id__in=notification_ids,
            recipient=request.user,
            is_read=False
        )
        
        # 批量更新
        updated_count = notifications.update(
            is_read=True,
            read_at=timezone.now()
        )
        
        return Response({
            'message': f'成功标记 {updated_count} 条通知为已读',
            'updated_count': updated_count
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="标记所有通知为已读",
    description="标记当前用户的所有未读通知为已读",
    responses={200: {"description": "标记成功"}}
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_notifications_read(request):
    """标记所有通知为已读"""
    updated_count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(
        is_read=True,
        read_at=timezone.now()
    )
    
    return Response({
        'message': f'成功标记 {updated_count} 条通知为已读',
        'updated_count': updated_count
    })


@extend_schema(
    summary="获取未读通知数量",
    description="获取当前用户的未读通知数量",
    responses={200: {"description": "未读通知数量"}}
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def unread_count(request):
    """获取未读通知数量"""
    count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()
    
    return Response({'unread_count': count})


class NotificationPreferenceView(generics.RetrieveUpdateAPIView):
    """通知偏好设置视图"""
    
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """获取或创建用户的通知偏好"""
        preference, created = NotificationPreference.objects.get_or_create(
            user=self.request.user
        )
        return preference
    
    @extend_schema(
        summary="获取通知偏好设置",
        description="获取当前用户的通知偏好设置"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="更新通知偏好设置",
        description="更新当前用户的通知偏好设置"
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary="部分更新通知偏好设置",
        description="部分更新当前用户的通知偏好设置"
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class NotificationTemplateListView(generics.ListAPIView):
    """通知模板列表视图（管理员用）"""
    
    serializer_class = NotificationTemplateSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = NotificationTemplate.objects.filter(is_active=True)
    
    @extend_schema(
        summary="获取通知模板列表",
        description="获取所有可用的通知模板（仅管理员）"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(
    summary="创建通知",
    description="创建并发送通知给指定用户（仅管理员）",
    request=CreateNotificationSerializer,
    responses={201: {"description": "通知创建成功"}}
)
@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def create_notification(request):
    """创建通知（管理员功能）"""
    serializer = CreateNotificationSerializer(data=request.data)
    
    if serializer.is_valid():
        data = serializer.validated_data
        recipients = User.objects.filter(id__in=data['recipient_ids'])
        
        notifications = notification_service.create_bulk_notifications(
            recipients=list(recipients),
            title=data['title'],
            message=data['message'],
            notification_type=data['notification_type'],
            priority=data['priority'],
            sender=request.user,
            extra_data=data.get('extra_data', {})
        )
        
        return Response({
            'message': f'成功创建 {len(notifications)} 条通知',
            'notification_count': len(notifications)
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
