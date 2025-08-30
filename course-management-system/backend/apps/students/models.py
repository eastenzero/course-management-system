from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class StudentProfile(models.Model):
    """学生扩展信息模型"""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile',
        limit_choices_to={'user_type': 'student'},
        verbose_name='用户'
    )
    
    # 学籍信息
    admission_year = models.IntegerField(
        default=2024,
        verbose_name='入学年份',
        help_text='如：2024'
    )
    major = models.CharField(
        max_length=100,
        default='未分配专业',
        verbose_name='专业'
    )
    class_name = models.CharField(
        max_length=50,
        default='未分配班级',
        verbose_name='班级',
        help_text='如：计算机科学与技术1班'
    )
    
    # 学业信息
    gpa = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(4.0)],
        verbose_name='GPA'
    )
    total_credits = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='总学分'
    )
    completed_credits = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='已完成学分'
    )
    
    # 状态信息
    enrollment_status = models.CharField(
        max_length=20,
        choices=[
            ('enrolled', '在读'),
            ('suspended', '休学'),
            ('graduated', '毕业'),
            ('dropped', '退学'),
        ],
        default='enrolled',
        verbose_name='学籍状态'
    )
    
    # 联系信息
    emergency_contact = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='紧急联系人'
    )
    emergency_phone = models.CharField(
        max_length=15,
        blank=True,
        verbose_name='紧急联系电话'
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
        verbose_name = '学生档案'
        verbose_name_plural = '学生档案'
        db_table = 'students_profile'
    
    def __str__(self):
        return f"{self.user.username} - {self.major}"
    
    @property
    def remaining_credits(self):
        """剩余学分"""
        return max(0, self.total_credits - self.completed_credits)
    
    @property
    def completion_rate(self):
        """完成率"""
        if self.total_credits == 0:
            return 0
        return round((self.completed_credits / self.total_credits) * 100, 2)


class StudentCourseProgress(models.Model):
    """学生课程进度模型"""
    
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='course_progress',
        limit_choices_to={'user_type': 'student'},
        verbose_name='学生'
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='student_progress',
        verbose_name='课程'
    )
    
    # 进度信息
    attendance_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='出勤率'
    )
    assignment_completion = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='作业完成率'
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
        verbose_name = '学生课程进度'
        verbose_name_plural = '学生课程进度'
        db_table = 'students_course_progress'
        unique_together = ['student', 'course']
    
    def __str__(self):
        return f"{self.student.username} - {self.course.name}"
