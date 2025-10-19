from rest_framework import generics, status, permissions
import re
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db import transaction
from django.db import models
from django.http import HttpResponse

from .models import TimeSlot, Schedule
from .serializers import (
    TimeSlotSerializer, ScheduleSerializer, ScheduleListSerializer,
    ScheduleCreateSerializer, ScheduleConflictSerializer,
    ScheduleBatchCreateSerializer
)
from .algorithms import create_auto_schedule, SchedulingAlgorithm
from .services import ScheduleImportExportService
from apps.users.permissions import CanManageSchedules, CanViewSchedules
from apps.courses.models import Course
from apps.classrooms.models import Classroom
from django.contrib.auth import get_user_model
User = get_user_model()

logger = logging.getLogger(__name__)

def normalize_semester(sem: str) -> str:
    """将学期别名规范化为 YYYY-YYYY-<1|2> 格式。
    支持示例：
    - 2025-2026-1 (已规范)
    - 2025-1 => 2025-2026-1
    - 2025-2 => 2024-2025-2
    - 2024春 / 2024年春季学期 => 2023-2024-2
    - 2024秋 / 2024年秋季学期 => 2024-2025-1
    """
    if not sem:
        return sem
    s = str(sem).strip()
    # 已规范
    if re.fullmatch(r"\d{4}-\d{4}-(1|2)", s):
        return s
    # 形如 YYYY-1 / YYYY-2
    m = re.fullmatch(r"(\d{4})-(1|2)", s)
    if m:
        y = int(m.group(1))
        term = m.group(2)
        return f"{y}-{y+1}-1" if term == '1' else f"{y-1}-{y}-2"
    # 春/秋 表达
    s_no_space = re.sub(r"\s+", "", s)
    m2 = re.search(r"(\d{4}).*(春|秋)", s_no_space)
    if m2:
        y = int(m2.group(1))
        is_spring = (m2.group(2) == '春')
        return f"{y-1}-{y}-2" if is_spring else f"{y}-{y+1}-1"
    return s


