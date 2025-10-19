from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from datetime import datetime, timedelta
import re
from apps.courses.models import Course
from apps.classrooms.models import Classroom

User = get_user_model()


class TimeSlot(models.Model):
    """时间段模型"""

    name = models.CharField(
        max_length=50,
        verbose_name='时间段名称',
        help_text='如：第1节课、第2节课'
    )
    start_time = models.TimeField(
        verbose_name='开始时间'
    )
    end_time = models.TimeField(
        verbose_name='结束时间'
    )
    order = models.PositiveIntegerField(
        unique=True,
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        verbose_name='排序',
        help_text='用于排序显示，数字越小越靠前'
    )
    duration_minutes = models.PositiveIntegerField(
        verbose_name='时长(分钟)',
        help_text='自动计算，不需要手动填写'
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
        verbose_name = '时间段'
        verbose_name_plural = '时间段'
        db_table = 'schedules_timeslot'
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['start_time']),
            models.Index(fields=['is_active']),
        ]
        ordering = ['order']

    def __str__(self):
        return f"{self.name} ({self.start_time}-{self.end_time})"

    def clean(self):
        """数据验证"""
        if self.start_time >= self.end_time:
            raise ValidationError('开始时间必须早于结束时间')

    def save(self, *args, **kwargs):
        # 自动计算时长
        if self.start_time and self.end_time:
            start_minutes = self.start_time.hour * 60 + self.start_time.minute
            end_minutes = self.end_time.hour * 60 + self.end_time.minute
            self.duration_minutes = end_minutes - start_minutes

        self.clean()
        super().save(*args, **kwargs)


