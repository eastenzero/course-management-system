# file: data-generator/generators/prerequisite_logic.py
# 功能: 课程依赖关系和先修课程逻辑系统

from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import networkx as nx
from course_scheduling_constraints import (
    PrerequisiteRule, DifficultyLevel, CourseType, 
    STANDARD_PREREQUISITE_CHAINS
)


class PrerequisiteType(Enum):
    """先修关系类型"""
    HARD = "硬先修"      # 必须先完成的课程
    SOFT = "软先修"      # 建议先修的课程
    CO = "同修"          # 可以同时修读的课程
    ALTERNATIVE = "选择性"  # 多个先修课程中选择一个


@dataclass
class CourseNode:
    """课程节点定义"""
    course_id: str
    course_name: str
    course_type: CourseType
    difficulty_level: DifficultyLevel
    credits: int
    semester: int
    department: str
    prerequisites: List[str] = None
    corequisites: List[str] = None  # 同修课程
    
    def __post_init__(self):
        if self.prerequisites is None:
            self.prerequisites = []
        if self.corequisites is None:
            self.corequisites = []


class DependencyGraph:
    """课程依赖关系图"""
    
    def __init__(self):
        self.graph = nx.DiGraph()  # 有向图
        self.courses: Dict[str, CourseNode] = {}
        self.prerequisite_rules: Dict[str, PrerequisiteRule] = {}
        
    def add_course(self, course: CourseNode):
        """添加课程节点"""
        self.courses[course.course_id] = course
        self.graph.add_node(course.course_id, **course.__dict__)
        
    def add_prerequisite_edge(self, prerequisite_id: str, course_id: str, 
                            prereq_type: PrerequisiteType = PrerequisiteType.HARD):
        """添加先修关系边"""
        if prerequisite_id in self.courses and course_id in self.courses:
            self.graph.add_edge(prerequisite_id, course_id, type=prereq_type)
            
    def validate_dependency_chain(self) -> Tuple[bool, List[str]]:
        """验证依赖链完整性"""
        errors = []
        
        # 检查循环依赖
        try:
            cycles = list(nx.simple_cycles(self.graph))
            if cycles:
                errors.extend([f"循环依赖: {' -> '.join(cycle)}" for cycle in cycles])
        except Exception as e:
            errors.append(f"循环检测失败: {str(e)}")
            
        # 检查孤立节点
        isolated_nodes = list(nx.isolates(self.graph))
        if isolated_nodes:
            # 基础课程可以是孤立的，这是正常的
            basic_courses = [
                node for node in isolated_nodes 
                if self.courses[node].difficulty_level == DifficultyLevel.BASIC
            ]
            non_basic_isolated = [node for node in isolated_nodes if node not in basic_courses]
            if non_basic_isolated:
                errors.append(f"非基础课程无先修关系: {non_basic_isolated}")
                
        # 检查学期逻辑
        for course_id, course in self.courses.items():
            for prereq_id in course.prerequisites:
                if prereq_id in self.courses:
                    prereq_course = self.courses[prereq_id]
                    if prereq_course.semester >= course.semester:
                        errors.append(f"先修课程学期错误: {prereq_id} ({prereq_course.semester}) -> {course_id} ({course.semester})")
                        
        return len(errors) == 0, errors
        
    def get_learning_path(self, target_course_id: str) -> List[List[str]]:
        """获取学习路径"""
        if target_course_id not in self.courses:
            return []
            
        # 获取所有可能的学习路径
        try:
            paths = []
            for source_node in self.courses:
                if self.graph.in_degree(source_node) == 0:  # 起始课程
                    try:
                        path = nx.shortest_path(self.graph, source_node, target_course_id)
                        paths.append(path)
                    except nx.NetworkXNoPath:
                        continue
            return paths
        except Exception:
            return []
            
    def get_semester_courses(self, semester: int) -> List[CourseNode]:
        """获取指定学期的课程"""
        return [course for course in self.courses.values() if course.semester == semester]
        
    def validate_semester_prerequisites(self, semester: int) -> List[str]:
        """验证学期先修关系"""
        errors = []
        semester_courses = self.get_semester_courses(semester)
        
        for course in semester_courses:
            for prereq_id in course.prerequisites:
                if prereq_id in self.courses:
                    prereq_course = self.courses[prereq_id]
                    if prereq_course.semester >= semester:
                        errors.append(
                            f"学期{semester}课程{course.course_id}的先修课程{prereq_id}在第{prereq_course.semester}学期"
                        )
        return errors