class TimeSlotListCreateView(generics.ListCreateAPIView):
    """时间段列表和创建视图"""

    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name']
    ordering_fields = ['order', 'start_time', 'created_at']
    ordering = ['order']

    def get_permissions(self):
        """只有管理员可以创建时间段"""
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), CanManageSchedules()]
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
            'message': '获取时间段列表成功',
            'data': serializer.data
        })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({
            'code': 201,
            'message': '创建时间段成功',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)


class TimeSlotDetailView(generics.RetrieveUpdateDestroyAPIView):
    """时间段详情视图"""

    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        """只有管理员可以修改和删除时间段"""
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated(), CanManageSchedules()]
        return [permissions.IsAuthenticated()]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'code': 200,
            'message': '获取时间段详情成功',
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
            'message': '更新时间段成功',
            'data': serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # 检查是否有课程安排使用该时间段
        if instance.schedules.filter(status='active').exists():
            return Response({
                'code': 400,
                'message': '该时间段有课程安排，无法删除',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        self.perform_destroy(instance)
        return Response({
            'code': 200,
            'message': '删除时间段成功',
            'data': None
        })


class ScheduleListCreateView(generics.ListCreateAPIView):
    """课程安排列表和创建视图"""

    queryset = Schedule.objects.select_related(
        'course', 'teacher', 'classroom', 'time_slot', 'classroom__building'
    ).all()
    permission_classes = [permissions.IsAuthenticated, CanViewSchedules]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        'course', 'teacher', 'classroom', 'day_of_week', 'time_slot',
        'semester', 'academic_year', 'status', 'course__department'
    ]
    search_fields = [
        'course__code', 'course__name', 'teacher__username',
        'classroom__room_number', 'classroom__building__name'
    ]
    ordering_fields = ['day_of_week', 'time_slot__order', 'created_at']
    ordering = ['day_of_week', 'time_slot__order']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ScheduleCreateSerializer
        return ScheduleListSerializer

    def get_permissions(self):
        """只有管理员可以创建课程安排"""
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), CanManageSchedules()]
        return [permissions.IsAuthenticated(), CanViewSchedules()]

    def get_queryset(self):
        """根据用户类型过滤数据"""
        queryset = super().get_queryset()
        user = self.request.user

        if user.user_type == 'student':
            # 学生只能看到自己选课的课程安排
            enrolled_courses = user.enrollments.filter(
                is_active=True, status='enrolled'
            ).values_list('course_id', flat=True)
            return queryset.filter(course_id__in=enrolled_courses, status='active')
        elif user.user_type == 'teacher':
            # 教师只能看到自己教授的课程安排
            return queryset.filter(teacher=user)
        else:
            # 管理员可以看到所有安排
            return queryset

    @method_decorator(cache_page(60 * 2))  # 缓存2分钟
    def list(self, request, *args, **kwargs):
        # 规范化学期参数，避免别名导致过滤为空
        sem = request.query_params.get('semester')
        if sem:
            norm = normalize_semester(sem)
            if norm != sem and hasattr(request, '_request') and hasattr(request._request, 'GET'):
                try:
                    qd = request._request.GET.copy()
                    qd['semester'] = norm
                    request._request.GET = qd
                except Exception as e:
                    logger.error(f"Failed to normalize semester: {e}")
                    return Response({
                        'code': 400,
                        'message': '学期参数格式错误',
                        'data': None
                    }, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.filter_queryset(self.get_queryset())

        weeks_param = request.query_params.get('weeks')
        week_param = request.query_params.get('week')
        if weeks_param:
            try:
                weeks_list = Schedule.parse_week_range(weeks_param)
                weeks_set = set(int(w) for w in weeks_list)
                if weeks_set:
                    queryset = [s for s in queryset if any(w in s.week_numbers for w in weeks_set)]
            except Exception as e:
                logger.error(f"Failed to parse weeks parameter: {e}")
                return Response({
                    'code': 400,
                    'message': '周次参数格式错误',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
        elif week_param:
            try:
                week_number = int(week_param)
                queryset = [s for s in queryset if s.is_active_in_week(week_number)]
            except Exception as e:
                logger.error(f"Failed to parse week parameter: {e}")
                return Response({
                    'code': 400,
                    'message': '周次参数格式错误',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'code': 200,
            'message': '获取课程安排列表成功',
            'data': serializer.data
        })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # 返回完整的排课信息
        schedule_serializer = ScheduleSerializer(serializer.instance)
        return Response({
            'code': 201,
            'message': '创建课程安排成功',
            'data': schedule_serializer.data
        }, status=status.HTTP_201_CREATED)


class ScheduleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """课程安排详情视图"""

    queryset = Schedule.objects.select_related(
        'course', 'teacher', 'classroom', 'time_slot', 'classroom__building'
    ).all()
    serializer_class = ScheduleSerializer
    permission_classes = [permissions.IsAuthenticated, CanViewSchedules]

    def get_permissions(self):
        """只有管理员可以修改和删除课程安排"""
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated(), CanManageSchedules()]
        return [permissions.IsAuthenticated(), CanViewSchedules()]

    def get_queryset(self):
        """根据用户类型过滤数据"""
        queryset = super().get_queryset()
        user = self.request.user

        if user.user_type == 'student':
            enrolled_courses = user.enrollments.filter(
                is_active=True, status='enrolled'
            ).values_list('course_id', flat=True)
            return queryset.filter(course_id__in=enrolled_courses, status='active')
        elif user.user_type == 'teacher':
            return queryset.filter(teacher=user)
        else:
            return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'code': 200,
            'message': '获取课程安排详情成功',
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
            'message': '更新课程安排成功',
            'data': serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'code': 200,
            'message': '删除课程安排成功',
            'data': None
        })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, CanManageSchedules])
