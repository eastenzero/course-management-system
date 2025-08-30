from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Avg, Sum, Count, Q
from django.utils import timezone
from datetime import date, timedelta
from apps.courses.models import Course, Enrollment
from apps.users.permissions import IsStudent
from .models import StudentProfile, StudentCourseProgress
from .serializers import (
    StudentProfileSerializer, StudentDashboardSerializer,
    StudentEnrollmentSerializer, AvailableCourseSerializer,
    CourseScheduleSerializer, StudentCourseProgressSerializer
)
from .services import StudentService

User = get_user_model()


class StudentProfileView(generics.RetrieveUpdateAPIView):
    """学生档案视图"""
    
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudent]
    
    def get_object(self):
        profile, created = StudentProfile.objects.get_or_create(
            user=self.request.user
        )
        return profile


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsStudent])
def student_dashboard(request):
    """学生仪表板数据"""
    
    try:
        service = StudentService(request.user)
        dashboard_data = service.get_dashboard_data()
        
        serializer = StudentDashboardSerializer(dashboard_data)
        return Response(serializer.data)
    
    except Exception as e:
        return Response(
            {'error': f'获取仪表板数据失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsStudent])
def available_courses(request):
    """获取可选课程列表"""
    
    try:
        # 获取查询参数
        semester = request.GET.get('semester')
        department = request.GET.get('department')
        course_type = request.GET.get('course_type')
        search = request.GET.get('search')
        
        # 构建查询条件
        queryset = Course.objects.filter(
            is_active=True,
            is_published=True
        )
        
        if semester:
            queryset = queryset.filter(semester=semester)
        if department:
            queryset = queryset.filter(department=department)
        if course_type:
            queryset = queryset.filter(course_type=course_type)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search) |
                Q(description__icontains=search)
            )
        
        # 排除已选课程
        enrolled_courses = Enrollment.objects.filter(
            student=request.user,
            status='enrolled'
        ).values_list('course_id', flat=True)
        
        queryset = queryset.exclude(id__in=enrolled_courses)
        
        # 序列化数据
        serializer = AvailableCourseSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        
        return Response(serializer.data)
    
    except Exception as e:
        return Response(
            {'error': f'获取可选课程失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsStudent])
def enroll_course(request):
    """选课"""
    
    try:
        course_id = request.data.get('course_id')
        if not course_id:
            return Response(
                {'error': '课程ID不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = StudentService(request.user)
        result = service.enroll_course(course_id)
        
        if result['success']:
            return Response({
                'message': '选课成功',
                'enrollment': result['enrollment']
            })
        else:
            return Response(
                {'error': result['error']},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    except Exception as e:
        return Response(
            {'error': f'选课失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated, IsStudent])
def drop_course(request, course_id):
    """退课"""
    
    try:
        service = StudentService(request.user)
        result = service.drop_course(course_id)
        
        if result['success']:
            return Response({'message': '退课成功'})
        else:
            return Response(
                {'error': result['error']},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    except Exception as e:
        return Response(
            {'error': f'退课失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsStudent])
def check_conflicts(request):
    """检查选课冲突"""
    
    try:
        course_ids = request.data.get('course_ids', [])
        if not course_ids:
            return Response(
                {'error': '课程ID列表不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = StudentService(request.user)
        conflicts = service.check_schedule_conflicts(course_ids)
        
        return Response({
            'has_conflicts': len(conflicts) > 0,
            'conflicts': conflicts
        })
    
    except Exception as e:
        return Response(
            {'error': f'冲突检测失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class MyCoursesView(generics.ListAPIView):
    """我的课程列表"""
    
    serializer_class = StudentEnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudent]
    
    def get_queryset(self):
        return Enrollment.objects.filter(
            student=self.request.user,
            is_active=True
        ).select_related('course').order_by('-enrolled_at')


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsStudent])
def course_schedule(request):
    """获取个人课程表"""
    
    try:
        semester = request.GET.get('semester')
        week = request.GET.get('week')
        
        service = StudentService(request.user)
        schedule_data = service.get_course_schedule(semester, week)
        
        serializer = CourseScheduleSerializer(schedule_data, many=True)
        return Response(serializer.data)
    
    except Exception as e:
        return Response(
            {'error': f'获取课程表失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsStudent])
def grades_list(request):
    """成绩列表"""
    
    try:
        semester = request.GET.get('semester')
        academic_year = request.GET.get('academic_year')
        
        queryset = Enrollment.objects.filter(
            student=request.user,
            is_active=True
        ).select_related('course')
        
        if semester:
            queryset = queryset.filter(course__semester=semester)
        if academic_year:
            queryset = queryset.filter(course__academic_year=academic_year)
        
        serializer = StudentEnrollmentSerializer(queryset, many=True)
        return Response(serializer.data)
    
    except Exception as e:
        return Response(
            {'error': f'获取成绩失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsStudent])
def gpa_statistics(request):
    """GPA统计"""
    
    try:
        service = StudentService(request.user)
        gpa_data = service.get_gpa_statistics()
        
        return Response(gpa_data)
    
    except Exception as e:
        return Response(
            {'error': f'获取GPA统计失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