class PrerequisitePatternGenerator:
    """先修关系模式生成器"""
    
    def __init__(self):
        self.knowledge_areas = self._define_knowledge_areas()
        self.difficulty_progression = self._define_difficulty_progression()
        
    def _define_knowledge_areas(self) -> Dict[str, Dict]:
        """定义知识领域及其课程层次"""
        return {
            '数学基础': {
                'foundation': ['高等数学A1', '高等数学A2'],
                'intermediate': ['线性代数', '概率论与数理统计'],
                'advanced': ['数值分析', '数学建模', '运筹学']
            },
            '计算机基础': {
                'foundation': ['计算机导论', '程序设计基础'],
                'intermediate': ['数据结构', '计算机组成原理'],
                'advanced': ['算法设计与分析', '操作系统', '编译原理']
            },
            '专业核心': {
                'foundation': ['数据库系统概论'],
                'intermediate': ['软件工程', '计算机网络'],
                'advanced': ['分布式系统', '机器学习', '人工智能']
            },
            '实践应用': {
                'foundation': ['程序设计实验'],
                'intermediate': ['数据库实验', '网络编程实验'],
                'advanced': ['毕业设计', '专业实习']
            }
        }
        
    def _define_difficulty_progression(self) -> Dict[DifficultyLevel, List[str]]:
        """定义难度递进关系"""
        return {
            DifficultyLevel.BASIC: ['foundation'],
            DifficultyLevel.INTERMEDIATE: ['foundation', 'intermediate'],
            DifficultyLevel.ADVANCED: ['intermediate', 'advanced'],
            DifficultyLevel.GRADUATE: ['advanced']
        }
        
    def generate_realistic_prerequisites(self, course_name: str, 
                                       difficulty: DifficultyLevel,
                                       knowledge_area: str) -> List[str]:
        """生成真实的先修课程关系"""
        prerequisites = []
        
        if knowledge_area not in self.knowledge_areas:
            return prerequisites
            
        area_courses = self.knowledge_areas[knowledge_area]
        allowed_levels = self.difficulty_progression.get(difficulty, [])
        
        # 根据难度等级确定先修课程
        if difficulty == DifficultyLevel.BASIC:
            # 基础课程通常无先修要求
            return prerequisites
            
        elif difficulty == DifficultyLevel.INTERMEDIATE:
            # 中级课程需要基础课程作为先修
            if 'foundation' in area_courses:
                prerequisites.extend(area_courses['foundation'])
                
        elif difficulty == DifficultyLevel.ADVANCED:
            # 高级课程需要中级课程作为先修
            if 'intermediate' in area_courses:
                prerequisites.extend(area_courses['intermediate'])
                
        elif difficulty == DifficultyLevel.GRADUATE:
            # 研究生课程需要高级课程作为先修
            if 'advanced' in area_courses:
                prerequisites.extend(area_courses['advanced'])
                
        # 跨领域先修关系
        cross_area_prerequisites = self._get_cross_area_prerequisites(course_name)
        prerequisites.extend(cross_area_prerequisites)
        
        return list(set(prerequisites))  # 去重
        
    def _get_cross_area_prerequisites(self, course_name: str) -> List[str]:
        """获取跨领域先修关系"""
        cross_area_rules = {
            # 需要数学基础的课程
            '算法': ['高等数学A1', '离散数学'],
            '机器学习': ['线性代数', '概率论与数理统计', '程序设计基础'],
            '数值': ['高等数学A2', '线性代数'],
            '图像': ['线性代数', '数字信号处理'],
            '网络': ['计算机组成原理', '操作系统'],
            '数据库': ['数据结构'],
            '编译': ['数据结构', '离散数学'],
            '操作系统': ['计算机组成原理', '数据结构'],
            '软件工程': ['程序设计基础', '数据结构']
        }
        
        prerequisites = []
        for keyword, prereqs in cross_area_rules.items():
            if keyword in course_name:
                prerequisites.extend(prereqs)
                
        return prerequisites


