from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Avg, Count
from .models import Course, Enrollment, Grade, CourseEvaluation, GradeComponent

User = get_user_model()


class CourseSerializer(serializers.ModelSerializer):
    """课程序列化器"""

    teachers_info = serializers.SerializerMethodField()
    prerequisites_info = serializers.SerializerMethodField()
    grade_components = serializers.SerializerMethodField()
    current_enrollment = serializers.ReadOnlyField()
    is_full = serializers.ReadOnlyField()
    can_open = serializers.ReadOnlyField()
    course_type_display = serializers.CharField(source='get_course_type_display', read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'code', 'name', 'english_name', 'course_type', 'course_type_display',
            'credits', 'hours', 'department', 'semester', 'academic_year',
            'description', 'objectives', 'prerequisites', 'prerequisites_info',
            'teachers', 'teachers_info', 'max_students', 'min_students',
            'grade_components', 'current_enrollment', 'is_full', 'can_open',
            'is_active', 'is_published', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'current_enrollment', 'is_full', 'can_open', 'created_at', 'updated_at']
    
    def get_teachers_info(self, obj):
        """获取教师信息"""
        return [
            {
                'id': teacher.id,
                'username': teacher.username,
                'name': f"{teacher.first_name} {teacher.last_name}".strip() or teacher.username,
                'department': teacher.department
            }
            for teacher in obj.teachers.all()
        ]
    
    def get_prerequisites_info(self, obj):
        """获取先修课程信息"""
        return [
            {
                'id': course.id,
                'code': course.code,
                'name': course.name
            }
            for course in obj.prerequisites.all()
        ]

    def get_grade_components(self, obj):
        """获取成绩组成信息"""
        components = obj.grade_components.all()
        return [
            {
                'id': component.id,
                'name': component.name,
                'weight': component.weight,
                'max_score': component.max_score,
                'is_required': component.is_required,
                'description': component.description,
                'order': component.order
            }
            for component in components
        ]


class CourseListSerializer(serializers.ModelSerializer):
    """课程列表序列化器（简化版）"""
    
    current_enrollment = serializers.ReadOnlyField()
    is_full = serializers.ReadOnlyField()
    course_type_display = serializers.CharField(source='get_course_type_display', read_only=True)
    teachers_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'code', 'name', 'course_type', 'course_type_display',
            'credits', 'hours', 'department', 'semester',
            'max_students', 'current_enrollment', 'is_full',
            'teachers_count', 'is_active', 'is_published'
        ]
    
    def get_teachers_count(self, obj):
        """获取教师数量"""
        return obj.teachers.count()


class EnrollmentSerializer(serializers.ModelSerializer):
    """选课记录序列化器"""
    
    student_info = serializers.SerializerMethodField()
    course_info = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'student', 'student_info', 'course', 'course_info',
            'status', 'status_display', 'score', 'grade',
            'enrolled_at', 'dropped_at', 'is_active'
        ]
        read_only_fields = ['id', 'enrolled_at']
    
    def get_student_info(self, obj):
        """获取学生信息"""
        return {
            'id': obj.student.id,
            'username': obj.student.username,
            'name': f"{obj.student.first_name} {obj.student.last_name}".strip() or obj.student.username,
            'student_id': obj.student.student_id,
            'department': obj.student.department
        }
    
    def get_course_info(self, obj):
        """获取课程信息"""
        return {
            'id': obj.course.id,
            'code': obj.course.code,
            'name': obj.course.name,
            'credits': obj.course.credits,
            'department': obj.course.department
        }


class EnrollmentCreateSerializer(serializers.ModelSerializer):
    """选课创建序列化器"""
    
    class Meta:
        model = Enrollment
        fields = ['student', 'course']
    
    def validate(self, attrs):
        """验证选课数据"""
        student = attrs['student']
        course = attrs['course']
        
        # 检查学生类型
        if student.user_type != 'student':
            raise serializers.ValidationError('只有学生可以选课')
        
        # 检查课程是否发布
        if not course.is_published:
            raise serializers.ValidationError('课程尚未发布')
        
        # 检查课程是否启用
        if not course.is_active:
            raise serializers.ValidationError('课程已停用')
        
        # 检查是否已选过该课程
        if Enrollment.objects.filter(student=student, course=course, is_active=True).exists():
            raise serializers.ValidationError('已选过该课程')
        
        # 检查课程是否已满
        if course.is_full:
            raise serializers.ValidationError('课程已满员')
        
        return attrs
    
    def create(self, validated_data):
        """创建选课记录"""
        return Enrollment.objects.create(**validated_data)


