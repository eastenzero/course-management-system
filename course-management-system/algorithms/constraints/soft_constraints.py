# file: algorithms/constraints/soft_constraints.py
# 功能: 软约束条件评分 - 优化目标，可以违反但会降低方案质量

from typing import List, Dict, Any
import numpy as np
from ..models import Assignment, TeacherPreference
import sys
import os

# 添加Django项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')

try:
    import django
    django.setup()
    from apps.users.models import User
    from apps.courses.models import Course
except ImportError:
    User = None
    Course = None


class SoftConstraints:
    """软约束条件评分器 - 优化目标，可以违反但会降低方案质量"""
    
    def __init__(self):
        self.score_cache = {}  # 缓存评分结果
    
    @staticmethod
    def teacher_preference_score(assignment: Assignment, teacher_preferences: Dict[int, List[TeacherPreference]] = None,
                               teacher_data: Dict = None) -> float:
        """教师时间偏好评分 (0.0-1.0)"""
        teacher_id = assignment.teacher_id
        day_of_week = assignment.day_of_week
        time_slot = assignment.time_slot
        
        # 从偏好数据中查找
        if teacher_preferences and teacher_id in teacher_preferences:
            for pref in teacher_preferences[teacher_id]:
                if pref.day_of_week == day_of_week and pref.time_slot == time_slot:
                    return pref.preference_score
        
        # 从教师数据中查找
        if teacher_data:
            preferences = teacher_data.get('time_preferences', {})
            day_prefs = preferences.get(str(day_of_week), {})
            return day_prefs.get(str(time_slot), 0.5)  # 默认中性偏好
        
        # 默认评分策略
        # 上午时间段(1-4)评分较高，下午(5-8)中等，晚上(9-12)较低
        if 1 <= time_slot <= 4:
            return 0.8
        elif 5 <= time_slot <= 8:
            return 0.6
        elif 9 <= time_slot <= 12:
            return 0.4
        else:
            return 0.2
    
    @staticmethod
    def workload_balance_score(assignment: Assignment, existing_assignments: List[Assignment],
                             teacher_data: Dict = None) -> float:
        """教师工作量平衡评分 (0.0-1.0)"""
        teacher_id = assignment.teacher_id
        
        # 计算教师当前总工作量
        current_load = len([a for a in existing_assignments if a.teacher_id == teacher_id]) + 1
        
        # 获取教师理想工作量
        if teacher_data:
            ideal_load = teacher_data.get('max_weekly_hours', 16)
        else:
            ideal_load = 16  # 默认每周16课时
        
        if current_load <= ideal_load:
            # 未达到理想工作量，评分递增
            return min(1.0, current_load / ideal_load)
        else:
            # 超过理想工作量，评分递减
            excess = current_load - ideal_load
            return max(0.0, 1.0 - (excess / ideal_load))
    
    @staticmethod
    def time_distribution_score(assignment: Assignment, existing_assignments: List[Assignment]) -> float:
        """课程时间分布均匀性评分 (0.0-1.0)"""
        course_id = assignment.course_id
        
        # 获取该课程的所有分配（包括当前分配）
        course_assignments = [a for a in existing_assignments if a.course_id == course_id]
        course_assignments.append(assignment)
        
        if len(course_assignments) <= 1:
            return 1.0
        
        # 计算时间间隔
        time_points = []
        for a in course_assignments:
            # 将星期和时间段转换为连续的时间点
            time_point = (a.day_of_week - 1) * 20 + a.time_slot
            time_points.append(time_point)
        
        time_points.sort()
        
        # 计算相邻时间点的间隔
        intervals = []
        for i in range(len(time_points) - 1):
            interval = time_points[i + 1] - time_points[i]
            intervals.append(interval)
        
        if not intervals:
            return 1.0
        
        # 计算间隔的方差，方差越小分数越高
        variance = np.var(intervals)
        max_variance = 50 * 50  # 假设最大方差
        return max(0.0, 1.0 - (variance / max_variance))
    
    @staticmethod
    def classroom_utilization_score(assignment: Assignment, existing_assignments: List[Assignment],
                                  classroom_data: Dict = None, course_data: Dict = None) -> float:
        """教室利用率评分 (0.0-1.0)"""
        classroom_id = assignment.classroom_id
        
        # 获取教室容量和课程人数
        if classroom_data and course_data:
            classroom_capacity = classroom_data.get('capacity', 100)
            course_students = course_data.get('max_students', 50)
        else:
            # 默认值
            classroom_capacity = 100
            course_students = 50
        
        # 计算利用率
        utilization = course_students / classroom_capacity
        
        # 理想利用率在70%-90%之间
        if 0.7 <= utilization <= 0.9:
            return 1.0
        elif utilization < 0.7:
            # 利用率过低
            return utilization / 0.7
        else:
            # 利用率过高（虽然满足硬约束，但不够舒适）
            return max(0.0, 2.0 - utilization)
    
    @staticmethod
    def day_balance_score(assignment: Assignment, existing_assignments: List[Assignment]) -> float:
        """每日课程分布平衡评分 (0.0-1.0)"""
        # 统计每天的课程数量
        daily_counts = {i: 0 for i in range(1, 8)}  # 周一到周日
        
        for a in existing_assignments:
            daily_counts[a.day_of_week] += 1
        
        # 加上当前分配
        daily_counts[assignment.day_of_week] += 1
        
        # 计算工作日(周一到周五)的课程分布
        weekday_counts = [daily_counts[i] for i in range(1, 6)]
        
        if not weekday_counts or all(c == 0 for c in weekday_counts):
            return 1.0
        
        # 计算方差，方差越小分布越均匀
        mean_count = np.mean(weekday_counts)
        variance = np.var(weekday_counts)
        
        # 标准化方差
        max_variance = mean_count * mean_count  # 假设最大方差
        if max_variance == 0:
            return 1.0
        
        return max(0.0, 1.0 - (variance / max_variance))
    
    @staticmethod
    def consecutive_classes_penalty(assignment: Assignment, existing_assignments: List[Assignment]) -> float:
        """连续课程惩罚评分 (0.0-1.0)"""
        teacher_id = assignment.teacher_id
        day_of_week = assignment.day_of_week
        time_slot = assignment.time_slot
        
        # 获取同一教师同一天的课程
        same_day_assignments = [
            a for a in existing_assignments 
            if a.teacher_id == teacher_id and a.day_of_week == day_of_week
        ]
        
        # 检查是否有连续的时间段
        consecutive_count = 1  # 包括当前分配
        
        # 检查前一个时间段
        if any(a.time_slot == time_slot - 1 for a in same_day_assignments):
            consecutive_count += 1
        
        # 检查后一个时间段
        if any(a.time_slot == time_slot + 1 for a in same_day_assignments):
            consecutive_count += 1
        
        # 连续课程数量越多，惩罚越大
        if consecutive_count <= 2:
            return 1.0  # 2节连续课是可以接受的
        elif consecutive_count == 3:
            return 0.7  # 3节连续课有一定惩罚
        elif consecutive_count == 4:
            return 0.4  # 4节连续课惩罚较大
        else:
            return 0.1  # 5节及以上连续课惩罚很大
    
    @staticmethod
    def room_type_match_score(assignment: Assignment, classroom_data: Dict = None,
                            course_data: Dict = None) -> float:
        """教室类型匹配评分 (0.0-1.0)"""
        if not classroom_data or not course_data:
            return 0.8  # 默认评分
        
        classroom_type = classroom_data.get('room_type', 'lecture')
        course_name = course_data.get('name', '').lower()
        
        # 定义课程类型与教室类型的匹配规则
        type_matches = {
            'computer': ['计算机', '编程', '软件', '数据库', '网络'],
            'lab': ['实验', '物理', '化学', '生物'],
            'multimedia': ['多媒体', '设计', '艺术', '影视'],
            'seminar': ['研讨', '讨论', '案例'],
            'auditorium': ['大课', '公共课', '讲座'],
        }
        
        # 检查课程名称是否匹配教室类型
        for room_type, keywords in type_matches.items():
            if classroom_type == room_type:
                for keyword in keywords:
                    if keyword in course_name:
                        return 1.0
        
        # 普通教室可以用于大多数课程
        if classroom_type == 'lecture':
            return 0.8
        
        return 0.6  # 不匹配但可以使用
    
    @classmethod
    def calculate_total_score(cls, assignment: Assignment, existing_assignments: List[Assignment],
                            teacher_preferences: Dict[int, List[TeacherPreference]] = None,
                            teacher_data: Dict = None, classroom_data: Dict = None,
                            course_data: Dict = None, weights: Dict[str, float] = None) -> float:
        """计算总的软约束评分"""
        if weights is None:
            weights = {
                'teacher_preference': 0.25,
                'workload_balance': 0.20,
                'time_distribution': 0.15,
                'classroom_utilization': 0.15,
                'day_balance': 0.10,
                'consecutive_penalty': 0.10,
                'room_type_match': 0.05,
            }
        
        scores = {}
        
        # 教师偏好评分
        scores['teacher_preference'] = cls.teacher_preference_score(
            assignment, teacher_preferences, teacher_data
        )
        
        # 工作量平衡评分
        scores['workload_balance'] = cls.workload_balance_score(
            assignment, existing_assignments, teacher_data
        )
        
        # 时间分布评分
        scores['time_distribution'] = cls.time_distribution_score(
            assignment, existing_assignments
        )
        
        # 教室利用率评分
        scores['classroom_utilization'] = cls.classroom_utilization_score(
            assignment, existing_assignments, classroom_data, course_data
        )
        
        # 每日平衡评分
        scores['day_balance'] = cls.day_balance_score(
            assignment, existing_assignments
        )
        
        # 连续课程惩罚
        scores['consecutive_penalty'] = cls.consecutive_classes_penalty(
            assignment, existing_assignments
        )
        
        # 教室类型匹配评分
        scores['room_type_match'] = cls.room_type_match_score(
            assignment, classroom_data, course_data
        )
        
        # 计算加权总分
        total_score = sum(scores[key] * weights[key] for key in scores)
        
        return total_score
