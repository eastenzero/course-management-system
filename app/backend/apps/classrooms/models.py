from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class Building(models.Model):
    """教学楼模型"""

    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='教学楼名称'
    )
    code = models.CharField(
        max_length=10,
        unique=True,
        verbose_name='教学楼代码'
    )
    address = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='地址'
    )
    description = models.TextField(
        blank=True,
        verbose_name='描述'
    )

    # 状态
    is_active = models.BooleanField(
        default=True,
        verbose_name='是否启用'
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
        verbose_name = '教学楼'
        verbose_name_plural = '教学楼'
        db_table = 'classrooms_building'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class Classroom(models.Model):
    """教室模型"""

    ROOM_TYPE_CHOICES = [
        ('lecture', '普通教室'),
        ('lab', '实验室'),
        ('computer', '机房'),
        ('multimedia', '多媒体教室'),
        ('seminar', '研讨室'),
        ('auditorium', '阶梯教室'),
        ('studio', '工作室'),
        ('library', '图书馆'),
        ('gym', '体育馆'),
        ('other', '其他'),
    ]

    # 基本信息
    building = models.ForeignKey(
        Building,
        on_delete=models.CASCADE,
        related_name='classrooms',
        verbose_name='教学楼'
    )
    room_number = models.CharField(
        max_length=20,
        verbose_name='教室号'
    )
    name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='教室名称'
    )

    # 教室属性
    capacity = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(1000)],
        verbose_name='容量'
    )
    room_type = models.CharField(
        max_length=20,
        choices=ROOM_TYPE_CHOICES,
        default='lecture',
        verbose_name='教室类型'
    )
    floor = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(50)],
        verbose_name='楼层'
    )
    area = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name='面积(平方米)'
    )

    # 设备信息（JSON格式存储）
    equipment = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='设备信息',
        help_text='存储教室设备信息，如投影仪、音响、空调等'
    )

    # 位置描述
    location_description = models.TextField(
        blank=True,
        verbose_name='位置描述'
    )

    # 状态
    is_available = models.BooleanField(
        default=True,
        verbose_name='是否可用'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='是否启用'
    )

    # 维护信息
    maintenance_notes = models.TextField(
        blank=True,
        verbose_name='维护备注'
    )
    last_maintenance = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='最后维护时间'
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
        verbose_name = '教室'
        verbose_name_plural = '教室'
        db_table = 'classrooms_classroom'
        unique_together = ['building', 'room_number']
        indexes = [
            models.Index(fields=['building', 'room_number']),
            models.Index(fields=['room_type']),
            models.Index(fields=['capacity']),
            models.Index(fields=['is_available', 'is_active']),
            models.Index(fields=['floor']),
        ]
        ordering = ['building__code', 'room_number']

    def __str__(self):
        return f"{self.building.code}-{self.room_number}"

    @property
    def full_name(self):
        """完整名称"""
        if self.name:
            return f"{self.building.name}{self.room_number}({self.name})"
        return f"{self.building.name}{self.room_number}"

    @property
    def equipment_list(self):
        """设备列表"""
        if not self.equipment:
            return []
        return [f"{k}: {v}" for k, v in self.equipment.items()]

    def is_suitable_for_course(self, course, student_count=None):
        """判断教室是否适合某门课程"""
        if not self.is_available or not self.is_active:
            return False

        # 检查容量
        required_capacity = student_count or course.max_students
        if self.capacity < required_capacity:
            return False

        # 根据课程类型检查教室类型
        course_room_requirements = {
            'computer': ['computer', 'lab'],
            'lab': ['lab', 'computer'],
            'lecture': ['lecture', 'multimedia', 'auditorium'],
        }

        # 这里可以根据课程名称或其他属性判断课程类型
        # 暂时返回True，实际应用中可以添加更复杂的逻辑
        return True
