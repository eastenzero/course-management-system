# file: algorithms/conflict/detector.py
# 功能: 冲突检测器

import logging
from typing import List, Dict, Set, Any
from collections import defaultdict
from ..models import Assignment, Conflict

logger = logging.getLogger(__name__)


class ConflictDetector:
    """冲突检测器"""
    
    def __init__(self):
        self.detected_conflicts = []
        self.conflict_cache = {}
        
        # 统计信息
        self.stats = {
            'total_checks': 0,
            'conflicts_found': 0,
            'teacher_conflicts': 0,
            'classroom_conflicts': 0,
            'capacity_conflicts': 0,
            'other_conflicts': 0,
        }
    
    def detect_all_conflicts(self, assignments: List[Assignment],
                           courses: List[Dict] = None,
                           teachers: List[Dict] = None,
                           classrooms: List[Dict] = None) -> List[Conflict]:
        """检测所有类型的冲突"""
        self.stats['total_checks'] += 1
        conflicts = []
        
        # 教师时间冲突
        teacher_conflicts = self.detect_teacher_conflicts(assignments)
        conflicts.extend(teacher_conflicts)
        self.stats['teacher_conflicts'] += len(teacher_conflicts)
        
        # 教室时间冲突
        classroom_conflicts = self.detect_classroom_conflicts(assignments)
        conflicts.extend(classroom_conflicts)
        self.stats['classroom_conflicts'] += len(classroom_conflicts)
        
        # 教室容量冲突
        if courses and classrooms:
            capacity_conflicts = self.detect_capacity_conflicts(assignments, courses, classrooms)
            conflicts.extend(capacity_conflicts)
            self.stats['capacity_conflicts'] += len(capacity_conflicts)
        
        # 教师资格冲突
        if courses and teachers:
            qualification_conflicts = self.detect_qualification_conflicts(assignments, courses, teachers)
            conflicts.extend(qualification_conflicts)
            self.stats['other_conflicts'] += len(qualification_conflicts)
        
        # 学生课程冲突（如果有学生选课数据）
        # student_conflicts = self.detect_student_conflicts(assignments, enrollments)
        # conflicts.extend(student_conflicts)
        
        self.stats['conflicts_found'] += len(conflicts)
        self.detected_conflicts = conflicts
        
        logger.info(f"Conflict detection completed: {len(conflicts)} conflicts found")
        return conflicts
    
    def detect_teacher_conflicts(self, assignments: List[Assignment]) -> List[Conflict]:
        """检测教师时间冲突"""
        conflicts = []
        teacher_schedule = defaultdict(list)
        
        # 按教师和时间分组
        for assignment in assignments:
            key = (assignment.teacher_id, assignment.day_of_week, assignment.time_slot)
            teacher_schedule[key].append(assignment)
        
        # 检查冲突
        for (teacher_id, day, time_slot), assignment_list in teacher_schedule.items():
            if len(assignment_list) > 1:
                conflict = Conflict(
                    conflict_type='teacher_time',
                    assignments=assignment_list,
                    description=f"教师 {teacher_id} 在 周{day} 第{time_slot}节 有时间冲突",
                    severity='high'
                )
                conflicts.append(conflict)
        
        return conflicts
    
    def detect_classroom_conflicts(self, assignments: List[Assignment]) -> List[Conflict]:
        """检测教室时间冲突"""
        conflicts = []
        classroom_schedule = defaultdict(list)
        
        # 按教室和时间分组
        for assignment in assignments:
            key = (assignment.classroom_id, assignment.day_of_week, assignment.time_slot)
            classroom_schedule[key].append(assignment)
        
        # 检查冲突
        for (classroom_id, day, time_slot), assignment_list in classroom_schedule.items():
            if len(assignment_list) > 1:
                conflict = Conflict(
                    conflict_type='classroom_time',
                    assignments=assignment_list,
                    description=f"教室 {classroom_id} 在 周{day} 第{time_slot}节 有时间冲突",
                    severity='high'
                )
                conflicts.append(conflict)
        
        return conflicts
    
    def detect_capacity_conflicts(self, assignments: List[Assignment],
                                courses: List[Dict], classrooms: List[Dict]) -> List[Conflict]:
        """检测教室容量冲突"""
        conflicts = []
        
        # 创建查找字典
        course_dict = {c['id']: c for c in courses}
        classroom_dict = {c['id']: c for c in classrooms}
        
        for assignment in assignments:
            course = course_dict.get(assignment.course_id)
            classroom = classroom_dict.get(assignment.classroom_id)
            
            if course and classroom:
                required_capacity = course.get('max_students', 0)
                available_capacity = classroom.get('capacity', 0)
                
                if required_capacity > available_capacity:
                    conflict = Conflict(
                        conflict_type='classroom_capacity',
                        assignments=[assignment],
                        description=f"教室 {assignment.classroom_id} 容量不足: "
                                  f"需要 {required_capacity} 人，只有 {available_capacity} 人",
                        severity='high'
                    )
                    conflicts.append(conflict)
        
        return conflicts
    
    def detect_qualification_conflicts(self, assignments: List[Assignment],
                                     courses: List[Dict], teachers: List[Dict]) -> List[Conflict]:
        """检测教师资格冲突"""
        conflicts = []
        
        # 创建查找字典
        course_dict = {c['id']: c for c in courses}
        teacher_dict = {t['id']: t for t in teachers}
        
        for assignment in assignments:
            course = course_dict.get(assignment.course_id)
            teacher = teacher_dict.get(assignment.teacher_id)
            
            if course and teacher:
                qualified_courses = teacher.get('qualified_courses', [])
                
                if assignment.course_id not in qualified_courses:
                    conflict = Conflict(
                        conflict_type='teacher_qualification',
                        assignments=[assignment],
                        description=f"教师 {assignment.teacher_id} 不具备教授课程 {assignment.course_id} 的资格",
                        severity='medium'
                    )
                    conflicts.append(conflict)
        
        return conflicts
    
    def detect_student_conflicts(self, assignments: List[Assignment],
                               enrollments: List[Dict]) -> List[Conflict]:
        """检测学生课程冲突"""
        conflicts = []
        
        # 按学生分组选课记录
        student_courses = defaultdict(list)
        for enrollment in enrollments:
            if enrollment.get('is_active', True):
                student_courses[enrollment['student_id']].append(enrollment['course_id'])
        
        # 检查学生的课程时间冲突
        for student_id, course_ids in student_courses.items():
            student_assignments = [a for a in assignments if a.course_id in course_ids]
            
            # 按时间分组
            time_groups = defaultdict(list)
            for assignment in student_assignments:
                key = (assignment.day_of_week, assignment.time_slot)
                time_groups[key].append(assignment)
            
            # 检查时间冲突
            for (day, time_slot), assignment_list in time_groups.items():
                if len(assignment_list) > 1:
                    conflict = Conflict(
                        conflict_type='student_course',
                        assignments=assignment_list,
                        description=f"学生 {student_id} 在 周{day} 第{time_slot}节 有课程冲突",
                        severity='high'
                    )
                    conflicts.append(conflict)
        
        return conflicts
    
    def detect_workload_conflicts(self, assignments: List[Assignment],
                                teachers: List[Dict]) -> List[Conflict]:
        """检测教师工作量冲突"""
        conflicts = []
        teacher_dict = {t['id']: t for t in teachers}
        
        # 计算每个教师的工作量
        teacher_workload = defaultdict(int)
        for assignment in assignments:
            teacher_workload[assignment.teacher_id] += 1
        
        # 检查工作量超限
        for teacher_id, workload in teacher_workload.items():
            teacher = teacher_dict.get(teacher_id)
            if teacher:
                max_hours = teacher.get('max_weekly_hours', 20)
                if workload > max_hours:
                    # 找到该教师的所有分配
                    teacher_assignments = [a for a in assignments if a.teacher_id == teacher_id]
                    
                    conflict = Conflict(
                        conflict_type='teacher_workload',
                        assignments=teacher_assignments,
                        description=f"教师 {teacher_id} 工作量超限: {workload} > {max_hours}",
                        severity='medium'
                    )
                    conflicts.append(conflict)
        
        return conflicts
    
    def detect_time_preference_conflicts(self, assignments: List[Assignment],
                                       teacher_preferences: List[Any]) -> List[Conflict]:
        """检测教师时间偏好冲突"""
        conflicts = []
        
        # 按教师分组偏好
        teacher_prefs = defaultdict(list)
        for pref in teacher_preferences:
            teacher_prefs[pref.teacher_id].append(pref)
        
        for assignment in assignments:
            teacher_id = assignment.teacher_id
            day_of_week = assignment.day_of_week
            time_slot = assignment.time_slot
            
            # 查找对应的偏好
            prefs = teacher_prefs.get(teacher_id, [])
            for pref in prefs:
                if (pref.day_of_week == day_of_week and 
                    pref.time_slot == time_slot and
                    not pref.is_available):
                    
                    conflict = Conflict(
                        conflict_type='teacher_preference',
                        assignments=[assignment],
                        description=f"教师 {teacher_id} 在 周{day_of_week} 第{time_slot}节 不可用",
                        severity='low'
                    )
                    conflicts.append(conflict)
                    break
        
        return conflicts
    
    def get_conflict_summary(self) -> Dict[str, Any]:
        """获取冲突摘要"""
        conflict_types = defaultdict(int)
        severity_counts = defaultdict(int)
        
        for conflict in self.detected_conflicts:
            conflict_types[conflict.conflict_type] += 1
            severity_counts[conflict.severity] += 1
        
        return {
            'total_conflicts': len(self.detected_conflicts),
            'conflict_types': dict(conflict_types),
            'severity_counts': dict(severity_counts),
            'stats': self.stats.copy(),
        }
    
    def get_conflicts_by_type(self, conflict_type: str) -> List[Conflict]:
        """按类型获取冲突"""
        return [c for c in self.detected_conflicts if c.conflict_type == conflict_type]
    
    def get_conflicts_by_severity(self, severity: str) -> List[Conflict]:
        """按严重性获取冲突"""
        return [c for c in self.detected_conflicts if c.severity == severity]
    
    def clear_cache(self):
        """清除缓存"""
        self.conflict_cache.clear()
        self.detected_conflicts.clear()
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.stats.copy()
    
    def reset_statistics(self):
        """重置统计信息"""
        self.stats = {
            'total_checks': 0,
            'conflicts_found': 0,
            'teacher_conflicts': 0,
            'classroom_conflicts': 0,
            'capacity_conflicts': 0,
            'other_conflicts': 0,
        }
