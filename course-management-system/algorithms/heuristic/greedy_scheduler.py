# file: algorithms/heuristic/greedy_scheduler.py
# 功能: 贪心算法排课器

import logging
import time
from typing import List, Dict, Any, Optional
from ..models import Assignment, ScheduleResult
from ..constraints.manager import ConstraintManager
from .priority_rules import PriorityRules

logger = logging.getLogger(__name__)


class GreedyScheduler:
    """贪心算法排课器"""
    
    def __init__(self, constraint_manager: Optional[ConstraintManager] = None,
                 priority_rule: str = 'hybrid',
                 max_attempts_per_course: int = 100,
                 backtrack_enabled: bool = True,
                 backtrack_depth: int = 3):
        """
        初始化贪心排课器
        
        Args:
            constraint_manager: 约束管理器
            priority_rule: 优先级规则 ('difficulty', 'constraints', 'enrollment', 'type', 'hybrid')
            max_attempts_per_course: 每门课程的最大尝试次数
            backtrack_enabled: 是否启用回溯
            backtrack_depth: 回溯深度
        """
        self.constraint_manager = constraint_manager or ConstraintManager()
        self.priority_rule = priority_rule
        self.max_attempts_per_course = max_attempts_per_course
        self.backtrack_enabled = backtrack_enabled
        self.backtrack_depth = backtrack_depth
        
        # 统计信息
        self.stats = {
            'total_attempts': 0,
            'successful_assignments': 0,
            'failed_assignments': 0,
            'backtrack_count': 0,
            'total_time': 0.0,
        }
    
    def set_data(self, courses: List[Dict], teachers: List[Dict], 
                classrooms: List[Dict], teacher_preferences: List[Any] = None):
        """设置排课数据"""
        self.courses = courses
        self.teachers = teachers
        self.classrooms = classrooms
        
        # 设置约束管理器的数据缓存
        self.constraint_manager.set_data_cache(
            courses, teachers, classrooms, teacher_preferences
        )
        
        logger.info(f"Greedy scheduler data set: {len(courses)} courses, "
                   f"{len(teachers)} teachers, {len(classrooms)} classrooms")
    
    def schedule(self) -> ScheduleResult:
        """执行贪心排课算法"""
        if not hasattr(self, 'courses'):
            raise ValueError("Data not set. Call set_data() first.")
        
        start_time = time.time()
        logger.info("Starting greedy scheduling algorithm")
        
        # 重置统计信息
        self.stats = {
            'total_attempts': 0,
            'successful_assignments': 0,
            'failed_assignments': 0,
            'backtrack_count': 0,
            'total_time': 0.0,
        }
        
        # 按优先级排序课程
        sorted_courses = self._prioritize_courses()
        
        assignments = []
        failed_courses = []
        
        for course in sorted_courses:
            assignment = self._schedule_course(course, assignments)
            
            if assignment:
                assignments.append(assignment)
                self.stats['successful_assignments'] += 1
                logger.debug(f"Successfully scheduled course {course['id']}: {course['name']}")
            else:
                failed_courses.append(course)
                self.stats['failed_assignments'] += 1
                logger.warning(f"Failed to schedule course {course['id']}: {course['name']}")
                
                # 尝试回溯
                if self.backtrack_enabled and len(assignments) > 0:
                    backtrack_result = self._backtrack_and_reschedule(
                        course, assignments, failed_courses
                    )
                    if backtrack_result:
                        assignment, new_assignments = backtrack_result
                        assignments = new_assignments
                        assignments.append(assignment)
                        failed_courses.remove(course)
                        self.stats['successful_assignments'] += 1
                        self.stats['failed_assignments'] -= 1
                        self.stats['backtrack_count'] += 1
                        logger.info(f"Backtrack successful for course {course['id']}")
        
        # 记录统计信息
        self.stats['total_time'] = time.time() - start_time
        
        # 检测冲突
        conflicts = self.constraint_manager.find_conflicts(assignments)
        
        # 计算适应度
        if assignments:
            evaluation = self.constraint_manager.evaluate_schedule(assignments)
            fitness_score = evaluation['overall_fitness']
        else:
            fitness_score = 0.0
        
        result = ScheduleResult(
            assignments=assignments,
            conflicts=conflicts,
            fitness_score=fitness_score,
            algorithm_used='greedy',
            generation_time=self.stats['total_time'],
            metadata={
                'failed_courses': [c['id'] for c in failed_courses],
                'stats': self.stats.copy(),
                'priority_rule': self.priority_rule,
            }
        )
        
        logger.info(f"Greedy scheduling completed: {len(assignments)} assignments, "
                   f"{len(failed_courses)} failed courses, "
                   f"{len(conflicts)} conflicts")
        
        return result
    
    def _prioritize_courses(self) -> List[Dict]:
        """按优先级排序课程"""
        priority_func = PriorityRules.get_priority_function(self.priority_rule)
        
        if self.priority_rule in ['constraints', 'hybrid']:
            return priority_func(self.courses, self.teachers, self.classrooms)
        else:
            return priority_func(self.courses)
    
    def _schedule_course(self, course: Dict, existing_assignments: List[Assignment]) -> Optional[Assignment]:
        """为单门课程安排时间"""
        best_assignment = None
        best_score = -1
        
        # 获取合格的教师
        qualified_teachers = [t for t in self.teachers 
                            if course['id'] in t.get('qualified_courses', [])]
        if not qualified_teachers:
            qualified_teachers = self.teachers  # 如果没有合格教师，使用所有教师
        
        # 获取合适的教室
        suitable_classrooms = [c for c in self.classrooms 
                             if c.get('capacity', 0) >= course.get('max_students', 0)]
        if not suitable_classrooms:
            suitable_classrooms = self.classrooms  # 如果没有合适教室，使用所有教室
        
        # 按优先级排序教师和教室
        qualified_teachers = PriorityRules.teacher_priority_by_workload(
            qualified_teachers, existing_assignments
        )
        suitable_classrooms = PriorityRules.classroom_priority_by_utilization(
            suitable_classrooms, course, existing_assignments
        )
        
        attempts = 0
        
        # 尝试所有可能的组合
        for teacher in qualified_teachers:
            for classroom in suitable_classrooms:
                for day in range(1, 6):  # 周一到周五
                    # 按偏好排序时间段
                    time_slots = list(range(1, 11))  # 10个时间段
                    time_slots = PriorityRules.time_slot_priority_by_preference(
                        time_slots, None, teacher['id']
                    )
                    
                    for time_slot in time_slots:
                        attempts += 1
                        self.stats['total_attempts'] += 1
                        
                        assignment = Assignment(
                            course_id=course['id'],
                            teacher_id=teacher['id'],
                            classroom_id=classroom['id'],
                            day_of_week=day,
                            time_slot=time_slot,
                            semester=course.get('semester', ''),
                            academic_year=course.get('academic_year', ''),
                        )
                        
                        # 检查硬约束
                        if self.constraint_manager.check_hard_constraints(assignment, existing_assignments):
                            # 计算软约束得分
                            score = self.constraint_manager.calculate_soft_score(assignment, existing_assignments)
                            
                            if score > best_score:
                                best_score = score
                                best_assignment = assignment
                                
                                # 如果找到很好的解，提前返回
                                if score >= 0.9:
                                    return best_assignment
                        
                        # 限制尝试次数
                        if attempts >= self.max_attempts_per_course:
                            break
                    
                    if attempts >= self.max_attempts_per_course:
                        break
                
                if attempts >= self.max_attempts_per_course:
                    break
            
            if attempts >= self.max_attempts_per_course:
                break
        
        return best_assignment
    
    def _backtrack_and_reschedule(self, failed_course: Dict, 
                                 current_assignments: List[Assignment],
                                 failed_courses: List[Dict]) -> Optional[tuple]:
        """回溯并重新安排"""
        if len(current_assignments) < self.backtrack_depth:
            return None
        
        # 尝试移除最后几个分配并重新安排
        for depth in range(1, min(self.backtrack_depth + 1, len(current_assignments) + 1)):
            # 保存当前状态
            backup_assignments = current_assignments[:-depth]
            removed_assignments = current_assignments[-depth:]
            
            # 尝试为失败的课程安排时间
            assignment = self._schedule_course(failed_course, backup_assignments)
            
            if assignment:
                # 尝试重新安排被移除的课程
                new_assignments = backup_assignments.copy()
                new_assignments.append(assignment)
                
                all_rescheduled = True
                for removed_assignment in removed_assignments:
                    # 找到对应的课程
                    removed_course = next(
                        (c for c in self.courses if c['id'] == removed_assignment.course_id), 
                        None
                    )
                    
                    if removed_course:
                        rescheduled_assignment = self._schedule_course(removed_course, new_assignments)
                        if rescheduled_assignment:
                            new_assignments.append(rescheduled_assignment)
                        else:
                            all_rescheduled = False
                            break
                
                if all_rescheduled:
                    return assignment, new_assignments
        
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取算法统计信息"""
        return self.stats.copy()
    
    def reset_statistics(self):
        """重置统计信息"""
        self.stats = {
            'total_attempts': 0,
            'successful_assignments': 0,
            'failed_assignments': 0,
            'backtrack_count': 0,
            'total_time': 0.0,
        }
