from django.db.models import Avg, Sum, Count, Q
from django.utils import timezone
from datetime import date, datetime, timedelta
from apps.courses.models import Course, Enrollment
from apps.schedules.models import Schedule, TimeSlot
from .models import StudentProfile, StudentCourseProgress
from .serializers import StudentProfileSerializer, StudentEnrollmentSerializer

# 临时禁用 notifications 导入，直到 app 配置正确
try:
    from apps.notifications.models import Notification, NotificationType
    NOTIFICATIONS_AVAILABLE = True
except (ImportError, RuntimeError):
    NOTIFICATIONS_AVAILABLE = False


class StudentService:
    """学生业务逻辑服务类"""
    
    def __init__(self, user):
        self.user = user
        try:
            self.profile = StudentProfile.objects.get(user=user)
        except StudentProfile.DoesNotExist:
            # 如果不存在，创建一个新的profile
            self.profile = StudentProfile.objects.create(
                user=user,
                admission_year=2024,  # 默认入学年份
                major='未分配专业',     # 默认专业
                class_name='未分配班级',  # 默认班级
                enrollment_status='enrolled',  # 默认在读状态
                emergency_contact='待填写',  # 默认紧急联系人
                emergency_phone='待填写',  # 默认紧急联系电话
            )
    
    def get_dashboard_data(self):
        """获取学生仪表板数据"""
        
        # 基本信息
        student_info = StudentProfileSerializer(self.profile).data
        
        # 选课统计
        enrollments = Enrollment.objects.filter(student=self.user, is_active=True)
        total_courses = enrollments.count()
        
        # 当前学期课程
        current_semester = self._get_current_semester()
        current_semester_courses = enrollments.filter(
            course__semester=current_semester
        ).count()
        
        # 已完成课程
        completed_courses = enrollments.filter(
            status='completed'
        ).count()
        
        # 成绩统计
        graded_enrollments = enrollments.filter(score__isnull=False)
        average_score = graded_enrollments.aggregate(
            avg_score=Avg('score')
        )['avg_score'] or 0
        
        # 最近成绩
        latest_grades = self._get_latest_grades()
        
        # 今日课程
        today_schedule = self._get_today_schedule()
        
        # 通知和截止日期
        notifications = self._get_notifications()
        upcoming_deadlines = self._get_upcoming_deadlines()
        
        return {
            'student_info': student_info,
            'total_courses': total_courses,
            'current_semester_courses': current_semester_courses,
            'completed_courses': completed_courses,
            'average_score': round(average_score, 2),
            'latest_grades': latest_grades,
            'today_schedule': today_schedule,
            'notifications': notifications,
            'upcoming_deadlines': upcoming_deadlines,
        }
    
    def enroll_course(self, course_id):
        """选课"""
        
        try:
            course = Course.objects.get(id=course_id, is_active=True, is_published=True)
        except Course.DoesNotExist:
            return {'success': False, 'error': '课程不存在或未发布'}
        
        # 检查是否已选课
        if Enrollment.objects.filter(
            student=self.user,
            course=course,
            status='enrolled'
        ).exists():
            return {'success': False, 'error': '您已经选择了这门课程'}
        
        # 检查是否已满员
        if course.is_full:
            return {'success': False, 'error': '课程已满员'}
        
        # 检查时间冲突
        conflicts = self.check_schedule_conflicts([course_id])
        if conflicts:
            return {
                'success': False,
                'error': f'时间冲突: {conflicts[0]["message"]}'
            }
        
        # 创建选课记录
        enrollment = Enrollment.objects.create(
            student=self.user,
            course=course,
            status='enrolled'
        )
        
        # 更新学生档案
        self._update_student_credits()
        
        return {
            'success': True,
            'enrollment': StudentEnrollmentSerializer(enrollment).data
        }
    
    def drop_course(self, course_id):
        """退课"""
        
        try:
            enrollment = Enrollment.objects.get(
                student=self.user,
                course_id=course_id,
                status='enrolled'
            )
        except Enrollment.DoesNotExist:
            return {'success': False, 'error': '未找到选课记录'}
        
        # 检查是否可以退课（例如：开课后一周内可以退课）
        if not self._can_drop_course(enrollment):
            return {'success': False, 'error': '已超过退课时间'}
        
        # 更新选课状态
        enrollment.status = 'dropped'
        enrollment.dropped_at = timezone.now()
        enrollment.save()
        
        # 更新学生档案
        self._update_student_credits()
        
        return {'success': True}
    
    def check_schedule_conflicts(self, course_ids):
        """检查课程时间冲突"""
        
        conflicts = []
        
        # 获取学生已选课程的时间安排
        enrolled_courses = Enrollment.objects.filter(
            student=self.user,
            status='enrolled'
        ).values_list('course_id', flat=True)
        
        # 这里应该检查具体的时间冲突
        # 由于当前没有详细的时间表模型，暂时返回空列表
        # 在实际实现中，需要根据课程表模型来检查时间冲突
        
        return conflicts
    
    def get_course_schedule(self, semester=None, week=None):
        """获取课程表 - 修复版本，正确关联Schedule模型"""
        
        # 获取学生选课的课程ID列表
        enrolled_courses = Enrollment.objects.filter(
            student=self.user,
            status='enrolled',
            is_active=True
        ).values_list('course_id', flat=True)
        
        # 基础查询：获取学生选课课程的实际排课数据
        schedules = Schedule.objects.filter(
            course_id__in=enrolled_courses,
            status='active'
        ).select_related(
            'course', 'teacher', 'classroom', 'time_slot'
        )
        
        # 按学期过滤
        if semester:
            schedules = schedules.filter(semester=semester)
        
        # 按周次过滤
        if week:
            try:
                week_num = int(week)
                schedules = [s for s in schedules if s.is_active_in_week(week_num)]
            except (ValueError, TypeError):
                pass  # 忽略无效的周次参数
        
        schedule_data = []
        
        # 构建标准化的课程表数据
        for schedule in schedules:
            # 获取教师姓名
            teacher_name = schedule.teacher.get_full_name() if hasattr(schedule.teacher, 'get_full_name') else schedule.teacher.username
            if not teacher_name.strip():
                teacher_name = f"{schedule.teacher.first_name} {schedule.teacher.last_name}".strip() or schedule.teacher.username
            
            schedule_data.append({
                'course_id': schedule.course.id,
                'course_name': schedule.course.name,
                'course_code': schedule.course.code,
                'teacher_name': teacher_name,
                'classroom': str(schedule.classroom),
                'classroom_id': schedule.classroom.id,
                'time_slot': schedule.time_slot.name,
                'time_slot_id': schedule.time_slot.id,
                'day_of_week': schedule.day_of_week,
                'day_of_week_display': schedule.get_day_of_week_display(),
                'start_time': schedule.time_slot.start_time.strftime('%H:%M'),
                'end_time': schedule.time_slot.end_time.strftime('%H:%M'),
                'week_range': schedule.week_range,
                'semester': schedule.semester,
                'academic_year': schedule.academic_year,
                'status': schedule.status,
                'notes': schedule.notes,
                'schedule_id': schedule.id,
                # 为前端课程表网格提供便利
                'grid_key': f"{schedule.day_of_week}_{schedule.time_slot.id}"
            })
        
        return schedule_data
    
    def get_gpa_statistics(self):
        """获取GPA统计"""
        
        enrollments = Enrollment.objects.filter(
            student=self.user,
            score__isnull=False
        ).select_related('course')
        
        if not enrollments.exists():
            return {
                'overall_gpa': 0.0,
                'semester_gpa': {},
                'credit_summary': {
                    'total_credits': 0,
                    'completed_credits': 0,
                    'gpa_credits': 0
                },
                'grade_distribution': {}
            }
        
        # 计算总GPA
        total_points = 0
        total_credits = 0
        
        semester_data = {}
        grade_distribution = {}
        
        for enrollment in enrollments:
            course = enrollment.course
            score = float(enrollment.score)
            credits = course.credits
            
            # 计算绩点
            gpa_point = self._score_to_gpa(score)
            total_points += gpa_point * credits
            total_credits += credits
            
            # 按学期统计
            semester = course.semester
            if semester not in semester_data:
                semester_data[semester] = {
                    'total_points': 0,
                    'total_credits': 0,
                    'courses': []
                }
            
            semester_data[semester]['total_points'] += gpa_point * credits
            semester_data[semester]['total_credits'] += credits
            semester_data[semester]['courses'].append({
                'course_name': course.name,
                'credits': credits,
                'score': score,
                'gpa_point': gpa_point
            })
            
            # 成绩分布
            grade_level = self._score_to_grade_level(score)
            grade_distribution[grade_level] = grade_distribution.get(grade_level, 0) + 1
        
        # 计算各学期GPA
        semester_gpa = {}
        for semester, data in semester_data.items():
            if data['total_credits'] > 0:
                semester_gpa[semester] = round(
                    data['total_points'] / data['total_credits'], 2
                )
        
        overall_gpa = round(total_points / total_credits, 2) if total_credits > 0 else 0.0
        
        return {
            'overall_gpa': overall_gpa,
            'semester_gpa': semester_gpa,
            'credit_summary': {
                'total_credits': self.profile.total_credits,
                'completed_credits': self.profile.completed_credits,
                'gpa_credits': total_credits
            },
            'grade_distribution': grade_distribution
        }
    
    def _get_current_semester(self):
        """获取当前学期"""
        # 简单的学期判断逻辑，实际应该根据学校的学期设置
        now = timezone.now()
        year = now.year
        month = now.month
        
        if month >= 9 or month <= 1:
            return f"{year}-{year+1}-1"  # 秋季学期
        else:
            return f"{year-1}-{year}-2"  # 春季学期
    
    def _get_latest_grades(self):
        """获取最近成绩"""
        latest_enrollments = Enrollment.objects.filter(
            student=self.user,
            score__isnull=False
        ).select_related('course').order_by('-enrolled_at')[:5]
        
        return [
            {
                'course_name': e.course.name,
                'score': float(e.score),
                'grade': e.grade,
                'credits': e.course.credits
            }
            for e in latest_enrollments
        ]
    
    def _get_today_schedule(self):
        """获取今日课程安排（对接真实排课数据）"""
        today = timezone.localdate()
        weekday = today.isoweekday()  # 1-7
        current_semester = self._get_current_semester()

        # 获取学生选课的课程ID列表
        enrolled_courses = Enrollment.objects.filter(
            student=self.user,
            status='enrolled',
            is_active=True
        ).values_list('course_id', flat=True)
        
        if not enrolled_courses:
            return []

        # 查询今日对应的排课
        schedules = Schedule.objects.filter(
            course_id__in=enrolled_courses,
            semester=current_semester,
            status='active',
            day_of_week=weekday,
        ).select_related(
            'course', 'teacher', 'classroom', 'time_slot'
        ).order_by('time_slot__order')

        # 计算当前周次（简化逻辑）
        now = timezone.now()
        # 假设学期从9月1日开始
        semester_start_year = now.year if now.month >= 9 else now.year - 1
        semester_start = datetime(semester_start_year, 9, 1, tzinfo=now.tzinfo)
        delta_days = (now - semester_start).days
        current_week = max(1, min(20, delta_days // 7 + 1))
        
        # 按周次过滤
        schedules = [s for s in schedules if s.is_active_in_week(current_week)]

        return [
            {
                'course_id': s.course.id,
                'course_name': s.course.name,
                'course_code': s.course.code,
                'teacher_name': s.teacher.get_full_name() if hasattr(s.teacher, 'get_full_name') 
                               else f"{s.teacher.first_name} {s.teacher.last_name}".strip() or s.teacher.username,
                'classroom': str(s.classroom),
                'classroom_id': s.classroom.id,
                'time_slot': s.time_slot.name,
                'time_slot_id': s.time_slot.id,
                'day_of_week': s.day_of_week,
                'start_time': s.time_slot.start_time.strftime('%H:%M'),
                'end_time': s.time_slot.end_time.strftime('%H:%M'),
                'week_range': s.week_range,
                'semester': s.semester,
                'status': s.status,
                'notes': s.notes
            }
            for s in schedules
        ]

    def _get_notifications(self):
        """获取最近通知（来自通知系统）"""
        if not NOTIFICATIONS_AVAILABLE:
            return []

        notifications = (
            Notification.objects.filter(recipient=self.user)
            .order_by('-created_at')[:5]
        )
        return [
            {
                'id': n.id,
                'title': n.title,
                'message': n.message,
                'notification_type': n.notification_type,
                'priority': n.priority,
                'created_at': n.created_at,
                'extra': n.extra_data or {},
            }
            for n in notifications
        ]

    def _get_upcoming_deadlines(self):
        """获取即将到来的截止日期（作业/考试等）"""
        if not NOTIFICATIONS_AVAILABLE:
            return []

        now = timezone.now()
        today = now.date()
        in_days = today + timedelta(days=14)

        # 从通知系统中提取带有截止时间的通知（assignment_due / exam_notification）
        qs = Notification.objects.filter(
            recipient=self.user,
            notification_type__in=[
                NotificationType.ASSIGNMENT_DUE,
                NotificationType.EXAM_NOTIFICATION,
            ],
        ).order_by('created_at')

        upcoming = []
        for n in qs:
            due_raw = None
            if isinstance(n.extra_data, dict):
                due_raw = n.extra_data.get('due_date') or n.extra_data.get('deadline')

            due_date = None
            if isinstance(due_raw, str):
                try:
                    # 兼容 'YYYY-MM-DD' 或 ISO 字符串
                    date_part = due_raw.split('T')[0]
                    due_date = datetime.strptime(date_part, '%Y-%m-%d').date()
                except Exception:
                    pass

            if due_date and today <= due_date <= in_days:
                upcoming.append({
                    'id': n.id,
                    'title': n.title,
                    'course': (n.extra_data or {}).get('course_name'),
                    'type': n.notification_type,
                    'due_date': due_date,
                    'priority': n.priority,
                })

        # 按截止日期排序
        upcoming.sort(key=lambda x: x['due_date'])
        return upcoming[:10]

    def _can_drop_course(self, enrollment):
        """检查是否可以退课"""
        # 简单的退课规则：选课后7天内可以退课
        return (timezone.now() - enrollment.enrolled_at).days <= 7
    
    def _update_student_credits(self):
        """更新学生学分信息"""
        completed_enrollments = Enrollment.objects.filter(
            student=self.user,
            status='completed'
        ).select_related('course')
        
        completed_credits = sum(e.course.credits for e in completed_enrollments)
        
        self.profile.completed_credits = completed_credits
        self.profile.save()
    
    def _score_to_gpa(self, score):
        """分数转换为绩点"""
        if score >= 90:
            return 4.0
        elif score >= 85:
            return 3.7
        elif score >= 82:
            return 3.3
        elif score >= 78:
            return 3.0
        elif score >= 75:
            return 2.7
        elif score >= 72:
            return 2.3
        elif score >= 68:
            return 2.0
        elif score >= 64:
            return 1.5
        elif score >= 60:
            return 1.0
        else:
            return 0.0
    
    def _score_to_grade_level(self, score):
        """分数转换为等级"""
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
