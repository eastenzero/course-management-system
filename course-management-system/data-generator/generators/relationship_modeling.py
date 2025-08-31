# file: data-generator/generators/relationship_modeling.py
# 功能: 关联性建模模块 - 强化数据间关联关系

import random
import networkx as nx
from typing import List, Dict, Any, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict
import numpy as np


@dataclass
class CourseRelationship:
    """课程关系定义"""
    prerequisite_id: int
    dependent_id: int 
    relationship_type: str  # "prerequisite", "corequisite", "recommended"
    strength: float  # 关系强度 0-1
    semester_gap: int  # 建议间隔学期数


@dataclass  
class TeacherCompetency:
    """教师能力特征"""
    teacher_id: int
    subject_areas: List[str]  # 专业领域
    competency_scores: Dict[str, float]  # 各领域能力分数
    teaching_load_preference: str  # "light", "medium", "heavy"
    course_level_preference: str  # "undergraduate", "graduate", "mixed"


class RelationshipModelingEngine:
    """关联性建模引擎
    
    构建并维护各类数据实体间的关联关系，确保数据的业务逻辑合理性
    """
    
    def __init__(self):
        self.knowledge_graph = nx.DiGraph()  # 知识图谱
        self.course_dependencies = {}  # 课程依赖关系
        self.teacher_competencies = {}  # 教师能力映射
        self.resource_conflicts = defaultdict(list)  # 资源冲突记录
        self.setup_knowledge_base()
        
    def setup_knowledge_base(self):
        """设置知识库和基础关联关系"""
        
        # 构建学科知识图谱
        self.subject_knowledge_graph = {
            # 计算机学科知识链
            "高等数学": {"leads_to": ["线性代数", "概率论与数理统计"], "difficulty": 1},
            "线性代数": {"leads_to": ["数据结构与算法", "机器学习"], "difficulty": 2},
            "概率论与数理统计": {"leads_to": ["机器学习", "数据挖掘"], "difficulty": 2},
            "数据结构与算法": {"leads_to": ["数据库系统", "操作系统", "计算机网络"], "difficulty": 3},
            "数据库系统": {"leads_to": ["数据挖掘", "大数据处理"], "difficulty": 3},
            "机器学习": {"leads_to": ["深度学习", "人工智能"], "difficulty": 4},
            "深度学习": {"leads_to": ["计算机视觉", "自然语言处理"], "difficulty": 5},
            
            # 物理学科知识链
            "大学物理": {"leads_to": ["理论力学", "电磁学"], "difficulty": 1},
            "理论力学": {"leads_to": ["量子力学", "固体物理"], "difficulty": 3},
            "电磁学": {"leads_to": ["光学", "电动力学"], "difficulty": 3},
            "量子力学": {"leads_to": ["粒子物理", "凝聚态物理"], "difficulty": 4},
            
            # 化学学科知识链  
            "无机化学": {"leads_to": ["分析化学", "物理化学"], "difficulty": 1},
            "有机化学": {"leads_to": ["生物化学", "药物化学"], "difficulty": 2},
            "物理化学": {"leads_to": ["材料化学", "催化化学"], "difficulty": 3},
            
            # 经济管理学科知识链
            "微观经济学": {"leads_to": ["产业经济学", "国际经济学"], "difficulty": 1},
            "宏观经济学": {"leads_to": ["货币银行学", "财政学"], "difficulty": 2},
            "管理学原理": {"leads_to": ["组织行为学", "战略管理"], "difficulty": 2},
            "组织行为学": {"leads_to": ["人力资源管理", "领导力"], "difficulty": 3}
        }
        
        # 教师专业能力模板
        self.teacher_competency_templates = {
            "计算机科学": {
                "required_areas": ["程序设计", "数据结构", "算法分析"],
                "advanced_areas": ["机器学习", "分布式系统", "网络安全"],
                "typical_courses": ["数据结构与算法", "计算机网络", "软件工程"]
            },
            "数学": {
                "required_areas": ["微积分", "线性代数", "概率统计"], 
                "advanced_areas": ["数值分析", "运筹学", "数学建模"],
                "typical_courses": ["高等数学", "线性代数", "概率论与数理统计"]
            },
            "物理": {
                "required_areas": ["力学", "电磁学", "热力学"],
                "advanced_areas": ["量子力学", "固体物理", "光学"],
                "typical_courses": ["大学物理", "理论力学", "量子力学"]
            }
        }
        
        # 资源竞争模式
        self.resource_competition_patterns = {
            "peak_hours": ["10:00-12:00", "14:00-16:00"],  # 高峰时段
            "popular_classrooms": ["阶梯教室", "多媒体教室"],  # 热门教室类型
            "star_teachers": 0.1,  # 明星教师比例
            "popular_courses": 0.2  # 热门课程比例
        }

    def build_course_dependency_network(self, courses: List[Dict[str, Any]]) -> Dict[int, List[CourseRelationship]]:
        """构建课程依赖网络
        
        Args:
            courses: 课程列表
            
        Returns:
            课程依赖关系字典
        """
        course_relationships = defaultdict(list)
        
        # 按课程名称分组，便于查找关联
        courses_by_name = {course['name']: course for course in courses}
        
        for course in courses:
            course_name = course['name']
            course_id = course['id']
            
            # 从知识图谱中查找先修关系
            prerequisites = self._find_prerequisites(course_name, courses_by_name)
            
            for prereq_course in prerequisites:
                relationship = CourseRelationship(
                    prerequisite_id=prereq_course['id'],
                    dependent_id=course_id,
                    relationship_type="prerequisite",
                    strength=self._calculate_relationship_strength(prereq_course['name'], course_name),
                    semester_gap=self._calculate_recommended_gap(prereq_course['name'], course_name)
                )
                course_relationships[course_id].append(relationship)
                
            # 查找同修课程
            corequisites = self._find_corequisites(course_name, courses_by_name)
            for coreq_course in corequisites:
                if coreq_course['id'] != course_id:  # 避免自引用
                    relationship = CourseRelationship(
                        prerequisite_id=coreq_course['id'],
                        dependent_id=course_id,
                        relationship_type="corequisite", 
                        strength=0.7,
                        semester_gap=0
                    )
                    course_relationships[course_id].append(relationship)
                    
        self.course_dependencies = course_relationships
        return course_relationships
        
    def _find_prerequisites(self, course_name: str, courses_by_name: Dict[str, Dict]) -> List[Dict]:
        """查找先修课程"""
        prerequisites = []
        
        # 检查知识图谱中的依赖关系
        for prereq_name, info in self.subject_knowledge_graph.items():
            if course_name in info.get("leads_to", []):
                if prereq_name in courses_by_name:
                    prerequisites.append(courses_by_name[prereq_name])
                    
        return prerequisites
        
    def _find_corequisites(self, course_name: str, courses_by_name: Dict[str, Dict]) -> List[Dict]:
        """查找同修课程"""
        corequisites = []
        
        # 基于课程名称相似性和同一学期的课程
        course_keywords = self._extract_course_keywords(course_name)
        
        for other_name, other_course in courses_by_name.items():
            if other_name != course_name:
                other_keywords = self._extract_course_keywords(other_name)
                
                # 如果有共同关键词，可能是同修课程
                common_keywords = set(course_keywords) & set(other_keywords)
                if len(common_keywords) > 0:
                    # 额外检查：理论+实验的组合
                    if (("理论" in course_name and "实验" in other_name) or
                        ("实验" in course_name and "理论" in other_name)):
                        corequisites.append(other_course)
                        
        return corequisites
        
    def _extract_course_keywords(self, course_name: str) -> List[str]:
        """提取课程关键词"""
        keywords = []
        
        # 学科关键词
        subjects = ["数学", "物理", "化学", "计算机", "管理", "经济"]
        for subject in subjects:
            if subject in course_name:
                keywords.append(subject)
                
        # 层次关键词
        levels = ["基础", "高级", "导论", "原理"]
        for level in levels:
            if level in course_name:
                keywords.append(level)
                
        return keywords
        
    def _calculate_relationship_strength(self, prereq_name: str, course_name: str) -> float:
        """计算关系强度"""
        base_strength = 0.5
        
        # 基于课程难度差异
        prereq_difficulty = self.subject_knowledge_graph.get(prereq_name, {}).get("difficulty", 1)
        course_difficulty = self.subject_knowledge_graph.get(course_name, {}).get("difficulty", 1)
        
        difficulty_gap = course_difficulty - prereq_difficulty
        if difficulty_gap == 1:
            base_strength = 0.9  # 紧密关联
        elif difficulty_gap == 2:
            base_strength = 0.7  # 中等关联
        else:
            base_strength = 0.5  # 一般关联
            
        return base_strength
        
    def _calculate_recommended_gap(self, prereq_name: str, course_name: str) -> int:
        """计算建议的学期间隔"""
        prereq_difficulty = self.subject_knowledge_graph.get(prereq_name, {}).get("difficulty", 1)
        course_difficulty = self.subject_knowledge_graph.get(course_name, {}).get("difficulty", 1)
        
        difficulty_gap = course_difficulty - prereq_difficulty
        
        if difficulty_gap <= 1:
            return 1  # 下一学期即可
        elif difficulty_gap <= 2:
            return 2  # 间隔一学期
        else:
            return 3  # 间隔两学期以上

    def generate_teacher_competency_profiles(self, teachers: List[Dict[str, Any]], 
                                           departments: List[Dict[str, Any]]) -> Dict[int, TeacherCompetency]:
        """生成教师能力特征档案
        
        Args:
            teachers: 教师列表
            departments: 院系列表
            
        Returns:
            教师能力特征字典
        """
        teacher_competencies = {}
        
        for teacher in teachers:
            # 确定教师的主要学科领域
            dept_name = teacher.get('department', '')
            primary_subject = self._map_department_to_subject(dept_name)
            
            # 获取该学科的能力模板
            competency_template = self.teacher_competency_templates.get(primary_subject, 
                                                                      self._get_default_template())
            
            # 生成个性化的能力档案
            competency_profile = self._generate_individual_competency(
                teacher, competency_template, primary_subject
            )
            
            teacher_competencies[teacher['id']] = competency_profile
            
        self.teacher_competencies = teacher_competencies
        return teacher_competencies
        
    def _map_department_to_subject(self, dept_name: str) -> str:
        """将院系映射到学科"""
        if any(keyword in dept_name for keyword in ["计算机", "软件", "信息"]):
            return "计算机科学"
        elif "数学" in dept_name:
            return "数学"
        elif "物理" in dept_name:
            return "物理"
        elif "化学" in dept_name:
            return "化学"
        elif any(keyword in dept_name for keyword in ["经济", "管理"]):
            return "经济管理"
        else:
            return "通用"
            
    def _get_default_template(self) -> Dict:
        """获取默认能力模板"""
        return {
            "required_areas": ["基础理论", "专业知识"],
            "advanced_areas": ["学科前沿", "跨学科应用"],
            "typical_courses": ["专业基础课", "专业核心课"]
        }
        
    def _generate_individual_competency(self, teacher: Dict, template: Dict, subject: str) -> TeacherCompetency:
        """生成个人能力档案"""
        # 基于教师职称和经验调整能力分数
        title = teacher.get('title', '讲师')
        experience_years = teacher.get('teaching_experience', 5)
        
        # 职称对应的基础能力水平
        title_base_scores = {
            "助教": 0.5,
            "讲师": 0.65,
            "副教授": 0.8,
            "教授": 0.9
        }
        
        base_score = title_base_scores.get(title, 0.6)
        
        # 生成各领域能力分数
        competency_scores = {}
        
        # 必修领域能力
        for area in template["required_areas"]:
            # 基础分数 + 经验加成 + 随机波动
            score = base_score + (experience_years / 50) + random.uniform(-0.1, 0.1)
            competency_scores[area] = max(0.3, min(1.0, score))
            
        # 高级领域能力  
        for area in template["advanced_areas"]:
            # 高级领域需要更高要求
            score = base_score * 0.8 + (experience_years / 40) + random.uniform(-0.2, 0.1)
            competency_scores[area] = max(0.1, min(1.0, score))
            
        # 确定教学偏好
        if title in ["教授", "副教授"]:
            load_preference = random.choices(["light", "medium"], weights=[0.6, 0.4])[0]
            level_preference = random.choices(["graduate", "mixed"], weights=[0.4, 0.6])[0]
        else:
            load_preference = random.choices(["medium", "heavy"], weights=[0.6, 0.4])[0]
            level_preference = "undergraduate"
            
        return TeacherCompetency(
            teacher_id=teacher['id'],
            subject_areas=[subject] + template["required_areas"][:2],  # 主要专业领域
            competency_scores=competency_scores,
            teaching_load_preference=load_preference,
            course_level_preference=level_preference
        )

    def optimize_teacher_course_assignments(self, courses: List[Dict[str, Any]], 
                                          teachers: List[Dict[str, Any]]) -> Dict[int, List[int]]:
        """优化教师课程分配
        
        基于教师能力特征和课程需求进行智能匹配
        
        Args:
            courses: 课程列表
            teachers: 教师列表
            
        Returns:
            课程到教师的最优分配字典
        """
        course_assignments = {}
        
        # 构建课程-教师匹配矩阵
        match_matrix = self._build_teacher_course_match_matrix(courses, teachers)
        
        # 考虑教师工作负荷约束
        teacher_loads = {teacher['id']: 0 for teacher in teachers}
        
        for course in courses:
            course_id = course['id']
            
            # 获取该课程的候选教师(按匹配度排序)
            candidates = self._get_sorted_teacher_candidates(course, match_matrix, teacher_loads)
            
            # 分配主讲教师
            primary_teacher = candidates[0] if candidates else None
            assigned_teachers = []
            
            if primary_teacher:
                assigned_teachers.append(primary_teacher['id'])
                teacher_loads[primary_teacher['id']] += course.get('credits', 3)
                
                # 对于高难度课程，可能需要助教
                if course.get('difficulty_level', 1) >= 4 and len(candidates) > 1:
                    assistant = candidates[1]
                    if teacher_loads[assistant['id']] < 15:  # 工作负荷限制
                        assigned_teachers.append(assistant['id'])
                        teacher_loads[assistant['id']] += 1  # 助教工作负荷较小
                        
            course_assignments[course_id] = assigned_teachers
            
        return course_assignments
        
    def _build_teacher_course_match_matrix(self, courses: List[Dict], teachers: List[Dict]) -> Dict:
        """构建教师-课程匹配矩阵"""
        match_matrix = {}
        
        for course in courses:
            course_id = course['id']
            course_name = course['name']
            course_subject = self._extract_primary_subject(course_name)
            
            match_matrix[course_id] = {}
            
            for teacher in teachers:
                teacher_id = teacher['id']
                
                # 计算匹配分数
                match_score = self._calculate_teacher_course_match_score(
                    teacher, course, course_subject
                )
                
                match_matrix[course_id][teacher_id] = match_score
                
        return match_matrix
        
    def _calculate_teacher_course_match_score(self, teacher: Dict, course: Dict, course_subject: str) -> float:
        """计算教师与课程的匹配分数"""
        score = 0.0
        
        # 获取教师能力档案
        teacher_competency = self.teacher_competencies.get(teacher['id'])
        if not teacher_competency:
            return 0.3  # 默认基础分数
            
        # 1. 学科匹配度 (40%)
        if course_subject in teacher_competency.subject_areas:
            score += 0.4
        elif any(subject in course_subject for subject in teacher_competency.subject_areas):
            score += 0.2
            
        # 2. 能力匹配度 (30%)
        relevant_competencies = [comp for area, comp in teacher_competency.competency_scores.items() 
                               if area in course['name'] or course_subject in area]
        if relevant_competencies:
            avg_competency = sum(relevant_competencies) / len(relevant_competencies)
            score += 0.3 * avg_competency
        else:
            score += 0.15  # 默认基础能力
            
        # 3. 课程难度适配 (20%)
        course_difficulty = course.get('difficulty_level', 1)
        teacher_title = teacher.get('title', '讲师')
        
        title_difficulty_match = {
            "助教": [1, 2],
            "讲师": [1, 2, 3],
            "副教授": [2, 3, 4],
            "教授": [3, 4, 5]
        }
        
        if course_difficulty in title_difficulty_match.get(teacher_title, [1]):
            score += 0.2
        else:
            score += 0.05
            
        # 4. 工作负荷偏好 (10%)
        course_credits = course.get('credits', 3)
        load_preference = teacher_competency.teaching_load_preference
        
        if load_preference == "light" and course_credits <= 2:
            score += 0.1
        elif load_preference == "medium" and 2 < course_credits <= 4:
            score += 0.1
        elif load_preference == "heavy" and course_credits > 4:
            score += 0.1
        else:
            score += 0.05
            
        return min(1.0, score)
        
    def _extract_primary_subject(self, course_name: str) -> str:
        """提取课程的主要学科"""
        subjects = ["计算机", "数学", "物理", "化学", "经济", "管理", "文学", "历史"]
        
        for subject in subjects:
            if subject in course_name:
                return subject
                
        return "通用"
        
    def _get_sorted_teacher_candidates(self, course: Dict, match_matrix: Dict, 
                                     teacher_loads: Dict) -> List[Dict]:
        """获取排序后的教师候选列表"""
        course_id = course['id']
        candidates = []
        
        for teacher_id, match_score in match_matrix[course_id].items():
            # 考虑工作负荷约束
            current_load = teacher_loads[teacher_id]
            max_load = 20  # 假设最大工作负荷
            
            if current_load < max_load:
                # 工作负荷惩罚
                load_penalty = current_load / max_load * 0.2
                adjusted_score = match_score - load_penalty
                
                candidates.append({
                    'id': teacher_id,
                    'match_score': match_score,
                    'adjusted_score': adjusted_score,
                    'current_load': current_load
                })
                
        # 按调整后分数排序
        candidates.sort(key=lambda x: x['adjusted_score'], reverse=True)
        
        return candidates

    def detect_resource_conflicts(self, courses: List[Dict], assignments: Dict, 
                                schedules: List[Dict] = None) -> Dict[str, List[Dict]]:
        """检测资源冲突
        
        Args:
            courses: 课程列表
            assignments: 教师分配
            schedules: 排课安排(可选)
            
        Returns:
            按类型分类的冲突列表
        """
        conflicts = {
            "teacher_conflicts": [],
            "classroom_conflicts": [],
            "time_conflicts": [],
            "capacity_conflicts": [],
            "complex_conflicts": []
        }
        
        # 检测教师冲突
        teacher_course_mapping = defaultdict(list)
        for course_id, teacher_ids in assignments.items():
            for teacher_id in teacher_ids:
                teacher_course_mapping[teacher_id].append(course_id)
                
        for teacher_id, course_ids in teacher_course_mapping.items():
            if len(course_ids) > 1:
                # 检查是否为过载
                total_credits = sum(course.get('credits', 3) for course in courses 
                                  if course['id'] in course_ids)
                if total_credits > 18:  # 假设教师最大工作负荷
                    conflicts["teacher_conflicts"].append({
                        "type": "overload",
                        "teacher_id": teacher_id,
                        "course_ids": course_ids,
                        "total_credits": total_credits,
                        "severity": "high" if total_credits > 25 else "medium"
                    })
                    
        # 检测热门资源竞争
        popular_courses = [course for course in courses 
                          if course.get('popularity_score', 50) > 80]
        
        if len(popular_courses) > 10:  # 热门课程过多
            conflicts["complex_conflicts"].append({
                "type": "popular_course_competition",
                "course_count": len(popular_courses),
                "affected_courses": [c['id'] for c in popular_courses],
                "severity": "high"
            })
            
        return conflicts