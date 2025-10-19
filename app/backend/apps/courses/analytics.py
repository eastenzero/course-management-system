"""
成绩分析服务
"""

from django.db.models import Avg, Count, Max, Min, StdDev, Q, F
from django.db.models.functions import Round
from decimal import Decimal
from typing import Dict, List, Any, Optional
import statistics
from collections import defaultdict

from .models import Course, Enrollment, Grade, GradeComponent
from apps.users.models import User


class GradeAnalyticsService:
    """成绩分析服务"""
    
    @staticmethod
    def get_course_grade_distribution(course_id: int) -> Dict[str, Any]:
        """获取课程成绩分布"""
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return {'error': '课程不存在'}
        
        enrollments = course.enrollments.filter(
            is_active=True,
            score__isnull=False
        )
        
        if not enrollments.exists():
            return {
                'course_info': {
                    'id': course.id,
                    'name': course.name,
                    'code': course.code
                },
                'total_students': 0,
                'distribution': {},
                'statistics': {}
            }
        
        # 成绩分布统计
        grade_ranges = [
            ('A', 90, 100),
            ('B', 80, 89),
            ('C', 70, 79),
            ('D', 60, 69),
            ('F', 0, 59)
        ]
        
        distribution = {}
        for grade_letter, min_score, max_score in grade_ranges:
            count = enrollments.filter(
                score__gte=min_score,
                score__lte=max_score
            ).count()
            distribution[grade_letter] = {
                'count': count,
                'percentage': round(count / enrollments.count() * 100, 2) if enrollments.count() > 0 else 0,
                'range': f'{min_score}-{max_score}'
            }
        
        # 基础统计
        scores = [enrollment.score for enrollment in enrollments]
        statistics_data = {
            'total_students': enrollments.count(),
            'average': round(sum(scores) / len(scores), 2),
            'median': round(statistics.median(scores), 2),
            'std_dev': round(statistics.stdev(scores) if len(scores) > 1 else 0, 2),
            'min_score': min(scores),
            'max_score': max(scores),
            'pass_rate': round(enrollments.filter(score__gte=60).count() / enrollments.count() * 100, 2)
        }
        
        return {
            'course_info': {
                'id': course.id,
                'name': course.name,
                'code': course.code
            },
            'total_students': enrollments.count(),
            'distribution': distribution,
            'statistics': statistics_data
        }
    
    @staticmethod
    def get_student_grade_trend(student_id: int, semester: str = None) -> Dict[str, Any]:
        """获取学生成绩趋势"""
        try:
            student = User.objects.get(id=student_id, user_type='student')
        except User.DoesNotExist:
            return {'error': '学生不存在'}
        
        enrollments = student.enrollments.filter(is_active=True)
        
        if semester:
            enrollments = enrollments.filter(course__semester=semester)
        
        enrollments = enrollments.select_related('course').order_by('course__semester', 'enrolled_at')
        
        trend_data = []
        semester_stats = defaultdict(list)
        
        for enrollment in enrollments:
            if enrollment.score is not None:
                course_data = {
                    'course_id': enrollment.course.id,
                    'course_name': enrollment.course.name,
                    'course_code': enrollment.course.code,
                    'semester': enrollment.course.semester,
                    'credits': enrollment.course.credits,
                    'score': float(enrollment.score),
                    'grade': enrollment.grade,
                    'enrolled_at': enrollment.enrolled_at.isoformat()
                }
                trend_data.append(course_data)
                semester_stats[enrollment.course.semester].append(float(enrollment.score))
        
        # 计算学期统计
        semester_summary = {}
        for sem, scores in semester_stats.items():
            if scores:
                semester_summary[sem] = {
                    'average': round(sum(scores) / len(scores), 2),
                    'course_count': len(scores),
                    'total_credits': sum(
                        enrollment.course.credits 
                        for enrollment in enrollments.filter(course__semester=sem)
                        if enrollment.score is not None
                    )
                }
        
        # 计算GPA趋势
        gpa_trend = []
        for sem in sorted(semester_summary.keys()):
            gpa_trend.append({
                'semester': sem,
                'gpa': GradeAnalyticsService._calculate_gpa(semester_stats[sem]),
                'average': semester_summary[sem]['average']
            })
        
        return {
            'student_info': {
                'id': student.id,
                'username': student.username,
                'name': f"{student.first_name} {student.last_name}".strip() or student.username
            },
            'trend_data': trend_data,
            'semester_summary': semester_summary,
            'gpa_trend': gpa_trend,
            'overall_stats': {
                'total_courses': len(trend_data),
                'overall_average': round(sum(item['score'] for item in trend_data) / len(trend_data), 2) if trend_data else 0,
                'overall_gpa': GradeAnalyticsService._calculate_gpa([item['score'] for item in trend_data])
            }
        }
    
    @staticmethod
    def get_course_difficulty_analysis(course_id: int) -> Dict[str, Any]:
        """分析课程难度"""
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return {'error': '课程不存在'}
        
        enrollments = course.enrollments.filter(
            is_active=True,
            score__isnull=False
        )
        
        if not enrollments.exists():
            return {
                'course_info': {
                    'id': course.id,
                    'name': course.name,
                    'code': course.code
                },
                'difficulty_level': 'unknown',
                'analysis': {}
            }
        
        scores = [float(enrollment.score) for enrollment in enrollments]
        avg_score = sum(scores) / len(scores)
        pass_rate = len([s for s in scores if s >= 60]) / len(scores) * 100
        std_dev = statistics.stdev(scores) if len(scores) > 1 else 0
        
        # 难度评估
        difficulty_level = 'medium'
        if avg_score >= 85 and pass_rate >= 90:
            difficulty_level = 'easy'
        elif avg_score <= 70 or pass_rate <= 60:
            difficulty_level = 'hard'
        
        # 成绩组成分析
        component_analysis = {}
        for component in course.grade_components.all():
            component_grades = Grade.objects.filter(
                enrollment__course=course,
                component=component,
                enrollment__is_active=True
            )
            
            if component_grades.exists():
                component_scores = [float(grade.percentage_score) for grade in component_grades]
                component_analysis[component.name] = {
                    'average': round(sum(component_scores) / len(component_scores), 2),
                    'weight': float(component.weight),
                    'pass_rate': round(len([s for s in component_scores if s >= 60]) / len(component_scores) * 100, 2),
                    'std_dev': round(statistics.stdev(component_scores) if len(component_scores) > 1 else 0, 2)
                }
        
        return {
            'course_info': {
                'id': course.id,
                'name': course.name,
                'code': course.code
            },
            'difficulty_level': difficulty_level,
            'analysis': {
                'average_score': round(avg_score, 2),
                'pass_rate': round(pass_rate, 2),
                'std_deviation': round(std_dev, 2),
                'total_students': len(scores),
                'component_analysis': component_analysis,
                'recommendations': GradeAnalyticsService._get_difficulty_recommendations(
                    difficulty_level, avg_score, pass_rate, std_dev
                )
            }
        }
    
    @staticmethod
    def get_class_comparison(class_name: str, semester: str) -> Dict[str, Any]:
        """班级成绩对比分析"""
        # 获取班级学生
        students = User.objects.filter(
            user_type='student',
            student_profile__class_name=class_name
        )
        
        if not students.exists():
            return {'error': '班级不存在或无学生'}
        
        # 获取该学期的所有选课记录
        enrollments = Enrollment.objects.filter(
            student__in=students,
            course__semester=semester,
            is_active=True,
            score__isnull=False
        ).select_related('course', 'student')
        
        if not enrollments.exists():
            return {
                'class_info': {
                    'class_name': class_name,
                    'semester': semester,
                    'student_count': students.count()
                },
                'course_analysis': {},
                'student_ranking': []
            }
        
        # 按课程分析
        course_analysis = {}
        courses = set(enrollment.course for enrollment in enrollments)
        
        for course in courses:
            course_enrollments = enrollments.filter(course=course)
            scores = [float(e.score) for e in course_enrollments]
            
            course_analysis[course.code] = {
                'course_name': course.name,
                'student_count': len(scores),
                'average': round(sum(scores) / len(scores), 2),
                'pass_rate': round(len([s for s in scores if s >= 60]) / len(scores) * 100, 2),
                'top_score': max(scores),
                'lowest_score': min(scores)
            }
        
        # 学生排名
        student_stats = defaultdict(lambda: {'total_score': 0, 'course_count': 0, 'courses': []})
        
        for enrollment in enrollments:
            student_id = enrollment.student.id
            student_stats[student_id]['total_score'] += float(enrollment.score)
            student_stats[student_id]['course_count'] += 1
            student_stats[student_id]['courses'].append({
                'course_code': enrollment.course.code,
                'course_name': enrollment.course.name,
                'score': float(enrollment.score),
                'grade': enrollment.grade
            })
            student_stats[student_id]['student_info'] = {
                'id': enrollment.student.id,
                'username': enrollment.student.username,
                'name': f"{enrollment.student.first_name} {enrollment.student.last_name}".strip() or enrollment.student.username
            }
        
        # 计算平均分并排序
        student_ranking = []
        for student_id, stats in student_stats.items():
            average = stats['total_score'] / stats['course_count'] if stats['course_count'] > 0 else 0
            student_ranking.append({
                'student_info': stats['student_info'],
                'average_score': round(average, 2),
                'course_count': stats['course_count'],
                'courses': stats['courses']
            })
        
        student_ranking.sort(key=lambda x: x['average_score'], reverse=True)
        
        # 添加排名
        for i, student in enumerate(student_ranking):
            student['rank'] = i + 1
        
        return {
            'class_info': {
                'class_name': class_name,
                'semester': semester,
                'student_count': students.count(),
                'enrolled_student_count': len(student_stats)
            },
            'course_analysis': course_analysis,
            'student_ranking': student_ranking,
            'class_statistics': {
                'class_average': round(sum(s['average_score'] for s in student_ranking) / len(student_ranking), 2) if student_ranking else 0,
                'top_student': student_ranking[0] if student_ranking else None,
                'course_count': len(course_analysis)
            }
        }
    
    @staticmethod
    def _calculate_gpa(scores: List[float]) -> float:
        """计算GPA"""
        if not scores:
            return 0.0
        
        gpa_points = []
        for score in scores:
            if score >= 90:
                gpa_points.append(4.0)
            elif score >= 80:
                gpa_points.append(3.0)
            elif score >= 70:
                gpa_points.append(2.0)
            elif score >= 60:
                gpa_points.append(1.0)
            else:
                gpa_points.append(0.0)
        
        return round(sum(gpa_points) / len(gpa_points), 2)
    
    @staticmethod
    def _get_difficulty_recommendations(difficulty_level: str, avg_score: float, pass_rate: float, std_dev: float) -> List[str]:
        """获取难度调整建议"""
        recommendations = []
        
        if difficulty_level == 'easy':
            recommendations.append('课程难度偏低，建议增加挑战性内容')
            recommendations.append('可以考虑提高作业和考试的难度')
        elif difficulty_level == 'hard':
            recommendations.append('课程难度偏高，建议适当降低难度')
            recommendations.append('可以增加辅导和答疑时间')
            if pass_rate < 50:
                recommendations.append('及格率过低，建议重新设计课程内容')
        
        if std_dev > 20:
            recommendations.append('成绩分布差异较大，建议关注学习困难的学生')
        
        if avg_score < 70:
            recommendations.append('平均分偏低，建议检查教学方法和内容设置')
        
        return recommendations
