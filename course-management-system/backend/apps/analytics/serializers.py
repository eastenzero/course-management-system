from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.courses.models import Course, Enrollment
from apps.classrooms.models import Classroom
from apps.schedules.models import Schedule

User = get_user_model()


class DashboardStatsSerializer(serializers.Serializer):
    """仪表板统计数据序列化器"""
    total_users = serializers.IntegerField(help_text="用户总数")
    total_students = serializers.IntegerField(help_text="学生总数")
    total_teachers = serializers.IntegerField(help_text="教师总数")
    total_courses = serializers.IntegerField(help_text="课程总数")
    total_enrollments = serializers.IntegerField(help_text="选课总数")
    total_classrooms = serializers.IntegerField(help_text="教室总数")
    total_schedules = serializers.IntegerField(help_text="课程安排总数")
    
    # 增长率数据
    user_growth_rate = serializers.FloatField(help_text="用户增长率")
    course_growth_rate = serializers.FloatField(help_text="课程增长率")
    enrollment_growth_rate = serializers.FloatField(help_text="选课增长率")


class CourseAnalyticsSerializer(serializers.Serializer):
    """课程分析数据序列化器"""
    course_id = serializers.IntegerField()
    course_name = serializers.CharField()
    course_code = serializers.CharField()
    enrollment_count = serializers.IntegerField(help_text="选课人数")
    max_students = serializers.IntegerField(help_text="最大选课人数")
    enrollment_rate = serializers.FloatField(help_text="选课率")
    department = serializers.CharField(help_text="开课院系")
    course_type = serializers.CharField(help_text="课程类型")
    credits = serializers.IntegerField(help_text="学分")


class UserAnalyticsSerializer(serializers.Serializer):
    """用户分析数据序列化器"""
    user_type = serializers.CharField(help_text="用户类型")
    count = serializers.IntegerField(help_text="用户数量")
    percentage = serializers.FloatField(help_text="占比")
    active_count = serializers.IntegerField(help_text="活跃用户数")
    active_rate = serializers.FloatField(help_text="活跃率")


class ClassroomAnalyticsSerializer(serializers.Serializer):
    """教室分析数据序列化器"""
    classroom_id = serializers.IntegerField()
    classroom_name = serializers.CharField()
    building_name = serializers.CharField()
    capacity = serializers.IntegerField(help_text="容量")
    utilization_rate = serializers.FloatField(help_text="使用率")
    schedule_count = serializers.IntegerField(help_text="排课数量")
    room_type = serializers.CharField(help_text="教室类型")


class EnrollmentTrendSerializer(serializers.Serializer):
    """选课趋势数据序列化器"""
    date = serializers.DateField(help_text="日期")
    enrollment_count = serializers.IntegerField(help_text="选课数量")
    new_enrollments = serializers.IntegerField(help_text="新增选课")
    dropped_enrollments = serializers.IntegerField(help_text="退课数量")


class DepartmentStatsSerializer(serializers.Serializer):
    """院系统计数据序列化器"""
    department = serializers.CharField(help_text="院系名称")
    student_count = serializers.IntegerField(help_text="学生数量")
    teacher_count = serializers.IntegerField(help_text="教师数量")
    course_count = serializers.IntegerField(help_text="课程数量")
    enrollment_count = serializers.IntegerField(help_text="选课数量")


class TimeSlotAnalyticsSerializer(serializers.Serializer):
    """时间段分析数据序列化器"""
    time_slot = serializers.CharField(help_text="时间段")
    schedule_count = serializers.IntegerField(help_text="排课数量")
    utilization_rate = serializers.FloatField(help_text="使用率")
    popular_courses = serializers.ListField(
        child=serializers.CharField(),
        help_text="热门课程"
    )


class OverviewAnalyticsSerializer(serializers.Serializer):
    """概览分析数据序列化器"""
    dashboard_stats = DashboardStatsSerializer()
    course_type_distribution = serializers.ListField(
        child=serializers.DictField(),
        help_text="课程类型分布"
    )
    enrollment_trends = serializers.ListField(
        child=EnrollmentTrendSerializer(),
        help_text="选课趋势"
    )
    department_stats = serializers.ListField(
        child=DepartmentStatsSerializer(),
        help_text="院系统计"
    )
    top_courses = serializers.ListField(
        child=CourseAnalyticsSerializer(),
        help_text="热门课程"
    )


class RealtimeStatsSerializer(serializers.Serializer):
    """实时统计数据序列化器"""
    total_active_users = serializers.IntegerField(help_text="活跃用户总数")
    recent_enrollments = serializers.IntegerField(help_text="最近24小时选课数")
    today_enrollments = serializers.IntegerField(help_text="今日选课数")
    enrollment_change = serializers.IntegerField(help_text="选课数变化")
    enrollment_change_percent = serializers.FloatField(help_text="选课数变化百分比")
    classroom_utilization = serializers.FloatField(help_text="教室利用率")
    popular_courses = serializers.ListField(
        child=serializers.DictField(),
        help_text="热门课程"
    )
    recent_activities = serializers.ListField(
        child=serializers.DictField(),
        help_text="最近活动"
    )
    system_status = serializers.DictField(help_text="系统状态")
    statistics_summary = serializers.DictField(help_text="统计摘要")


class ExportRequestSerializer(serializers.Serializer):
    """导出请求序列化器"""
    format = serializers.ChoiceField(
        choices=['excel', 'csv', 'pdf'],
        default='excel',
        help_text="导出格式"
    )
    date_range = serializers.CharField(
        required=False,
        help_text="日期范围，格式：YYYY-MM-DD,YYYY-MM-DD"
    )
    filters = serializers.DictField(
        required=False,
        help_text="过滤条件"
    )
