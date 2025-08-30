# file: backend/apps/algorithms/serializers.py
# 功能: 算法API序列化器

from rest_framework import serializers
from apps.courses.models import Course
from apps.classrooms.models import Classroom
from apps.users.models import User
from apps.schedules.models import Schedule


class ScheduleGenerationRequestSerializer(serializers.Serializer):
    """排课生成请求序列化器"""
    
    algorithm = serializers.ChoiceField(
        choices=[
            ('greedy', '贪心算法'),
            ('genetic', '遗传算法'),
            ('parallel_genetic', '并行遗传算法'),
            ('hybrid', '混合算法'),
            ('optimizer', '优化算法'),
        ],
        default='hybrid',
        help_text='选择排课算法'
    )
    
    semester = serializers.CharField(
        max_length=20,
        help_text='学期，如"2024春"'
    )
    
    academic_year = serializers.CharField(
        max_length=20,
        help_text='学年，如"2023-2024"'
    )
    
    course_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text='指定课程ID列表，为空则使用所有启用课程'
    )
    
    teacher_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text='指定教师ID列表，为空则使用所有启用教师'
    )
    
    classroom_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text='指定教室ID列表，为空则使用所有可用教室'
    )
    
    algorithm_params = serializers.JSONField(
        required=False,
        default=dict,
        help_text='算法参数配置'
    )
    
    enable_conflict_resolution = serializers.BooleanField(
        default=True,
        help_text='是否启用冲突解决'
    )
    
    enable_optimization = serializers.BooleanField(
        default=True,
        help_text='是否启用后优化'
    )


class AssignmentSerializer(serializers.Serializer):
    """分配序列化器"""
    
    course_id = serializers.IntegerField()
    course_name = serializers.CharField(read_only=True)
    teacher_id = serializers.IntegerField()
    teacher_name = serializers.CharField(read_only=True)
    classroom_id = serializers.IntegerField()
    classroom_name = serializers.CharField(read_only=True)
    day_of_week = serializers.IntegerField()
    day_name = serializers.CharField(read_only=True)
    time_slot = serializers.IntegerField()
    time_name = serializers.CharField(read_only=True)
    semester = serializers.CharField()
    academic_year = serializers.CharField()
    week_range = serializers.CharField(default="1-16")


class ConflictSerializer(serializers.Serializer):
    """冲突序列化器"""
    
    conflict_type = serializers.CharField()
    assignments = AssignmentSerializer(many=True)
    description = serializers.CharField()
    severity = serializers.CharField()
    created_at = serializers.DateTimeField()


class ScheduleResultSerializer(serializers.Serializer):
    """排课结果序列化器"""
    
    assignments = AssignmentSerializer(many=True)
    conflicts = ConflictSerializer(many=True)
    fitness_score = serializers.FloatField()
    algorithm_used = serializers.CharField()
    generation_time = serializers.FloatField()
    is_valid = serializers.BooleanField()
    total_assignments = serializers.IntegerField()
    conflict_count = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    metadata = serializers.JSONField()


class ScheduleAnalysisSerializer(serializers.Serializer):
    """排课分析序列化器"""
    
    schedule_summary = serializers.JSONField()
    conflict_analysis = serializers.JSONField()
    constraint_evaluation = serializers.JSONField()
    resource_analysis = serializers.JSONField()


class AlgorithmStatisticsSerializer(serializers.Serializer):
    """算法统计序列化器"""
    
    engine_stats = serializers.JSONField()
    constraint_manager_stats = serializers.JSONField()
    conflict_detector_stats = serializers.JSONField()
    conflict_resolver_stats = serializers.JSONField()


class ScheduleOptimizationRequestSerializer(serializers.Serializer):
    """排课优化请求序列化器"""
    
    schedule_id = serializers.IntegerField(
        help_text='要优化的排课方案ID'
    )
    
    optimization_strategies = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text='优化策略列表'
    )
    
    max_iterations = serializers.IntegerField(
        default=1000,
        help_text='最大迭代次数'
    )
    
    improvement_threshold = serializers.FloatField(
        default=0.01,
        help_text='改进阈值'
    )


class ConflictResolutionRequestSerializer(serializers.Serializer):
    """冲突解决请求序列化器"""
    
    schedule_id = serializers.IntegerField(
        help_text='要解决冲突的排课方案ID'
    )
    
    resolution_strategies = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text='解决策略列表'
    )
    
    max_attempts_per_conflict = serializers.IntegerField(
        default=50,
        help_text='每个冲突的最大解决尝试次数'
    )


class ScheduleExportRequestSerializer(serializers.Serializer):
    """排课导出请求序列化器"""
    
    schedule_id = serializers.IntegerField(
        help_text='要导出的排课方案ID'
    )
    
    format = serializers.ChoiceField(
        choices=[
            ('json', 'JSON格式'),
            ('excel', 'Excel格式'),
            ('csv', 'CSV格式'),
            ('pdf', 'PDF格式'),
        ],
        default='json',
        help_text='导出格式'
    )
    
    include_conflicts = serializers.BooleanField(
        default=True,
        help_text='是否包含冲突信息'
    )
    
    include_analysis = serializers.BooleanField(
        default=False,
        help_text='是否包含分析报告'
    )


class ScheduleImportRequestSerializer(serializers.Serializer):
    """排课导入请求序列化器"""
    
    file = serializers.FileField(
        help_text='要导入的文件'
    )
    
    format = serializers.ChoiceField(
        choices=[
            ('json', 'JSON格式'),
            ('excel', 'Excel格式'),
            ('csv', 'CSV格式'),
        ],
        help_text='文件格式'
    )
    
    validate_data = serializers.BooleanField(
        default=True,
        help_text='是否验证数据'
    )
    
    overwrite_existing = serializers.BooleanField(
        default=False,
        help_text='是否覆盖现有数据'
    )


class TeacherPreferenceSerializer(serializers.Serializer):
    """教师偏好序列化器"""
    
    teacher_id = serializers.IntegerField()
    teacher_name = serializers.CharField(read_only=True)
    day_of_week = serializers.IntegerField()
    day_name = serializers.CharField(read_only=True)
    time_slot = serializers.IntegerField()
    time_name = serializers.CharField(read_only=True)
    preference_score = serializers.FloatField()
    is_available = serializers.BooleanField()
    reason = serializers.CharField(required=False, allow_blank=True)


class CourseRequirementSerializer(serializers.Serializer):
    """课程需求序列化器"""
    
    course_id = serializers.IntegerField()
    course_name = serializers.CharField(read_only=True)
    required_sessions = serializers.IntegerField()
    session_duration = serializers.IntegerField(default=1)
    preferred_days = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    preferred_times = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    room_requirements = serializers.JSONField(required=False)


class AlgorithmConfigSerializer(serializers.Serializer):
    """算法配置序列化器"""
    
    algorithm_type = serializers.CharField()
    parameters = serializers.JSONField()
    is_default = serializers.BooleanField(default=False)
    description = serializers.CharField(required=False, allow_blank=True)
    created_by = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
