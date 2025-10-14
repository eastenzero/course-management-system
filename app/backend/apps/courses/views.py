from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db.models import Count, Q, Avg
from django.utils import timezone
from django.db import models
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.openapi import OpenApiTypes
from .cache_service import course_cache, cache_result

from .models import Course, Enrollment, Grade, CourseEvaluation
from .serializers import (
    CourseSerializer, CourseListSerializer, EnrollmentSerializer,
    EnrollmentCreateSerializer, CourseStatisticsSerializer,
    GradeSerializer, CourseEvaluationSerializer, GradeSummarySerializer,
    CourseGradeStatisticsSerializer
)
from apps.users.permissions import (
    IsTeacherOrAdmin, IsStudentOrTeacherOrAdmin, CanManageCourses
)


@extend_schema(tags=['课程管理'])
class CourseListCreateView(generics.ListCreateAPIView):
    """课程列表和创建视图"""

    queryset = Course.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        'course_type', 'department', 'semester', 'academic_year',
        'is_active', 'is_published', 'credits'
    ]
    search_fields = ['code', 'name', 'english_name', 'description']
    ordering_fields = ['code', 'name', 'credits', 'hours', 'created_at']
    ordering = ['code']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CourseListSerializer
        return CourseSerializer

    def get_permissions(self):
        """只有管理员可以创建课程"""
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), CanManageCourses()]
        return [permissions.IsAuthenticated()]

    @method_decorator(cache_page(60 * 5))  # 缓存5分钟
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # 学生只能看到已发布的课程
        if request.user.user_type == 'student':
            queryset = queryset.filter(is_published=True, is_active=True)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'code': 200,
            'message': '获取课程列表成功',
            'data': serializer.data
        })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({
            'code': 201,
            'message': '创建课程成功',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)


class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """课程详情视图"""

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        """只有管理员可以修改和删除课程"""
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated(), CanManageCourses()]
        return [permissions.IsAuthenticated()]

    @method_decorator(cache_page(60 * 10))  # 缓存10分钟
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'code': 200,
            'message': '获取课程详情成功',
            'data': serializer.data
        })

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # 清除相关缓存
        course_cache.invalidate_course_cache(instance.id)

        return Response({
            'code': 200,
            'message': '更新课程成功',
            'data': serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        course_id = instance.id
        self.perform_destroy(instance)

        # 清除相关缓存
        course_cache.invalidate_course_cache(course_id)

        return Response({
            'code': 200,
            'message': '删除课程成功'
        }, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        # 学生只能查看已发布的课程
        if request.user.user_type == 'student' and not instance.is_published:
            return Response({
                'code': 404,
                'message': '课程不存在或未发布',
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(instance)
        return Response({
            'code': 200,
            'message': '获取课程详情成功',
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
            'message': '更新课程成功',
            'data': serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # 检查是否有学生选课
        if instance.enrollments.filter(is_active=True).exists():
            return Response({
                'code': 400,
                'message': '该课程有学生选课，无法删除',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        self.perform_destroy(instance)
        return Response({
            'code': 200,
            'message': '删除课程成功',
            'data': None
        })


class EnrollmentListCreateView(generics.ListCreateAPIView):
    """选课记录列表和创建视图"""

    queryset = Enrollment.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsStudentOrTeacherOrAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'course__department', 'course__semester', 'is_active']
    search_fields = ['student__username', 'course__code', 'course__name']
    ordering_fields = ['enrolled_at', 'score']
    ordering = ['-enrolled_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return EnrollmentCreateSerializer
        return EnrollmentSerializer

    def get_queryset(self):
        """根据用户类型过滤数据"""
        queryset = super().get_queryset()
        user = self.request.user

        if user.user_type == 'student':
            # 学生只能看到自己的选课记录
            return queryset.filter(student=user)
        elif user.user_type == 'teacher':
            # 教师只能看到自己教授课程的选课记录
            return queryset.filter(course__teachers=user)
        else:
            # 管理员可以看到所有记录
            return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'code': 200,
                'message': '获取选课记录成功',
                'data': serializer.data
            })

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'code': 200,
            'message': '获取选课记录成功',
            'data': serializer.data
        })

    def create(self, request, *args, **kwargs):
        # 学生选课时自动设置student为当前用户
        if request.user.user_type == 'student':
            request.data['student'] = request.user.id

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # 返回完整的选课信息
        enrollment_serializer = EnrollmentSerializer(serializer.instance)
        return Response({
            'code': 201,
            'message': '选课成功',
            'data': enrollment_serializer.data
        }, status=status.HTTP_201_CREATED)


class EnrollmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """选课记录详情视图"""

    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """根据用户类型过滤数据"""
        queryset = super().get_queryset()
        user = self.request.user

        if user.user_type == 'student':
            return queryset.filter(student=user)
        elif user.user_type == 'teacher':
            return queryset.filter(course__teachers=user)
        else:
            return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'code': 200,
            'message': '获取选课详情成功',
            'data': serializer.data
        })

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # 学生只能退课，不能修改其他信息
        if request.user.user_type == 'student':
            if 'status' in request.data and request.data['status'] != 'dropped':
                return Response({
                    'code': 403,
                    'message': '学生只能退课',
                    'data': None
                }, status=status.HTTP_403_FORBIDDEN)

        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            'code': 200,
            'message': '更新选课记录成功',
            'data': serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # 只有管理员可以删除选课记录
        if request.user.user_type not in ['admin', 'academic_admin']:
            return Response({
                'code': 403,
                'message': '权限不足',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        self.perform_destroy(instance)
        return Response({
            'code': 200,
            'message': '删除选课记录成功',
            'data': None
        })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def drop_course(request, course_id):
    """退课"""
    try:
        course = Course.objects.get(id=course_id)
        enrollment = Enrollment.objects.get(
            student=request.user,
            course=course,
            is_active=True,
            status='enrolled'
        )

        enrollment.status = 'dropped'
        enrollment.is_active = False
        enrollment.save()

        return Response({
            'code': 200,
            'message': '退课成功',
            'data': None
        })

    except Course.DoesNotExist:
        return Response({
            'code': 404,
            'message': '课程不存在',
            'data': None
        }, status=status.HTTP_404_NOT_FOUND)

    except Enrollment.DoesNotExist:
        return Response({
            'code': 400,
            'message': '未选择该课程或已退课',
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, CanManageCourses])
def course_statistics(request):
    """课程统计"""
    semester = request.GET.get('semester')

    # 基础统计
    courses_qs = Course.objects.all()
    if semester:
        courses_qs = courses_qs.filter(semester=semester)

    total_courses = courses_qs.count()
    active_courses = courses_qs.filter(is_active=True).count()
    published_courses = courses_qs.filter(is_published=True).count()

    # 选课统计
    enrollments_qs = Enrollment.objects.filter(is_active=True)
    if semester:
        enrollments_qs = enrollments_qs.filter(course__semester=semester)

    total_enrollments = enrollments_qs.count()

    # 按院系统计
    by_department = courses_qs.values('department').annotate(
        count=Count('id')
    ).order_by('-count')

    # 按课程类型统计
    by_course_type = courses_qs.values('course_type').annotate(
        count=Count('id')
    ).order_by('-count')

    # 选课趋势（最近7天）
    from django.utils import timezone
    from datetime import timedelta

    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=6)

    enrollment_trend = []
    for i in range(7):
        date = start_date + timedelta(days=i)
        count = enrollments_qs.filter(enrolled_at__date=date).count()
        enrollment_trend.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': count
        })

    data = {
        'total_courses': total_courses,
        'active_courses': active_courses,
        'published_courses': published_courses,
        'total_enrollments': total_enrollments,
        'by_department': {item['department']: item['count'] for item in by_department},
        'by_course_type': {item['course_type']: item['count'] for item in by_course_type},
        'enrollment_trend': enrollment_trend
    }

    serializer = CourseStatisticsSerializer(data)
    return Response({
        'code': 200,
        'message': '获取课程统计成功',
        'data': serializer.data
    })


# 成绩管理相关视图

class GradeListCreateView(generics.ListCreateAPIView):
    """成绩列表和创建视图"""

    serializer_class = GradeSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['grade_type', 'enrollment__course', 'enrollment__student']
    search_fields = ['name', 'description', 'enrollment__student__username']
    ordering_fields = ['score', 'created_at', 'graded_at']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if user.user_type in ['admin', 'academic_admin']:
            return Grade.objects.all().select_related(
                'enrollment__student', 'enrollment__course', 'graded_by'
            )
        elif user.user_type == 'teacher':
            return Grade.objects.filter(
                enrollment__course__teachers=user
            ).select_related(
                'enrollment__student', 'enrollment__course', 'graded_by'
            )
        return Grade.objects.none()

    def perform_create(self, serializer):
        serializer.save(graded_by=self.request.user, graded_at=timezone.now())


class GradeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """成绩详情视图"""

    serializer_class = GradeSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.user_type in ['admin', 'academic_admin']:
            return Grade.objects.all()
        elif user.user_type == 'teacher':
            return Grade.objects.filter(enrollment__course__teachers=user)
        return Grade.objects.none()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def course_grade_summary(request, course_id):
    """获取课程成绩汇总"""

    try:
        course = Course.objects.get(id=course_id)

        # 权限检查
        user = request.user
        if user.user_type == 'teacher' and user not in course.teachers.all():
            return Response(
                {'error': '您没有权限查看此课程的成绩'},
                status=status.HTTP_403_FORBIDDEN
            )
        elif user.user_type == 'student':
            # 学生只能查看自己的成绩
            enrollments = Enrollment.objects.filter(
                course=course,
                student=user,
                is_active=True
            )
        else:
            # 管理员和教师可以查看所有成绩
            enrollments = Enrollment.objects.filter(
                course=course,
                is_active=True
            )

        summary_data = []
        for enrollment in enrollments.select_related('student'):
            detailed_grades = Grade.objects.filter(enrollment=enrollment)

            # 计算最终成绩
            total_weighted_score = 0
            total_weight = 0

            for grade in detailed_grades:
                if grade.weight > 0:
                    total_weighted_score += grade.percentage_score * (grade.weight / 100)
                    total_weight += grade.weight

            final_score = total_weighted_score if total_weight > 0 else 0

            # 计算最终等级
            if final_score >= 90:
                final_grade = 'A'
            elif final_score >= 80:
                final_grade = 'B'
            elif final_score >= 70:
                final_grade = 'C'
            elif final_score >= 60:
                final_grade = 'D'
            else:
                final_grade = 'F'

            # 成绩分解
            grade_breakdown = {}
            for grade in detailed_grades:
                grade_type = grade.get_grade_type_display()
                if grade_type not in grade_breakdown:
                    grade_breakdown[grade_type] = []
                grade_breakdown[grade_type].append({
                    'name': grade.name,
                    'score': grade.score,
                    'max_score': grade.max_score,
                    'percentage': grade.percentage_score,
                    'weight': grade.weight
                })

            summary_data.append({
                'enrollment_id': enrollment.id,
                'student_info': {
                    'id': enrollment.student.id,
                    'username': enrollment.student.username,
                    'name': f"{enrollment.student.first_name} {enrollment.student.last_name}",
                    'student_id': enrollment.student.student_id
                },
                'course_info': {
                    'id': course.id,
                    'code': course.code,
                    'name': course.name
                },
                'detailed_grades': GradeSerializer(detailed_grades, many=True).data,
                'final_score': round(final_score, 2),
                'final_grade': final_grade,
                'grade_breakdown': grade_breakdown
            })

        return Response(summary_data)

    except Course.DoesNotExist:
        return Response(
            {'error': '课程不存在'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'获取成绩汇总失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class CourseEvaluationListCreateView(generics.ListCreateAPIView):
    """课程评价列表和创建视图"""

    serializer_class = CourseEvaluationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['enrollment__course', 'would_recommend']
    ordering_fields = ['overall_satisfaction', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if user.user_type in ['admin', 'academic_admin']:
            return CourseEvaluation.objects.all().select_related(
                'enrollment__student', 'enrollment__course'
            )
        elif user.user_type == 'teacher':
            return CourseEvaluation.objects.filter(
                enrollment__course__teachers=user
            ).select_related(
                'enrollment__student', 'enrollment__course'
            )
        elif user.user_type == 'student':
            return CourseEvaluation.objects.filter(
                enrollment__student=user
            ).select_related(
                'enrollment__student', 'enrollment__course'
            )
        return CourseEvaluation.objects.none()


class CourseEvaluationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """课程评价详情视图"""

    serializer_class = CourseEvaluationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.user_type in ['admin', 'academic_admin']:
            return CourseEvaluation.objects.all()
        elif user.user_type == 'teacher':
            return CourseEvaluation.objects.filter(
                enrollment__course__teachers=user
            )
        elif user.user_type == 'student':
            return CourseEvaluation.objects.filter(
                enrollment__student=user
            )
        return CourseEvaluation.objects.none()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsTeacherOrAdmin])
def course_evaluation_statistics(request, course_id):
    """获取课程评价统计"""

    try:
        course = Course.objects.get(id=course_id)

        # 权限检查
        user = request.user
        if user.user_type == 'teacher' and user not in course.teachers.all():
            return Response(
                {'error': '您没有权限查看此课程的评价统计'},
                status=status.HTTP_403_FORBIDDEN
            )

        evaluations = CourseEvaluation.objects.filter(
            enrollment__course=course
        )

        if not evaluations.exists():
            return Response({
                'course_info': {
                    'id': course.id,
                    'code': course.code,
                    'name': course.name
                },
                'total_evaluations': 0,
                'average_ratings': {},
                'recommendation_rate': 0,
                'rating_distribution': {}
            })

        # 计算平均评分
        total_evaluations = evaluations.count()

        avg_teaching_quality = evaluations.aggregate(
            avg=models.Avg('teaching_quality')
        )['avg'] or 0

        avg_course_content = evaluations.aggregate(
            avg=models.Avg('course_content')
        )['avg'] or 0

        avg_difficulty_level = evaluations.aggregate(
            avg=models.Avg('difficulty_level')
        )['avg'] or 0

        avg_workload = evaluations.aggregate(
            avg=models.Avg('workload')
        )['avg'] or 0

        avg_overall_satisfaction = evaluations.aggregate(
            avg=models.Avg('overall_satisfaction')
        )['avg'] or 0

        # 推荐率
        recommend_count = evaluations.filter(would_recommend=True).count()
        recommendation_rate = (recommend_count / total_evaluations) * 100

        # 评分分布
        rating_distribution = {}
        for i in range(1, 6):
            rating_distribution[f'{i}星'] = {
                'teaching_quality': evaluations.filter(teaching_quality=i).count(),
                'course_content': evaluations.filter(course_content=i).count(),
                'difficulty_level': evaluations.filter(difficulty_level=i).count(),
                'workload': evaluations.filter(workload=i).count(),
                'overall_satisfaction': evaluations.filter(overall_satisfaction=i).count(),
            }

        return Response({
            'course_info': {
                'id': course.id,
                'code': course.code,
                'name': course.name
            },
            'total_evaluations': total_evaluations,
            'average_ratings': {
                'teaching_quality': round(avg_teaching_quality, 2),
                'course_content': round(avg_course_content, 2),
                'difficulty_level': round(avg_difficulty_level, 2),
                'workload': round(avg_workload, 2),
                'overall_satisfaction': round(avg_overall_satisfaction, 2),
            },
            'recommendation_rate': round(recommendation_rate, 2),
            'rating_distribution': rating_distribution
        })

    except Course.DoesNotExist:
        return Response(
            {'error': '课程不存在'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'获取评价统计失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
