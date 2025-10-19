from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class TeacherProfile(models.Model):
    """教师扩展信息模型"""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='teacher_profile',
        limit_choices_to={'user_type': 'teacher'},
        verbose_name='用户'
    )
    
    # 职业信息
    title = models.CharField(
        max_length=50,
        choices=[
            ('assistant', '助教'),
            ('lecturer', '讲师'),
            ('associate_professor', '副教授'),
            ('professor', '教授'),
            ('researcher', '研究员'),
        ],
        default='lecturer',
        verbose_name='职称'
    )
    
    research_area = models.TextField(
        blank=True,
        verbose_name='研究方向',
        help_text='请简要描述您的研究领域和方向'
    )
    
    office_location = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='办公室位置',
        help_text='如：理学院A座301室'
    )
    
    office_hours = models.TextField(
        blank=True,
        verbose_name='答疑时间',
        help_text='请填写您的答疑时间安排'
    )
    
    # 教学信息
    teaching_experience = models.PositiveIntegerField(
        default=0,
        verbose_name='教学经验年数'
    )
    
    education_background = models.TextField(
        blank=True,
        verbose_name='教育背景'
    )
    
    # 联系信息
    office_phone = models.CharField(
        max_length=15,
        blank=True,
        verbose_name='办公电话'
    )
    
    personal_website = models.URLField(
        blank=True,
        verbose_name='个人网站'
    )
    
    # 状态信息
    is_active_teacher = models.BooleanField(
        default=True,
        verbose_name='是否在职'
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
        verbose_name = '教师档案'
        verbose_name_plural = '教师档案'
        db_table = 'teachers_profile'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_title_display()}"
    
    @property
    def full_name(self):
        """获取教师全名"""
        return f"{self.user.first_name} {self.user.last_name}".strip()
    
    @property
    def teaching_courses_count(self):
        """获取教授课程数量"""
        return self.user.teaching_courses.filter(is_active=True).count()


class TeacherCourseAssignment(models.Model):
    """教师课程分配模型"""
    
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='course_assignments',
        limit_choices_to={'user_type': 'teacher'},
        verbose_name='教师'
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='teacher_assignments',
        verbose_name='课程'
    )
    
    # 分配信息
    role = models.CharField(
        max_length=20,
        choices=[
            ('primary', '主讲教师'),
            ('assistant', '助教'),
            ('co_teacher', '合作教师'),
        ],
        default='primary',
        verbose_name='角色'
    )
    
    workload_hours = models.PositiveIntegerField(
        default=0,
        verbose_name='工作量(学时)'
    )
    
    # 时间信息
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='分配时间'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='是否有效'
    )
    
    class Meta:
        verbose_name = '教师课程分配'
        verbose_name_plural = '教师课程分配'
        db_table = 'teachers_course_assignment'
        unique_together = ['teacher', 'course', 'role']
    
    def __str__(self):
        return f"{self.teacher.username} - {self.course.name} ({self.get_role_display()})"


class TeacherNotice(models.Model):
    """教师通知模型"""
    
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='teacher_notices',
        limit_choices_to={'user_type': 'teacher'},
        verbose_name='发布教师'
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='teacher_notices',
        verbose_name='相关课程'
    )
    
    # 通知内容
    title = models.CharField(
        max_length=200,
        verbose_name='通知标题'
    )
    content = models.TextField(
        verbose_name='通知内容'
    )
    
    # 通知类型
    notice_type = models.CharField(
        max_length=20,
        choices=[
            ('announcement', '课程公告'),
            ('assignment', '作业通知'),
            ('exam', '考试通知'),
            ('schedule_change', '课程调整'),
            ('other', '其他'),
        ],
        default='announcement',
        verbose_name='通知类型'
    )
    
    # 优先级
    priority = models.CharField(
        max_length=10,
        choices=[
            ('low', '低'),
            ('normal', '普通'),
            ('high', '高'),
            ('urgent', '紧急'),
        ],
        default='normal',
        verbose_name='优先级'
    )
    
    # 状态
    is_published = models.BooleanField(
        default=False,
        verbose_name='是否发布'
    )
    
    # 时间信息
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='发布时间'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )
    
    class Meta:
        verbose_name = '教师通知'
        verbose_name_plural = '教师通知'
        db_table = 'teachers_notice'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.course.name} - {self.title}"