class SemesterPlanningLogic:
    """学期规划逻辑"""
    
    def __init__(self, total_semesters: int = 8):
        self.total_semesters = total_semesters
        self.semester_rules = self._define_semester_rules()
        
    def _define_semester_rules(self) -> Dict[int, Dict]:
        """定义各学期的课程安排规则"""
        return {
            1: {
                'focus': '基础适应',
                'course_types': [CourseType.GENERAL, CourseType.REQUIRED],
                'max_courses': 6,
                'difficulty_range': [DifficultyLevel.BASIC],
                'typical_courses': ['高等数学A1', '大学英语1', '思想道德修养', '计算机导论']
            },
            2: {
                'focus': '基础建设',
                'course_types': [CourseType.GENERAL, CourseType.REQUIRED],
                'max_courses': 7,
                'difficulty_range': [DifficultyLevel.BASIC, DifficultyLevel.INTERMEDIATE],
                'typical_courses': ['高等数学A2', '大学英语2', '程序设计基础', '大学物理']
            },
            3: {
                'focus': '专业入门',
                'course_types': [CourseType.REQUIRED, CourseType.EXPERIMENT],
                'max_courses': 7,
                'difficulty_range': [DifficultyLevel.INTERMEDIATE],
                'typical_courses': ['线性代数', '数据结构', '电路分析', '程序设计实验']
            },
            4: {
                'focus': '专业核心',
                'course_types': [CourseType.REQUIRED, CourseType.ELECTIVE],
                'max_courses': 6,
                'difficulty_range': [DifficultyLevel.INTERMEDIATE, DifficultyLevel.ADVANCED],
                'typical_courses': ['算法设计', '计算机组成', '概率统计', '专业选修']
            },
            5: {
                'focus': '专业深化',
                'course_types': [CourseType.REQUIRED, CourseType.ELECTIVE],
                'max_courses': 6,
                'difficulty_range': [DifficultyLevel.ADVANCED],
                'typical_courses': ['操作系统', '数据库系统', '计算机网络', '专业选修']
            },
            6: {
                'focus': '专业拓展',
                'course_types': [CourseType.ELECTIVE, CourseType.EXPERIMENT],
                'max_courses': 5,
                'difficulty_range': [DifficultyLevel.ADVANCED],
                'typical_courses': ['软件工程', '人工智能', '专业实习', '选修课']
            },
            7: {
                'focus': '专业综合',
                'course_types': [CourseType.ELECTIVE, CourseType.THESIS],
                'max_courses': 4,
                'difficulty_range': [DifficultyLevel.ADVANCED],
                'typical_courses': ['毕业设计选题', '专业前沿', '高级选修']
            },
            8: {
                'focus': '毕业设计',
                'course_types': [CourseType.THESIS],
                'max_courses': 2,
                'difficulty_range': [DifficultyLevel.ADVANCED],
                'typical_courses': ['毕业设计', '毕业实习']
            }
        }
        
    def validate_semester_load(self, semester: int, courses: List[CourseNode]) -> bool:
        """验证学期课程负荷"""
        if semester not in self.semester_rules:
            return True
            
        rules = self.semester_rules[semester]
        
        # 检查课程数量
        if len(courses) > rules['max_courses']:
            return False
            
        # 检查课程类型分布
        course_types = [course.course_type for course in courses]
        allowed_types = rules['course_types']
        for course_type in course_types:
            if course_type not in allowed_types:
                return False
                
        # 检查难度分布
        difficulties = [course.difficulty_level for course in courses]
        allowed_difficulties = rules['difficulty_range']
        for difficulty in difficulties:
            if difficulty not in allowed_difficulties:
                return False
                
        return True
        
    def suggest_semester_for_course(self, course: CourseNode, 
                                  prerequisite_semesters: Dict[str, int]) -> int:
        """建议课程安排学期"""
        # 基于先修课程确定最早学期
        min_semester = 1
        for prereq_id in course.prerequisites:
            if prereq_id in prerequisite_semesters:
                min_semester = max(min_semester, prerequisite_semesters[prereq_id] + 1)
                
        # 基于课程类型和难度调整
        type_semester_mapping = {
            CourseType.GENERAL: (1, 4),      # 通识课通常在前4学期
            CourseType.REQUIRED: (1, 6),     # 必修课通常在前6学期
            CourseType.ELECTIVE: (4, 7),     # 选修课通常在后4学期
            CourseType.EXPERIMENT: (2, 6),   # 实验课在2-6学期
            CourseType.THESIS: (7, 8)        # 论文课在最后2学期
        }
        
        difficulty_semester_mapping = {
            DifficultyLevel.BASIC: (1, 3),
            DifficultyLevel.INTERMEDIATE: (2, 5),
            DifficultyLevel.ADVANCED: (4, 7),
            DifficultyLevel.GRADUATE: (6, 8)
        }
        
        # 确定推荐学期范围
        type_range = type_semester_mapping.get(course.course_type, (1, 8))
        difficulty_range = difficulty_semester_mapping.get(course.difficulty_level, (1, 8))
        
        # 取交集
        start_semester = max(min_semester, type_range[0], difficulty_range[0])
        end_semester = min(type_range[1], difficulty_range[1], self.total_semesters)
        
        # 返回推荐的中间学期
        return min(start_semester + 1, end_semester) if start_semester <= end_semester else min_semester


