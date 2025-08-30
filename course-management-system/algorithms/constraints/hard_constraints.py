# file: algorithms/constraints/hard_constraints.py
# 功能: 硬约束条件检查 - 必须满足的约束条件

from typing import List, Dict, Set, Any
from ..models import Assignment
import sys
import os

# 添加Django项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')

try:
    import django
    django.setup()
    from apps.courses.models import Course
    from apps.classrooms.models import Classroom
    from apps.users.models import User
    from apps.schedules.models import Schedule, TimeSlot
except ImportError:
    # 如果Django不可用，使用模拟类
    Course = None
    Classroom = None
    User = None
    Schedule = None
    TimeSlot = None


class HardConstraints:
    """硬约束条件检查器 - 必须满足的约束条件"""
    
    def __init__(self):
        self.violation_cache = {}  # 缓存违反记录
    
    @staticmethod
    def teacher_conflict_check(assignment: Assignment, existing_assignments: List[Assignment]) -> bool:
        """检查教师时间冲突"""
        teacher_id = assignment.teacher_id
        time_key = assignment.time_key
        
        # 检查同一教师在同一时间是否已有课程
        for existing in existing_assignments:
            if (existing.teacher_id == teacher_id and 
                existing.time_key == time_key and
                existing != assignment):
                return False
        
        return True
    
    @staticmethod
    def classroom_conflict_check(assignment: Assignment, existing_assignments: List[Assignment]) -> bool:
        """检查教室时间冲突"""
        classroom_id = assignment.classroom_id
        time_key = assignment.time_key
        
        # 检查同一教室在同一时间是否已被占用
        for existing in existing_assignments:
            if (existing.classroom_id == classroom_id and 
                existing.time_key == time_key and
                existing != assignment):
                return False
        
        return True
    
    @staticmethod
    def classroom_capacity_check(assignment: Assignment, course_data: Dict = None, 
                               classroom_data: Dict = None) -> bool:
        """检查教室容量是否满足课程需求"""
        try:
            if Course and Classroom:
                # 使用Django模型
                course = Course.objects.get(id=assignment.course_id)
                classroom = Classroom.objects.get(id=assignment.classroom_id)
                return classroom.capacity >= course.max_students
            else:
                # 使用传入的数据
                if course_data and classroom_data:
                    course_max_students = course_data.get('max_students', 0)
                    classroom_capacity = classroom_data.get('capacity', 0)
                    return classroom_capacity >= course_max_students
                return True
        except Exception:
            return True
    
    @staticmethod
    def teacher_qualification_check(assignment: Assignment, teacher_data: Dict = None,
                                  course_data: Dict = None) -> bool:
        """检查教师是否有资格教授该课程"""
        try:
            if Course and User:
                # 使用Django模型
                course = Course.objects.get(id=assignment.course_id)
                teacher = User.objects.get(id=assignment.teacher_id)
                return course.teachers.filter(id=teacher.id).exists()
            else:
                # 使用传入的数据
                if teacher_data and course_data:
                    qualified_courses = teacher_data.get('qualified_courses', [])
                    return assignment.course_id in qualified_courses
                return True
        except Exception:
            return True
    
    @staticmethod
    def time_slot_validity_check(assignment: Assignment) -> bool:
        """检查时间段是否有效"""
        try:
            if TimeSlot:
                # 检查时间段是否存在且启用
                return TimeSlot.objects.filter(
                    order=assignment.time_slot, 
                    is_active=True
                ).exists()
            else:
                # 基本范围检查
                return 1 <= assignment.time_slot <= 20
        except Exception:
            return 1 <= assignment.time_slot <= 20
    
    @staticmethod
    def classroom_availability_check(assignment: Assignment, classroom_data: Dict = None) -> bool:
        """检查教室是否可用"""
        try:
            if Classroom:
                # 使用Django模型
                classroom = Classroom.objects.get(id=assignment.classroom_id)
                return classroom.is_available and classroom.is_active
            else:
                # 使用传入的数据
                if classroom_data:
                    return (classroom_data.get('is_available', True) and 
                           classroom_data.get('is_active', True))
                return True
        except Exception:
            return True
    
    @staticmethod
    def course_active_check(assignment: Assignment, course_data: Dict = None) -> bool:
        """检查课程是否启用"""
        try:
            if Course:
                # 使用Django模型
                course = Course.objects.get(id=assignment.course_id)
                return course.is_active and course.is_published
            else:
                # 使用传入的数据
                if course_data:
                    return (course_data.get('is_active', True) and 
                           course_data.get('is_published', True))
                return True
        except Exception:
            return True
    
    @staticmethod
    def teacher_workload_check(assignment: Assignment, existing_assignments: List[Assignment],
                             teacher_data: Dict = None, max_hours_per_day: int = 8) -> bool:
        """检查教师当日工作量是否超限"""
        teacher_id = assignment.teacher_id
        day_of_week = assignment.day_of_week
        
        # 计算教师当日已有课时
        daily_hours = 0
        for existing in existing_assignments:
            if (existing.teacher_id == teacher_id and 
                existing.day_of_week == day_of_week):
                daily_hours += 1
        
        # 加上当前分配的课时
        daily_hours += 1
        
        # 检查是否超过最大限制
        if teacher_data:
            max_daily_hours = teacher_data.get('max_daily_hours', max_hours_per_day)
        else:
            max_daily_hours = max_hours_per_day
        
        return daily_hours <= max_daily_hours
    
    @classmethod
    def check_all_hard_constraints(cls, assignment: Assignment, 
                                 existing_assignments: List[Assignment],
                                 course_data: Dict = None,
                                 classroom_data: Dict = None,
                                 teacher_data: Dict = None) -> Dict[str, bool]:
        """检查所有硬约束条件"""
        results = {}
        
        # 教师时间冲突检查
        results['teacher_conflict'] = cls.teacher_conflict_check(assignment, existing_assignments)
        
        # 教室时间冲突检查
        results['classroom_conflict'] = cls.classroom_conflict_check(assignment, existing_assignments)
        
        # 教室容量检查
        results['classroom_capacity'] = cls.classroom_capacity_check(
            assignment, course_data, classroom_data
        )
        
        # 教师资格检查
        results['teacher_qualification'] = cls.teacher_qualification_check(
            assignment, teacher_data, course_data
        )
        
        # 时间段有效性检查
        results['time_slot_validity'] = cls.time_slot_validity_check(assignment)
        
        # 教室可用性检查
        results['classroom_availability'] = cls.classroom_availability_check(
            assignment, classroom_data
        )
        
        # 课程启用检查
        results['course_active'] = cls.course_active_check(assignment, course_data)
        
        # 教师工作量检查
        results['teacher_workload'] = cls.teacher_workload_check(
            assignment, existing_assignments, teacher_data
        )
        
        return results
    
    @classmethod
    def is_valid_assignment(cls, assignment: Assignment, 
                          existing_assignments: List[Assignment],
                          course_data: Dict = None,
                          classroom_data: Dict = None,
                          teacher_data: Dict = None) -> bool:
        """检查分配是否满足所有硬约束"""
        results = cls.check_all_hard_constraints(
            assignment, existing_assignments, course_data, classroom_data, teacher_data
        )
        return all(results.values())
    
    @classmethod
    def get_violations(cls, assignment: Assignment, 
                      existing_assignments: List[Assignment],
                      course_data: Dict = None,
                      classroom_data: Dict = None,
                      teacher_data: Dict = None) -> List[str]:
        """获取违反的约束条件列表"""
        results = cls.check_all_hard_constraints(
            assignment, existing_assignments, course_data, classroom_data, teacher_data
        )
        violations = []
        
        constraint_messages = {
            'teacher_conflict': '教师时间冲突',
            'classroom_conflict': '教室时间冲突',
            'classroom_capacity': '教室容量不足',
            'teacher_qualification': '教师不具备授课资格',
            'time_slot_validity': '时间段无效',
            'classroom_availability': '教室不可用',
            'course_active': '课程未启用',
            'teacher_workload': '教师工作量超限',
        }
        
        for constraint, passed in results.items():
            if not passed:
                violations.append(constraint_messages.get(constraint, constraint))
        
        return violations
