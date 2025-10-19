from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Avg, Sum, Count
from apps.courses.models import Course, Enrollment
from apps.courses.serializers import CourseSerializer
from .models import StudentProfile, StudentCourseProgress

User = get_user_model()


class StudentProfileSerializer(serializers.ModelSerializer):
    """学生档案序列化器"""
    
    user_info = serializers.SerializerMethodField()
    enrollment_status_display = serializers.CharField(source='get_enrollment_status_display', read_only=True)
    
    class Meta:
        model = StudentProfile
        fields = [
            'id', 'user', 'user_info', 'admission_year', 'major', 'class_name',
            'gpa', 'total_credits', 'completed_credits', 'remaining_credits',
            'completion_rate', 'enrollment_status', 'enrollment_status_display',
            'emergency_contact', 'emergency_phone', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'remaining_credits', 'completion_rate', 'created_at', 'updated_at']
    
    def get_user_info(self, obj):
        """获取用户基本信息"""
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'email': obj.user.email,
            'student_id': obj.user.student_id,
            'department': obj.user.department,
        }


class StudentCourseProgressSerializer(serializers.ModelSerializer):
    """学生课程进度序列化器"""
    
    course_info = CourseSerializer(source='course', read_only=True)
    student_name = serializers.CharField(source='student.first_name', read_only=True)
    
    class Meta:
        model = StudentCourseProgress
        fields = [
            'id', 'student', 'student_name', 'course', 'course_info',
            'attendance_rate', 'assignment_completion', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StudentDashboardSerializer(serializers.Serializer):
    """学生仪表板数据序列化器"""

    # 基本信息 - 已经是序列化后的数据
    student_info = serializers.DictField(read_only=True)

    # 选课统计
    total_courses = serializers.IntegerField(read_only=True)
    current_semester_courses = serializers.IntegerField(read_only=True)
    completed_courses = serializers.IntegerField(read_only=True)

    # 成绩统计
    average_score = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    latest_grades = serializers.ListField(read_only=True)

    # 今日课程
    today_schedule = serializers.ListField(read_only=True)

    # 通知和截止日期
    notifications = serializers.ListField(read_only=True)
    upcoming_deadlines = serializers.ListField(read_only=True)


class StudentEnrollmentSerializer(serializers.ModelSerializer):
    """学生选课记录序列化器"""
    
    course_info = CourseSerializer(source='course', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    grade_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'course', 'course_info', 'status', 'status_display',
            'score', 'grade', 'grade_display', 'enrolled_at', 'dropped_at', 'is_active'
        ]
        read_only_fields = ['id', 'enrolled_at', 'dropped_at']
    
    def get_grade_display(self, obj):
        """获取成绩显示"""
        if obj.score is not None:
            return f"{obj.score}分"
        return "未录入"


class AvailableCourseSerializer(serializers.ModelSerializer):
    """可选课程序列化器"""
    
    teachers_info = serializers.SerializerMethodField()
    enrollment_info = serializers.SerializerMethodField()
    can_enroll = serializers.SerializerMethodField()
    conflict_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'code', 'name', 'credits', 'hours', 'course_type',
            'department', 'semester', 'description', 'teachers_info',
            'max_students', 'current_enrollment', 'enrollment_info',
            'can_enroll', 'conflict_info', 'is_published'
        ]
    
    def get_teachers_info(self, obj):
        """获取教师信息"""
        return [
            {
                'id': teacher.id,
                'name': f"{teacher.first_name} {teacher.last_name}",
                'employee_id': teacher.employee_id
            }
            for teacher in obj.teachers.all()
        ]
    
    def get_enrollment_info(self, obj):
        """获取选课信息"""
        return {
            'current': obj.current_enrollment,
            'max': obj.max_students,
            'available': obj.max_students - obj.current_enrollment,
            'is_full': obj.is_full
        }
    
    def get_can_enroll(self, obj):
        """检查是否可以选课"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        
        # 检查是否已选课
        if Enrollment.objects.filter(
            student=request.user,
            course=obj,
            status='enrolled'
        ).exists():
            return False
        
        # 检查是否已满员
        if obj.is_full:
            return False
        
        return True
    
    def get_conflict_info(self, obj):
        """获取时间冲突信息"""
        # 这里可以添加时间冲突检测逻辑
        # 暂时返回空，后续可以扩展
        return []


class CourseScheduleSerializer(serializers.Serializer):
    """课程表序列化器"""
    
    course_id = serializers.IntegerField()
    course_name = serializers.CharField()
    course_code = serializers.CharField()
    teacher_name = serializers.CharField()
    classroom = serializers.CharField()
    time_slot = serializers.CharField()
    day_of_week = serializers.IntegerField()
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()
    week_range = serializers.CharField()
