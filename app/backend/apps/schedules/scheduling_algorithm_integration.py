"""
排课算法集成模块
提供统一的接口来运行和管理不同的排课算法
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from django.utils import timezone
from django.db import transaction

from .algorithms import SchedulingAlgorithm, ScheduleConstraint, create_auto_schedule
from .genetic_algorithm import GeneticSchedulingAlgorithm, create_genetic_schedule
from .hybrid_algorithm import HybridSchedulingAlgorithm
from .models import Schedule, TimeSlot
from apps.courses.models import Course
from apps.classrooms.models import Classroom
from apps.users.models import User

logger = logging.getLogger(__name__)


class SchedulingAlgorithmIntegration:
    """排课算法集成类"""
    
    def __init__(self):
        self.semester = ""
        self.academic_year = ""
        self.course_filter_ids = []
        self.teacher_filter_ids = []
        self.custom_constraints = {}
        self.algorithm_results = {}
    
    def run_scheduling_algorithm(self, algorithm_type: str = 'greedy') -> Dict:
        """
        运行指定的排课算法
        
        Args:
            algorithm_type: 算法类型 ('greedy', 'genetic', 'hybrid')
            
        Returns:
            排课结果字典
        """
        if not self.semester or not self.academic_year:
            raise ValueError("学期和学年信息不能为空")
        
        logger.info(f"开始运行{algorithm_type}排课算法")
        
        try:
            # 根据算法类型选择不同的实现
            if algorithm_type == 'genetic':
                result = create_genetic_schedule(
                    semester=self.semester,
                    academic_year=self.academic_year,
                    course_ids=self.course_filter_ids if self.course_filter_ids else None
                )
            elif algorithm_type == 'hybrid':
                # 创建混合算法实例
                algorithm = HybridSchedulingAlgorithm(
                    semester=self.semester,
                    academic_year=self.academic_year
                )
                result = self._run_hybrid_algorithm(algorithm)
            else:
                # 默认使用贪心算法
                result = create_auto_schedule(
                    semester=self.semester,
                    academic_year=self.academic_year,
                    course_ids=self.course_filter_ids if self.course_filter_ids else None,
                    algorithm_type='greedy'
                )
            
            # 保存结果
            self.algorithm_results[algorithm_type] = result
            
            # 添加时间戳
            result['timestamp'] = str(timezone.now())
            
            logger.info(f"{algorithm_type}算法运行完成")
            return result
            
        except Exception as e:
            logger.exception(f"运行{algorithm_type}算法时发生错误: {e}")
            raise
    
    def _run_hybrid_algorithm(self, algorithm: HybridSchedulingAlgorithm) -> Dict:
        """
        运行混合算法
        
        Args:
            algorithm: 混合算法实例
            
        Returns:
            排课结果字典
        """
        # 获取需要排课的课程
        courses_query = Course.objects.filter(
            semester=self.semester,
            academic_year=self.academic_year,
            is_active=True,
            is_published=True
        ).select_related().prefetch_related('teachers')
        
        if self.course_filter_ids:
            courses_query = courses_query.filter(id__in=self.course_filter_ids)
        
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
        result = algorithm.solve()
        
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
            'algorithm_type': 'hybrid',
            'constraint_stats': constraint_stats,
            'resource_utilization': resource_utilization
        })
        
        return result
    
    def apply_scheduling_results(self, scheduling_result: Dict) -> bool:
        """
        将排课结果应用到系统中
        
        Args:
            scheduling_result: 排课结果数据
            
        Returns:
            是否成功应用
        """
        try:
            with transaction.atomic():
                # 获取学期信息
                semester = scheduling_result.get('semester', self.semester)
                academic_year = scheduling_result.get('academic_year', self.academic_year)
                
                # 获取分配结果
                assigned_slots = scheduling_result.get('assignments', {})
                if not assigned_slots:
                    assigned_slots = scheduling_result.get('assigned_slots', {})
                
                # 如果没有分配结果，尝试从算法实例获取
                if not assigned_slots and 'algorithm_instance' in scheduling_result:
                    algorithm = scheduling_result['algorithm_instance']
                    if hasattr(algorithm, 'assigned_slots'):
                        assigned_slots = algorithm.assigned_slots
                
                # 创建Schedule对象
                schedules_to_create = []
                
                # 处理每个约束的分配结果
                if isinstance(assigned_slots, dict):
                    for constraint, slots in assigned_slots.items():
                        for slot in slots:
                            # 创建Schedule对象
                            schedule = Schedule(
                                course=constraint.course,
                                teacher=constraint.teacher,
                                classroom=slot.classroom,
                                time_slot=slot.time_slot,
                                day_of_week=slot.day_of_week,
                                semester=semester,
                                academic_year=academic_year,
                                week_range="1-18",  # 默认18周
                                status='active'
                            )
                            schedules_to_create.append(schedule)
                
                # 批量创建Schedule对象
                if schedules_to_create:
                    Schedule.objects.bulk_create(schedules_to_create)
                    logger.info(f"成功创建了 {len(schedules_to_create)} 个课程安排")
                
                return True
                
        except Exception as e:
            logger.exception(f"应用排课结果时发生错误: {e}")
            return False
    
    def generate_scheduling_report(self, result: Dict) -> Dict:
        """
        生成排课报告
        
        Args:
            result: 排课算法结果
            
        Returns:
            排课报告字典
        """
        report = {
            'summary': {
                'total_constraints': result.get('total_constraints', 0),
                'successful_assignments': result.get('successful_assignments', 0),
                'success_rate': result.get('success_rate', 0),
                'failed_assignments': len(result.get('failed_assignments', [])),
                'execution_time': result.get('execution_time', 0),
                'algorithm_type': result.get('algorithm_type', 'unknown')
            },
            'constraints': result.get('constraint_stats', {}),
            'resources': result.get('resource_utilization', {}),
            'suggestions': result.get('suggestions', []),
            'timestamp': result.get('timestamp', str(datetime.now()))
        }
        
        return report
    
    def get_algorithm_comparison(self) -> Dict:
        """
        获取不同算法的对比结果
        
        Returns:
            算法对比结果字典
        """
        comparison = {}
        
        for algorithm_type, result in self.algorithm_results.items():
            comparison[algorithm_type] = {
                'success_rate': result.get('success_rate', 0),
                'execution_time': result.get('execution_time', 0),
                'successful_assignments': result.get('successful_assignments', 0),
                'total_constraints': result.get('total_constraints', 0)
            }
        
        return comparison


# 辅助函数
def format_constraint_for_api(constraint: ScheduleConstraint) -> Dict:
    """格式化约束用于API响应"""
    return {
        'course_id': constraint.course.id,
        'course_name': constraint.course.name,
        'teacher_id': constraint.teacher.id,
        'teacher_name': constraint.teacher.get_full_name() or constraint.teacher.username,
        'preferred_classrooms': [c.id for c in constraint.preferred_classrooms],
        'preferred_time_slots': [t.id for t in constraint.preferred_time_slots],
        'preferred_days': constraint.preferred_days,
        'sessions_per_week': constraint.sessions_per_week,
        'priority': constraint.priority
    }


def format_slot_for_api(slot) -> Dict:
    """格式化时间槽用于API响应"""
    return {
        'day_of_week': slot.day_of_week,
        'time_slot_id': slot.time_slot.id,
        'time_slot_name': slot.time_slot.name,
        'classroom_id': slot.classroom.id,
        'classroom_name': str(slot.classroom)
    }