from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from apps.courses.models import Course
from apps.classrooms.models import Classroom

User = get_user_model()


class CourseStatistics(models.Model):
    """课程统计模型"""

    course = models.OneToOneField(
        Course,
        on_delete=models.CASCADE,
        related_name='statistics',
        verbose_name='课程'
    )
    semester = models.CharField(
        max_length=20,
        verbose_name='学期'
    )

    # 选课统计
    total_enrolled = models.PositiveIntegerField(
        default=0,
        verbose_name='总选课人数'
    )
    total_dropped = models.PositiveIntegerField(
        default=0,
        verbose_name='总退课人数'
    )
    current_enrolled = models.PositiveIntegerField(
        default=0,
        verbose_name='当前选课人数'
    )

    # 成绩统计
    average_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='平均分'
    )
    pass_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='及格率(%)'
    )
    excellent_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='优秀率(%)'
    )

    # 教室利用率
    classroom_utilization = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='教室利用率(%)'
    )

    # 时间戳
    last_updated = models.DateTimeField(
        auto_now=True,
        verbose_name='最后更新时间'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    class Meta:
        verbose_name = '课程统计'
        verbose_name_plural = '课程统计'
        db_table = 'analytics_course_statistics'
        unique_together = ['course', 'semester']
        indexes = [
            models.Index(fields=['semester']),
            models.Index(fields=['last_updated']),
        ]

    def __str__(self):
        return f"{self.course.name} - {self.semester}"


class ClassroomUtilization(models.Model):
    """教室利用率模型"""

    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name='utilization_records',
        verbose_name='教室'
    )
    semester = models.CharField(
        max_length=20,
        verbose_name='学期'
    )
    week_number = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(52)],
        verbose_name='周次'
    )

    # 利用率统计
    total_time_slots = models.PositiveIntegerField(
        default=0,
        verbose_name='总时间段数'
    )
    occupied_time_slots = models.PositiveIntegerField(
        default=0,
        verbose_name='已占用时间段数'
    )
    utilization_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='利用率(%)'
    )

    # 时间戳
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )

    class Meta:
        verbose_name = '教室利用率'
        verbose_name_plural = '教室利用率'
        db_table = 'analytics_classroom_utilization'
        unique_together = ['classroom', 'semester', 'week_number']
        indexes = [
            models.Index(fields=['semester', 'week_number']),
            models.Index(fields=['utilization_rate']),
        ]

    def __str__(self):
        return f"{self.classroom} - 第{self.week_number}周 ({self.utilization_rate}%)"


class TeacherWorkload(models.Model):
    """教师工作量模型"""

    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='workload_records',
        limit_choices_to={'user_type': 'teacher'},
        verbose_name='教师'
    )
    semester = models.CharField(
        max_length=20,
        verbose_name='学期'
    )

    # 工作量统计
    total_courses = models.PositiveIntegerField(
        default=0,
        verbose_name='授课门数'
    )
    total_hours = models.PositiveIntegerField(
        default=0,
        verbose_name='总学时'
    )
    total_students = models.PositiveIntegerField(
        default=0,
        verbose_name='总学生数'
    )

    # 课程类型分布
    required_courses = models.PositiveIntegerField(
        default=0,
        verbose_name='必修课门数'
    )
    elective_courses = models.PositiveIntegerField(
        default=0,
        verbose_name='选修课门数'
    )

    # 时间戳
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )

    class Meta:
        verbose_name = '教师工作量'
        verbose_name_plural = '教师工作量'
        db_table = 'analytics_teacher_workload'
        unique_together = ['teacher', 'semester']
        indexes = [
            models.Index(fields=['semester']),
            models.Index(fields=['total_hours']),
        ]

    def __str__(self):
        return f"{self.teacher.username} - {self.semester}"


class SystemReport(models.Model):
    """系统报表模型"""

    REPORT_TYPE_CHOICES = [
        ('enrollment', '选课统计报表'),
        ('classroom', '教室利用率报表'),
        ('teacher', '教师工作量报表'),
        ('course', '课程统计报表'),
        ('schedule', '排课统计报表'),
    ]

    name = models.CharField(
        max_length=100,
        verbose_name='报表名称'
    )
    report_type = models.CharField(
        max_length=20,
        choices=REPORT_TYPE_CHOICES,
        verbose_name='报表类型'
    )
    semester = models.CharField(
        max_length=20,
        verbose_name='学期'
    )

    # 报表数据（JSON格式存储）
    data = models.JSONField(
        default=dict,
        verbose_name='报表数据'
    )

    # 生成信息
    generated_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='generated_reports',
        verbose_name='生成人'
    )
    generated_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='生成时间'
    )

    # 状态
    is_public = models.BooleanField(
        default=False,
        verbose_name='是否公开'
    )

    class Meta:
        verbose_name = '系统报表'
        verbose_name_plural = '系统报表'
        db_table = 'analytics_system_report'
        indexes = [
            models.Index(fields=['report_type', 'semester']),
            models.Index(fields=['generated_at']),
        ]
        ordering = ['-generated_at']

    def __str__(self):
        return f"{self.name} - {self.semester}"