def check_schedule_conflicts(request):
    """检查排课冲突"""
    course_id = request.data.get('course_id')
    teacher_id = request.data.get('teacher_id')
    classroom_id = request.data.get('classroom_id')
    day_of_week = request.data.get('day_of_week')
    time_slot_id = request.data.get('time_slot_id')
    semester = request.data.get('semester')
    exclude_schedule_id = request.data.get('exclude_schedule_id')  # 更新时排除当前排课

    if not all([course_id, teacher_id, classroom_id, day_of_week, time_slot_id, semester]):
        return Response({
            'code': 400,
            'message': '缺少必要参数',
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)

    conflicts = []

    # 查询同一时间段的排课
    existing_schedules = Schedule.objects.filter(
        day_of_week=day_of_week,
        time_slot_id=time_slot_id,
        semester=semester,
        status='active'
    ).select_related('course', 'teacher', 'classroom')

    if exclude_schedule_id:
        existing_schedules = existing_schedules.exclude(id=exclude_schedule_id)

    # 检查教室冲突
    classroom_conflict = existing_schedules.filter(classroom_id=classroom_id).first()
    if classroom_conflict:
        conflicts.append({
            'conflict_type': 'classroom',
            'conflicting_schedule': ScheduleListSerializer(classroom_conflict).data,
            'message': f'教室在该时间段已被课程 {classroom_conflict.course.code} 占用'
        })

    # 检查教师冲突
    teacher_conflict = existing_schedules.filter(teacher_id=teacher_id).first()
    if teacher_conflict:
        conflicts.append({
            'conflict_type': 'teacher',
            'conflicting_schedule': ScheduleListSerializer(teacher_conflict).data,
            'message': f'教师在该时间段已有课程 {teacher_conflict.course.code}'
        })

    serializer = ScheduleConflictSerializer(conflicts, many=True)
    return Response({
        'code': 200,
        'message': '冲突检查完成',
        'data': {
            'has_conflicts': len(conflicts) > 0,
            'conflicts': serializer.data
        }
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, CanManageSchedules])
def batch_create_schedules(request):
    """批量创建课程安排"""
    serializer = ScheduleBatchCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    validated_data = serializer.validated_data
    course = validated_data['course']
    teacher = validated_data['teacher']
    classroom = validated_data['classroom']
    semester = validated_data['semester']
    academic_year = validated_data['academic_year']
    week_range = validated_data['week_range']
    time_slots = validated_data['time_slots']

    created_schedules = []
    conflicts = []

    with transaction.atomic():
        for slot_data in time_slots:
            day_of_week = slot_data['day_of_week']
            time_slot_id = slot_data['time_slot_id']

            # 检查冲突
            existing_schedules = Schedule.objects.filter(
                day_of_week=day_of_week,
                time_slot_id=time_slot_id,
                semester=semester,
                status='active'
            )

            # 检查教室冲突
            if existing_schedules.filter(classroom=classroom).exists():
                conflicts.append({
                    'day_of_week': day_of_week,
                    'time_slot_id': time_slot_id,
                    'conflict_type': 'classroom',
                    'message': '教室已被占用'
                })
                continue

            # 检查教师冲突
            if existing_schedules.filter(teacher=teacher).exists():
                conflicts.append({
                    'day_of_week': day_of_week,
                    'time_slot_id': time_slot_id,
                    'conflict_type': 'teacher',
                    'message': '教师已有课程安排'
                })
                continue

            # 创建排课
            schedule = Schedule.objects.create(
                course=course,
                teacher=teacher,
                classroom=classroom,
                time_slot_id=time_slot_id,
                day_of_week=day_of_week,
                week_range=week_range,
                semester=semester,
                academic_year=academic_year
            )
            created_schedules.append(schedule)

    # 序列化结果
    created_data = ScheduleListSerializer(created_schedules, many=True).data

    return Response({
        'code': 201 if created_schedules else 400,
        'message': f'批量排课完成，成功创建{len(created_schedules)}个，冲突{len(conflicts)}个',
        'data': {
            'created_count': len(created_schedules),
            'conflict_count': len(conflicts),
            'created_schedules': created_data,
            'conflicts': conflicts
        }
    }, status=status.HTTP_201_CREATED if created_schedules else status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, CanViewSchedules])
