from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Course(models.Model):
    """课程模型"""

    COURSE_TYPE_CHOICES = [
        ('required', '必修课'),
        ('elective', '选修课'),
        ('public', '公共课'),
        ('professional', '专业课'),
    ]

    # 基本信息
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='课程代码',
        help_text='课程的唯一标识代码'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='课程名称'
    )
    english_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='英文名称'
    )

    # 课程属性
    credits = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='学分'
    )
    hours = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(200)],
        verbose_name='学时'
    )
    course_type = models.CharField(
        max_length=20,
        choices=COURSE_TYPE_CHOICES,
        default='elective',
        verbose_name='课程类型'
    )

    # 开课信息
    department = models.CharField(
        max_length=100,
        verbose_name='开课院系'
    )
    semester = models.CharField(
        max_length=20,
        verbose_name='开课学期',
        help_text='如：2024-2025-1'
    )
    academic_year = models.CharField(
        max_length=10,
        verbose_name='学年',
        help_text='如：2024-2025'
    )

    # 课程描述
    description = models.TextField(
        blank=True,
        verbose_name='课程描述'
    )
    objectives = models.TextField(
        blank=True,
        verbose_name='课程目标'
    )

    # 先修课程
    prerequisites = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        verbose_name='先修课程'
    )

    # 授课教师
    teachers = models.ManyToManyField(
        User,
        related_name='teaching_courses',
        limit_choices_to={'user_type': 'teacher'},
        verbose_name='授课教师'
    )

    # 选课限制
    max_students = models.PositiveIntegerField(
        default=50,
        validators=[MinValueValidator(1), MaxValueValidator(500)],
        verbose_name='最大选课人数'
    )
    min_students = models.PositiveIntegerField(
        default=10,
        validators=[MinValueValidator(1)],
        verbose_name='最少开课人数'
    )

    # 状态
    is_active = models.BooleanField(
        default=True,
        verbose_name='是否启用'
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name='是否发布'
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
        verbose_name = '课程'
        verbose_name_plural = '课程'
        db_table = 'courses_course'
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['department']),
            models.Index(fields=['semester']),
            models.Index(fields=['course_type']),
            models.Index(fields=['is_active', 'is_published']),
        ]
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def current_enrollment(self):
        """当前选课人数"""
        return self.enrollments.filter(is_active=True).count()

    @property
    def is_full(self):
        """是否已满员"""
        return self.current_enrollment >= self.max_students

    @property
    def can_open(self):
        """是否可以开课"""
        return self.current_enrollment >= self.min_students

    def clean(self):
        """数据验证"""
        from django.core.exceptions import ValidationError

        if self.min_students > self.max_students:
            raise ValidationError('最少开课人数不能大于最大选课人数')


