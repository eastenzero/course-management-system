# file: data-generator/generators/constraint_aware_generator.py
# 功能: 约束感知的课程数据生成器

from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import random
import logging
from datetime import datetime, time, timedelta
import networkx as nx

from course_scheduling_constraints import (
    CourseSchedulingConstraints, TimeSlot, CourseType, 
    DifficultyLevel, TeacherTitle, CourseRealismValidator
)
from prerequisite_logic import (
    DependencyGraph, CourseNode, PrerequisitePatternGenerator,
    SemesterPlanningLogic, build_realistic_curriculum
)
from teacher_course_matching import (
    TeacherProfile, CourseProfile, TeacherCourseMatchingEngine,
    generate_realistic_teacher_profiles
)


class GenerationMode(Enum):
    """生成模式"""
    CONSERVATIVE = "保守模式"     # 严格遵循所有约束
    BALANCED = "平衡模式"        # 平衡约束和多样性
    FLEXIBLE = "灵活模式"        # 允许适度违反软约束
    STRESS_TEST = "压力测试"     # 生成边界情况


@dataclass
class GenerationConfig:
    """生成配置"""
    # 规模配置
    target_students: int = 100000
    target_teachers: int = 5000
    target_courses: int = 10000
    target_schedules: int = 500000
    
    # 约束配置
    enable_prerequisite_constraints: bool = True
    enable_time_conflict_detection: bool = True
    enable_capacity_constraints: bool = True
    enable_teacher_workload_limits: bool = True
    
    # 真实性配置
    realism_level: float = 0.8  # 0-1，真实性要求等级
    constraint_strictness: float = 0.9  # 0-1，约束严格程度
    
    # 分布配置
    semester_count: int = 8
    departments: List[str] = field(default_factory=lambda: [
        '计算机科学与技术学院', '数学与统计学院', '物理与电子学院',
        '外国语学院', '经济管理学院', '机械工程学院'
    ])
    
    # 性能配置
    batch_size: int = 5000
    validation_sampling_rate: float = 0.1
    
    # 模式配置
    generation_mode: GenerationMode = GenerationMode.BALANCED


