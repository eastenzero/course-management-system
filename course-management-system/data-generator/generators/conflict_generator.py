# file: data-generator/generators/conflict_generator.py
# 功能: 分级冲突生成模块 - 创造复杂冲突场景以测试算法

import random
import numpy as np
from typing import List, Dict, Any, Tuple, Set
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict
import math


class ConflictSeverity(Enum):
    """冲突严重程度枚举"""
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"


class ConflictType(Enum):
    """冲突类型枚举"""
    TIME_CONFLICT = "time_conflict"
    RESOURCE_COMPETITION = "resource_competition"
    CAPACITY_OVERFLOW = "capacity_overflow"
    TEACHER_OVERLOAD = "teacher_overload"
    PREREQUISITE_VIOLATION = "prerequisite_violation"
    COMPLEX_CHAIN = "complex_chain_conflict"
    CASCADING = "cascading_conflict"


@dataclass
class ConflictScenario:
    """冲突场景定义"""
    conflict_id: str
    conflict_type: ConflictType
    severity: ConflictSeverity
    description: str
    affected_entities: Dict[str, List[int]]  # 受影响的实体ID
    conflict_details: Dict[str, Any]
    resolution_difficulty: float  # 解决难度 0-1
    algorithm_stress_points: List[str]  # 算法压力测试点