class CourseStatisticsSerializer(serializers.Serializer):
    """课程统计序列化器"""

    total_courses = serializers.IntegerField()
    active_courses = serializers.IntegerField()
    published_courses = serializers.IntegerField()
    total_enrollments = serializers.IntegerField()
    by_department = serializers.DictField()
    by_course_type = serializers.DictField()
    enrollment_trend = serializers.ListField()


class GradeComponentSerializer(serializers.ModelSerializer):
    """成绩组成序列化器"""

    class Meta:
        model = GradeComponent
        fields = [
            'id', 'course', 'name', 'weight', 'max_score',
            'is_required', 'description', 'order',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        """验证权重总和"""
        course = data.get('course')
        weight = data.get('weight', 0)

        if course:
            # 计算其他组成的权重总和
            existing_weight = GradeComponent.objects.filter(
                course=course
            ).exclude(pk=self.instance.pk if self.instance else None).aggregate(
                total=models.Sum('weight')
            )['total'] or 0

            if existing_weight + weight > 100:
                raise serializers.ValidationError(
                    f'权重总和不能超过100%，当前总和为{existing_weight + weight}%'
                )

        return data


class GradeSerializer(serializers.ModelSerializer):
    """详细成绩序列化器"""

    student_info = serializers.SerializerMethodField()
    course_info = serializers.SerializerMethodField()
    component_info = serializers.SerializerMethodField()
    graded_by_name = serializers.CharField(source='graded_by.first_name', read_only=True)
    grade_type_display = serializers.CharField(source='get_grade_type_display', read_only=True)
    percentage_score = serializers.ReadOnlyField()
    weighted_score = serializers.ReadOnlyField()
    letter_grade = serializers.ReadOnlyField()

    class Meta:
        model = Grade
        fields = [
            'id', 'enrollment', 'component', 'student_info', 'course_info', 'component_info',
            'grade_type', 'grade_type_display', 'name', 'description',
            'score', 'max_score', 'percentage_score', 'weighted_score', 'letter_grade', 'weight',
            'graded_by', 'graded_by_name', 'graded_at', 'feedback',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'percentage_score', 'weighted_score', 'letter_grade', 'created_at', 'updated_at']

    def get_student_info(self, obj):
        """获取学生信息"""
        student = obj.enrollment.student
        return {
            'id': student.id,
            'username': student.username,
            'name': f"{student.first_name} {student.last_name}",
            'student_id': student.student_id
        }

    def get_course_info(self, obj):
        """获取课程信息"""
        course = obj.enrollment.course
        return {
            'id': course.id,
            'code': course.code,
            'name': course.name
        }

    def get_component_info(self, obj):
        """获取成绩组成信息"""
        if obj.component:
            return {
                'id': obj.component.id,
                'name': obj.component.name,
                'weight': obj.component.weight,
                'max_score': obj.component.max_score
            }
        return None


class CourseEvaluationSerializer(serializers.ModelSerializer):
    """课程评价序列化器"""

    student_info = serializers.SerializerMethodField()
    course_info = serializers.SerializerMethodField()
    average_rating = serializers.ReadOnlyField()

    class Meta:
        model = CourseEvaluation
        fields = [
            'id', 'enrollment', 'student_info', 'course_info',
            'teaching_quality', 'course_content', 'difficulty_level',
            'workload', 'overall_satisfaction', 'average_rating',
            'comments', 'suggestions', 'would_recommend',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'average_rating', 'created_at', 'updated_at']

    def get_student_info(self, obj):
        """获取学生信息"""
        student = obj.enrollment.student
        return {
            'id': student.id,
            'username': student.username,
            'name': f"{student.first_name} {student.last_name}",
            'student_id': student.student_id
        }

    def get_course_info(self, obj):
        """获取课程信息"""
        course = obj.enrollment.course
        return {
            'id': course.id,
            'code': course.code,
            'name': course.name
        }


class GradeSummarySerializer(serializers.Serializer):
    """成绩汇总序列化器"""

    enrollment_id = serializers.IntegerField()
    student_info = serializers.DictField()
    course_info = serializers.DictField()
    detailed_grades = GradeSerializer(many=True, read_only=True)
    final_score = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    final_grade = serializers.CharField(read_only=True)
    grade_breakdown = serializers.DictField(read_only=True)


class CourseGradeStatisticsSerializer(serializers.Serializer):
    """课程成绩统计序列化器"""

    course_info = serializers.DictField()
    total_students = serializers.IntegerField()
    graded_students = serializers.IntegerField()
    average_score = serializers.DecimalField(max_digits=5, decimal_places=2)
    grade_distribution = serializers.DictField()
    pass_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    score_range = serializers.DictField()
