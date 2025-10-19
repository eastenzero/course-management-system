from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Count, Avg, Q
from django.utils import timezone
from apps.courses.models import Course, Enrollment
from apps.users.permissions import IsTeacher
from .models import TeacherProfile, TeacherCourseAssignment, TeacherNotice
from .serializers import (
    TeacherProfileSerializer, TeacherDashboardSerializer,
    TeacherCourseDetailSerializer, CourseStudentSerializer,
    GradeEntrySerializer, TeacherNoticeSerializer
)
from .services import TeacherService

User = get_user_model()


class TeacherProfileView(generics.RetrieveUpdateAPIView):
    """教师档案视图"""
    
    serializer_class = TeacherProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacher]
    
    def get_object(self):
        profile, created = TeacherProfile.objects.get_or_create(
            user=self.request.user
        )
        return profile


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsTeacher])
def teacher_dashboard(request):
    """教师仪表板数据"""
    
    try:
        service = TeacherService(request.user)
        dashboard_data = service.get_dashboard_data()
        
        serializer = TeacherDashboardSerializer(dashboard_data)
        return Response(serializer.data)
    
    except Exception as e:
        return Response(
            {'error': f'获取仪表板数据失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class MyCoursesView(generics.ListAPIView):
    """我的课程列表"""
    
    serializer_class = TeacherCourseDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacher]
    
    def get_queryset(self):
        return Course.objects.filter(
            teachers=self.request.user,
            is_active=True
        ).prefetch_related('teachers', 'enrollments')


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsTeacher])
def course_students(request, course_id):
    """获取课程学生列表"""
    
    try:
        # 验证教师是否有权限访问该课程
        course = Course.objects.get(
            id=course_id,
            teachers=request.user,
            is_active=True
        )
        
        # 获取选课学生
        enrollments = Enrollment.objects.filter(
            course=course,
            is_active=True
        ).select_related('student', 'student__student_profile')
        
        # 过滤参数
        status_filter = request.GET.get('status')
        search = request.GET.get('search')
        
        if status_filter:
            enrollments = enrollments.filter(status=status_filter)
        
        if search:
            enrollments = enrollments.filter(
                Q(student__username__icontains=search) |
                Q(student__first_name__icontains=search) |
                Q(student__last_name__icontains=search) |
                Q(student__student_id__icontains=search)
            )
        
        serializer = CourseStudentSerializer(enrollments, many=True)
        return Response(serializer.data)
    
    except Course.DoesNotExist:
        return Response(
            {'error': '课程不存在或您没有权限访问'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'获取学生列表失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsTeacher])
def batch_grade_entry(request):
    """批量录入成绩"""
    
    try:
        grades_data = request.data.get('grades', [])
        if not grades_data:
            return Response(
                {'error': '成绩数据不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = TeacherService(request.user)
        result = service.batch_update_grades(grades_data)
        
        if result['success']:
            return Response({
                'message': f'成功录入 {result["updated_count"]} 条成绩',
                'updated_count': result['updated_count'],
                'failed_count': result['failed_count'],
                'errors': result['errors']
            })
        else:
            return Response(
                {'error': result['error']},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    except Exception as e:
        return Response(
            {'error': f'批量录入成绩失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated, IsTeacher])
def update_grade(request, enrollment_id):
    """更新单个学生成绩"""

    try:
        enrollment = Enrollment.objects.get(
            id=enrollment_id,
            course__teachers=request.user,
            is_active=True
        )

        serializer = GradeEntrySerializer(enrollment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': '成绩更新成功',
                'data': serializer.data
            })
        else:
            return Response(
                {'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

    except Enrollment.DoesNotExist:
        return Response(
            {'error': '选课记录不存在或您没有权限修改'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'更新成绩失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsTeacher])
def course_grade_statistics(request, course_id):
    """获取课程成绩统计"""

    try:
        course = Course.objects.get(
            id=course_id,
            teachers=request.user,
            is_active=True
        )

        service = TeacherService(request.user)
        statistics = service.get_course_grade_statistics(course_id)

        return Response(statistics)

    except Course.DoesNotExist:
        return Response(
            {'error': '课程不存在或您没有权限访问'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'获取成绩统计失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsTeacher])
def teaching_schedule(request):
    """获取教学安排"""

    try:
        semester = request.GET.get('semester')
        week = request.GET.get('week')

        service = TeacherService(request.user)
        schedule_data = service.get_teaching_schedule(semester, week)

        return Response(schedule_data)

    except Exception as e:
        return Response(
            {'error': f'获取教学安排失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class TeacherNoticeListCreateView(generics.ListCreateAPIView):
    """教师通知列表和创建"""

    serializer_class = TeacherNoticeSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacher]

    def get_queryset(self):
        course_id = self.request.GET.get('course_id')
        queryset = TeacherNotice.objects.filter(teacher=self.request.user)

        if course_id:
            queryset = queryset.filter(course_id=course_id)

        return queryset.select_related('course').order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)


class TeacherNoticeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """教师通知详情"""

    serializer_class = TeacherNoticeSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacher]

    def get_queryset(self):
        return TeacherNotice.objects.filter(teacher=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsTeacher])
def publish_notice(request, notice_id):
    """发布通知"""

    try:
        notice = TeacherNotice.objects.get(
            id=notice_id,
            teacher=request.user
        )

        notice.is_published = True
        notice.published_at = timezone.now()
        notice.save()

        return Response({'message': '通知发布成功'})

    except TeacherNotice.DoesNotExist:
        return Response(
            {'error': '通知不存在或您没有权限操作'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'发布通知失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
