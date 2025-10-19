from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import logout
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.openapi import OpenApiTypes

from .models import User, UserPreference
from .serializers import (
    UserSerializer, UserProfileSerializer, LoginSerializer,
    ChangePasswordSerializer, RegisterSerializer, UserPreferenceSerializer
)
from .permissions import IsOwnerOrAdmin, IsAdminUser
from rest_framework.permissions import AllowAny



class CustomTokenObtainPairView(TokenObtainPairView):
    """自定义JWT登录视图"""

    @extend_schema(
        tags=['用户管理'],
        summary='用户登录',
        description='使用用户名/邮箱和密码进行登录，返回JWT访问令牌',
        request=LoginSerializer,
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'code': {'type': 'integer', 'example': 200},
                    'message': {'type': 'string', 'example': '登录成功'},
                    'data': {
                        'type': 'object',
                        'properties': {
                            'access': {'type': 'string', 'description': 'JWT访问令牌'},
                            'refresh': {'type': 'string', 'description': 'JWT刷新令牌'},
                            'user': {'$ref': '#/components/schemas/UserProfile'}
                        }
                    }
                }
            },
            400: {
                'type': 'object',
                'properties': {
                    'code': {'type': 'integer', 'example': 400},
                    'message': {'type': 'string', 'example': '用户名或密码错误'}
                }
            }
        },
        examples=[
            OpenApiExample(
                'Login Example',
                summary='登录示例',
                description='使用用户名和密码登录',
                value={
                    'username': 'student001',
                    'password': 'password123'
                },
                request_only=True,
            ),
        ]
    )
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        # 为兼容旧前端，除 data 内外，额外在顶层回显 access/refresh/user 字段
        access_token = str(refresh.access_token)
        user_data = UserProfileSerializer(user).data

        return Response({
            'code': 200,
            'message': '登录成功',
            'data': {
                'access': access_token,
                'refresh': str(refresh),
                'user': user_data
            },
            'access': access_token,
            'refresh': str(refresh),
            'user': user_data
        })


@extend_schema(
    tags=['用户管理'],
    summary='用户登出',
    description='用户登出，将刷新令牌加入黑名单',
    request={
        'type': 'object',
        'properties': {
            'refresh': {
                'type': 'string',
                'description': 'JWT刷新令牌'
            }
        },
        'required': ['refresh']
    },
    responses={
        200: {
            'type': 'object',
            'properties': {
                'code': {'type': 'integer', 'example': 200},
                'message': {'type': 'string', 'example': '登出成功'}
            }
        },
        400: {
            'type': 'object',
            'properties': {
                'code': {'type': 'integer', 'example': 400},
                'message': {'type': 'string', 'example': '登出失败'}
            }
        }
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """登出视图"""
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()

        logout(request)
        return Response({
            'code': 200,
            'message': '登出成功',
            'data': None
        })
    except Exception as e:
        return Response({
            'code': 400,
            'message': '登出失败',
            'data': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """用户资料视图"""

    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'code': 200,
            'message': '获取用户信息成功',
            'data': serializer.data
        })

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            'code': 200,
            'message': '更新用户信息成功',
            'data': serializer.data
        })


class RegisterView(generics.GenericAPIView):
    """匿名注册视图（默认注册为学生）"""
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['用户管理'],
        summary='用户注册',
        request=RegisterSerializer,
        responses={200: UserProfileSerializer},
        examples=[
            OpenApiExample(
                '注册示例',
                value={
                    'username': 'newstudent',
                    'email': 'new@example.com',
                    'password': 'Password123!',
                    'password_confirm': 'Password123!',
                    'first_name': '新',
                    'last_name': '同学'
                }
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'code': 201,
            'message': '注册成功',
            'data': UserProfileSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class ChangePasswordView(generics.GenericAPIView):
    """修改密码视图"""

    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'code': 200,
            'message': '密码修改成功',
            'data': None
        })


class UserListCreateView(generics.ListCreateAPIView):
    """用户列表和创建视图（管理员专用）"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['user_type', 'department', 'is_active']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'employee_id', 'student_id']
    ordering_fields = ['date_joined', 'username']
    ordering = ['-date_joined']

    def get_permissions(self):
        """只有管理员可以创建用户"""
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), IsAdminUser()]
        return [permissions.IsAuthenticated()]

    @method_decorator(cache_page(60 * 5))  # 缓存5分钟
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = UserProfileSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = UserProfileSerializer(queryset, many=True)
        return Response({
            'code': 200,
            'message': '获取用户列表成功',
            'data': serializer.data
        })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({
            'code': 201,
            'message': '创建用户成功',
            'data': UserProfileSerializer(serializer.instance).data
        }, status=status.HTTP_201_CREATED)


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """用户详情视图（管理员专用）"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = UserProfileSerializer(instance)
        return Response({
            'code': 200,
            'message': '获取用户详情成功',
            'data': serializer.data
        })

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            'code': 200,
            'message': '更新用户成功',
            'data': UserProfileSerializer(serializer.instance).data
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'code': 200,
            'message': '删除用户成功',
            'data': None
        })


class UserPreferenceView(generics.RetrieveUpdateAPIView):
    """用户偏好设置视图"""

    serializer_class = UserPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """获取或创建用户的偏好设置"""
        preference, created = UserPreference.objects.get_or_create(
            user=self.request.user
        )
        return preference

    @extend_schema(
        summary="获取用户偏好设置",
        description="获取当前用户的偏好设置"
    )
    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'code': 200,
            'message': '获取用户偏好设置成功',
            'data': serializer.data
        })

    @extend_schema(
        summary="更新用户偏好设置",
        description="更新当前用户的偏好设置"
    )
    def put(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            'code': 200,
            'message': '更新用户偏好设置成功',
            'data': serializer.data
        })

    @extend_schema(
        summary="部分更新用户偏好设置",
        description="部分更新当前用户的偏好设置"
    )
    def patch(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.put(request, *args, **kwargs)