def build_realistic_curriculum(departments: List[str], courses_per_department: int = 30) -> DependencyGraph:
    """构建真实的课程体系"""
    dependency_graph = DependencyGraph()
    pattern_generator = PrerequisitePatternGenerator()
    semester_planner = SemesterPlanningLogic()
    
    course_counter = 0
    
    for department in departments:
        # 确定该院系的知识领域
        if '计算机' in department or '软件' in department:
            knowledge_areas = ['数学基础', '计算机基础', '专业核心', '实践应用']
        elif '数学' in department or '统计' in department:
            knowledge_areas = ['数学基础']
        else:
            knowledge_areas = ['数学基础', '专业核心']
            
        for area in knowledge_areas:
            area_courses = pattern_generator.knowledge_areas.get(area, {})
            
            for level, course_names in area_courses.items():
                for course_name in course_names:
                    course_counter += 1
                    course_id = f"COURSE_{course_counter:06d}"
                    
                    # 确定课程难度
                    if level == 'foundation':
                        difficulty = DifficultyLevel.BASIC
                    elif level == 'intermediate':
                        difficulty = DifficultyLevel.INTERMEDIATE
                    else:
                        difficulty = DifficultyLevel.ADVANCED
                        
                    # 确定课程类型
                    if '实验' in course_name or '实习' in course_name or '设计' in course_name:
                        course_type = CourseType.EXPERIMENT
                    elif '毕业' in course_name:
                        course_type = CourseType.THESIS
                    elif area == '数学基础' or '基础' in course_name:
                        course_type = CourseType.REQUIRED
                    else:
                        course_type = CourseType.ELECTIVE
                        
                    # 生成先修关系
                    prerequisites = pattern_generator.generate_realistic_prerequisites(
                        course_name, difficulty, area
                    )
                    
                    # 创建课程节点
                    course = CourseNode(
                        course_id=course_id,
                        course_name=course_name,
                        course_type=course_type,
                        difficulty_level=difficulty,
                        credits=2 if course_type == CourseType.EXPERIMENT else 3,
                        semester=1,  # 临时值，后面会调整
                        department=department,
                        prerequisites=prerequisites
                    )
                    
                    dependency_graph.add_course(course)
                    
    # 建立先修关系边
    for course_id, course in dependency_graph.courses.items():
        for prereq_name in course.prerequisites:
            # 查找先修课程ID
            prereq_id = None
            for pid, pcourse in dependency_graph.courses.items():
                if pcourse.course_name == prereq_name:
                    prereq_id = pid
                    break
                    
            if prereq_id:
                dependency_graph.add_prerequisite_edge(prereq_id, course_id)
                
    return dependency_graph