class ConstraintAwareCourseGenerator:
    """约束感知课程生成器"""
    
    def __init__(self, config: GenerationConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 初始化组件
        self.constraints = CourseSchedulingConstraints()
        self.realism_validator = CourseRealismValidator()
        self.pattern_generator = PrerequisitePatternGenerator()
        self.semester_planner = SemesterPlanningLogic(config.semester_count)
        self.matching_engine = TeacherCourseMatchingEngine()
        
        # 数据存储
        self.dependency_graph = DependencyGraph()
        self.teachers: List[TeacherProfile] = []
        self.courses: List[CourseProfile] = []
        self.schedules: List[Dict] = []
        
        # 约束验证计数器
        self.constraint_violations = {
            'prerequisite': 0,
            'time_conflict': 0,
            'capacity': 0,
            'workload': 0,
            'realism': 0
        }
        
    def generate_complete_dataset(self) -> Dict[str, Any]:
        """生成完整的约束感知数据集"""
        self.logger.info(f"开始生成约束感知数据集 - 模式: {self.config.generation_mode.value}")
        
        try:
            # 第一阶段：生成基础数据
            self._generate_departments_and_majors()
            self._generate_teacher_profiles()
            self._generate_course_curriculum()
            
            # 第二阶段：建立关系和约束
            self._build_prerequisite_relationships()
            self._assign_teachers_to_courses()
            
            # 第三阶段：生成排课数据
            self._generate_schedule_data()
            
            # 第四阶段：验证和优化
            self._validate_constraints()
            self._optimize_data_quality()
            
            # 生成报告
            report = self._generate_quality_report()
            
            return {
                'teachers': [self._teacher_to_dict(t) for t in self.teachers],
                'courses': [self._course_to_dict(c) for c in self.courses],
                'schedules': self.schedules,
                'prerequisites': self._extract_prerequisites(),
                'quality_report': report,
                'constraint_violations': self.constraint_violations
            }
            
        except Exception as e:
            self.logger.error(f"数据生成失败: {str(e)}")
            raise
            
    def _generate_departments_and_majors(self):
        """生成院系和专业数据"""
        self.logger.info("生成院系和专业数据...")
        
        self.department_data = []
        major_counter = 0
        
        for dept_name in self.config.departments:
            # 生成院系数据
            dept_id = f"DEPT_{len(self.department_data)+1:03d}"
            dept_data = {
                'department_id': dept_id,
                'name': dept_name,
                'established_year': random.randint(1950, 2010),
                'student_capacity': random.randint(500, 2000)
            }
            
            # 生成专业数据
            majors = []
            major_count = random.randint(3, 6)
            
            for i in range(major_count):
                major_counter += 1
                major_name = self._generate_realistic_major_name(dept_name)
                major_data = {
                    'major_id': f"MAJOR_{major_counter:04d}",
                    'name': major_name,
                    'department_id': dept_id,
                    'degree_type': random.choice(['本科', '硕士', '博士']),
                    'duration_years': 4 if '本科' in major_name else 3
                }
                majors.append(major_data)
                
            dept_data['majors'] = majors
            self.department_data.append(dept_data)
            
    def _generate_realistic_major_name(self, dept_name: str) -> str:
        """生成真实的专业名称"""
        major_templates = {
            '计算机': ['计算机科学与技术', '软件工程', '人工智能', '数据科学与大数据技术', '网络空间安全'],
            '数学': ['数学与应用数学', '统计学', '信息与计算科学', '应用统计学'],
            '物理': ['物理学', '应用物理学', '电子信息工程', '通信工程'],
            '外国语': ['英语', '商务英语', '翻译', '日语', '德语'],
            '经济': ['经济学', '国际经济与贸易', '金融学', '工商管理', '市场营销'],
            '机械': ['机械工程', '机械设计制造及其自动化', '材料科学与工程', '工业设计']
        }
        
        for key, templates in major_templates.items():
            if key in dept_name:
                return random.choice(templates)
                
        return "通用专业"
        
    def _generate_teacher_profiles(self):
        """生成教师档案"""
        self.logger.info("生成教师档案...")
        
        self.teachers = generate_realistic_teacher_profiles(
            count=self.config.target_teachers,
            departments=self.config.departments
        )
        
        # 为每个教师分配专业化约束
        for teacher in self.teachers:
            spec = self._create_teacher_specialization(teacher)
            self.constraints.add_teacher_specialization(spec)
            
    def _create_teacher_specialization(self, teacher: TeacherProfile):
        """创建教师专业化约束"""
        from course_scheduling_constraints import TeacherSpecialization, TimeConstraint
        
        # 根据职称确定偏好时间段
        if teacher.title == TeacherTitle.PROFESSOR:
            preferred_slots = TimeConstraint.GOLDEN_SLOTS
        elif teacher.title == TeacherTitle.ASSOCIATE_PROFESSOR:
            preferred_slots = TimeConstraint.GOLDEN_SLOTS + TimeConstraint.AFTERNOON_SLOTS[:2]
        else:
            preferred_slots = TimeConstraint.AFTERNOON_SLOTS
            
        return TeacherSpecialization(
            teacher_id=teacher.teacher_id,
            title=teacher.title,
            specialization_areas=teacher.specialization_areas,
            experience_years=teacher.experience_years,
            max_courses_per_semester=teacher.max_courses_per_semester,
            preferred_time_slots=preferred_slots,
            max_weekly_hours=teacher.max_weekly_hours
        )
        
    def _generate_course_curriculum(self):
        """生成课程体系"""
        self.logger.info("生成课程体系...")
        
        # 构建真实的课程依赖图
        self.dependency_graph = build_realistic_curriculum(
            departments=self.config.departments,
            courses_per_department=self.config.target_courses // len(self.config.departments)
        )
        
        # 转换为CourseProfile对象
        for course_id, course_node in self.dependency_graph.courses.items():
            course_profile = self._course_node_to_profile(course_node)
            self.courses.append(course_profile)
            
    def _course_node_to_profile(self, course_node: CourseNode) -> CourseProfile:
        """将CourseNode转换为CourseProfile"""
        
        # 确定所需专业技能
        required_expertise = self._determine_required_expertise(course_node)
        
        # 确定偏好教师职称
        preferred_titles = self._determine_preferred_teacher_titles(course_node)
        
        return CourseProfile(
            course_id=course_node.course_id,
            course_name=course_node.course_name,
            course_type=course_node.course_type,
            difficulty_level=course_node.difficulty_level,
            department=course_node.department,
            subject_area=self._extract_subject_area(course_node.course_name),
            weekly_hours=random.randint(2, 4),
            total_hours=course_node.credits * 16,  # 每学分16学时
            credits=course_node.credits,
            student_capacity=random.randint(30, 120),
            required_expertise=required_expertise,
            preferred_teacher_title=preferred_titles
        )
        
    def _determine_required_expertise(self, course_node: CourseNode) -> List[str]:
        """确定课程所需专业技能"""
        course_name = course_node.course_name.lower()
        
        expertise_mapping = {
            '数学': ['数学', '数值计算', '统计'],
            '计算机': ['计算机科学', '编程', '算法'],
            '物理': ['物理', '电子', '电路'],
            '英语': ['英语', '语言学', '翻译'],
            '管理': ['管理学', '经济学', '商务'],
            '实验': ['实验技能', '工程实践']
        }
        
        required = []
        for keyword, skills in expertise_mapping.items():
            if keyword in course_name:
                required.extend(skills)
                
        return required if required else ['通用教学']
        
    def _determine_preferred_teacher_titles(self, course_node: CourseNode) -> List[TeacherTitle]:
        """确定偏好的教师职称"""
        if course_node.difficulty_level == DifficultyLevel.GRADUATE:
            return [TeacherTitle.PROFESSOR]
        elif course_node.difficulty_level == DifficultyLevel.ADVANCED:
            return [TeacherTitle.PROFESSOR, TeacherTitle.ASSOCIATE_PROFESSOR]
        elif course_node.difficulty_level == DifficultyLevel.INTERMEDIATE:
            return [TeacherTitle.ASSOCIATE_PROFESSOR, TeacherTitle.LECTURER]
        else:
            return [TeacherTitle.LECTURER, TeacherTitle.ASSISTANT]
            
    def _extract_subject_area(self, course_name: str) -> str:
        """提取学科领域"""
        subject_keywords = {
            '数学': ['数学', '微积分', '线性代数', '概率', '统计'],
            '计算机': ['计算机', '编程', '算法', '数据结构', '软件'],
            '物理': ['物理', '电路', '电子', '通信'],
            '英语': ['英语', '外语'],
            '管理': ['管理', '经济', '商务', '市场'],
            '工程': ['工程', '机械', '材料', '设计']
        }
        
        for subject, keywords in subject_keywords.items():
            if any(keyword in course_name for keyword in keywords):
                return subject
                
        return '通用'
        
    def _build_prerequisite_relationships(self):
        """建立先修关系"""
        self.logger.info("建立先修关系...")
        
        # 验证依赖图的完整性
        is_valid, errors = self.dependency_graph.validate_dependency_chain()
        
        if not is_valid:
            self.logger.warning(f"发现依赖关系问题: {errors}")
            if self.config.generation_mode == GenerationMode.CONSERVATIVE:
                raise ValueError("严格模式下不允许依赖关系错误")
                
        # 为每门课程添加先修规则
        for course_id, course_node in self.dependency_graph.courses.items():
            if course_node.prerequisites:
                from course_scheduling_constraints import PrerequisiteRule
                rule = PrerequisiteRule(
                    course_id=course_id,
                    prerequisites=course_node.prerequisites,
                    semester_gap=1
                )
                self.constraints.add_prerequisite_rule(rule)
                
    def _assign_teachers_to_courses(self):
        """分配教师到课程"""
        self.logger.info("分配教师到课程...")
        
        # 使用优化分配算法
        assignment = self.matching_engine.optimize_global_assignment(
            teachers=self.teachers,
            courses=self.courses
        )
        
        # 应用分配结果
        assigned_courses = set()
        for course_id, teacher_id in assignment.items():
            # 找到对应的课程和教师对象
            course = next((c for c in self.courses if c.course_id == course_id), None)
            teacher = next((t for t in self.teachers if t.teacher_id == teacher_id), None)
            
            if course and teacher:
                # 更新教师工作负荷
                teacher.current_course_load += 1
                teacher.current_weekly_hours += course.weekly_hours
                teacher.taught_courses.add(course_id)
                
                # 记录分配关系
                course.historical_teachers.add(teacher_id)
                assigned_courses.add(course_id)
                
        # 处理未分配的课程
        unassigned_courses = [c for c in self.courses if c.course_id not in assigned_courses]
        if unassigned_courses:
            self.logger.warning(f"有 {len(unassigned_courses)} 门课程未分配教师")
            self._handle_unassigned_courses(unassigned_courses)
            
    def _handle_unassigned_courses(self, unassigned_courses: List[CourseProfile]):
        """处理未分配的课程"""
        if self.config.generation_mode == GenerationMode.FLEXIBLE:
            # 灵活模式：允许超出工作负荷限制
            for course in unassigned_courses:
                # 找到专业最匹配的教师，即使超出负荷
                best_teacher = None
                best_score = -1
                
                for teacher in self.teachers:
                    score, _ = self.matching_engine.calculate_comprehensive_score(teacher, course)
                    if score > best_score:
                        best_score = score
                        best_teacher = teacher
                        
                if best_teacher:
                    best_teacher.current_course_load += 1
                    best_teacher.current_weekly_hours += course.weekly_hours
                    best_teacher.taught_courses.add(course.course_id)
                    course.historical_teachers.add(best_teacher.teacher_id)
                    self.constraint_violations['workload'] += 1
                    
    def _generate_schedule_data(self):
        """生成排课数据"""
        self.logger.info("生成排课数据...")
        
        # 为每门课程生成排课记录
        schedule_counter = 0
        
        for course in self.courses:
            # 确定授课教师
            assigned_teacher_id = None
            for teacher in self.teachers:
                if course.course_id in teacher.taught_courses:
                    assigned_teacher_id = teacher.teacher_id
                    break
                    
            if not assigned_teacher_id:
                continue
                
            # 生成该课程的排课记录
            course_schedules = self._generate_course_schedules(course, assigned_teacher_id)
            
            for schedule in course_schedules:
                schedule_counter += 1
                schedule['schedule_id'] = f"SCHED_{schedule_counter:08d}"
                self.schedules.append(schedule)
                
        self.logger.info(f"生成了 {len(self.schedules)} 条排课记录")
        
    def _generate_course_schedules(self, course: CourseProfile, teacher_id: str) -> List[Dict]:
        """为单门课程生成排课记录"""
        schedules = []
        
        # 根据课程类型确定排课模式
        if course.course_type == CourseType.EXPERIMENT:
            # 实验课：连续3小时，每周1次
            sessions_per_week = 1
            hours_per_session = 3
        elif course.weekly_hours >= 4:
            # 大学时课程：分2次，每次2小时
            sessions_per_week = 2
            hours_per_session = 2
        else:
            # 普通课程：每周1-2次
            sessions_per_week = min(course.weekly_hours, 2)
            hours_per_session = course.weekly_hours // sessions_per_week
            
        # 为每个教学周生成排课
        for week in range(1, 17):  # 16周教学周
            for session in range(sessions_per_week):
                schedule = self._generate_single_schedule(
                    course, teacher_id, week, session, hours_per_session
                )
                if schedule:
                    schedules.append(schedule)
                    
        return schedules
        
    def _generate_single_schedule(self, course: CourseProfile, teacher_id: str, 
                                 week: int, session: int, hours: int) -> Optional[Dict]:
        """生成单次排课记录"""
        
        # 选择合适的时间段
        optimal_time_slot = self.constraints.get_optimal_time_slot(
            course_type=course.course_type,
            teacher_preferences=[],  # 简化处理
            available_slots=list(TimeSlot)
        )
        
        if not optimal_time_slot:
            return None
            
        # 选择星期几
        weekday = random.randint(1, 5)  # 周一到周五
        
        # 选择教室
        classroom = self._select_suitable_classroom(course)
        
        # 创建排课记录
        schedule = {
            'course_id': course.course_id,
            'teacher_id': teacher_id,
            'classroom_id': classroom['classroom_id'],
            'week': week,
            'weekday': weekday,
            'time_slot': optimal_time_slot.value,
            'duration_hours': hours,
            'student_count': random.randint(
                int(course.student_capacity * 0.7),
                course.student_capacity
            )
        }
        
        # 验证时间冲突
        if self._validate_time_conflict(schedule):
            return schedule
        else:
            self.constraint_violations['time_conflict'] += 1
            if self.config.generation_mode != GenerationMode.FLEXIBLE:
                return None
            else:
                return schedule  # 灵活模式允许冲突
                
    def _select_suitable_classroom(self, course: CourseProfile) -> Dict:
        """选择合适的教室"""
        # 根据课程类型选择教室类型
        if course.course_type == CourseType.EXPERIMENT:
            classroom_type = "实验室"
            base_capacity = 40
        elif course.student_capacity > 100:
            classroom_type = "阶梯教室"
            base_capacity = 150
        else:
            classroom_type = "普通教室"
            base_capacity = 60
            
        # 确保容量足够
        required_capacity = int(course.student_capacity * 1.1)  # 10%安全边距
        capacity = max(base_capacity, required_capacity)
        
        return {
            'classroom_id': f"ROOM_{random.randint(1000, 9999)}",
            'type': classroom_type,
            'capacity': capacity,
            'building': f"教学楼{random.randint(1, 8)}"
        }
        
    def _validate_time_conflict(self, schedule: Dict) -> bool:
        """验证时间冲突"""
        # 检查教师时间冲突
        for existing_schedule in self.schedules:
            if (existing_schedule['teacher_id'] == schedule['teacher_id'] and
                existing_schedule['week'] == schedule['week'] and
                existing_schedule['weekday'] == schedule['weekday'] and
                existing_schedule['time_slot'] == schedule['time_slot']):
                return False
                
        return True
        
    def _validate_constraints(self):
        """验证约束"""
        self.logger.info("验证约束...")
        
        # 验证先修关系
        if self.config.enable_prerequisite_constraints:
            self._validate_prerequisite_constraints()
            
        # 验证容量约束
        if self.config.enable_capacity_constraints:
            self._validate_capacity_constraints()
            
        # 验证工作负荷约束
        if self.config.enable_teacher_workload_limits:
            self._validate_workload_constraints()
            
    def _validate_prerequisite_constraints(self):
        """验证先修关系约束"""
        violations = 0
        
        for course_id, course_node in self.dependency_graph.courses.items():
            if course_node.prerequisites:
                for prereq_id in course_node.prerequisites:
                    if prereq_id in self.dependency_graph.courses:
                        prereq_node = self.dependency_graph.courses[prereq_id]
                        if prereq_node.semester >= course_node.semester:
                            violations += 1
                            
        self.constraint_violations['prerequisite'] = violations
        
    def _validate_capacity_constraints(self):
        """验证容量约束"""
        violations = 0
        
        for schedule in self.schedules:
            course = next((c for c in self.courses if c.course_id == schedule['course_id']), None)
            if course:
                if schedule['student_count'] > course.student_capacity:
                    violations += 1
                    
        self.constraint_violations['capacity'] = violations
        
    def _validate_workload_constraints(self):
        """验证工作负荷约束"""
        violations = 0
        
        for teacher in self.teachers:
            if (teacher.current_course_load > teacher.max_courses_per_semester or
                teacher.current_weekly_hours > teacher.max_weekly_hours):
                violations += 1
                
        self.constraint_violations['workload'] = violations
        
    def _optimize_data_quality(self):
        """优化数据质量"""
        self.logger.info("优化数据质量...")
        
        # 计算真实性得分
        realism_scores = []
        for course in self.courses:
            course_data = self._course_to_dict(course)
            score = self.realism_validator.calculate_realism_score(course_data)
            realism_scores.append(score)
            
        avg_realism = sum(realism_scores) / len(realism_scores) if realism_scores else 0.0
        
        if avg_realism < self.config.realism_level:
            self.logger.warning(f"真实性得分 {avg_realism:.2f} 低于要求 {self.config.realism_level}")
            self.constraint_violations['realism'] = int((self.config.realism_level - avg_realism) * 100)
            
    def _generate_quality_report(self) -> Dict:
        """生成质量报告"""
        total_violations = sum(self.constraint_violations.values())
        total_records = len(self.courses) + len(self.schedules)
        
        violation_rate = total_violations / max(1, total_records)
        
        quality_score = max(0.0, 1.0 - violation_rate)
        
        return {
            'generation_time': datetime.now().isoformat(),
            'generation_mode': self.config.generation_mode.value,
            'total_teachers': len(self.teachers),
            'total_courses': len(self.courses),
            'total_schedules': len(self.schedules),
            'constraint_violations': self.constraint_violations,
            'violation_rate': violation_rate,
            'quality_score': quality_score,
            'recommendations': self._generate_recommendations()
        }
        
    def _generate_recommendations(self) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        if self.constraint_violations['prerequisite'] > 0:
            recommendations.append("建议调整先修关系或学期安排")
            
        if self.constraint_violations['time_conflict'] > 0:
            recommendations.append("建议增加可用时间段或教师数量")
            
        if self.constraint_violations['capacity'] > 0:
            recommendations.append("建议增加教室容量或减少班级规模")
            
        if self.constraint_violations['workload'] > 0:
            recommendations.append("建议增加教师数量或调整工作负荷限制")
            
        if not recommendations:
            recommendations.append("数据质量良好，无需特殊改进")
            
        return recommendations
        
    def _teacher_to_dict(self, teacher: TeacherProfile) -> Dict:
        """将教师对象转换为字典"""
        return {
            'teacher_id': teacher.teacher_id,
            'name': teacher.name,
            'title': teacher.title.value,
            'department': teacher.department,
            'specialization_areas': teacher.specialization_areas,
            'experience_years': teacher.experience_years,
            'education_background': teacher.education_background,
            'max_courses_per_semester': teacher.max_courses_per_semester,
            'max_weekly_hours': teacher.max_weekly_hours,
            'current_course_load': teacher.current_course_load,
            'current_weekly_hours': teacher.current_weekly_hours,
            'average_evaluation': teacher.get_average_evaluation()
        }
        
    def _course_to_dict(self, course: CourseProfile) -> Dict:
        """将课程对象转换为字典"""
        return {
            'course_id': course.course_id,
            'name': course.course_name,
            'type': course.course_type.value,
            'difficulty_level': course.difficulty_level.value,
            'department': course.department,
            'subject_area': course.subject_area,
            'weekly_hours': course.weekly_hours,
            'total_hours': course.total_hours,
            'credits': course.credits,
            'student_capacity': course.student_capacity,
            'required_expertise': course.required_expertise,
            'preferred_teacher_titles': [title.value for title in course.preferred_teacher_title]
        }
        
    def _extract_prerequisites(self) -> List[Dict]:
        """提取先修关系"""
        prerequisites = []
        
        for course_id, rule in self.constraints.prerequisite_rules.items():
            for prereq_id in rule.prerequisites:
                prerequisites.append({
                    'course_id': course_id,
                    'prerequisite_id': prereq_id,
                    'semester_gap': rule.semester_gap
                })
                
        return prerequisites