class ConflictGeneratorEngine:
    """分级冲突生成引擎
    
    系统性地生成不同复杂度的冲突场景，用于充分测试排课算法的性能
    """
    
    def __init__(self):
        self.conflict_scenarios = []
        self.conflict_counter = 0
        self.setup_conflict_templates()
        
    def setup_conflict_templates(self):
        """设置冲突模板"""
        
        # Level 1: 基础冲突场景 (30%)
        self.basic_conflicts = {
            "simple_time_conflict": {
                "probability": 0.4,
                "description": "简单时间冲突：同一教师同一时间安排多门课程",
                "stress_points": ["时间约束检查", "教师资源分配"]
            },
            "classroom_double_booking": {
                "probability": 0.3,
                "description": "教室重复预定：同一教室同一时间安排多门课程",
                "stress_points": ["空间约束检查", "资源竞争处理"]
            },
            "student_schedule_conflict": {
                "probability": 0.3,
                "description": "学生课表冲突：学生必修课时间重叠",
                "stress_points": ["学生约束验证", "必修课调度"]
            }
        }
        
        # Level 2: 复杂冲突场景 (50%)
        self.complex_conflicts = {
            "resource_competition": {
                "probability": 0.25,
                "description": "资源竞争：热门教师、教室、时间段的多重竞争",
                "stress_points": ["资源优先级", "竞争解决策略", "权衡决策"]
            },
            "capacity_constraints": {
                "probability": 0.25,
                "description": "容量约束：教室容量不足、选课人数超限",
                "stress_points": ["容量计算", "溢出处理", "教室分级"]
            },
            "cross_campus_logistics": {
                "probability": 0.15,
                "description": "跨校区物流：教师在不同校区间通勤时间不足",
                "stress_points": ["空间距离计算", "时间缓冲设计", "路径优化"]
            },
            "prerequisite_chains": {
                "probability": 0.2,
                "description": "先修链冲突：先修课程关系导致的排课约束",
                "stress_points": ["依赖关系验证", "时间序列约束", "课程链调度"]
            },
            "teacher_workload_imbalance": {
                "probability": 0.15,
                "description": "教师负荷不均：部分教师过载而其他教师空闲",
                "stress_points": ["负荷平衡算法", "工作量计算", "公平性保证"]
            }
        }
        
        # Level 3: 极限冲突场景 (20%)
        self.extreme_conflicts = {
            "multi_dimensional_conflict": {
                "probability": 0.3,
                "description": "多维度冲突：同时涉及时间、空间、人员、设备的复合约束",
                "stress_points": ["多约束求解", "复合优化", "约束权重平衡"]
            },
            "cascading_failure": {
                "probability": 0.25,
                "description": "级联失效：一个调整引发多个相关课程的连锁冲突",
                "stress_points": ["影响传播分析", "连锁反应处理", "稳定性保证"]
            },
            "optimization_paradox": {
                "probability": 0.2,
                "description": "优化悖论：满足硬约束但严重违反软约束的两难情况",
                "stress_points": ["硬软约束权衡", "多目标优化", "妥协策略"]
            },
            "resource_deadlock": {
                "probability": 0.15,
                "description": "资源死锁：多个课程相互等待对方释放资源",
                "stress_points": ["死锁检测", "死锁预防", "资源调度"]
            },
            "dynamic_constraint_changes": {
                "probability": 0.1,
                "description": "动态约束变化：排课过程中约束条件发生变化",
                "stress_points": ["动态适应", "增量调整", "实时重排"]
            }
        }

    def generate_conflict_scenarios(self, courses: List[Dict], teachers: List[Dict], 
                                  classrooms: List[Dict], target_difficulty: str = "mixed") -> List[ConflictScenario]:
        """生成分级冲突场景
        
        Args:
            courses: 课程列表
            teachers: 教师列表
            classrooms: 教室列表
            target_difficulty: 目标难度 ("basic", "complex", "extreme", "mixed")
            
        Returns:
            冲突场景列表
        """
        scenarios = []
        
        if target_difficulty == "mixed":
            # 混合难度：30%基础 + 50%复杂 + 20%极限
            basic_count = int(len(courses) * 0.15)  # 15%课程有基础冲突
            complex_count = int(len(courses) * 0.10)  # 10%课程有复杂冲突
            extreme_count = int(len(courses) * 0.05)  # 5%课程有极限冲突
        elif target_difficulty == "basic":
            basic_count = int(len(courses) * 0.20)
            complex_count = 0
            extreme_count = 0
        elif target_difficulty == "complex":
            basic_count = int(len(courses) * 0.10)
            complex_count = int(len(courses) * 0.15)
            extreme_count = 0
        else:  # extreme
            basic_count = 0
            complex_count = int(len(courses) * 0.10)
            extreme_count = int(len(courses) * 0.10)
            
        # 生成基础冲突
        basic_scenarios = self._generate_basic_conflicts(courses, teachers, classrooms, basic_count)
        scenarios.extend(basic_scenarios)
        
        # 生成复杂冲突
        complex_scenarios = self._generate_complex_conflicts(courses, teachers, classrooms, complex_count)
        scenarios.extend(complex_scenarios)
        
        # 生成极限冲突
        extreme_scenarios = self._generate_extreme_conflicts(courses, teachers, classrooms, extreme_count)
        scenarios.extend(extreme_scenarios)
        
        self.conflict_scenarios = scenarios
        return scenarios

    def _generate_basic_conflicts(self, courses: List[Dict], teachers: List[Dict], 
                                classrooms: List[Dict], count: int) -> List[ConflictScenario]:
        """生成基础冲突场景"""
        scenarios = []
        
        for _ in range(count):
            conflict_type = random.choices(
                list(self.basic_conflicts.keys()),
                weights=[info["probability"] for info in self.basic_conflicts.values()]
            )[0]
            
            if conflict_type == "simple_time_conflict":
                scenario = self._create_teacher_time_conflict(courses, teachers)
            elif conflict_type == "classroom_double_booking":
                scenario = self._create_classroom_conflict(courses, classrooms)
            else:  # student_schedule_conflict
                scenario = self._create_student_schedule_conflict(courses)
                
            if scenario:
                scenarios.append(scenario)
                
        return scenarios
        
    def _create_teacher_time_conflict(self, courses: List[Dict], teachers: List[Dict]) -> ConflictScenario:
        """创建教师时间冲突"""
        # 选择一个繁忙的教师
        teacher = random.choice(teachers)
        teacher_courses = [c for c in courses if teacher['id'] in c.get('teacher_ids', [])]
        
        if len(teacher_courses) < 2:
            return None
            
        # 选择2-3门课程制造时间冲突
        conflicted_courses = random.sample(teacher_courses, min(3, len(teacher_courses)))
        
        conflict_id = f"TC{self.conflict_counter:04d}"
        self.conflict_counter += 1
        
        return ConflictScenario(
            conflict_id=conflict_id,
            conflict_type=ConflictType.TIME_CONFLICT,
            severity=ConflictSeverity.LOW,
            description=f"教师{teacher['name']}在同一时间段被分配{len(conflicted_courses)}门课程",
            affected_entities={
                "teachers": [teacher['id']],
                "courses": [c['id'] for c in conflicted_courses]
            },
            conflict_details={
                "teacher_name": teacher['name'],
                "course_names": [c['name'] for c in conflicted_courses],
                "time_slot": "10:00-12:00",  # 假设冲突时间
                "resolution_options": ["调整时间", "分配助教", "课程合并"]
            },
            resolution_difficulty=0.3,
            algorithm_stress_points=self.basic_conflicts["simple_time_conflict"]["stress_points"]
        )

    def _create_classroom_conflict(self, courses: List[Dict], classrooms: List[Dict]) -> ConflictScenario:
        """创建教室冲突"""
        # 选择一个热门教室
        classroom = random.choice(classrooms)
        
        # 选择2-3门需要该教室的课程
        suitable_courses = [c for c in courses if c.get('max_students', 50) <= classroom.get('capacity', 100)]
        if len(suitable_courses) < 2:
            suitable_courses = courses  # 如果筛选后课程不足，使用所有课程
            
        conflicted_courses = random.sample(suitable_courses, min(3, len(suitable_courses)))
        
        conflict_id = f"CC{self.conflict_counter:04d}"
        self.conflict_counter += 1
        
        return ConflictScenario(
            conflict_id=conflict_id,
            conflict_type=ConflictType.RESOURCE_COMPETITION,
            severity=ConflictSeverity.LOW,
            description=f"教室{classroom.get('name', '未知教室')}被{len(conflicted_courses)}门课程同时申请",
            affected_entities={
                "classrooms": [classroom['id']],
                "courses": [c['id'] for c in conflicted_courses]
            },
            conflict_details={
                "classroom_name": classroom.get('name', '未知教室'),
                "classroom_capacity": classroom.get('capacity', 100),
                "course_names": [c['name'] for c in conflicted_courses],
                "total_students": sum(c.get('max_students', 50) for c in conflicted_courses),
                "time_slot": "14:00-16:00"
            },
            resolution_difficulty=0.4,
            algorithm_stress_points=self.basic_conflicts["classroom_double_booking"]["stress_points"]
        )

    def _create_student_schedule_conflict(self, courses: List[Dict]) -> ConflictScenario:
        """创建学生课表冲突"""
        # 选择必修课程
        required_courses = [c for c in courses if c.get('course_type') == '必修']
        if len(required_courses) < 2:
            required_courses = courses[:min(5, len(courses))]  # 如果必修课不足，选择前几门
            
        conflicted_courses = random.sample(required_courses, min(3, len(required_courses)))
        
        conflict_id = f"SC{self.conflict_counter:04d}"
        self.conflict_counter += 1
        
        return ConflictScenario(
            conflict_id=conflict_id,
            conflict_type=ConflictType.TIME_CONFLICT,
            severity=ConflictSeverity.MEDIUM,
            description=f"{len(conflicted_courses)}门必修课程时间冲突，影响学生正常选课",
            affected_entities={
                "courses": [c['id'] for c in conflicted_courses],
                "students": list(range(1, 100))  # 假设影响前100个学生
            },
            conflict_details={
                "course_names": [c['name'] for c in conflicted_courses],
                "course_types": [c.get('course_type', '未知') for c in conflicted_courses],
                "affected_student_count": 100,
                "time_slot": "10:00-12:00"
            },
            resolution_difficulty=0.5,
            algorithm_stress_points=self.basic_conflicts["student_schedule_conflict"]["stress_points"]
        )

    def _generate_complex_conflicts(self, courses: List[Dict], teachers: List[Dict], 
                                  classrooms: List[Dict], count: int) -> List[ConflictScenario]:
        """生成复杂冲突场景"""
        scenarios = []
        
        for _ in range(count):
            conflict_type = random.choices(
                list(self.complex_conflicts.keys()),
                weights=[info["probability"] for info in self.complex_conflicts.values()]
            )[0]
            
            if conflict_type == "resource_competition":
                scenario = self._create_resource_competition_conflict(courses, teachers, classrooms)
            elif conflict_type == "capacity_constraints":
                scenario = self._create_capacity_constraint_conflict(courses, classrooms)
            elif conflict_type == "cross_campus_logistics":
                scenario = self._create_cross_campus_conflict(courses, teachers)
            elif conflict_type == "prerequisite_chains":
                scenario = self._create_prerequisite_chain_conflict(courses)
            else:  # teacher_workload_imbalance
                scenario = self._create_workload_imbalance_conflict(courses, teachers)
                
            if scenario:
                scenarios.append(scenario)
                
        return scenarios

    def _create_resource_competition_conflict(self, courses: List[Dict], teachers: List[Dict], 
                                            classrooms: List[Dict]) -> ConflictScenario:
        """创建资源竞争冲突"""
        # 模拟热门时间段的多重竞争
        peak_time_slot = "10:00-12:00"
        
        # 选择热门教师(假设前20%为热门)
        popular_teachers = teachers[:max(1, len(teachers) // 5)]
        
        # 选择热门教室(容量大的)
        popular_classrooms = sorted(classrooms, key=lambda x: x.get('capacity', 0), reverse=True)[:max(1, len(classrooms) // 3)]
        
        # 选择竞争该时间段的课程
        competing_courses = random.sample(courses, min(8, len(courses) // 4))
        
        conflict_id = f"RC{self.conflict_counter:04d}"
        self.conflict_counter += 1
        
        competition_intensity = len(competing_courses) / max(len(popular_teachers), len(popular_classrooms))
        
        return ConflictScenario(
            conflict_id=conflict_id,
            conflict_type=ConflictType.RESOURCE_COMPETITION,
            severity=ConflictSeverity.HIGH if competition_intensity > 2 else ConflictSeverity.MEDIUM,
            description=f"{len(competing_courses)}门课程竞争{len(popular_teachers)}名热门教师和{len(popular_classrooms)}间热门教室",
            affected_entities={
                "courses": [c['id'] for c in competing_courses],
                "teachers": [t['id'] for t in popular_teachers],
                "classrooms": [c['id'] for c in popular_classrooms]
            },
            conflict_details={
                "time_slot": peak_time_slot,
                "competition_intensity": round(competition_intensity, 2),
                "resource_shortage": {
                    "teachers": max(0, len(competing_courses) - len(popular_teachers)),
                    "classrooms": max(0, len(competing_courses) - len(popular_classrooms))
                },
                "course_priorities": [c.get('popularity_score', 50) for c in competing_courses]
            },
            resolution_difficulty=0.7,
            algorithm_stress_points=self.complex_conflicts["resource_competition"]["stress_points"]
        )

    def _create_capacity_constraint_conflict(self, courses: List[Dict], classrooms: List[Dict]) -> ConflictScenario:
        """创建容量约束冲突"""
        # 选择大班课程
        large_courses = [c for c in courses if c.get('max_students', 50) > 80]
        if not large_courses:
            large_courses = sorted(courses, key=lambda x: x.get('max_students', 50), reverse=True)[:3]
            
        # 选择容量不足的教室
        small_classrooms = [c for c in classrooms if c.get('capacity', 100) < 100]
        if not small_classrooms:
            small_classrooms = classrooms[:len(classrooms)//2]
            
        selected_courses = large_courses[:min(5, len(large_courses))]
        total_student_demand = sum(c.get('max_students', 50) for c in selected_courses)
        total_classroom_capacity = sum(c.get('capacity', 100) for c in small_classrooms)
        
        conflict_id = f"CAP{self.conflict_counter:04d}"
        self.conflict_counter += 1
        
        overflow_ratio = total_student_demand / max(total_classroom_capacity, 1)
        
        return ConflictScenario(
            conflict_id=conflict_id,
            conflict_type=ConflictType.CAPACITY_OVERFLOW,
            severity=ConflictSeverity.HIGH if overflow_ratio > 1.5 else ConflictSeverity.MEDIUM,
            description=f"容量需求溢出：{total_student_demand}学生需求超过{total_classroom_capacity}座位容量",
            affected_entities={
                "courses": [c['id'] for c in selected_courses],
                "classrooms": [c['id'] for c in small_classrooms]
            },
            conflict_details={
                "student_demand": total_student_demand,
                "classroom_capacity": total_classroom_capacity,
                "overflow_ratio": round(overflow_ratio, 2),
                "course_sizes": [c.get('max_students', 50) for c in selected_courses],
                "classroom_capacities": [c.get('capacity', 100) for c in small_classrooms]
            },
            resolution_difficulty=0.6,
            algorithm_stress_points=self.complex_conflicts["capacity_constraints"]["stress_points"]
        )

    def _generate_extreme_conflicts(self, courses: List[Dict], teachers: List[Dict], 
                                  classrooms: List[Dict], count: int) -> List[ConflictScenario]:
        """生成极限冲突场景"""
        scenarios = []
        
        for _ in range(count):
            conflict_type = random.choices(
                list(self.extreme_conflicts.keys()),
                weights=[info["probability"] for info in self.extreme_conflicts.values()]
            )[0]
            
            if conflict_type == "multi_dimensional_conflict":
                scenario = self._create_multi_dimensional_conflict(courses, teachers, classrooms)
            elif conflict_type == "cascading_failure":
                scenario = self._create_cascading_conflict(courses, teachers)
            elif conflict_type == "optimization_paradox":
                scenario = self._create_optimization_paradox(courses, teachers, classrooms)
            elif conflict_type == "resource_deadlock":
                scenario = self._create_deadlock_scenario(courses, teachers, classrooms)
            else:  # dynamic_constraint_changes
                scenario = self._create_dynamic_constraint_scenario(courses)
                
            if scenario:
                scenarios.append(scenario)
                
        return scenarios

    def _create_multi_dimensional_conflict(self, courses: List[Dict], teachers: List[Dict], 
                                         classrooms: List[Dict]) -> ConflictScenario:
        """创建多维度复合冲突"""
        # 选择一组相互关联的课程
        core_courses = random.sample(courses, min(6, len(courses) // 3))
        
        # 创建复合约束条件
        constraints = {
            "time_constraints": ["所有课程必须在工作日安排", "不能安排在周五下午"],
            "teacher_constraints": ["每位教师最多连续2小时授课", "教授不能安排晚课"],
            "classroom_constraints": ["实验课必须在实验室", "大班课需要阶梯教室"],
            "student_constraints": ["同专业学生不能有课程冲突", "必修课优先级最高"],
            "equipment_constraints": ["需要特殊设备的课程受限", "多媒体设备数量有限"]
        }
        
        conflict_id = f"MDC{self.conflict_counter:04d}"
        self.conflict_counter += 1
        
        return ConflictScenario(
            conflict_id=conflict_id,
            conflict_type=ConflictType.COMPLEX_CHAIN,
            severity=ConflictSeverity.CRITICAL,
            description=f"多维度复合冲突：{len(core_courses)}门课程涉及时间、空间、人员、设备多重约束",
            affected_entities={
                "courses": [c['id'] for c in core_courses],
                "teachers": [t['id'] for t in teachers[:len(core_courses)]],
                "classrooms": [c['id'] for c in classrooms[:len(core_courses)]]
            },
            conflict_details={
                "constraint_types": list(constraints.keys()),
                "constraint_count": len(constraints),
                "course_interdependencies": self._generate_course_interdependencies(core_courses),
                "complexity_score": len(constraints) * len(core_courses) / 10
            },
            resolution_difficulty=0.9,
            algorithm_stress_points=self.extreme_conflicts["multi_dimensional_conflict"]["stress_points"]
        )

    def _create_cascading_conflict(self, courses: List[Dict], teachers: List[Dict]) -> ConflictScenario:
        """创建级联冲突"""
        # 选择一个核心课程作为触发点
        trigger_course = random.choice(courses)
        
        # 模拟级联影响的课程链
        cascade_chain = [trigger_course]
        current_course = trigger_course
        
        for _ in range(random.randint(3, 6)):
            # 寻找与当前课程有关联的课程
            related_courses = [c for c in courses 
                             if (c['id'] != current_course['id'] and
                                 (c.get('department_id') == current_course.get('department_id') or
                                  any(teacher_id in current_course.get('teacher_ids', []) 
                                      for teacher_id in c.get('teacher_ids', []))))]
            
            if related_courses:
                next_course = random.choice(related_courses)
                cascade_chain.append(next_course)
                current_course = next_course
            else:
                break
                
        conflict_id = f"CAS{self.conflict_counter:04d}"
        self.conflict_counter += 1
        
        return ConflictScenario(
            conflict_id=conflict_id,
            conflict_type=ConflictType.CASCADING,
            severity=ConflictSeverity.CRITICAL,
            description=f"级联冲突：调整{trigger_course['name']}引发{len(cascade_chain)-1}门相关课程的连锁反应",
            affected_entities={
                "courses": [c['id'] for c in cascade_chain],
                "teachers": list(set(tid for c in cascade_chain for tid in c.get('teacher_ids', [])))
            },
            conflict_details={
                "trigger_course": trigger_course['name'],
                "cascade_length": len(cascade_chain),
                "propagation_path": [c['name'] for c in cascade_chain],
                "impact_radius": len(set(c.get('department_id') for c in cascade_chain))
            },
            resolution_difficulty=0.85,
            algorithm_stress_points=self.extreme_conflicts["cascading_failure"]["stress_points"]
        )

    def generate_conflict_statistics(self) -> Dict[str, Any]:
        """生成冲突统计信息"""
        if not self.conflict_scenarios:
            return {}
            
        stats = {
            "total_conflicts": len(self.conflict_scenarios),
            "severity_distribution": {},
            "type_distribution": {},
            "difficulty_distribution": {},
            "algorithm_stress_coverage": set()
        }
        
        # 统计严重程度分布
        for scenario in self.conflict_scenarios:
            severity = scenario.severity.value
            stats["severity_distribution"][severity] = stats["severity_distribution"].get(severity, 0) + 1
            
            # 统计类型分布
            conflict_type = scenario.conflict_type.value
            stats["type_distribution"][conflict_type] = stats["type_distribution"].get(conflict_type, 0) + 1
            
            # 收集算法压力测试点
            stats["algorithm_stress_coverage"].update(scenario.algorithm_stress_points)
            
        # 计算难度分布
        for scenario in self.conflict_scenarios:
            difficulty = scenario.resolution_difficulty
            if difficulty < 0.3:
                level = "easy"
            elif difficulty < 0.6:
                level = "medium"
            elif difficulty < 0.8:
                level = "hard"
            else:
                level = "extreme"
            stats["difficulty_distribution"][level] = stats["difficulty_distribution"].get(level, 0) + 1
            
        stats["algorithm_stress_coverage"] = list(stats["algorithm_stress_coverage"])
        
        return stats

    def _generate_course_interdependencies(self, courses: List[Dict]) -> List[Dict]:
        """生成课程间的相互依赖关系"""
        dependencies = []
        
        for i, course1 in enumerate(courses):
            for j, course2 in enumerate(courses[i+1:], i+1):
                # 随机生成依赖关系
                if random.random() < 0.3:  # 30%概率有依赖
                    dep_type = random.choice(["时间依赖", "资源依赖", "逻辑依赖"])
                    dependencies.append({
                        "course1": course1['name'],
                        "course2": course2['name'], 
                        "dependency_type": dep_type,
                        "strength": random.uniform(0.3, 0.9)
                    })
                    
        return dependencies

    def export_conflict_scenarios(self, output_file: str):
        """导出冲突场景到文件"""
        import json
        
        export_data = {
            "metadata": {
                "total_scenarios": len(self.conflict_scenarios),
                "generation_timestamp": "2024-08-30",
                "version": "1.0"
            },
            "statistics": self.generate_conflict_statistics(),
            "scenarios": []
        }
        
        for scenario in self.conflict_scenarios:
            scenario_data = {
                "conflict_id": scenario.conflict_id,
                "conflict_type": scenario.conflict_type.value,
                "severity": scenario.severity.value,
                "description": scenario.description,
                "affected_entities": scenario.affected_entities,
                "conflict_details": scenario.conflict_details,
                "resolution_difficulty": scenario.resolution_difficulty,
                "algorithm_stress_points": scenario.algorithm_stress_points
            }
            export_data["scenarios"].append(scenario_data)
            
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)