def get_schedule_table(request):
    """获取课程表"""
    semester = request.GET.get('semester')
    user_type = request.GET.get('user_type')  # 'student', 'teacher', 'classroom'
    user_id = request.GET.get('user_id')
    classroom_id = request.GET.get('classroom_id')
    week_param = request.GET.get('week')
    weeks_param = request.GET.get('weeks')

    if not semester:
        return Response({
            'code': 400,
            'message': '缺少学期参数',
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)

    # 规范化学期编码
    semester = normalize_semester(semester)

    # 参数校验：当传入筛选参数时，避免由于类型/ID不匹配导致静默空结果
    if user_type:
        if user_type not in ['student', 'teacher']:
            return Response({
                'code': 400,
                'message': 'user_type 参数仅支持 student 或 teacher',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        if user_id:
            try:
                uid = int(user_id)
            except (ValueError, TypeError):
                return Response({
                    'code': 400,
                    'message': 'user_id 必须为整数',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                u = User.objects.get(id=uid)
            except User.DoesNotExist:
                return Response({
                    'code': 400,
                    'message': '指定的用户不存在',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)

            if user_type == 'teacher' and u.user_type != 'teacher':
                return Response({
                    'code': 400,
                    'message': '指定的用户不是教师',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
            if user_type == 'student' and u.user_type != 'student':
                return Response({
                    'code': 400,
                    'message': '指定的用户不是学生',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)

    if classroom_id:
        try:
            cid = int(classroom_id)
        except (ValueError, TypeError):
            return Response({
                'code': 400,
                'message': 'classroom_id 必须为整数',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        if not Classroom.objects.filter(id=cid).exists():
            return Response({
                'code': 400,
                'message': '指定的教室不存在',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

    # 基础查询
    schedules = Schedule.objects.filter(
        semester=semester,
        status='active'
    ).select_related('course', 'teacher', 'classroom', 'time_slot')

    # 根据查询类型过滤
    if user_type == 'student' and user_id:
        # 学生课程表：查询学生选课的课程安排
        from apps.courses.models import Enrollment
        enrolled_courses = Enrollment.objects.filter(
            student_id=user_id,
            is_active=True,
            status='enrolled'
        ).values_list('course_id', flat=True)
        schedules = schedules.filter(course_id__in=enrolled_courses)
    elif user_type == 'teacher' and user_id:
        # 教师课程表：查询教师的课程安排
        schedules = schedules.filter(teacher_id=user_id)
    elif classroom_id:
        # 教室课程表：查询教室的使用安排
        schedules = schedules.filter(classroom_id=classroom_id)
    elif request.user.user_type == 'student':
        # 当前学生的课程表
        enrolled_courses = request.user.enrollments.filter(
            is_active=True,
            status='enrolled'
        ).values_list('course_id', flat=True)
        schedules = schedules.filter(course_id__in=enrolled_courses)
    elif request.user.user_type == 'teacher':
        # 当前教师的课程表
        schedules = schedules.filter(teacher=request.user)

    # 按周次过滤（可选）：优先使用 weeks，其次使用 week
    if weeks_param:
        try:
            weeks_list = Schedule.parse_week_range(weeks_param)
            weeks_set = set(int(w) for w in weeks_list)
        except Exception:
            weeks_set = set()
        if weeks_set:
            schedules = [s for s in schedules if any(w in s.week_numbers for w in weeks_set)]
    elif week_param:
        try:
            week_number = int(week_param)
            schedules = [s for s in schedules if s.is_active_in_week(week_number)]
        except (ValueError, TypeError):
            pass

    # 构建课程表数据结构
    time_slots = TimeSlot.objects.filter(is_active=True).order_by('order')
    schedule_table = {}

    # 初始化课程表结构
    for day in range(1, 8):  # 周一到周日
        schedule_table[day] = {}
        for time_slot in time_slots:
            schedule_table[day][time_slot.id] = None

    # 填充课程表数据
    for schedule in schedules:
        day = schedule.day_of_week
        time_slot_id = schedule.time_slot.id

        schedule_table[day][time_slot_id] = {
            'id': schedule.id,
            'course_code': schedule.course.code,
            'course_name': schedule.course.name,
            'teacher_name': f"{schedule.teacher.first_name} {schedule.teacher.last_name}".strip() or schedule.teacher.username,
            'classroom': schedule.classroom.full_name,
            'week_range': schedule.week_range,
            'notes': schedule.notes
        }

    # 构建时间段信息
    time_slot_info = [
        {
            'id': ts.id,
            'name': ts.name,
            'start_time': ts.start_time,
            'end_time': ts.end_time,
            'order': ts.order
        }
        for ts in time_slots
    ]

    return Response({
        'code': 200,
        'message': '获取课程表成功',
        'data': {
            'semester': semester,
            'time_slots': time_slot_info,
            'schedule_table': schedule_table
        }
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, CanManageSchedules])
def schedule_statistics(request):
    """排课统计"""
    semester = request.GET.get('semester')

    if not semester:
        return Response({
            'code': 400,
            'message': '缺少学期参数',
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        semester = normalize_semester(semester)

        total_schedules = Schedule.objects.filter(semester=semester, status='active').count()
        total_courses = Course.objects.filter(semester=semester, is_active=True).count()
        scheduled_courses = Schedule.objects.filter(
            semester=semester, status='active'
        ).values('course').distinct().count()

        total_classrooms = Classroom.objects.filter(is_active=True).count()
        used_classrooms = Schedule.objects.filter(
            semester=semester, status='active'
        ).values('classroom').distinct().count()

        teacher_workload = Schedule.objects.filter(
            semester=semester, status='active'
        ).values('teacher__username').annotate(
            schedule_count=models.Count('id')
        ).order_by('-schedule_count')[:10]

        time_slot_usage = Schedule.objects.filter(
            semester=semester, status='active'
        ).values('time_slot__name').annotate(
            usage_count=models.Count('id')
        ).order_by('-usage_count')

        department_stats = Schedule.objects.filter(
            semester=semester, status='active'
        ).values('course__department').annotate(
            schedule_count=models.Count('id')
        ).order_by('-schedule_count')

        return Response({
            'code': 200,
            'message': '获取排课统计成功',
            'data': {
                'total_schedules': total_schedules,
                'total_courses': total_courses,
                'scheduled_courses': scheduled_courses,
                'unscheduled_courses': total_courses - scheduled_courses,
                'total_classrooms': total_classrooms,
                'used_classrooms': used_classrooms,
                'classroom_utilization_rate': round(used_classrooms / total_classrooms * 100, 2) if total_classrooms > 0 else 0,
                'teacher_workload': list(teacher_workload),
                'time_slot_usage': list(time_slot_usage),
                'department_stats': list(department_stats)
            }
        })
    except Exception as e:
        logging.exception('schedule_statistics error')
        return Response({
            'code': 500,
            'message': '获取排课统计失败',
            'data': {'error': str(e)}
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, CanManageSchedules])
def auto_schedule(request):
    """智能自动排课"""
    semester = request.data.get('semester')
    academic_year = request.data.get('academic_year')
    course_ids = request.data.get('course_ids')  # 可选，指定要排课的课程
    algorithm_type = request.data.get('algorithm_type', 'greedy')  # 算法类型
    force_recreate = request.data.get('force_recreate', False)  # 是否强制重新排课
    timeout_seconds = request.data.get('timeout_seconds', 300)  # 超时时间

    if not semester or not academic_year:
        return Response({
            'code': 400,
            'message': '缺少必要参数：semester 和 academic_year',
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        # 如果强制重新排课，先删除现有排课
        if force_recreate:
            existing_schedules = Schedule.objects.filter(
                semester=semester,
                academic_year=academic_year,
                status='active'
            )
            if course_ids:
                existing_schedules = existing_schedules.filter(course_id__in=course_ids)

            deleted_count = existing_schedules.count()
            existing_schedules.delete()

        # 执行自动排课算法
        result = create_auto_schedule(semester, academic_year, course_ids, algorithm_type, timeout_seconds)

        # 创建Schedule对象
        algorithm_instance = result.pop('algorithm_instance')
        schedules_to_create = algorithm_instance.create_schedules()

        # 批量创建排课记录
        created_schedules = []
        with transaction.atomic():
            for schedule in schedules_to_create:
                schedule.save()
                created_schedules.append(schedule)

        # 序列化创建的排课记录
        created_data = ScheduleListSerializer(created_schedules, many=True).data

        # 处理失败分配的详情，移除不可序列化的对象
        failed_assignments_detail = []
        for failed in result['failed_assignments']:
            constraint = failed['constraint']
            failed_assignments_detail.append({
                'course_id': constraint.course.id,
                'course_name': constraint.course.name,
                'course_code': constraint.course.code,
                'teacher_id': constraint.teacher.id,
                'teacher_name': constraint.teacher.get_full_name() or constraint.teacher.username,
                'assigned_slots': failed['assigned_slots'],
                'required_slots': failed['required_slots'],
                'reason': failed['reason']
            })

        response_data = {
            'algorithm_type': result.get('algorithm_type', algorithm_type),
            'total_constraints': result['total_constraints'],
            'successful_assignments': result['successful_assignments'],
            'failed_assignments': len(result['failed_assignments']),
            'success_rate': result['success_rate'],
            'execution_time': result.get('execution_time', 0),
            'created_schedules_count': len(created_schedules),
            'created_schedules': created_data,
            'failed_assignments_detail': failed_assignments_detail,
            'suggestions': result['suggestions'],
            'constraint_stats': result.get('constraint_stats', {}),
            'resource_utilization': result.get('resource_utilization', {})
        }

        if force_recreate:
            response_data['deleted_schedules_count'] = deleted_count

        return Response({
            'code': 200,
            'message': f'自动排课完成，成功率: {result["success_rate"]:.1f}%，耗时: {result.get("execution_time", 0):.2f}秒',
            'data': response_data
        })

    except Exception as e:
        return Response({
            'code': 500,
            'message': f'自动排课失败: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, CanManageSchedules])
def optimize_schedule(request):
    """优化现有排课"""
    semester = request.data.get('semester')
    academic_year = request.data.get('academic_year')
    optimization_type = request.data.get('type', 'all')  # 'classroom', 'teacher', 'time', 'all'

    if not semester or not academic_year:
        return Response({
            'code': 400,
            'message': '缺少必要参数',
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        # 获取现有排课
        existing_schedules = Schedule.objects.filter(
            semester=semester,
            academic_year=academic_year,
            status='active'
        ).select_related('course', 'teacher', 'classroom', 'time_slot')

        optimization_suggestions = []

        if optimization_type in ['classroom', 'all']:
            # 教室优化建议
            classroom_usage = {}
            for schedule in existing_schedules:
                classroom_id = schedule.classroom.id
                if classroom_id not in classroom_usage:
                    classroom_usage[classroom_id] = {
                        'classroom': schedule.classroom,
                        'schedules': [],
                        'total_hours': 0
                    }
                classroom_usage[classroom_id]['schedules'].append(schedule)
                classroom_usage[classroom_id]['total_hours'] += 1

            # 找出利用率低的教室
            for classroom_id, usage_info in classroom_usage.items():
                if usage_info['total_hours'] < 10:  # 少于10课时认为利用率低
                    optimization_suggestions.append({
                        'type': 'classroom_underutilized',
                        'classroom_name': usage_info['classroom'].full_name,
                        'current_hours': usage_info['total_hours'],
                        'suggestion': '考虑将其他教室的课程调整到此教室'
                    })

        if optimization_type in ['teacher', 'all']:
            # 教师工作量优化建议
            teacher_workload = {}
            for schedule in existing_schedules:
                teacher_id = schedule.teacher.id
                if teacher_id not in teacher_workload:
                    teacher_workload[teacher_id] = {
                        'teacher': schedule.teacher,
                        'schedules': [],
                        'total_hours': 0
                    }
                teacher_workload[teacher_id]['schedules'].append(schedule)
                teacher_workload[teacher_id]['total_hours'] += 1

            # 找出工作量不均衡的情况
            if teacher_workload:
                avg_workload = sum(info['total_hours'] for info in teacher_workload.values()) / len(teacher_workload)
                for teacher_id, workload_info in teacher_workload.items():
                    if workload_info['total_hours'] > avg_workload * 1.5:
                        optimization_suggestions.append({
                            'type': 'teacher_overloaded',
                            'teacher_name': workload_info['teacher'].get_full_name() or workload_info['teacher'].username,
                            'current_hours': workload_info['total_hours'],
                            'average_hours': round(avg_workload, 1),
                            'suggestion': '工作量过重，建议分配部分课程给其他教师'
                        })

        if optimization_type in ['time', 'all']:
            # 时间分布优化建议
            time_distribution = {}
            for schedule in existing_schedules:
                key = f"{schedule.day_of_week}-{schedule.time_slot.id}"
                if key not in time_distribution:
                    time_distribution[key] = 0
                time_distribution[key] += 1

            # 检查时间分布是否均衡
            if time_distribution:
                max_usage = max(time_distribution.values())
                min_usage = min(time_distribution.values())
                if max_usage > min_usage * 2:
                    optimization_suggestions.append({
                        'type': 'time_imbalance',
                        'max_usage': max_usage,
                        'min_usage': min_usage,
                        'suggestion': '时间段使用不均衡，建议调整课程时间分布'
                    })

        return Response({
            'code': 200,
            'message': '排课优化分析完成',
            'data': {
                'total_schedules': existing_schedules.count(),
                'optimization_suggestions': optimization_suggestions,
                'optimization_count': len(optimization_suggestions)
            }
        })

    except Exception as e:
        return Response({
            'code': 500,
            'message': f'排课优化分析失败: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, CanManageSchedules])
def import_schedules(request):
    """导入课程表"""
    try:
        import_data = request.data

        # 验证导入数据
        is_valid, errors = ScheduleImportExportService.validate_import_data(import_data)

        if not is_valid:
            return Response({
                'code': 400,
                'message': '导入数据验证失败',
                'data': {'errors': errors}
            }, status=status.HTTP_400_BAD_REQUEST)

        # 执行导入
        created_count, import_errors = ScheduleImportExportService.import_schedules_from_data(import_data)

        if import_errors:
            return Response({
                'code': 206,  # Partial Content
                'message': f'部分导入成功，成功创建{created_count}条记录',
                'data': {
                    'created_count': created_count,
                    'errors': import_errors
                }
            }, status=status.HTTP_206_PARTIAL_CONTENT)

        return Response({
            'code': 201,
            'message': f'导入成功，共创建{created_count}条课程安排',
            'data': {'created_count': created_count}
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            'code': 500,
            'message': f'导入失败: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, CanViewSchedules])
def export_schedules(request):
    """导出课程表"""
    try:
        semester = request.query_params.get('semester')
        format_type = request.query_params.get('format', 'excel')
        include_weekend = request.query_params.get('include_weekend', 'false').lower() == 'true'
        group_by = request.query_params.get('group_by', 'teacher')

        if not semester:
            return Response({
                'code': 400,
                'message': '请提供学期参数',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        export_options = {
            'include_weekend': include_weekend,
            'group_by': group_by
        }

        if format_type == 'excel':
            file_content = ScheduleImportExportService.export_schedule_to_excel(semester, export_options)
            response = HttpResponse(
                file_content,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="课程表-{semester}.xlsx"'
            return response

        elif format_type == 'csv':
            file_content = ScheduleImportExportService.export_schedule_to_csv(semester, export_options)
            response = HttpResponse(file_content, content_type='text/csv; charset=utf-8')
            response['Content-Disposition'] = f'attachment; filename="课程表-{semester}.csv"'
            return response

        elif format_type == 'pdf':
            file_content = ScheduleImportExportService.export_schedule_to_pdf(semester, export_options)
            response = HttpResponse(file_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="课程表-{semester}.pdf"'
            return response

        else:
            # 返回JSON格式数据
            export_data = ScheduleImportExportService.export_schedule_to_dict(semester)
            return Response({
                'code': 200,
                'message': '导出成功',
                'data': export_data
            })

    except Exception as e:
        return Response({
            'code': 500,
            'message': f'导出失败: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_time_slots(request):
    """获取时间段列表 - 简化版本，供前端使用"""
    try:
        time_slots = TimeSlot.objects.filter(is_active=True).order_by('order')
        
        data = [{
            'id': slot.id,
            'name': slot.name,
            'start_time': slot.start_time.strftime('%H:%M'),
            'end_time': slot.end_time.strftime('%H:%M'),
            'order': slot.order,
            'duration_minutes': slot.duration_minutes
        } for slot in time_slots]
        
        return Response({
            'code': 200,
            'message': '获取时间段列表成功',
            'data': data
        })
    
    except Exception as e:
        return Response({
            'code': 500,
            'message': f'获取时间段列表失败: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, CanViewSchedules])
def schedule_statistics(request):
    """获取课程表统计信息"""
    try:
        semester = request.query_params.get('semester')

        if not semester:
            return Response({
                'code': 400,
                'message': '请提供学期参数',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        schedules = Schedule.objects.filter(semester=semester, status='active')

        # 基础统计
        stats = {
            'total_schedules': schedules.count(),
            'courses_count': schedules.values('course').distinct().count(),
            'teachers_count': schedules.values('teacher').distinct().count(),
            'classrooms_count': schedules.values('classroom').distinct().count(),
        }

        # 按星期分布
        day_distribution = {}
        for day_num, day_name in Schedule.DAY_CHOICES:
            count = schedules.filter(day_of_week=day_num).count()
            day_distribution[day_name] = count
        stats['day_distribution'] = day_distribution

        # 按时间段分布
        time_distribution = {}
        time_slots = TimeSlot.objects.filter(is_active=True)
        for time_slot in time_slots:
            count = schedules.filter(time_slot=time_slot).count()
            time_distribution[time_slot.name] = count
        stats['time_distribution'] = time_distribution

        # 教室利用率
        classroom_utilization = {}
        classrooms = Classroom.objects.filter(is_active=True)
        total_time_slots = len(Schedule.DAY_CHOICES) * time_slots.count()

        for classroom in classrooms:
            count = schedules.filter(classroom=classroom).count()
            utilization = (count / total_time_slots * 100) if total_time_slots > 0 else 0
            classroom_utilization[str(classroom)] = {
                'scheduled_count': count,
                'utilization_rate': round(utilization, 2)
            }
        stats['classroom_utilization'] = classroom_utilization

        # 教师工作量统计
        teacher_workload = {}
        teachers = User.objects.filter(user_type='teacher')
        for teacher in teachers:
            count = schedules.filter(teacher=teacher).count()
            teacher_workload[teacher.get_full_name() or teacher.username] = count
        stats['teacher_workload'] = teacher_workload

        return Response({
            'code': 200,
            'message': '获取统计信息成功',
            'data': {
                'semester': semester,
                'statistics': stats
            }
        })

    except Exception as e:
        return Response({
            'code': 500,
            'message': f'获取统计信息失败: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_teacher_schedules(request):
    """获取当前登录教师的课程安排"""
    semester = request.query_params.get('semester')
    course_id = request.query_params.get('course_id')
    
    if not semester:
        return Response({
            'code': 400,
            'message': '缺少学期参数',
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 获取当前教师的课程安排
    schedules = Schedule.objects.filter(
        teacher=request.user,
        semester=semester,
        status='active'
    ).select_related('course', 'classroom', 'time_slot')
    
    if course_id:
        schedules = schedules.filter(course_id=course_id)
    
    # 序列化数据
    data = []
    for schedule in schedules:
        data.append({
            'id': schedule.id,
            'course': {
                'id': schedule.course.id,
                'name': schedule.course.name,
                'code': schedule.course.code,
                'credits': schedule.course.credits
            },
            'classroom': {
                'id': schedule.classroom.id,
                'name': schedule.classroom.room_number,
                'building': schedule.classroom.building.name if schedule.classroom.building else '',
                'capacity': schedule.classroom.capacity
            },
            'day_of_week': schedule.day_of_week,
            'start_time': schedule.time_slot.start_time.strftime('%H:%M'),
            'end_time': schedule.time_slot.end_time.strftime('%H:%M'),
            'weeks': schedule.week_range,
            'semester': schedule.semester,
            'status': schedule.status,
            'created_at': schedule.created_at.isoformat()
        })
    
    return Response({
        'code': 200,
        'message': '获取教师课程表成功',
        'data': data
    })
