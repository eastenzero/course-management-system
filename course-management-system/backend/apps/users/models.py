from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    自定义用户模型
    扩展Django默认用户模型，添加校园课程管理系统所需的字段
    """

    USER_TYPE_CHOICES = [
        ('admin', '超级管理员'),
        ('academic_admin', '教务管理员'),
        ('teacher', '教师'),
        ('student', '学生'),
    ]

    # 用户类型
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='student',
        verbose_name='用户类型'
    )

    # 工号（教师和管理员）
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        verbose_name='工号'
    )

    # 学号（学生）
    student_id = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        verbose_name='学号'
    )

    # 院系
    department = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='院系'
    )

    # 手机号
    phone = models.CharField(
        max_length=15,
        blank=True,
        verbose_name='手机号'
    )

    # 头像
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        verbose_name='头像'
    )

    # 创建时间
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    # 更新时间
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
        db_table = 'users_user'

    def __str__(self):
        return f"{self.username} - {self.get_user_type_display()}"

    @property
    def display_id(self):
        """返回显示用的ID（学号或工号）"""
        if self.user_type == 'student':
            return self.student_id
        else:
            return self.employee_id


class UserPreference(models.Model):
    """用户偏好设置模型"""

    THEME_CHOICES = [
        ('light', '浅色主题'),
        ('dark', '深色主题'),
        ('auto', '跟随系统'),
    ]

    LANGUAGE_CHOICES = [
        ('zh-CN', '简体中文'),
        ('en-US', 'English'),
    ]

    DATE_FORMAT_CHOICES = [
        ('YYYY-MM-DD', 'YYYY-MM-DD'),
        ('MM/DD/YYYY', 'MM/DD/YYYY'),
        ('DD/MM/YYYY', 'DD/MM/YYYY'),
    ]

    PROFILE_VISIBILITY_CHOICES = [
        ('public', '公开'),
        ('private', '私有'),
        ('friends', '仅好友'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='user_preference',
        verbose_name='用户'
    )

    # 界面设置
    theme = models.CharField(
        max_length=10,
        choices=THEME_CHOICES,
        default='light',
        verbose_name='主题'
    )
    language = models.CharField(
        max_length=10,
        choices=LANGUAGE_CHOICES,
        default='zh-CN',
        verbose_name='语言'
    )

    # 显示设置
    page_size = models.IntegerField(
        default=10,
        validators=[MinValueValidator(5), MaxValueValidator(100)],
        verbose_name='每页显示数量'
    )
    date_format = models.CharField(
        max_length=20,
        choices=DATE_FORMAT_CHOICES,
        default='YYYY-MM-DD',
        verbose_name='日期格式'
    )

    # 隐私设置
    profile_visibility = models.CharField(
        max_length=10,
        choices=PROFILE_VISIBILITY_CHOICES,
        default='public',
        verbose_name='个人资料可见性'
    )
    show_email = models.BooleanField(
        default=True,
        verbose_name='显示邮箱'
    )
    show_phone = models.BooleanField(
        default=False,
        verbose_name='显示手机号'
    )

    # 安全设置
    auto_logout = models.IntegerField(
        default=30,
        validators=[MinValueValidator(5), MaxValueValidator(480)],
        verbose_name='自动登出时间（分钟）'
    )
    session_timeout = models.BooleanField(
        default=True,
        verbose_name='启用会话超时'
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'user_preferences'
        verbose_name = '用户偏好'
        verbose_name_plural = '用户偏好'

    def __str__(self):
        return f"{self.user.username}的偏好设置"

    def clean(self):
        """数据验证"""
        from django.core.exceptions import ValidationError

        # 超级用户跳过验证
        if self.is_superuser:
            return

        # 学生必须有学号
        if self.user_type == 'student' and not self.student_id:
            raise ValidationError({'student_id': '学生必须填写学号'})

        # 教师和管理员必须有工号
        if self.user_type in ['teacher', 'admin', 'academic_admin'] and not self.employee_id:
            raise ValidationError({'employee_id': '教师和管理员必须填写工号'})

    def save(self, *args, **kwargs):
        # 超级用户默认为admin类型
        if self.is_superuser and not self.user_type:
            self.user_type = 'admin'

        self.clean()
        super().save(*args, **kwargs)