class Enrollment(models.Model):
    """选课记录模型"""

    STATUS_CHOICES = [
        ('enrolled', '已选课'),
        ('dropped', '已退课'),
        ('completed', '已完成'),
        ('failed', '未通过'),
    ]

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='enrollments',
        limit_choices_to={'user_type': 'student'},
        verbose_name='学生'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name='课程'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='enrolled',
        verbose_name='状态'
    )

    # 成绩
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='成绩'
    )
    grade = models.CharField(
        max_length=5,
        blank=True,
        verbose_name='等级',
        help_text='如：A+, A, B+, B, C+, C, D, F'
    )

    # 时间戳
    enrolled_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='选课时间'
    )
    dropped_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='退课时间'
    )

    # 状态
    is_active = models.BooleanField(
        default=True,
        verbose_name='是否有效'
    )

    class Meta:
        verbose_name = '选课记录'
        verbose_name_plural = '选课记录'
        db_table = 'courses_enrollment'
        unique_together = ['student', 'course']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['course', 'status']),
            models.Index(fields=['enrolled_at']),
        ]
        ordering = ['-enrolled_at']

    def __str__(self):
        return f"{self.student.username} - {self.course.name}"

    def calculate_final_score(self):
        """计算总成绩"""
        # 获取课程的成绩组成配置
        components = self.course.grade_components.all()

        if not components.exists():
            # 如果没有配置成绩组成，使用传统方式计算
            return self._calculate_traditional_score()

        total_score = 0
        total_weight = 0

        for component in components:
            # 获取该组成的成绩
            component_grades = self.detailed_grades.filter(component=component)

            if component_grades.exists():
                # 计算该组成的平均分
                avg_score = sum(grade.percentage_score for grade in component_grades) / component_grades.count()
                weighted_score = avg_score * component.weight / 100
                total_score += weighted_score
                total_weight += component.weight
            elif component.is_required:
                # 必需项目没有成绩，返回0
                return 0

        # 如果权重不足100%，按比例调整
        if total_weight > 0 and total_weight < 100:
            total_score = total_score * 100 / total_weight

        return round(total_score, 2)

    def _calculate_traditional_score(self):
        """传统方式计算成绩（基于权重字段）"""
        grades = self.detailed_grades.all()

        if not grades.exists():
            return 0

        total_weighted_score = 0
        total_weight = 0

        for grade in grades:
            weight = grade.weight if grade.weight > 0 else 1
            total_weighted_score += grade.percentage_score * weight
            total_weight += weight

        if total_weight > 0:
            return round(total_weighted_score / total_weight, 2)

        return 0

    def get_grade_breakdown(self):
        """获取成绩明细"""
        breakdown = {}
        components = self.course.grade_components.all()

        if components.exists():
            for component in components:
                component_grades = self.detailed_grades.filter(component=component)
                if component_grades.exists():
                    avg_score = sum(grade.percentage_score for grade in component_grades) / component_grades.count()
                    breakdown[component.name] = {
                        'score': round(avg_score, 2),
                        'weight': component.weight,
                        'weighted_score': round(avg_score * component.weight / 100, 2),
                        'grades': [
                            {
                                'name': grade.name,
                                'score': grade.score,
                                'max_score': grade.max_score,
                                'percentage': grade.percentage_score
                            }
                            for grade in component_grades
                        ]
                    }
                else:
                    breakdown[component.name] = {
                        'score': 0,
                        'weight': component.weight,
                        'weighted_score': 0,
                        'grades': []
                    }
        else:
            # 传统方式的明细
            for grade in self.detailed_grades.all():
                grade_type = grade.get_grade_type_display()
                if grade_type not in breakdown:
                    breakdown[grade_type] = {
                        'score': 0,
                        'weight': 0,
                        'weighted_score': 0,
                        'grades': []
                    }

                breakdown[grade_type]['grades'].append({
                    'name': grade.name,
                    'score': grade.score,
                    'max_score': grade.max_score,
                    'percentage': grade.percentage_score,
                    'weight': grade.weight
                })

        return breakdown

    def update_final_score(self):
        """更新总成绩"""
        final_score = self.calculate_final_score()
        self.score = final_score

        # 计算等级
        if final_score >= 90:
            self.grade = 'A'
        elif final_score >= 80:
            self.grade = 'B'
        elif final_score >= 70:
            self.grade = 'C'
        elif final_score >= 60:
            self.grade = 'D'
        else:
            self.grade = 'F'

        self.save(update_fields=['score', 'grade'])


class GradeComponent(models.Model):
    """成绩组成配置模型"""

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='grade_components',
        verbose_name='课程'
    )

    name = models.CharField(
        max_length=100,
        verbose_name='成绩项目名称',
        help_text='如：平时成绩、期中考试、期末考试等'
    )

    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='权重(%)',
        help_text='在总成绩中的权重百分比'
    )

    max_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=100,
        validators=[MinValueValidator(0)],
        verbose_name='满分'
    )

    is_required = models.BooleanField(
        default=True,
        verbose_name='是否必需',
        help_text='是否为必需的成绩项目'
    )

    description = models.TextField(
        blank=True,
        verbose_name='描述'
    )

    # 排序
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='排序',
        help_text='显示顺序，数字越小越靠前'
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
        verbose_name = '成绩组成'
        verbose_name_plural = '成绩组成'
        db_table = 'courses_grade_component'
        unique_together = ['course', 'name']
        ordering = ['order', 'id']
        indexes = [
            models.Index(fields=['course', 'order']),
        ]

    def __str__(self):
        return f"{self.course.name} - {self.name} ({self.weight}%)"

    def clean(self):
        """验证数据"""
        super().clean()

        # 检查同一课程的权重总和不能超过100%
        if self.course_id:
            total_weight = GradeComponent.objects.filter(
                course=self.course
            ).exclude(pk=self.pk).aggregate(
                total=models.Sum('weight')
            )['total'] or 0

            if total_weight + self.weight > 100:
                raise ValidationError(
                    f'权重总和不能超过100%，当前总和为{total_weight + self.weight}%'
                )


