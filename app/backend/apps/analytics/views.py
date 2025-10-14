from django.shortcuts import render
from django.db.models import Count, Q, Avg, Sum, F
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.http import HttpResponse
import json

from apps.courses.models import Course, Enrollment
from apps.classrooms.models import Classroom, Building
from apps.schedules.models import Schedule, TimeSlot
from .serializers import (
    DashboardStatsSerializer, CourseAnalyticsSerializer, UserAnalyticsSerializer,
    ClassroomAnalyticsSerializer, EnrollmentTrendSerializer, DepartmentStatsSerializer,
    OverviewAnalyticsSerializer, RealtimeStatsSerializer, ExportRequestSerializer
)

User = get_user_model()


class DashboardViewSet(viewsets.ViewSet):
    """仪表板数据视图集"""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """获取仪表板统计数据"""
        try:
            # 基础统计
            total_users = User.objects.count()
            total_students = User.objects.filter(user_type='student').count()
            total_teachers = User.objects.filter(user_type='teacher').count()
            total_courses = Course.objects.count()
            total_enrollments = Enrollment.objects.count()
            total_classrooms = Classroom.objects.count()
            total_schedules = Schedule.objects.count()

            # 计算增长率（与上月对比）
            last_month = timezone.now() - timedelta(days=30)

            last_month_users = User.objects.filter(date_joined__lt=last_month).count()
            user_growth_rate = ((total_users - last_month_users) / max(last_month_users, 1)) * 100

            last_month_courses = Course.objects.filter(created_at__lt=last_month).count()
            course_growth_rate = ((total_courses - last_month_courses) / max(last_month_courses, 1)) * 100

            last_month_enrollments = Enrollment.objects.filter(enrolled_at__lt=last_month).count()
            enrollment_growth_rate = ((total_enrollments - last_month_enrollments) / max(last_month_enrollments, 1)) * 100

            data = {
                'total_users': total_users,
                'total_students': total_students,
                'total_teachers': total_teachers,
                'total_courses': total_courses,
                'total_enrollments': total_enrollments,
                'total_classrooms': total_classrooms,
                'total_schedules': total_schedules,
                'user_growth_rate': round(user_growth_rate, 2),
                'course_growth_rate': round(course_growth_rate, 2),
                'enrollment_growth_rate': round(enrollment_growth_rate, 2),
            }

            serializer = DashboardStatsSerializer(data)
            return Response({
                'code': 200,
                'message': '获取仪表板统计数据成功',
                'data': serializer.data
            })

        except Exception as e:
            return Response({
                'code': 500,
                'message': f'获取统计数据失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def course_distribution(self, request):
        """获取课程类型分布"""
        try:
            distribution = Course.objects.values('course_type').annotate(
                count=Count('id'),
                percentage=Count('id') * 100.0 / Course.objects.count()
            ).order_by('-count')

            return Response({
                'code': 200,
                'message': '获取课程分布成功',
                'data': list(distribution)
            })

        except Exception as e:
            return Response({
                'code': 500,
                'message': f'获取课程分布失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CourseAnalyticsViewSet(viewsets.ViewSet):
    """课程分析视图集"""
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """获取课程分析列表"""
        try:
            courses = Course.objects.annotate(
                enrollment_count=Count('enrollments', filter=Q(enrollments__is_active=True)),
                enrollment_rate=Count('enrollments', filter=Q(enrollments__is_active=True)) * 100.0 / F('max_students')
            ).order_by('-enrollment_count')[:20]

            data = []
            for course in courses:
                data.append({
                    'course_id': course.id,
                    'course_name': course.name,
                    'course_code': course.code,
                    'enrollment_count': course.enrollment_count,
                    'max_students': course.max_students,
                    'enrollment_rate': round(course.enrollment_rate or 0, 2),
                    'department': course.department,
                    'course_type': course.course_type,
                    'credits': course.credits,
                })

            return Response({
                'code': 200,
                'message': '获取课程分析数据成功',
                'data': data
            })

        except Exception as e:
            return Response({
                'code': 500,
                'message': f'获取课程分析数据失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def popular_courses(self, request):
        """获取热门课程"""
        try:
            popular_courses = Course.objects.annotate(
                enrollment_count=Count('enrollments', filter=Q(enrollments__is_active=True))
            ).filter(enrollment_count__gt=0).order_by('-enrollment_count')[:10]

            data = []
            for course in popular_courses:
                data.append({
                    'course_id': course.id,
                    'course_name': course.name,
                    'course_code': course.code,
                    'enrollment_count': course.enrollment_count,
                    'department': course.department,
                })

            return Response({
                'code': 200,
                'message': '获取热门课程成功',
                'data': data
            })

        except Exception as e:
            return Response({
                'code': 500,
                'message': f'获取热门课程失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserAnalyticsViewSet(viewsets.ViewSet):
    """用户分析视图集"""
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """获取用户分析数据"""
        try:
            total_users = User.objects.count()
            user_stats = User.objects.values('user_type').annotate(
                count=Count('id'),
                active_count=Count('id', filter=Q(is_active=True)),
                percentage=Count('id') * 100.0 / total_users,
                active_rate=Count('id', filter=Q(is_active=True)) * 100.0 / Count('id')
            )

            data = []
            for stat in user_stats:
                data.append({
                    'user_type': stat['user_type'],
                    'count': stat['count'],
                    'percentage': round(stat['percentage'], 2),
                    'active_count': stat['active_count'],
                    'active_rate': round(stat['active_rate'] or 0, 2),
                })

            return Response({
                'code': 200,
                'message': '获取用户分析数据成功',
                'data': data
            })

        except Exception as e:
            return Response({
                'code': 500,
                'message': f'获取用户分析数据失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ClassroomAnalyticsViewSet(viewsets.ViewSet):
    """教室分析视图集"""
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """获取教室分析数据"""
        try:
            classrooms = Classroom.objects.annotate(
                schedule_count=Count('schedules', filter=Q(schedules__status='active')),
                utilization_rate=Count('schedules', filter=Q(schedules__status='active')) * 100.0 / 40  # 假设每周40个时间段
            ).select_related('building')

            data = []
            for classroom in classrooms:
                data.append({
                    'classroom_id': classroom.id,
                    'classroom_name': f"{classroom.building.name}{classroom.room_number}",
                    'building_name': classroom.building.name,
                    'capacity': classroom.capacity,
                    'utilization_rate': round(classroom.utilization_rate or 0, 2),
                    'schedule_count': classroom.schedule_count,
                    'room_type': classroom.room_type,
                })

            return Response({
                'code': 200,
                'message': '获取教室分析数据成功',
                'data': data
            })

        except Exception as e:
            return Response({
                'code': 500,
                'message': f'获取教室分析数据失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EnrollmentAnalyticsViewSet(viewsets.ViewSet):
    """选课分析视图集"""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def trends(self, request):
        """获取选课趋势数据"""
        try:
            # 获取最近30天的选课趋势
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)

            trends = []
            current_date = start_date
            while current_date <= end_date:
                enrollment_count = Enrollment.objects.filter(
                    enrolled_at__date=current_date
                ).count()

                new_enrollments = Enrollment.objects.filter(
                    enrolled_at__date=current_date,
                    status='enrolled'
                ).count()

                dropped_enrollments = Enrollment.objects.filter(
                    dropped_at__date=current_date,
                    status='dropped'
                ).count()

                trends.append({
                    'date': current_date.isoformat(),
                    'enrollment_count': enrollment_count,
                    'new_enrollments': new_enrollments,
                    'dropped_enrollments': dropped_enrollments,
                })

                current_date += timedelta(days=1)

            return Response({
                'code': 200,
                'message': '获取选课趋势数据成功',
                'data': trends
            })

        except Exception as e:
            return Response({
                'code': 500,
                'message': f'获取选课趋势数据失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OverviewAnalyticsView(APIView):
    """概览分析视图"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """获取概览分析数据"""
        try:
            # 仪表板统计
            dashboard_view = DashboardViewSet()
            dashboard_view.request = request
            dashboard_response = dashboard_view.stats(request)
            dashboard_stats = dashboard_response.data['data']

            # 课程类型分布
            course_distribution = Course.objects.values('course_type').annotate(
                count=Count('id'),
                percentage=Count('id') * 100.0 / Course.objects.count()
            ).order_by('-count')

            # 院系统计
            department_stats = Course.objects.values('department').annotate(
                course_count=Count('id'),
                student_count=Count('enrollments__student', distinct=True),
                enrollment_count=Count('enrollments')
            ).order_by('-course_count')[:10]

            # 热门课程
            top_courses = Course.objects.annotate(
                enrollment_count=Count('enrollments', filter=Q(enrollments__is_active=True))
            ).filter(enrollment_count__gt=0).order_by('-enrollment_count')[:5]

            data = {
                'dashboard_stats': dashboard_stats,
                'course_type_distribution': list(course_distribution),
                'department_stats': list(department_stats),
                'top_courses': [
                    {
                        'course_id': course.id,
                        'course_name': course.name,
                        'course_code': course.code,
                        'enrollment_count': course.enrollment_count,
                        'department': course.department,
                    } for course in top_courses
                ]
            }

            return Response({
                'code': 200,
                'message': '获取概览分析数据成功',
                'data': data
            })

        except Exception as e:
            return Response({
                'code': 500,
                'message': f'获取概览分析数据失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TrendAnalyticsView(APIView):
    """趋势分析视图"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """获取趋势分析数据"""
        try:
            days = int(request.query_params.get('days', 30))
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days)

            # 用户注册趋势
            user_trends = []
            # 选课趋势
            enrollment_trends = []
            # 课程创建趋势
            course_trends = []

            current_date = start_date
            while current_date <= end_date:
                user_count = User.objects.filter(date_joined__date=current_date).count()
                enrollment_count = Enrollment.objects.filter(enrolled_at__date=current_date).count()
                course_count = Course.objects.filter(created_at__date=current_date).count()

                user_trends.append({'date': current_date.isoformat(), 'count': user_count})
                enrollment_trends.append({'date': current_date.isoformat(), 'count': enrollment_count})
                course_trends.append({'date': current_date.isoformat(), 'count': course_count})

                current_date += timedelta(days=1)

            return Response({
                'code': 200,
                'message': '获取趋势分析数据成功',
                'data': {
                    'user_trends': user_trends,
                    'enrollment_trends': enrollment_trends,
                    'course_trends': course_trends,
                }
            })

        except Exception as e:
            return Response({
                'code': 500,
                'message': f'获取趋势分析数据失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReportAnalyticsView(APIView):
    """报表分析视图"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """获取报表数据"""
        try:
            report_type = request.query_params.get('type', 'summary')

            if report_type == 'summary':
                # 汇总报表
                data = {
                    'total_stats': {
                        'users': User.objects.count(),
                        'courses': Course.objects.count(),
                        'enrollments': Enrollment.objects.count(),
                        'classrooms': Classroom.objects.count(),
                    },
                    'user_distribution': list(User.objects.values('user_type').annotate(count=Count('id'))),
                    'course_distribution': list(Course.objects.values('course_type').annotate(count=Count('id'))),
                    'department_distribution': list(Course.objects.values('department').annotate(count=Count('id')))
                }
            elif report_type == 'enrollment':
                # 选课报表
                data = {
                    'enrollment_stats': Enrollment.objects.values('status').annotate(count=Count('id')),
                    'popular_courses': list(Course.objects.annotate(
                        enrollment_count=Count('enrollments')
                    ).order_by('-enrollment_count')[:10].values('name', 'code', 'enrollment_count')),
                    'enrollment_by_department': list(Course.objects.values('department').annotate(
                        enrollment_count=Count('enrollments')
                    ).order_by('-enrollment_count'))
                }
            else:
                data = {'message': '不支持的报表类型'}

            return Response({
                'code': 200,
                'message': '获取报表数据成功',
                'data': data
            })

        except Exception as e:
            return Response({
                'code': 500,
                'message': f'获取报表数据失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RealtimeStatsView(APIView):
    """实时统计视图"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """获取实时统计数据"""
        try:
            now = timezone.now()
            today = now.date()
            yesterday = today - timedelta(days=1)
            last_hour = now - timedelta(hours=1)
            last_24_hours = now - timedelta(hours=24)
            last_week = now - timedelta(days=7)

            # 基础统计
            total_active_users = User.objects.filter(is_active=True).count()

            # 最近活动统计
            recent_enrollments = Enrollment.objects.filter(
                enrolled_at__gte=last_24_hours
            ).count()

            recent_courses_created = Course.objects.filter(
                created_at__gte=last_24_hours
            ).count()

            recent_schedules_created = Schedule.objects.filter(
                created_at__gte=last_24_hours
            ).count()

            # 今日vs昨日对比
            today_enrollments = Enrollment.objects.filter(
                enrolled_at__date=today
            ).count()

            yesterday_enrollments = Enrollment.objects.filter(
                enrolled_at__date=yesterday
            ).count()

            enrollment_change = today_enrollments - yesterday_enrollments
            enrollment_change_percent = (
                (enrollment_change / max(yesterday_enrollments, 1)) * 100
                if yesterday_enrollments > 0 else 0
            )

            # 热门课程（最近一周选课最多）
            popular_courses = Course.objects.annotate(
                recent_enrollments=Count(
                    'enrollments',
                    filter=Q(enrollments__enrolled_at__gte=last_week)
                )
            ).filter(recent_enrollments__gt=0).order_by('-recent_enrollments')[:5]

            # 活跃教师（最近一周有课程安排）
            active_teachers = User.objects.filter(
                user_type='teacher',
                taught_schedules__created_at__gte=last_week
            ).distinct().count()

            # 教室利用率（今日）
            total_classrooms = Classroom.objects.filter(is_active=True).count()
            used_classrooms_today = Classroom.objects.filter(
                schedules__created_at__date=today
            ).distinct().count()

            classroom_utilization = (
                (used_classrooms_today / max(total_classrooms, 1)) * 100
                if total_classrooms > 0 else 0
            )

            # 系统健康状态检查
            try:
                # 检查数据库连接
                User.objects.first()
                db_status = 'healthy'
            except Exception:
                db_status = 'error'

            # 检查缓存（如果使用Redis）
            cache_status = 'healthy'  # 简化处理

            # API状态
            api_status = 'healthy'

            recent_activities = [
                {
                    'type': 'enrollment',
                    'count': recent_enrollments,
                    'time': '最近24小时',
                    'change': enrollment_change,
                    'change_percent': round(enrollment_change_percent, 1)
                },
                {
                    'type': 'course_creation',
                    'count': recent_courses_created,
                    'time': '最近24小时'
                },
                {
                    'type': 'schedule_creation',
                    'count': recent_schedules_created,
                    'time': '最近24小时'
                },
                {
                    'type': 'active_teachers',
                    'count': active_teachers,
                    'time': '最近一周'
                }
            ]

            system_status = {
                'database': db_status,
                'api': api_status,
                'cache': cache_status,
                'last_updated': now.isoformat(),
                'uptime': '99.9%',  # 模拟数据
                'response_time': '120ms'  # 模拟数据
            }

            data = {
                'total_active_users': total_active_users,
                'recent_enrollments': recent_enrollments,
                'today_enrollments': today_enrollments,
                'enrollment_change': enrollment_change,
                'enrollment_change_percent': round(enrollment_change_percent, 1),
                'classroom_utilization': round(classroom_utilization, 1),
                'popular_courses': [
                    {
                        'id': course.id,
                        'name': course.name,
                        'code': course.code,
                        'recent_enrollments': course.recent_enrollments
                    } for course in popular_courses
                ],
                'recent_activities': recent_activities,
                'system_status': system_status,
                'statistics_summary': {
                    'total_courses': Course.objects.count(),
                    'total_students': User.objects.filter(user_type='student').count(),
                    'total_teachers': User.objects.filter(user_type='teacher').count(),
                    'total_classrooms': total_classrooms,
                    'active_schedules': Schedule.objects.filter(status='active').count()
                }
            }

            return Response({
                'code': 200,
                'message': '获取实时统计数据成功',
                'data': data
            })

        except Exception as e:
            return Response({
                'code': 500,
                'message': f'获取实时统计数据失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdvancedAnalyticsView(APIView):
    """高级分析视图"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """获取高级分析数据"""
        try:
            # 获取查询参数
            time_range = request.query_params.get('time_range', '30')  # 默认30天
            analysis_type = request.query_params.get('type', 'enrollment')

            days = int(time_range)
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)

            if analysis_type == 'enrollment':
                data = self._get_enrollment_analysis(start_date, end_date)
            elif analysis_type == 'course_performance':
                data = self._get_course_performance_analysis(start_date, end_date)
            elif analysis_type == 'teacher_workload':
                data = self._get_teacher_workload_analysis(start_date, end_date)
            elif analysis_type == 'classroom_efficiency':
                data = self._get_classroom_efficiency_analysis(start_date, end_date)
            else:
                return Response({
                    'code': 400,
                    'message': '不支持的分析类型',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                'code': 200,
                'message': '获取高级分析数据成功',
                'data': data
            })

        except Exception as e:
            return Response({
                'code': 500,
                'message': f'获取高级分析数据失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _get_enrollment_analysis(self, start_date, end_date):
        """选课趋势分析"""
        # 按日期分组的选课统计
        daily_enrollments = Enrollment.objects.filter(
            enrolled_at__range=[start_date, end_date]
        ).extra(
            select={'date': 'DATE(enrolled_at)'}
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')

        # 按课程类型分组的选课统计
        enrollment_by_type = Enrollment.objects.filter(
            enrolled_at__range=[start_date, end_date]
        ).values('course__course_type').annotate(
            count=Count('id'),
            percentage=Count('id') * 100.0 / Enrollment.objects.filter(
                enrolled_at__range=[start_date, end_date]
            ).count()
        )

        # 按院系分组的选课统计
        enrollment_by_department = Enrollment.objects.filter(
            enrolled_at__range=[start_date, end_date]
        ).values('course__department').annotate(
            count=Count('id'),
            unique_students=Count('student', distinct=True)
        ).order_by('-count')

        # 选课高峰时间分析
        hourly_enrollments = Enrollment.objects.filter(
            enrolled_at__range=[start_date, end_date]
        ).extra(
            select={'hour': 'EXTRACT(hour FROM enrolled_at)'}
        ).values('hour').annotate(
            count=Count('id')
        ).order_by('hour')

        return {
            'daily_trend': list(daily_enrollments),
            'by_course_type': list(enrollment_by_type),
            'by_department': list(enrollment_by_department),
            'hourly_pattern': list(hourly_enrollments),
            'summary': {
                'total_enrollments': Enrollment.objects.filter(
                    enrolled_at__range=[start_date, end_date]
                ).count(),
                'unique_students': Enrollment.objects.filter(
                    enrolled_at__range=[start_date, end_date]
                ).values('student').distinct().count(),
                'unique_courses': Enrollment.objects.filter(
                    enrolled_at__range=[start_date, end_date]
                ).values('course').distinct().count()
            }
        }

    def _get_course_performance_analysis(self, start_date, end_date):
        """课程表现分析"""
        # 课程选课率分析
        courses_with_stats = Course.objects.annotate(
            enrollment_count=Count('enrollments', filter=Q(
                enrollments__enrolled_at__range=[start_date, end_date],
                enrollments__is_active=True
            )),
            enrollment_rate=Case(
                When(max_students__gt=0, then=Count('enrollments', filter=Q(
                    enrollments__enrolled_at__range=[start_date, end_date],
                    enrollments__is_active=True
                )) * 100.0 / F('max_students')),
                default=0,
                output_field=FloatField()
            )
        ).filter(enrollment_count__gt=0).order_by('-enrollment_rate')

        # 热门课程排行
        top_courses = courses_with_stats[:10]

        # 冷门课程（选课率低）
        low_enrollment_courses = courses_with_stats.filter(
            enrollment_rate__lt=50
        ).order_by('enrollment_rate')[:10]

        # 按学分分组的课程表现
        performance_by_credits = Course.objects.filter(
            enrollments__enrolled_at__range=[start_date, end_date]
        ).values('credits').annotate(
            course_count=Count('id', distinct=True),
            avg_enrollment_rate=Avg(
                Case(
                    When(max_students__gt=0, then=Count('enrollments', filter=Q(
                        enrollments__is_active=True
                    )) * 100.0 / F('max_students')),
                    default=0,
                    output_field=FloatField()
                )
            )
        ).order_by('credits')

        return {
            'top_courses': [
                {
                    'id': course.id,
                    'name': course.name,
                    'code': course.code,
                    'enrollment_count': course.enrollment_count,
                    'enrollment_rate': round(course.enrollment_rate, 2),
                    'max_students': course.max_students,
                    'department': course.department
                } for course in top_courses
            ],
            'low_enrollment_courses': [
                {
                    'id': course.id,
                    'name': course.name,
                    'code': course.code,
                    'enrollment_count': course.enrollment_count,
                    'enrollment_rate': round(course.enrollment_rate, 2),
                    'max_students': course.max_students,
                    'department': course.department
                } for course in low_enrollment_courses
            ],
            'performance_by_credits': list(performance_by_credits),
            'summary': {
                'total_courses': Course.objects.count(),
                'active_courses': Course.objects.filter(
                    enrollments__enrolled_at__range=[start_date, end_date]
                ).distinct().count(),
                'avg_enrollment_rate': courses_with_stats.aggregate(
                    avg_rate=Avg('enrollment_rate')
                )['avg_rate'] or 0
            }
        }

    def _get_teacher_workload_analysis(self, start_date, end_date):
        """教师工作量分析"""
        # 教师工作量统计
        teachers_with_workload = User.objects.filter(
            user_type='teacher'
        ).annotate(
            course_count=Count('taught_courses', distinct=True),
            schedule_count=Count('taught_schedules', filter=Q(
                taught_schedules__created_at__range=[start_date, end_date]
            )),
            total_students=Count('taught_courses__enrollments', filter=Q(
                taught_courses__enrollments__is_active=True
            )),
            avg_class_size=Avg('taught_courses__enrollments__count', filter=Q(
                taught_courses__enrollments__is_active=True
            ))
        ).filter(course_count__gt=0).order_by('-course_count')

        # 工作量分布
        workload_distribution = teachers_with_workload.aggregate(
            light_workload=Count('id', filter=Q(course_count__lte=2)),
            medium_workload=Count('id', filter=Q(course_count__range=[3, 5])),
            heavy_workload=Count('id', filter=Q(course_count__gte=6))
        )

        # 按院系分组的教师工作量
        workload_by_department = User.objects.filter(
            user_type='teacher',
            teacher_profile__department__isnull=False
        ).values('teacher_profile__department').annotate(
            teacher_count=Count('id'),
            avg_courses=Avg('taught_courses__count'),
            total_courses=Count('taught_courses', distinct=True)
        ).order_by('-total_courses')

        return {
            'teacher_workload': [
                {
                    'id': teacher.id,
                    'name': teacher.get_full_name() or teacher.username,
                    'course_count': teacher.course_count,
                    'schedule_count': teacher.schedule_count,
                    'total_students': teacher.total_students,
                    'avg_class_size': round(teacher.avg_class_size or 0, 1)
                } for teacher in teachers_with_workload[:20]
            ],
            'workload_distribution': workload_distribution,
            'by_department': list(workload_by_department),
            'summary': {
                'total_teachers': User.objects.filter(user_type='teacher').count(),
                'active_teachers': teachers_with_workload.count(),
                'avg_courses_per_teacher': teachers_with_workload.aggregate(
                    avg=Avg('course_count')
                )['avg'] or 0
            }
        }

    def _get_classroom_efficiency_analysis(self, start_date, end_date):
        """教室效率分析"""
        # 教室使用统计
        classrooms_with_usage = Classroom.objects.annotate(
            schedule_count=Count('schedules', filter=Q(
                schedules__created_at__range=[start_date, end_date],
                schedules__status='active'
            )),
            total_hours=Sum('schedules__time_slot__duration', filter=Q(
                schedules__created_at__range=[start_date, end_date],
                schedules__status='active'
            )),
            utilization_rate=Case(
                When(capacity__gt=0, then=Count('schedules', filter=Q(
                    schedules__created_at__range=[start_date, end_date],
                    schedules__status='active'
                )) * 100.0 / 40),  # 假设每周40个时间段
                default=0,
                output_field=FloatField()
            )
        ).filter(is_active=True).order_by('-utilization_rate')

        # 使用率分布
        utilization_distribution = classrooms_with_usage.aggregate(
            low_utilization=Count('id', filter=Q(utilization_rate__lt=30)),
            medium_utilization=Count('id', filter=Q(utilization_rate__range=[30, 70])),
            high_utilization=Count('id', filter=Q(utilization_rate__gt=70))
        )

        # 按建筑分组的教室使用情况
        usage_by_building = Classroom.objects.filter(
            is_active=True
        ).values('building__name').annotate(
            classroom_count=Count('id'),
            avg_utilization=Avg('utilization_rate'),
            total_schedules=Count('schedules', filter=Q(
                schedules__created_at__range=[start_date, end_date],
                schedules__status='active'
            ))
        ).order_by('-avg_utilization')

        # 教室类型效率分析
        efficiency_by_type = Classroom.objects.filter(
            is_active=True
        ).values('room_type').annotate(
            classroom_count=Count('id'),
            avg_utilization=Avg('utilization_rate'),
            avg_capacity=Avg('capacity')
        ).order_by('-avg_utilization')

        return {
            'classroom_usage': [
                {
                    'id': classroom.id,
                    'name': f"{classroom.building.name}{classroom.room_number}",
                    'building': classroom.building.name,
                    'capacity': classroom.capacity,
                    'room_type': classroom.room_type,
                    'schedule_count': classroom.schedule_count,
                    'utilization_rate': round(classroom.utilization_rate or 0, 2)
                } for classroom in classrooms_with_usage[:20]
            ],
            'utilization_distribution': utilization_distribution,
            'by_building': list(usage_by_building),
            'by_room_type': list(efficiency_by_type),
            'summary': {
                'total_classrooms': Classroom.objects.filter(is_active=True).count(),
                'avg_utilization': classrooms_with_usage.aggregate(
                    avg=Avg('utilization_rate')
                )['avg'] or 0,
                'most_efficient': classrooms_with_usage.first().building.name if classrooms_with_usage.exists() else None
            }
        }


class RealtimeActivitiesView(APIView):
    """实时活动视图"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """获取实时活动数据"""
        try:
            # 最近的选课活动
            recent_enrollments = Enrollment.objects.select_related(
                'student', 'course'
            ).filter(
                enrolled_at__gte=timezone.now() - timedelta(hours=24)
            ).order_by('-enrolled_at')[:10]

            activities = []
            for enrollment in recent_enrollments:
                activities.append({
                    'type': 'enrollment',
                    'user': enrollment.student.first_name or enrollment.student.username,
                    'course': enrollment.course.name,
                    'time': enrollment.enrolled_at.isoformat(),
                    'description': f'{enrollment.student.first_name or enrollment.student.username} 选择了课程 {enrollment.course.name}'
                })

            return Response({
                'code': 200,
                'message': '获取实时活动数据成功',
                'data': activities
            })

        except Exception as e:
            return Response({
                'code': 500,
                'message': f'获取实时活动数据失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 导出视图类
class ExportDashboardView(APIView):
    """导出仪表板数据"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """导出仪表板数据"""
        try:
            serializer = ExportRequestSerializer(data=request.data)
            if serializer.is_valid():
                # 这里可以实现实际的导出逻辑
                return Response({
                    'code': 200,
                    'message': '导出请求已提交，请稍后下载',
                    'data': {'download_url': '/api/v1/analytics/download/dashboard.xlsx'}
                })
            else:
                return Response({
                    'code': 400,
                    'message': '请求参数错误',
                    'data': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'code': 500,
                'message': f'导出失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExportCourseAnalyticsView(APIView):
    """导出课程分析数据"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """导出课程分析数据"""
        # 类似的导出逻辑
        return Response({
            'code': 200,
            'message': '导出请求已提交',
            'data': {'download_url': '/api/v1/analytics/download/courses.xlsx'}
        })


class ExportUserAnalyticsView(APIView):
    """导出用户分析数据"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """导出用户分析数据"""
        # 类似的导出逻辑
        return Response({
            'code': 200,
            'message': '导出请求已提交',
            'data': {'download_url': '/api/v1/analytics/download/users.xlsx'}
        })
