from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import datetime
from django.db import transaction
from apps.courses.models import Course, Enrollment
from apps.schedules.models import Schedule, TimeSlot
from .models import TeacherProfile, TeacherCourseAssignment, TeacherNotice
from .serializers import TeacherProfileSerializer, GradeEntrySerializer


class TeacherService:
    """教师业务逻辑服务类"""
    
    def __init__(self, user):
        self.user = user
        self.profile, _ = TeacherProfile.objects.get_or_create(
            user=user,
            defaults={
                'title': 'lecturer',  # 默认职称
                'research_area': '待完善',  # 默认研究方向
                'office_location': '待分配',  # 默认办公室
                'office_hours': '待安排',  # 默认答疑时间
            }
        )
    
    def get_dashboard_data(self):
        """获取教师仪表板数据"""
        
        # 基本信息
        teacher_info = TeacherProfileSerializer(self.profile).data
        
        # 教学统计
        my_courses = Course.objects.filter(
            teachers=self.user,
            is_active=True
        )
        total_courses = my_courses.count()
        
        # 当前学期课程
        current_semester = self._get_current_semester()
        current_semester_courses = my_courses.filter(
            semester=current_semester
        ).count()
        
        # 学生总数
        total_students = Enrollment.objects.filter(
            course__in=my_courses,
            status='enrolled',
            is_active=True
        ).count()
        
        # 课程统计
        course_statistics = self._get_course_statistics()
        
        # 今日教学安排
        today_schedule = self._get_today_schedule()
        
        # 待处理任务
        pending_tasks = self._get_pending_tasks()
        
        # 最近通知
        recent_notices = self._get_recent_notices()
        
        return {
            'teacher_info': teacher_info,
            'total_courses': total_courses,
            'current_semester_courses': current_semester_courses,
            'total_students': total_students,
            'course_statistics': course_statistics,
            'today_schedule': today_schedule,
            'pending_tasks': pending_tasks,
            'recent_notices': recent_notices,
        }
    
    def batch_update_grades(self, grades_data):
        """批量更新成绩"""
        
        updated_count = 0
        failed_count = 0
        errors = []
        
        try:
            with transaction.atomic():
                for grade_item in grades_data:
                    try:
                        enrollment_id = grade_item.get('enrollment_id')
                        score = grade_item.get('score')
                        
                        if not enrollment_id:
                            errors.append({'error': '缺少选课记录ID'})
                            failed_count += 1
                            continue
                        
                        # 验证教师权限
                        enrollment = Enrollment.objects.get(
                            id=enrollment_id,
                            course__teachers=self.user,
                            is_active=True
                        )
                        
                        # 更新成绩
                        serializer = GradeEntrySerializer(
                            enrollment,
                            data={'score': score},
                            partial=True
                        )
                        
                        if serializer.is_valid():
                            serializer.save()
                            updated_count += 1
                        else:
                            errors.append({
                                'enrollment_id': enrollment_id,
                                'errors': serializer.errors
                            })
                            failed_count += 1
                    
                    except Enrollment.DoesNotExist:
                        errors.append({
                            'enrollment_id': enrollment_id,
                            'error': '选课记录不存在或无权限'
                        })
                        failed_count += 1
                    except Exception as e:
                        errors.append({
                            'enrollment_id': enrollment_id,
                            'error': str(e)
                        })
                        failed_count += 1
            
            return {
                'success': True,
                'updated_count': updated_count,
                'failed_count': failed_count,
                'errors': errors
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'批量更新失败: {str(e)}'
            }
    
    def get_course_grade_statistics(self, course_id):
        """获取课程成绩统计"""
        
        try:
            course = Course.objects.get(
                id=course_id,
                teachers=self.user,
                is_active=True
            )
            
            enrollments = Enrollment.objects.filter(
                course=course,
                is_active=True
            )
            
            # 基本统计
            total_students = enrollments.count()
            graded_students = enrollments.filter(score__isnull=False).count()
            ungraded_students = total_students - graded_students
            
            # 成绩统计
            graded_enrollments = enrollments.filter(score__isnull=False)
            
            if graded_enrollments.exists():
                scores = [float(e.score) for e in graded_enrollments]
                average_score = sum(scores) / len(scores)
                max_score = max(scores)
                min_score = min(scores)
                pass_count = sum(1 for score in scores if score >= 60)
                pass_rate = (pass_count / len(scores)) * 100
                
                # 成绩分布
                grade_distribution = {
                    'A (90-100)': sum(1 for score in scores if score >= 90),
                    'B (80-89)': sum(1 for score in scores if 80 <= score < 90),
                    'C (70-79)': sum(1 for score in scores if 70 <= score < 80),
                    'D (60-69)': sum(1 for score in scores if 60 <= score < 70),
                    'F (0-59)': sum(1 for score in scores if score < 60),
                }
            else:
                average_score = 0
                max_score = 0
                min_score = 0
                pass_rate = 0
                grade_distribution = {}
            
            return {
                'course_info': {
                    'id': course.id,
                    'name': course.name,
                    'code': course.code
                },
                'student_statistics': {
                    'total_students': total_students,
                    'graded_students': graded_students,
                    'ungraded_students': ungraded_students
                },
                'grade_statistics': {
                    'average_score': round(average_score, 2),
                    'max_score': max_score,
                    'min_score': min_score,
                    'pass_rate': round(pass_rate, 2),
                    'grade_distribution': grade_distribution
                }
            }
        
        except Course.DoesNotExist:
            raise ValueError('课程不存在或无权限访问')
    
    def get_teaching_schedule(self, semester=None, week=None):
        """获取教学安排"""
        
        my_courses = Course.objects.filter(
            teachers=self.user,
            is_active=True
        )
        
        if semester:
            my_courses = my_courses.filter(semester=semester)
        
        schedule_data = []
        
        # 这里应该根据实际的课程表模型来生成教学安排数据
        # 暂时返回基本的课程信息
        for course in my_courses:
            schedule_data.append({
                'course_id': course.id,
                'course_name': course.name,
                'course_code': course.code,
                'student_count': course.current_enrollment,
                'classroom': '待安排',  # 需要从课程表模型获取
                'time_slot': '待安排',  # 需要从课程表模型获取
                'day_of_week': 1,  # 需要从课程表模型获取
                'start_time': '08:00',  # 需要从课程表模型获取
                'end_time': '09:40',  # 需要从课程表模型获取
                'week_range': '1-18周',  # 需要从课程表模型获取
            })
        
        return schedule_data
    
    def _get_current_semester(self):
        """获取当前学期"""
        now = timezone.now()
        year = now.year
        month = now.month
        
        if month >= 9 or month <= 1:
            return f"{year}-{year+1}-1"  # 秋季学期
        else:
            return f"{year-1}-{year}-2"  # 春季学期
    
    def _get_course_statistics(self):
        """获取课程统计"""
        my_courses = Course.objects.filter(
            teachers=self.user,
            is_active=True
        )
        
        # 按课程类型统计
        course_type_stats = {}
        for course in my_courses:
            course_type = course.get_course_type_display()
            if course_type not in course_type_stats:
                course_type_stats[course_type] = 0
            course_type_stats[course_type] += 1
        
        # 按院系统计
        department_stats = {}
        for course in my_courses:
            dept = course.department
            if dept not in department_stats:
                department_stats[dept] = 0
            department_stats[dept] += 1
        
        return {
            'by_type': course_type_stats,
            'by_department': department_stats
        }
    
    def _get_today_schedule(self):
        """获取今日教学安排（对接真实排课数据）"""
        today = timezone.localdate()
        weekday = today.isoweekday()  # 1-7
        current_semester = self._get_current_semester()

        schedules = (
            Schedule.objects.filter(
                teacher=self.user,
                semester=current_semester,
                status='active',
                day_of_week=weekday,
            )
            .select_related('course', 'classroom', 'time_slot')
            .order_by('time_slot__order')
        )

        # 按当前周次过滤
        def _current_week_number():
            now = timezone.now()
            semester_start_year = now.year if now.month >= 9 else now.year - 1
            semester_start = datetime(semester_start_year, 9, 1, tzinfo=now.tzinfo)
            delta_days = (now - semester_start).days
            return max(1, min(20, delta_days // 7 + 1))

        week_no = _current_week_number()
        schedules = [s for s in schedules if s.is_active_in_week(week_no)]

        return [
            {
                'course_id': s.course.id,
                'course_name': s.course.name,
                'course_code': s.course.code,
                'classroom': str(s.classroom),
                'time_slot': s.time_slot.name,
                'day_of_week': s.day_of_week,
                'start_time': s.time_slot.start_time.strftime('%H:%M'),
                'end_time': s.time_slot.end_time.strftime('%H:%M'),
                'week_range': s.week_range,
            }
            for s in schedules
        ]

    def _get_pending_tasks(self):
        """获取待处理任务"""
        tasks = []
        
        # 未录入成绩的学生数量
        my_courses = Course.objects.filter(
            teachers=self.user,
            is_active=True
        )
        
        for course in my_courses:
            ungraded_count = Enrollment.objects.filter(
                course=course,
                status='enrolled',
                score__isnull=True,
                is_active=True
            ).count()
            
            if ungraded_count > 0:
                tasks.append({
                    'type': 'grade_entry',
                    'title': f'{course.name} - 成绩录入',
                    'description': f'有 {ungraded_count} 名学生成绩待录入',
                    'count': ungraded_count,
                    'course_id': course.id
                })
        
        # 未发布的通知
        unpublished_notices = TeacherNotice.objects.filter(
            teacher=self.user,
            is_published=False
        ).count()
        
        if unpublished_notices > 0:
            tasks.append({
                'type': 'notice_publish',
                'title': '待发布通知',
                'description': f'有 {unpublished_notices} 条通知待发布',
                'count': unpublished_notices
            })
        
        return tasks
    
    def _get_recent_notices(self):
        """获取最近通知"""
        recent_notices = TeacherNotice.objects.filter(
            teacher=self.user
        ).select_related('course').order_by('-created_at')[:5]
        
        return [
            {
                'id': notice.id,
                'title': notice.title,
                'course_name': notice.course.name,
                'notice_type': notice.get_notice_type_display(),
                'is_published': notice.is_published,
                'created_at': notice.created_at
            }
            for notice in recent_notices
        ]