class Grade(models.Model):
    """成绩详细记录模型"""

    GRADE_TYPE_CHOICES = [
        ('assignment', '作业'),
        ('quiz', '小测验'),
        ('midterm', '期中考试'),
        ('final', '期末考试'),
        ('project', '项目'),
        ('participation', '课堂参与'),
        ('lab', '实验'),
        ('other', '其他'),
    ]

    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='detailed_grades',
        verbose_name='选课记录'
    )

    # 成绩组成关联
    component = models.ForeignKey(
        GradeComponent,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='grades',
        verbose_name='成绩组成',
        help_text='关联的成绩组成配置'
    )

    # 成绩类型和基本信息
    grade_type = models.CharField(
        max_length=20,
        choices=GRADE_TYPE_CHOICES,
        verbose_name='成绩类型'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='成绩项目名称',
        help_text='如：第一次作业、期中考试等'
    )
    description = models.TextField(
        blank=True,
        verbose_name='描述'
    )

    # 成绩和权重
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='得分'
    )
    max_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=100,
        validators=[MinValueValidator(0)],
        verbose_name='满分'
    )
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='权重(%)',
        help_text='在总成绩中的权重百分比'
    )

    # 评分信息
    graded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'user_type': 'teacher'},
        verbose_name='评分教师'
    )
    graded_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='评分时间'
    )

    # 反馈
    feedback = models.TextField(
        blank=True,
        verbose_name='评语'
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
        verbose_name = '详细成绩'
        verbose_name_plural = '详细成绩'
        db_table = 'courses_grade'
        indexes = [
            models.Index(fields=['enrollment', 'grade_type']),
            models.Index(fields=['graded_at']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.enrollment.student.username} - {self.enrollment.course.name} - {self.name}"

    @property
    def percentage_score(self):
        """百分比得分"""
        if self.max_score > 0:
            return round((self.score / self.max_score) * 100, 2)
        return 0

    @property
    def weighted_score(self):
        """加权得分"""
        if self.component and self.component.weight > 0:
            return round((self.percentage_score * self.component.weight / 100), 2)
        elif self.weight > 0:
            return round((self.percentage_score * self.weight / 100), 2)
        return 0

    @property
    def letter_grade(self):
        """等级成绩"""
        score = self.percentage_score
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'

    def clean(self):
        """验证数据"""
        super().clean()

        # 如果关联了成绩组成，验证课程一致性
        if self.component and self.enrollment:
            if self.component.course != self.enrollment.course:
                raise ValidationError('成绩组成与选课记录的课程不一致')

        # 验证分数不能超过满分
        if self.score > self.max_score:
            raise ValidationError('得分不能超过满分')

    @property
    def letter_grade(self):
        """字母等级"""
        percentage = self.percentage_score
        if percentage >= 90:
            return 'A'
        elif percentage >= 80:
            return 'B'
        elif percentage >= 70:
            return 'C'
        elif percentage >= 60:
            return 'D'
        else:
            return 'F'


class CourseEvaluation(models.Model):
    """课程评价模型"""

    enrollment = models.OneToOneField(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='evaluation',
        verbose_name='选课记录'
    )

    # 评价维度
    teaching_quality = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='教学质量',
        help_text='1-5分'
    )
    course_content = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='课程内容',
        help_text='1-5分'
    )
    difficulty_level = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='难度水平',
        help_text='1-5分'
    )
    workload = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='课业负担',
        help_text='1-5分'
    )
    overall_satisfaction = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='总体满意度',
        help_text='1-5分'
    )

    # 文字评价
    comments = models.TextField(
        blank=True,
        verbose_name='评价意见'
    )
    suggestions = models.TextField(
        blank=True,
        verbose_name='改进建议'
    )

    # 推荐度
    would_recommend = models.BooleanField(
        default=True,
        verbose_name='是否推荐'
    )

    # 时间戳
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='评价时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )

    class Meta:
        verbose_name = '课程评价'
        verbose_name_plural = '课程评价'
        db_table = 'courses_evaluation'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.enrollment.student.username} - {self.enrollment.course.name} 评价"

    @property
    def average_rating(self):
        """平均评分"""
        ratings = [
            self.teaching_quality,
            self.course_content,
            self.difficulty_level,
            self.workload,
            self.overall_satisfaction
        ]
        return round(sum(ratings) / len(ratings), 2)
