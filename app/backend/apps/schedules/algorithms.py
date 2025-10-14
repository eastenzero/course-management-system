"""
智能排课算法模块
实现基于约束满足问题(CSP)的自动排课算法
"""

import random
import time
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from collections import defaultdict
from django.db import models
from django.db.models import Q

from .models import Schedule, TimeSlot
from apps.courses.models import Course
from apps.classrooms.models import Classroom
from apps.users.models import User


@dataclass
class ScheduleConstraint:
    """排课约束"""
    course: Course
    teacher: User
    preferred_classrooms: List[Classroom]
    preferred_time_slots: List[TimeSlot]
    preferred_days: List[int]  # 1-7 表示周一到周日
    sessions_per_week: int  # 每周课时数
    avoid_consecutive: bool = False  # 是否避免连续排课
    avoid_noon: bool = False  # 是否避免中午时间
    max_daily_sessions: int = 0  # 每天最大课时数，0表示无限制
    fixed_time_slots: List[Tuple[int, TimeSlot]] = None  # 固定时间槽 [(星期, 时间段)]
    priority: int = 1  # 优先级，数字越大优先级越高

    def __post_init__(self):
        if self.fixed_time_slots is None:
            self.fixed_time_slots = []

    def __hash__(self):
        return hash((self.course.id, self.teacher.id, self.sessions_per_week))

    def __eq__(self, other):
        return (self.course.id == other.course.id and
                self.teacher.id == other.teacher.id and
                self.sessions_per_week == other.sessions_per_week)


@dataclass
class ScheduleSlot:
    """排课时间槽"""
    day_of_week: int
    time_slot: TimeSlot
    classroom: Classroom
    
    def __hash__(self):
        return hash((self.day_of_week, self.time_slot.id, self.classroom.id))
    
    def __eq__(self, other):
        return (self.day_of_week == other.day_of_week and 
                self.time_slot.id == other.time_slot.id and 
                self.classroom.id == other.classroom.id)


