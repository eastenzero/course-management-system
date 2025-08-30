from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Count, Avg
from apps.courses.models import Course, Enrollment
from apps.courses.serializers import CourseSerializer
from .models import TeacherProfile, TeacherCourseAssignment, TeacherNotice

User = get_user_model()


class TeacherProfileSerializer(serializers.ModelSerializer):
    """教师档案序列化器"""
    
    user_info = serializers.SerializerMethodField()
    title_display = serializers.CharField(source='get_title_display', read_only=True)
    full_name = serializers.CharField(read_only=True)
    teaching_courses_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = TeacherProfile
        fields = [
            'id', 'user', 'user_info', 'title', 'title_display', 'full_name',
            'research_area', 'office_location', 'office_hours', 'teaching_experience',
            'education_background', 'office_phone', 'personal_website',
            'teaching_courses_count', 'is_active_teacher', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'teaching_courses_count', 'created_at', 'updated_at']
    
    def get_user_info(self, obj):
        """获取用户基本信息"""
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'email': obj.user.email,
            'employee_id': obj.user.employee_id,
            'department': obj.user.department,
        }


class TeacherCourseAssignmentSerializer(serializers.ModelSerializer):
    """教师课程分配序列化器"""
    
    course_info = CourseSerializer(source='course', read_only=True)
    teacher_name = serializers.CharField(source='teacher.first_name', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = TeacherCourseAssignment
        fields = [
            'id', 'teacher', 'teacher_name', 'course', 'course_info',
            'role', 'role_display', 'workload_hours', 'assigned_at', 'is_active'
        ]
        read_only_fields = ['id', 'assigned_at']


class TeacherNoticeSerializer(serializers.ModelSerializer):
    """教师通知序列化器"""
    
    course_info = serializers.SerializerMethodField()
    teacher_name = serializers.CharField(source='teacher.first_name', read_only=True)
    notice_type_display = serializers.CharField(source='get_notice_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = TeacherNotice
        fields = [
            'id', 'teacher', 'teacher_name', 'course', 'course_info',
            'title', 'content', 'notice_type', 'notice_type_display',
            'priority', 'priority_display', 'is_published', 'published_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'published_at', 'created_at', 'updated_at']
    
    def get_course_info(self, obj):
        """获取课程基本信息"""
        return {
            'id': obj.course.id,
            'code': obj.course.code,
            'name': obj.course.name,
            'semester': obj.course.semester
        }


class TeacherDashboardSerializer(serializers.Serializer):
    """教师仪表板数据序列化器"""
    
    # 基本信息 - 已经是序列化后的数据
    teacher_info = serializers.DictField(read_only=True)
    
    # 教学统计
    total_courses = serializers.IntegerField(read_only=True)
    current_semester_courses = serializers.IntegerField(read_only=True)
    total_students = serializers.IntegerField(read_only=True)
    
    # 课程统计
    course_statistics = serializers.DictField(read_only=True)
    
    # 今日教学安排
    today_schedule = serializers.ListField(read_only=True)
    
    # 待处理任务
    pending_tasks = serializers.ListField(read_only=True)
    
    # 最近通知
    recent_notices = serializers.ListField(read_only=True)


class TeacherCourseDetailSerializer(serializers.ModelSerializer):
    """教师课程详情序列化器"""
    
    teachers_info = serializers.SerializerMethodField()
    enrollment_statistics = serializers.SerializerMethodField()
    grade_statistics = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'code', 'name', 'credits', 'hours', 'course_type',
            'department', 'semester', 'academic_year', 'description',
            'objectives', 'teachers_info', 'max_students', 'min_students',
            'current_enrollment', 'enrollment_statistics', 'grade_statistics',
            'is_active', 'is_published', 'created_at', 'updated_at'
        ]
    
    def get_teachers_info(self, obj):
        """获取教师信息"""
        return [
            {
                'id': teacher.id,
                'name': f"{teacher.first_name} {teacher.last_name}",
                'employee_id': teacher.employee_id,
                'title': getattr(teacher.teacher_profile, 'get_title_display', lambda: '未设置')()
            }
            for teacher in obj.teachers.all()
        ]
    
    def get_enrollment_statistics(self, obj):
        """获取选课统计"""
        enrollments = obj.enrollments.filter(is_active=True)
        
        return {
            'total': enrollments.count(),
            'by_status': {
                'enrolled': enrollments.filter(status='enrolled').count(),
                'completed': enrollments.filter(status='completed').count(),
                'dropped': enrollments.filter(status='dropped').count(),
                'failed': enrollments.filter(status='failed').count(),
            }
        }
    
    def get_grade_statistics(self, obj):
        """获取成绩统计"""
        graded_enrollments = obj.enrollments.filter(
            is_active=True,
            score__isnull=False
        )
        
        if not graded_enrollments.exists():
            return {
                'total_graded': 0,
                'average_score': 0,
                'grade_distribution': {},
                'pass_rate': 0
            }
        
        scores = [float(e.score) for e in graded_enrollments]
        average_score = sum(scores) / len(scores)
        pass_count = sum(1 for score in scores if score >= 60)
        pass_rate = (pass_count / len(scores)) * 100
        
        # 成绩分布
        grade_distribution = {
            'A (90-100)': sum(1 for score in scores if score >= 90),
            'B (80-89)': sum(1 for score in scores if 80 <= score < 90),
            'C (70-79)': sum(1 for score in scores if 70 <= score < 80),
            'D (60-69)': sum(1 for score in scores if 60 <= score < 70),
            'F (0-59)': sum(1 for score in scores if score < 60),
        }
        
        return {
            'total_graded': len(scores),
            'average_score': round(average_score, 2),
            'grade_distribution': grade_distribution,
            'pass_rate': round(pass_rate, 2)
        }


class CourseStudentSerializer(serializers.ModelSerializer):
    """课程学生序列化器"""
    
    student_info = serializers.SerializerMethodField()
    enrollment_info = serializers.SerializerMethodField()
    progress_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'student_info', 'enrollment_info', 'progress_info',
            'score', 'grade', 'enrolled_at', 'status'
        ]
    
    def get_student_info(self, obj):
        """获取学生基本信息"""
        student = obj.student
        profile = getattr(student, 'student_profile', None)
        
        return {
            'id': student.id,
            'username': student.username,
            'name': f"{student.first_name} {student.last_name}",
            'student_id': student.student_id,
            'email': student.email,
            'department': student.department,
            'major': profile.major if profile else '',
            'class_name': profile.class_name if profile else '',
        }
    
    def get_enrollment_info(self, obj):
        """获取选课信息"""
        return {
            'enrolled_at': obj.enrolled_at,
            'status': obj.status,
            'status_display': obj.get_status_display(),
            'is_active': obj.is_active
        }
    
    def get_progress_info(self, obj):
        """获取学习进度信息"""
        # 这里可以添加学习进度相关信息
        # 暂时返回基本信息
        return {
            'attendance_rate': 0,  # 需要从考勤系统获取
            'assignment_completion': 0,  # 需要从作业系统获取
            'participation_score': 0,  # 需要从课堂表现系统获取
        }


class GradeEntrySerializer(serializers.ModelSerializer):
    """成绩录入序列化器"""
    
    student_name = serializers.CharField(source='student.first_name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'student', 'student_name', 'student_id',
            'course', 'course_name', 'score', 'grade', 'status'
        ]
        read_only_fields = ['id', 'student', 'course']
    
    def validate_score(self, value):
        """验证成绩"""
        if value is not None and (value < 0 or value > 100):
            raise serializers.ValidationError('成绩必须在0-100之间')
        return value
    
    def update(self, instance, validated_data):
        """更新成绩时自动计算等级"""
        score = validated_data.get('score')
        if score is not None:
            # 自动计算等级
            if score >= 90:
                validated_data['grade'] = 'A'
            elif score >= 80:
                validated_data['grade'] = 'B'
            elif score >= 70:
                validated_data['grade'] = 'C'
            elif score >= 60:
                validated_data['grade'] = 'D'
            else:
                validated_data['grade'] = 'F'
            
            # 如果成绩及格，更新状态为已完成
            if score >= 60 and instance.status == 'enrolled':
                validated_data['status'] = 'completed'
            elif score < 60 and instance.status == 'enrolled':
                validated_data['status'] = 'failed'
        
        return super().update(instance, validated_data)