class Schedule(models.Model):
    """课程安排模型"""

    DAY_CHOICES = [
        (1, '周一'),
        (2, '周二'),
        (3, '周三'),
        (4, '周四'),
        (5, '周五'),
        (6, '周六'),
        (7, '周日'),
    ]

    STATUS_CHOICES = [
        ('active', '正常'),
        ('cancelled', '取消'),
        ('rescheduled', '调课'),
        ('suspended', '暂停'),
    ]

    # 基本信息
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name='课程'
    )
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name='教室'
    )
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='teaching_schedules',
        limit_choices_to={'user_type': 'teacher'},
        verbose_name='授课教师'
    )
    time_slot = models.ForeignKey(
        TimeSlot,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name='时间段'
    )

    # 时间信息
    day_of_week = models.PositiveIntegerField(
        choices=DAY_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(7)],
        verbose_name='星期'
    )
    week_range = models.CharField(
        max_length=50,
        verbose_name='周次范围',
        help_text='如：1-16周、1-8,10-16周'
    )
    semester = models.CharField(
        max_length=20,
        verbose_name='学期',
        help_text='如：2024-2025-1'
    )
    academic_year = models.CharField(
        max_length=10,
        verbose_name='学年',
        help_text='如：2024-2025'
    )

    # 状态
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='状态'
    )

    # 备注信息
    notes = models.TextField(
        blank=True,
        verbose_name='备注'
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
        verbose_name = '课程安排'
        verbose_name_plural = '课程安排'
        db_table = 'schedules_schedule'
        indexes = [
            models.Index(fields=['course', 'semester']),
            models.Index(fields=['teacher', 'semester']),
            models.Index(fields=['classroom', 'day_of_week', 'time_slot']),
            models.Index(fields=['day_of_week', 'time_slot']),
            models.Index(fields=['semester', 'academic_year']),
            models.Index(fields=['status']),
        ]
        # 确保同一时间段、同一教室不能有多个课程
        constraints = [
            models.UniqueConstraint(
                fields=['classroom', 'day_of_week', 'time_slot', 'semester'],
                condition=models.Q(status='active'),
                name='unique_classroom_schedule'
            ),
            # 确保同一教师在同一时间段不能有多个课程
            models.UniqueConstraint(
                fields=['teacher', 'day_of_week', 'time_slot', 'semester'],
                condition=models.Q(status='active'),
                name='unique_teacher_schedule'
            ),
        ]
        ordering = ['day_of_week', 'time_slot__order']

    def __str__(self):
        return f"{self.course.name} - {self.get_day_of_week_display()} {self.time_slot.name}"

    @property
    def time_display(self):
        """时间显示"""
        return f"{self.get_day_of_week_display()} {self.time_slot.name}"

    @property
    def location_display(self):
        """地点显示"""
        return str(self.classroom)

    def clean(self):
        """数据验证"""
        # 检查教师是否是该课程的授课教师
        if self.teacher and self.course and not self.course.teachers.filter(id=self.teacher.id).exists():
            raise ValidationError('该教师不是此课程的授课教师')

        # 检查教室容量是否足够
        if self.classroom and self.course:
            if self.classroom.capacity < self.course.max_students:
                raise ValidationError(f'教室容量({self.classroom.capacity})小于课程最大选课人数({self.course.max_students})')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @classmethod
    def parse_week_range(cls, week_range):
        """解析周次范围字符串

        Args:
            week_range (str): 周次范围，如 "1-16周", "1-8,10-16周", "1,3,5-8周"

        Returns:
            list: 周次列表，如 [1, 2, 3, ..., 16]
        """
        if not week_range:
            return []

        # 移除"周"字
        week_range = week_range.replace('周', '').strip()
        weeks = []

        # 按逗号分割
        parts = week_range.split(',')

        for part in parts:
            part = part.strip()
            if '-' in part:
                # 处理范围，如 "1-16"
                start, end = map(int, part.split('-'))
                weeks.extend(range(start, end + 1))
            else:
                # 处理单个周次
                weeks.append(int(part))

        return sorted(list(set(weeks)))  # 去重并排序

    @property
    def week_numbers(self):
        """获取周次列表"""
        return self.parse_week_range(self.week_range)

    def is_active_in_week(self, week_number):
        """检查在指定周次是否有课"""
        return week_number in self.week_numbers

    def get_conflicts(self, exclude_self=True):
        """获取与当前课程安排冲突的其他安排

        Args:
            exclude_self (bool): 是否排除自身

        Returns:
            QuerySet: 冲突的课程安排
        """
        conflicts = Schedule.objects.filter(
            day_of_week=self.day_of_week,
            time_slot=self.time_slot,
            semester=self.semester,
            status='active'
        ).filter(
            Q(classroom=self.classroom) | Q(teacher=self.teacher)
        )

        if exclude_self and self.pk:
            conflicts = conflicts.exclude(pk=self.pk)

        return conflicts

    def has_conflicts(self):
        """检查是否有冲突"""
        return self.get_conflicts().exists()

    @classmethod
    def check_classroom_conflicts(cls, classroom, day_of_week, time_slot, semester, exclude_pk=None):
        """检查教室冲突

        Args:
            classroom: 教室对象
            day_of_week: 星期
            time_slot: 时间段
            semester: 学期
            exclude_pk: 排除的课程安排ID

        Returns:
            QuerySet: 冲突的课程安排
        """
        conflicts = cls.objects.filter(
            classroom=classroom,
            day_of_week=day_of_week,
            time_slot=time_slot,
            semester=semester,
            status='active'
        )

        if exclude_pk:
            conflicts = conflicts.exclude(pk=exclude_pk)

        return conflicts

    @classmethod
    def check_teacher_conflicts(cls, teacher, day_of_week, time_slot, semester, exclude_pk=None):
        """检查教师冲突

        Args:
            teacher: 教师对象
            day_of_week: 星期
            time_slot: 时间段
            semester: 学期
            exclude_pk: 排除的课程安排ID

        Returns:
            QuerySet: 冲突的课程安排
        """
        conflicts = cls.objects.filter(
            teacher=teacher,
            day_of_week=day_of_week,
            time_slot=time_slot,
            semester=semester,
            status='active'
        )

        if exclude_pk:
            conflicts = conflicts.exclude(pk=exclude_pk)

        return conflicts

    @classmethod
    def get_schedule_matrix(cls, semester, week_number=None):
        """获取课程表矩阵数据

        Args:
            semester: 学期
            week_number: 周次（可选）

        Returns:
            dict: 课程表矩阵数据
        """
        schedules = cls.objects.filter(
            semester=semester,
            status='active'
        ).select_related(
            'course', 'teacher', 'classroom', 'time_slot'
        ).order_by('day_of_week', 'time_slot__order')

        # 如果指定了周次，过滤出该周有课的安排
        if week_number:
            active_schedules = []
            for schedule in schedules:
                if schedule.is_active_in_week(week_number):
                    active_schedules.append(schedule)
            schedules = active_schedules

        # 构建矩阵
        matrix = {}
        for schedule in schedules:
            day = schedule.day_of_week
            time_slot_id = schedule.time_slot.id

            if day not in matrix:
                matrix[day] = {}
            if time_slot_id not in matrix[day]:
                matrix[day][time_slot_id] = []

            matrix[day][time_slot_id].append({
                'id': schedule.id,
                'course': {
                    'id': schedule.course.id,
                    'name': schedule.course.name,
                    'code': schedule.course.code,
                },
                'teacher': {
                    'id': schedule.teacher.id,
                    'name': schedule.teacher.get_full_name() or schedule.teacher.username,
                },
                'classroom': {
                    'id': schedule.classroom.id,
                    'name': str(schedule.classroom),
                },
                'time_slot': {
                    'id': schedule.time_slot.id,
                    'name': schedule.time_slot.name,
                    'start_time': schedule.time_slot.start_time.strftime('%H:%M'),
                    'end_time': schedule.time_slot.end_time.strftime('%H:%M'),
                },
                'week_range': schedule.week_range,
                'notes': schedule.notes,
            })

        return matrix