class SchedulingAlgorithm:
    """智能排课算法"""
    
    def __init__(self, semester: str, academic_year: str):
        self.semester = semester
        self.academic_year = academic_year
        self.constraints: List[ScheduleConstraint] = []
        self.available_slots: Set[ScheduleSlot] = set()
        self.assigned_slots: Dict[ScheduleConstraint, List[ScheduleSlot]] = {}
        self.conflicts: List[Dict] = []

        # 优化：使用字典快速查找已分配的时间槽
        self.teacher_schedule: Dict[int, Dict[tuple, ScheduleConstraint]] = {}
        self.classroom_schedule: Dict[int, Dict[tuple, ScheduleConstraint]] = {}
        
    def add_constraint(self, constraint: ScheduleConstraint):
        """添加排课约束"""
        self.constraints.append(constraint)
        
    def initialize_available_slots(self):
        """初始化可用时间槽"""
        time_slots = TimeSlot.objects.filter(is_active=True).order_by('order')
        classrooms = Classroom.objects.filter(is_active=True)
        
        # 获取已有的排课，避免冲突
        existing_schedules = Schedule.objects.filter(
            semester=self.semester,
            academic_year=self.academic_year,
            status='active'
        ).select_related('time_slot', 'classroom')
        
        occupied_slots = set()
        for schedule in existing_schedules:
            slot = ScheduleSlot(
                day_of_week=schedule.day_of_week,
                time_slot=schedule.time_slot,
                classroom=schedule.classroom
            )
            occupied_slots.add(slot)
        
        # 生成所有可能的时间槽
        for day in range(1, 8):  # 周一到周日
            for time_slot in time_slots:
                for classroom in classrooms:
                    slot = ScheduleSlot(
                        day_of_week=day,
                        time_slot=time_slot,
                        classroom=classroom
                    )
                    if slot not in occupied_slots:
                        self.available_slots.add(slot)
    
    def check_teacher_conflict(self, teacher: User, slot: ScheduleSlot) -> bool:
        """检查教师时间冲突（优化版）"""
        teacher_id = teacher.id
        time_key = (slot.day_of_week, slot.time_slot.id)

        # 使用字典快速查找，O(1)时间复杂度
        if teacher_id in self.teacher_schedule:
            return time_key in self.teacher_schedule[teacher_id]
        return False

    def check_classroom_conflict(self, classroom: Classroom, slot: ScheduleSlot) -> bool:
        """检查教室冲突（优化版）"""
        classroom_id = classroom.id
        time_key = (slot.day_of_week, slot.time_slot.id)

        # 使用字典快速查找，O(1)时间复杂度
        if classroom_id in self.classroom_schedule:
            return time_key in self.classroom_schedule[classroom_id]
        return False

    def _update_conflict_tracking(self, constraint: ScheduleConstraint, slots: List[ScheduleSlot]):
        """更新冲突跟踪字典"""
        teacher_id = constraint.teacher.id

        # 初始化教师时间表
        if teacher_id not in self.teacher_schedule:
            self.teacher_schedule[teacher_id] = {}

        for slot in slots:
            time_key = (slot.day_of_week, slot.time_slot.id)

            # 更新教师时间表
            self.teacher_schedule[teacher_id][time_key] = constraint

            # 更新教室时间表
            classroom_id = slot.classroom.id
            if classroom_id not in self.classroom_schedule:
                self.classroom_schedule[classroom_id] = {}
            self.classroom_schedule[classroom_id][time_key] = constraint
    
    def calculate_slot_score(self, constraint: ScheduleConstraint, slot: ScheduleSlot) -> float:
        """计算时间槽的适合度分数"""
        score = 0.0
        
        # 优先级权重
        score += constraint.priority * 10
        
        # 偏好教室权重
        if slot.classroom in constraint.preferred_classrooms:
            score += 20
        
        # 偏好时间段权重
        if slot.time_slot in constraint.preferred_time_slots:
            score += 15
        
        # 偏好星期权重
        if slot.day_of_week in constraint.preferred_days:
            score += 10
        
        # 教室容量适合度
        if hasattr(constraint.course, 'max_students') and constraint.course.max_students:
            capacity_ratio = constraint.course.max_students / slot.classroom.capacity
            if 0.5 <= capacity_ratio <= 0.9:  # 理想的容量利用率
                score += 15
            elif capacity_ratio <= 1.0:
                score += 10
            else:
                score -= 20  # 容量不足，大幅减分
        
        # 避免过早或过晚的时间
        if 2 <= slot.time_slot.order <= 6:  # 假设这是比较好的时间段
            score += 5
        
        # 避免中午时间
        if constraint.avoid_noon and self._is_noon_time(slot.time_slot):
            score -= 30
        
        return score
    
    def find_best_slots(self, constraint: ScheduleConstraint) -> List[ScheduleSlot]:
        """为约束找到最佳时间槽"""
        candidate_slots = []
        
        # 处理固定时间槽
        if constraint.fixed_time_slots:
            fixed_slots = []
            for day_of_week, time_slot in constraint.fixed_time_slots:
                # 查找匹配的教室
                for classroom in constraint.preferred_classrooms or self._get_all_classrooms():
                    slot = ScheduleSlot(day_of_week=day_of_week, time_slot=time_slot, classroom=classroom)
                    if slot in self.available_slots:
                        # 检查冲突
                        if (not self.check_teacher_conflict(constraint.teacher, slot) and
                            not self.check_classroom_conflict(slot.classroom, slot)):
                            fixed_slots.append(slot)
            
            # 如果固定时间槽数量满足要求
            if len(fixed_slots) >= constraint.sessions_per_week:
                # 从可用槽中移除
                for slot in fixed_slots[:constraint.sessions_per_week]:
                    self.available_slots.discard(slot)
                return fixed_slots[:constraint.sessions_per_week]
        
        # 筛选可用的时间槽
        for slot in self.available_slots:
            # 检查基本约束
            if (slot.classroom in constraint.preferred_classrooms or 
                not constraint.preferred_classrooms):
                if (slot.time_slot in constraint.preferred_time_slots or 
                    not constraint.preferred_time_slots):
                    if (slot.day_of_week in constraint.preferred_days or 
                        not constraint.preferred_days):
                        # 检查中午时间约束
                        if constraint.avoid_noon and self._is_noon_time(slot.time_slot):
                            continue
                        
                        # 检查冲突
                        if (not self.check_teacher_conflict(constraint.teacher, slot) and
                            not self.check_classroom_conflict(slot.classroom, slot)):
                            score = self.calculate_slot_score(constraint, slot)
                            candidate_slots.append((slot, score))
        
        # 按分数排序
        candidate_slots.sort(key=lambda x: x[1], reverse=True)
        
        # 选择最佳的时间槽
        selected_slots = []
        daily_sessions = defaultdict(int)  # 每天课时计数
        
        for slot, score in candidate_slots:
            if len(selected_slots) >= constraint.sessions_per_week:
                break
                
            # 检查每天最大课时数限制
            if (constraint.max_daily_sessions > 0 and 
                daily_sessions[slot.day_of_week] >= constraint.max_daily_sessions):
                continue
                
            # 如果避免连续排课，检查是否在同一天（如果已经排了一天的课）
            if constraint.avoid_consecutive and daily_sessions[slot.day_of_week] > 0:
                # 检查是否与已选的同一日课程连续
                if self._would_be_consecutive(slot, selected_slots):
                    continue
                
            selected_slots.append(slot)
            daily_sessions[slot.day_of_week] += 1
            
            # 从可用槽中移除
            self.available_slots.discard(slot)
        
        return selected_slots
    
    def solve(self, timeout_seconds: int = 300) -> Dict:
        """执行排课算法
        
        Args:
            timeout_seconds: 算法执行超时时间（秒）
        """
        start_time = time.time()
        self.initialize_available_slots()
        
        # 按优先级排序约束
        sorted_constraints = sorted(self.constraints, key=lambda x: x.priority, reverse=True)
        
        successful_assignments = 0
        failed_assignments = []
        
        for i, constraint in enumerate(sorted_constraints):
            # 检查超时
            if time.time() - start_time > timeout_seconds:
                failed_assignments.extend([{
                    'constraint': c,
                    'assigned_slots': 0,
                    'required_slots': c.sessions_per_week,
                    'reason': '算法执行超时'
                } for c in sorted_constraints[i:]])
                break
                
            try:
                best_slots = self.find_best_slots(constraint)
                
                if len(best_slots) >= constraint.sessions_per_week:
                    self.assigned_slots[constraint] = best_slots
                    # 更新冲突跟踪
                    self._update_conflict_tracking(constraint, best_slots)
                    successful_assignments += 1
                else:
                    failed_assignments.append({
                        'constraint': constraint,
                        'assigned_slots': len(best_slots),
                        'required_slots': constraint.sessions_per_week,
                        'reason': '无法找到足够的合适时间槽'
                    })
                    # 即使部分成功也记录
                    if best_slots:
                        self.assigned_slots[constraint] = best_slots
                        # 更新冲突跟踪
                        self._update_conflict_tracking(constraint, best_slots)
                        
            except Exception as e:
                failed_assignments.append({
                    'constraint': constraint,
                    'assigned_slots': 0,
                    'required_slots': constraint.sessions_per_week,
                    'reason': f'排课失败: {str(e)}'
                })
        
        # 尝试解决失败的分配
        if failed_assignments and time.time() - start_time <= timeout_seconds:
            resolved_assignments = self._attempt_conflict_resolution(failed_assignments, 
                                                                    timeout_seconds - (time.time() - start_time))
            successful_assignments += resolved_assignments

        execution_time = time.time() - start_time
        return {
            'successful_assignments': successful_assignments,
            'failed_assignments': [fa for fa in failed_assignments if fa.get('resolved', False) != True],
            'total_constraints': len(sorted_constraints),
            'success_rate': successful_assignments / len(sorted_constraints) * 100 if sorted_constraints else 0,
            'assigned_slots': self.assigned_slots,
            'optimization_suggestions': self.get_optimization_suggestions(),
            'execution_time': execution_time
        }

    def _attempt_conflict_resolution(self, failed_assignments: List[Dict], timeout_seconds: float = 60) -> int:
        """尝试解决冲突的分配
        
        Args:
            failed_assignments: 失败的分配列表
            timeout_seconds: 解决冲突的超时时间（秒）
        """
        start_time = time.time()
        resolved_count = 0

        for failure in failed_assignments:
            # 检查超时
            if time.time() - start_time > timeout_seconds:
                break
                
            constraint = failure['constraint']

            # 尝试放宽约束条件
            if self._try_relaxed_constraints(constraint):
                failure['resolved'] = True
                resolved_count += 1

        return resolved_count

    def _try_relaxed_constraints(self, constraint: ScheduleConstraint) -> bool:
        """尝试放宽约束条件重新分配"""
        # 备份原始偏好
        original_classrooms = constraint.preferred_classrooms.copy()
        original_time_slots = constraint.preferred_time_slots.copy()
        original_days = constraint.preferred_days.copy()

        try:
            # 放宽教室限制
            if constraint.preferred_classrooms:
                constraint.preferred_classrooms = []
                best_slots = self.find_best_slots(constraint)
                if len(best_slots) >= constraint.sessions_per_week:
                    self.assigned_slots[constraint] = best_slots
                    self._update_conflict_tracking(constraint, best_slots)
                    return True

            # 放宽时间段限制
            if constraint.preferred_time_slots:
                constraint.preferred_time_slots = []
                best_slots = self.find_best_slots(constraint)
                if len(best_slots) >= constraint.sessions_per_week:
                    self.assigned_slots[constraint] = best_slots
                    self._update_conflict_tracking(constraint, best_slots)
                    return True

            # 放宽日期限制
            if constraint.preferred_days:
                constraint.preferred_days = []
                best_slots = self.find_best_slots(constraint)
                if len(best_slots) >= constraint.sessions_per_week:
                    self.assigned_slots[constraint] = best_slots
                    self._update_conflict_tracking(constraint, best_slots)
                    return True

        except Exception:
            pass
        finally:
            # 恢复原始偏好
            constraint.preferred_classrooms = original_classrooms
            constraint.preferred_time_slots = original_time_slots
            constraint.preferred_days = original_days

        return False

    def create_schedules(self) -> List[Schedule]:
        """根据分配结果创建Schedule对象"""
        schedules = []
        
        for constraint, slots in self.assigned_slots.items():
            for slot in slots:
                schedule = Schedule(
                    course=constraint.course,
                    teacher=constraint.teacher,
                    classroom=slot.classroom,
                    time_slot=slot.time_slot,
                    day_of_week=slot.day_of_week,
                    semester=self.semester,
                    academic_year=self.academic_year,
                    week_range="1-18",  # 默认18周
                    status='active'
                )
                schedules.append(schedule)
        
        return schedules
    
    def get_optimization_suggestions(self) -> List[Dict]:
        """获取优化建议"""
        suggestions = []
        
        # 分析教室利用率
        classroom_usage = defaultdict(int)
        for slots in self.assigned_slots.values():
            for slot in slots:
                classroom_usage[slot.classroom.id] += 1
        
        # 找出利用率低的教室
        total_classrooms = len(set(slot.classroom for slots in self.assigned_slots.values() for slot in slots))
        if total_classrooms > 0:
            avg_usage = sum(classroom_usage.values()) / total_classrooms
            for classroom_id, usage in classroom_usage.items():
                if usage < avg_usage * 0.5:
                    suggestions.append({
                        'type': 'classroom_underutilized',
                        'message': f'教室 {classroom_id} 利用率较低，建议调整',
                        'classroom_id': classroom_id,
                        'usage_count': usage
                    })
        
        # 分析时间段分布
        time_slot_usage = defaultdict(int)
        for slots in self.assigned_slots.values():
            for slot in slots:
                time_slot_usage[slot.time_slot.id] += 1
        
        # 建议平衡时间段使用
        if time_slot_usage:
            max_usage = max(time_slot_usage.values())
            min_usage = min(time_slot_usage.values())
            if max_usage > min_usage * 2:
                suggestions.append({
                    'type': 'time_slot_imbalance',
                    'message': '时间段使用不均衡，建议调整课程时间分布',
                    'max_usage': max_usage,
                    'min_usage': min_usage
                })
        
        return suggestions

    def _is_noon_time(self, time_slot: TimeSlot) -> bool:
        """判断是否为中午时间（12:00-13:00）"""
        # 检查时间段是否在中午12点到1点之间
        if (time_slot.start_time.hour == 12 or 
            (time_slot.start_time.hour == 11 and time_slot.end_time.hour >= 12) or
            (time_slot.start_time.hour < 12 and time_slot.end_time.hour > 12)):
            return True
        return False
    
    def _would_be_consecutive(self, new_slot: ScheduleSlot, selected_slots: List[ScheduleSlot]) -> bool:
        """检查新时间槽是否与已选时间槽连续"""
        for slot in selected_slots:
            if slot.day_of_week == new_slot.day_of_week:
                # 检查时间是否连续
                if abs(slot.time_slot.order - new_slot.time_slot.order) == 1:
                    return True
        return False
    
    def _get_all_classrooms(self) -> List[Classroom]:
        """获取所有可用教室"""
        return list(Classroom.objects.filter(is_active=True))
    
    def get_constraint_stats(self) -> Dict:
        """获取约束统计信息"""
        stats = {
            'total_constraints': len(self.constraints),
            'constraints_by_priority': defaultdict(int),
            'constraints_by_type': defaultdict(int),
            'constraints_with_fixed_slots': 0,
            'constraints_with_avoid_consecutive': 0,
            'constraints_with_avoid_noon': 0
        }
        
        for constraint in self.constraints:
            stats['constraints_by_priority'][constraint.priority] += 1
            stats['constraints_by_type'][constraint.course.course_type] += 1
            if constraint.fixed_time_slots:
                stats['constraints_with_fixed_slots'] += 1
            if constraint.avoid_consecutive:
                stats['constraints_with_avoid_consecutive'] += 1
            if constraint.avoid_noon:
                stats['constraints_with_avoid_noon'] += 1
        
        return dict(stats)
        
    def get_resource_utilization(self) -> Dict:
        """获取资源利用率统计"""
        # 教室利用率
        classroom_usage = defaultdict(int)
        for slots in self.assigned_slots.values():
            for slot in slots:
                classroom_usage[slot.classroom.id] += 1
        
        # 教师工作量
        teacher_workload = defaultdict(int)
        for constraint in self.assigned_slots.keys():
            teacher_workload[constraint.teacher.id] += constraint.sessions_per_week
        
        # 时间段分布
        time_slot_distribution = defaultdict(int)
        for slots in self.assigned_slots.values():
            for slot in slots:
                time_slot_distribution[slot.time_slot.id] += 1
        
        return {
            'classroom_usage': dict(classroom_usage),
            'teacher_workload': dict(teacher_workload),
            'time_slot_distribution': dict(time_slot_distribution)
        }


