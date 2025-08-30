# file: algorithms/heuristic/priority_rules.py
# 功能: 优先级规则定义

from typing import List, Dict, Any, Callable
import random


class PriorityRules:
    """优先级规则定义类"""
    
    @staticmethod
    def course_priority_by_difficulty(courses: List[Dict]) -> List[Dict]:
        """按课程难度排序 - 难排的课程优先"""
        def difficulty_score(course: Dict) -> float:
            score = 0.0
            
            # 选课人数多的课程更难排
            max_students = course.get('max_students', 50)
            score += max_students * 0.01
            
            # 必修课比选修课难排
            if course.get('course_type') == 'required':
                score += 10
            
            # 学分高的课程优先
            credits = course.get('credits', 3)
            score += credits * 2
            
            # 有先修课程要求的课程更难排
            prerequisites = course.get('prerequisites', [])
            score += len(prerequisites) * 5
            
            return score
        
        return sorted(courses, key=difficulty_score, reverse=True)
    
    @staticmethod
    def course_priority_by_constraints(courses: List[Dict], teachers: List[Dict], 
                                     classrooms: List[Dict]) -> List[Dict]:
        """按约束紧密度排序 - 约束多的课程优先"""
        def constraint_score(course: Dict) -> float:
            score = 0.0
            
            # 计算可用教师数量（越少越优先）
            qualified_teachers = [t for t in teachers 
                                if course['id'] in t.get('qualified_courses', [])]
            if qualified_teachers:
                score += 100 / len(qualified_teachers)
            else:
                score += 1000  # 没有合格教师的课程最优先
            
            # 计算可用教室数量（越少越优先）
            suitable_classrooms = [c for c in classrooms 
                                 if c.get('capacity', 0) >= course.get('max_students', 0)]
            if suitable_classrooms:
                score += 50 / len(suitable_classrooms)
            else:
                score += 500  # 没有合适教室的课程高优先级
            
            return score
        
        return sorted(courses, key=constraint_score, reverse=True)
    
    @staticmethod
    def course_priority_by_enrollment(courses: List[Dict]) -> List[Dict]:
        """按选课人数排序 - 选课人数多的优先"""
        return sorted(courses, key=lambda c: c.get('max_students', 0), reverse=True)
    
    @staticmethod
    def course_priority_by_type(courses: List[Dict]) -> List[Dict]:
        """按课程类型排序 - 必修课优先"""
        type_priority = {
            'required': 4,      # 必修课
            'professional': 3,  # 专业课
            'public': 2,        # 公共课
            'elective': 1,      # 选修课
        }
        
        def type_score(course: Dict) -> int:
            course_type = course.get('course_type', 'elective')
            return type_priority.get(course_type, 0)
        
        return sorted(courses, key=type_score, reverse=True)
    
    @staticmethod
    def course_priority_hybrid(courses: List[Dict], teachers: List[Dict], 
                             classrooms: List[Dict], weights: Dict[str, float] = None) -> List[Dict]:
        """混合优先级排序"""
        if weights is None:
            weights = {
                'difficulty': 0.3,
                'constraints': 0.3,
                'enrollment': 0.2,
                'type': 0.2,
            }
        
        def hybrid_score(course: Dict) -> float:
            score = 0.0
            
            # 难度评分
            if weights.get('difficulty', 0) > 0:
                max_students = course.get('max_students', 50)
                credits = course.get('credits', 3)
                prerequisites = len(course.get('prerequisites', []))
                difficulty = max_students * 0.01 + credits * 2 + prerequisites * 5
                score += difficulty * weights['difficulty']
            
            # 约束评分
            if weights.get('constraints', 0) > 0:
                qualified_teachers = [t for t in teachers 
                                    if course['id'] in t.get('qualified_courses', [])]
                suitable_classrooms = [c for c in classrooms 
                                     if c.get('capacity', 0) >= course.get('max_students', 0)]
                
                teacher_constraint = 100 / len(qualified_teachers) if qualified_teachers else 1000
                classroom_constraint = 50 / len(suitable_classrooms) if suitable_classrooms else 500
                constraint_score = teacher_constraint + classroom_constraint
                score += constraint_score * weights['constraints']
            
            # 选课人数评分
            if weights.get('enrollment', 0) > 0:
                enrollment = course.get('max_students', 0)
                score += enrollment * weights['enrollment']
            
            # 课程类型评分
            if weights.get('type', 0) > 0:
                type_priority = {
                    'required': 40,
                    'professional': 30,
                    'public': 20,
                    'elective': 10,
                }
                course_type = course.get('course_type', 'elective')
                type_score = type_priority.get(course_type, 0)
                score += type_score * weights['type']
            
            return score
        
        return sorted(courses, key=hybrid_score, reverse=True)
    
    @staticmethod
    def teacher_priority_by_workload(teachers: List[Dict], existing_assignments: List[Any]) -> List[Dict]:
        """按教师工作量排序 - 工作量少的优先"""
        # 计算每个教师的当前工作量
        teacher_workload = {}
        for assignment in existing_assignments:
            teacher_id = assignment.teacher_id
            teacher_workload[teacher_id] = teacher_workload.get(teacher_id, 0) + 1
        
        def workload_score(teacher: Dict) -> int:
            return teacher_workload.get(teacher['id'], 0)
        
        return sorted(teachers, key=workload_score)
    
    @staticmethod
    def teacher_priority_by_preference(teachers: List[Dict], day_of_week: int, 
                                     time_slot: int, teacher_preferences: Dict = None) -> List[Dict]:
        """按教师时间偏好排序 - 偏好高的优先"""
        def preference_score(teacher: Dict) -> float:
            teacher_id = teacher['id']
            
            if teacher_preferences and teacher_id in teacher_preferences:
                prefs = teacher_preferences[teacher_id]
                for pref in prefs:
                    if pref.day_of_week == day_of_week and pref.time_slot == time_slot:
                        return pref.preference_score
            
            # 默认偏好评分
            if 1 <= time_slot <= 4:  # 上午
                return 0.8
            elif 5 <= time_slot <= 8:  # 下午
                return 0.6
            else:  # 晚上
                return 0.4
        
        return sorted(teachers, key=preference_score, reverse=True)
    
    @staticmethod
    def classroom_priority_by_utilization(classrooms: List[Dict], course: Dict,
                                        existing_assignments: List[Any]) -> List[Dict]:
        """按教室利用率排序 - 利用率适中的优先"""
        # 计算每个教室的当前使用次数
        classroom_usage = {}
        for assignment in existing_assignments:
            classroom_id = assignment.classroom_id
            classroom_usage[classroom_id] = classroom_usage.get(classroom_id, 0) + 1
        
        def utilization_score(classroom: Dict) -> float:
            classroom_id = classroom['id']
            capacity = classroom.get('capacity', 100)
            course_students = course.get('max_students', 50)
            usage_count = classroom_usage.get(classroom_id, 0)
            
            # 容量利用率评分
            capacity_utilization = course_students / capacity
            if 0.7 <= capacity_utilization <= 0.9:
                capacity_score = 1.0
            elif capacity_utilization < 0.7:
                capacity_score = capacity_utilization / 0.7
            else:
                capacity_score = max(0.0, 2.0 - capacity_utilization)
            
            # 使用频率评分（使用次数少的优先）
            usage_score = 1.0 / (1.0 + usage_count * 0.1)
            
            return capacity_score * 0.7 + usage_score * 0.3
        
        return sorted(classrooms, key=utilization_score, reverse=True)
    
    @staticmethod
    def time_slot_priority_by_preference(time_slots: List[int], 
                                       teacher_preferences: Dict = None,
                                       teacher_id: int = None) -> List[int]:
        """按时间段偏好排序"""
        def time_preference_score(time_slot: int) -> float:
            if teacher_preferences and teacher_id and teacher_id in teacher_preferences:
                prefs = teacher_preferences[teacher_id]
                for pref in prefs:
                    if pref.time_slot == time_slot:
                        return pref.preference_score
            
            # 默认时间偏好
            if 1 <= time_slot <= 4:  # 上午
                return 0.8
            elif 5 <= time_slot <= 8:  # 下午
                return 0.6
            else:  # 晚上
                return 0.4
        
        return sorted(time_slots, key=time_preference_score, reverse=True)
    
    @staticmethod
    def get_priority_function(rule_name: str) -> Callable:
        """根据规则名称获取优先级函数"""
        rule_map = {
            'difficulty': PriorityRules.course_priority_by_difficulty,
            'constraints': PriorityRules.course_priority_by_constraints,
            'enrollment': PriorityRules.course_priority_by_enrollment,
            'type': PriorityRules.course_priority_by_type,
            'hybrid': PriorityRules.course_priority_hybrid,
        }
        
        return rule_map.get(rule_name, PriorityRules.course_priority_hybrid)
