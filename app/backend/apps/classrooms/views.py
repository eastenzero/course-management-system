from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Building, Classroom
from .serializers import (
    BuildingSerializer, ClassroomSerializer, ClassroomListSerializer,
    ClassroomAvailabilitySerializer, ClassroomUtilizationSerializer
)
from apps.users.permissions import CanManageCourses, IsTeacherOrAdmin


class BuildingListCreateView(generics.ListCreateAPIView):
    """教学楼列表和创建视图"""

    queryset = Building.objects.all()
    serializer_class = BuildingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'code', 'address']
    ordering_fields = ['code', 'name', 'created_at']
    ordering = ['code']

    def get_permissions(self):
        """只有管理员可以创建教学楼"""
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), CanManageCourses()]
        return [permissions.IsAuthenticated()]

    @method_decorator(cache_page(60 * 10))  # 缓存10分钟
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'code': 200,
            'message': '获取教学楼列表成功',
            'data': serializer.data
        })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({
            'code': 201,
            'message': '创建教学楼成功',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)


class BuildingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """教学楼详情视图"""

    queryset = Building.objects.all()
    serializer_class = BuildingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        """只有管理员可以修改和删除教学楼"""
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated(), CanManageCourses()]
        return [permissions.IsAuthenticated()]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'code': 200,
            'message': '获取教学楼详情成功',
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
            'message': '更新教学楼成功',
            'data': serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # 检查是否有教室
        if instance.classrooms.exists():
            return Response({
                'code': 400,
                'message': '该教学楼下有教室，无法删除',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        self.perform_destroy(instance)
        return Response({
            'code': 200,
            'message': '删除教学楼成功',
            'data': None
        })


class ClassroomListCreateView(generics.ListCreateAPIView):
    """教室列表和创建视图"""

    queryset = Classroom.objects.select_related('building').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        'building', 'room_type', 'floor', 'is_available', 'is_active'
    ]
    search_fields = ['room_number', 'name', 'building__name', 'building__code']
    ordering_fields = ['building__code', 'room_number', 'capacity', 'created_at']
    ordering = ['building__code', 'room_number']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ClassroomListSerializer
        return ClassroomSerializer

    def get_permissions(self):
        """只有管理员可以创建教室"""
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), CanManageCourses()]
        return [permissions.IsAuthenticated()]

    @method_decorator(cache_page(60 * 5))  # 缓存5分钟
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # 添加容量过滤
        min_capacity = request.GET.get('min_capacity')
        if min_capacity:
            try:
                queryset = queryset.filter(capacity__gte=int(min_capacity))
            except ValueError:
                pass

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'code': 200,
            'message': '获取教室列表成功',
            'data': serializer.data
        })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({
            'code': 201,
            'message': '创建教室成功',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)


class ClassroomDetailView(generics.RetrieveUpdateDestroyAPIView):
    """教室详情视图"""

    queryset = Classroom.objects.select_related('building').all()
    serializer_class = ClassroomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        """只有管理员可以修改和删除教室"""
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated(), CanManageCourses()]
        return [permissions.IsAuthenticated()]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'code': 200,
            'message': '获取教室详情成功',
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
            'message': '更新教室成功',
            'data': serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # 检查是否有课程安排
        if instance.schedules.filter(status='active').exists():
            return Response({
                'code': 400,
                'message': '该教室有课程安排，无法删除',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        self.perform_destroy(instance)
        return Response({
            'code': 200,
            'message': '删除教室成功',
            'data': None
        })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsTeacherOrAdmin])
def classroom_availability(request):
    """查询教室可用性"""
    from apps.schedules.models import TimeSlot, Schedule

    semester = request.GET.get('semester')
    day_of_week = request.GET.get('day_of_week')
    time_slot_id = request.GET.get('time_slot_id')
    building_id = request.GET.get('building_id')
    min_capacity = request.GET.get('min_capacity')

    if not all([semester, day_of_week, time_slot_id]):
        return Response({
            'code': 400,
            'message': '缺少必要参数：semester, day_of_week, time_slot_id',
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        day_of_week = int(day_of_week)
        time_slot_id = int(time_slot_id)
        time_slot = TimeSlot.objects.get(id=time_slot_id)
    except (ValueError, TimeSlot.DoesNotExist):
        return Response({
            'code': 400,
            'message': '无效的参数',
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)

    # 获取教室列表
    classrooms = Classroom.objects.filter(is_active=True, is_available=True)

    if building_id:
        classrooms = classrooms.filter(building_id=building_id)

    if min_capacity:
        try:
            classrooms = classrooms.filter(capacity__gte=int(min_capacity))
        except ValueError:
            pass

    # 获取已占用的教室
    occupied_schedules = Schedule.objects.filter(
        semester=semester,
        day_of_week=day_of_week,
        time_slot_id=time_slot_id,
        status='active'
    ).select_related('course', 'classroom')

    occupied_classroom_ids = set(schedule.classroom_id for schedule in occupied_schedules)
    occupied_info = {
        schedule.classroom_id: f"{schedule.course.code} - {schedule.course.name}"
        for schedule in occupied_schedules
    }

    # 构建结果
    availability_data = []
    for classroom in classrooms:
        is_available = classroom.id not in occupied_classroom_ids
        occupied_by = occupied_info.get(classroom.id) if not is_available else None

        availability_data.append({
            'classroom_id': classroom.id,
            'classroom_name': str(classroom),
            'day_of_week': day_of_week,
            'time_slot_id': time_slot_id,
            'time_slot_name': time_slot.name,
            'is_available': is_available,
            'occupied_by': occupied_by
        })

    serializer = ClassroomAvailabilitySerializer(availability_data, many=True)
    return Response({
        'code': 200,
        'message': '获取教室可用性成功',
        'data': serializer.data
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, CanManageCourses])
def classroom_utilization(request):
    """教室利用率统计"""
    from apps.schedules.models import TimeSlot, Schedule

    semester = request.GET.get('semester')
    week_number = request.GET.get('week_number')
    building_id = request.GET.get('building_id')

    if not semester:
        return Response({
            'code': 400,
            'message': '缺少必要参数：semester',
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)

    # 获取教室列表
    classrooms = Classroom.objects.filter(is_active=True)
    if building_id:
        classrooms = classrooms.filter(building_id=building_id)

    # 获取时间段总数（一周7天 * 每天的时间段数）
    total_time_slots_per_week = TimeSlot.objects.filter(is_active=True).count() * 7

    utilization_data = []
    for classroom in classrooms:
        # 获取该教室的课程安排
        schedules = Schedule.objects.filter(
            classroom=classroom,
            semester=semester,
            status='active'
        )

        # 计算占用的时间段数
        occupied_time_slots = schedules.count()

        # 计算利用率
        utilization_rate = (occupied_time_slots / total_time_slots_per_week * 100) if total_time_slots_per_week > 0 else 0

        utilization_data.append({
            'classroom_id': classroom.id,
            'classroom_name': str(classroom),
            'total_time_slots': total_time_slots_per_week,
            'occupied_time_slots': occupied_time_slots,
            'utilization_rate': round(utilization_rate, 2),
            'week_number': int(week_number) if week_number else None,
            'semester': semester
        })

    # 按利用率排序
    utilization_data.sort(key=lambda x: x['utilization_rate'], reverse=True)

    serializer = ClassroomUtilizationSerializer(utilization_data, many=True)
    return Response({
        'code': 200,
        'message': '获取教室利用率成功',
        'data': serializer.data
    })