def create_auto_schedule(semester: str, academic_year: str, course_ids: List[int] = None, 
                        algorithm_type: str = 'greedy', timeout_seconds: int = 300) -> Dict:
    """
    自动排课主函数
    
    Args:
        semester: 学期
        academic_year: 学年
        course_ids: 要排课的课程ID列表，如果为None则排所有课程
        algorithm_type: 算法类型 ('greedy', 'genetic', 'hybrid')
        timeout_seconds: 算法执行超时时间（秒）
    
    Returns:
        排课结果字典
    """
    # 根据算法类型选择算法实现
    if algorithm_type == 'genetic':
        try:
            from .genetic_algorithm import GeneticSchedulingAlgorithm
            algorithm = GeneticSchedulingAlgorithm(semester, academic_year)
        except ImportError:
            # 如果遗传算法不可用，回退到贪心算法
            algorithm = SchedulingAlgorithm(semester, academic_year)
    elif algorithm_type == 'hybrid':
        try:
            from .hybrid_algorithm import HybridSchedulingAlgorithm
            algorithm = HybridSchedulingAlgorithm(semester, academic_year)
        except ImportError:
            # 如果混合算法不可用，回退到贪心算法
            algorithm = SchedulingAlgorithm(semester, academic_year)
    else:
        algorithm = SchedulingAlgorithm(semester, academic_year)
    
    # 获取需要排课的课程
    courses_query = Course.objects.filter(
        semester=semester,
        academic_year=academic_year,
        is_active=True,
        is_published=True
    ).select_related().prefetch_related('teachers')
    
    if course_ids:
        courses_query = courses_query.filter(id__in=course_ids)
    
    # 获取可用资源
    available_classrooms = list(Classroom.objects.filter(is_active=True))
    available_time_slots = list(TimeSlot.objects.filter(is_active=True))
    
    # 为每个课程创建约束
    for course in courses_query:
        # 获取课程的主要教师
        main_teacher = course.teachers.first()
        if not main_teacher:
            continue
            
        # 根据课程类型设置偏好
        preferred_classrooms = available_classrooms
        preferred_time_slots = available_time_slots
        preferred_days = list(range(1, 6))  # 周一到周五
        
        # 根据课程类型调整偏好
        if course.course_type == 'lab':
            # 实验课偏好实验室
            preferred_classrooms = [c for c in available_classrooms if c.room_type == 'lab']
        elif course.course_type == 'lecture':
            # 理论课偏好大教室
            preferred_classrooms = [c for c in available_classrooms if c.capacity >= 50]
        
        # 计算每周课时数（简化计算）
        sessions_per_week = min(course.hours // 18, 4)  # 假设18周，最多4次/周
        if sessions_per_week == 0:
            sessions_per_week = 1
        
        constraint = ScheduleConstraint(
            course=course,
            teacher=main_teacher,
            preferred_classrooms=preferred_classrooms,
            preferred_time_slots=preferred_time_slots,
            preferred_days=preferred_days,
            sessions_per_week=sessions_per_week,
            avoid_consecutive=course.course_type == 'lecture',  # 理论课避免连续
            avoid_noon=False,  # 默认不禁用中午时间
            max_daily_sessions=0,  # 默认无每日限制
            priority=3 if course.course_type == 'required' else 2  # 必修课优先级高
        )
        
        algorithm.add_constraint(constraint)
    
    # 执行排课算法
    result = algorithm.solve(timeout_seconds)
    
    # 生成优化建议
    suggestions = algorithm.get_optimization_suggestions()
    
    # 添加约束统计和资源利用率
    constraint_stats = {}
    resource_utilization = {}
    if hasattr(algorithm, 'get_constraint_stats'):
        constraint_stats = algorithm.get_constraint_stats()
    if hasattr(algorithm, 'get_resource_utilization'):
        resource_utilization = algorithm.get_resource_utilization()
    
    # 准备返回结果
    result.update({
        'suggestions': suggestions,
        'algorithm_instance': algorithm,  # 用于后续创建Schedule对象
        'algorithm_type': algorithm_type,
        'constraint_stats': constraint_stats,
        'resource_utilization': resource_utilization
    })
    
    return result
