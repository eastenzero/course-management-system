# file: data-generator/generators/teacher_course_matching.py
# 功能: 教师-课程专业匹配算法

from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import math
import random
from course_scheduling_constraints import (
    TeacherTitle, CourseType, DifficultyLevel, TeacherSpecialization
)


class MatchingMethod(Enum):
    """匹配方法枚举"""
    EXPERTISE_BASED = "基于专业领域"
    WORKLOAD_BALANCED = "基于工作负荷平衡"
    PREFERENCE_BASED = "基于时间偏好"
    COMPREHENSIVE = "综合评分"


@dataclass
class TeacherProfile:
    """教师档案"""
    teacher_id: str
    name: str
    title: TeacherTitle
    department: str
    specialization_areas: List[str]
    experience_years: int
    education_background: str
    research_interests: List[str]
    
    # 工作负荷相关
    max_courses_per_semester: int
    current_course_load: int = 0
    max_weekly_hours: int = 16
    current_weekly_hours: int = 0
    
    # 偏好设置
    preferred_course_types: List[CourseType] = field(default_factory=list)
    preferred_difficulty_levels: List[DifficultyLevel] = field(default_factory=list)
    preferred_time_slots: List[str] = field(default_factory=list)
    
    # 历史记录
    taught_courses: Set[str] = field(default_factory=set)
    teaching_evaluations: List[float] = field(default_factory=list)
    
    def get_average_evaluation(self) -> float:
        """获取平均教学评价"""
        return sum(self.teaching_evaluations) / len(self.teaching_evaluations) if self.teaching_evaluations else 4.0
        
    def can_teach_more_courses(self) -> bool:
        """检查是否可以承担更多课程"""
        return self.current_course_load < self.max_courses_per_semester
        
    def can_teach_more_hours(self, additional_hours: int) -> bool:
        """检查是否可以承担更多学时"""
        return self.current_weekly_hours + additional_hours <= self.max_weekly_hours


@dataclass
class CourseProfile:
    """课程档案"""
    course_id: str
    course_name: str
    course_type: CourseType
    difficulty_level: DifficultyLevel
    department: str
    subject_area: str
    weekly_hours: int
    total_hours: int
    credits: int
    student_capacity: int
    
    # 需求描述
    required_expertise: List[str]
    preferred_teacher_title: List[TeacherTitle]
    special_requirements: List[str] = field(default_factory=list)
    
    # 历史数据
    historical_teachers: Set[str] = field(default_factory=set)
    difficulty_rating: float = 3.0  # 1-5难度评级


class ExpertiseMatchingEngine:
    """专业领域匹配引擎"""
    
    def __init__(self):
        self.subject_keywords = self._load_subject_keywords()
        self.discipline_hierarchy = self._build_discipline_hierarchy()
        
    def _load_subject_keywords(self) -> Dict[str, List[str]]:
        """加载学科关键词库"""
        return {
            '数学': ['数学', '微积分', '线性代数', '概率', '统计', '离散', '数值', '建模'],
            '计算机科学': ['计算机', '编程', '算法', '数据结构', '软件', '系统', '网络', '数据库'],
            '人工智能': ['人工智能', '机器学习', '深度学习', '神经网络', '模式识别', '自然语言'],
            '软件工程': ['软件工程', '项目管理', '需求分析', '系统设计', '测试', '维护'],
            '物理': ['物理', '力学', '电磁', '热力', '光学', '量子', '电路'],
            '英语': ['英语', '听力', '口语', '阅读', '写作', '翻译', '文学'],
            '管理': ['管理', '经济', '商务', '市场', '财务', '人力资源', '运营']
        }
        
    def _build_discipline_hierarchy(self) -> Dict[str, Dict]:
        """构建学科层次结构"""
        return {
            '理工类': {
                '数学': ['基础数学', '应用数学', '统计学'],
                '计算机': ['计算机科学', '软件工程', '人工智能', '信息安全'],
                '物理': ['理论物理', '应用物理', '电子信息']
            },
            '文科类': {
                '语言': ['中文', '英语', '其他外语'],
                '管理': ['工商管理', '公共管理', '经济学']
            },
            '综合类': {
                '通识': ['思政', '体育', '艺术', '创新创业']
            }
        }
        
    def calculate_expertise_score(self, teacher: TeacherProfile, course: CourseProfile) -> float:
        """计算专业匹配度得分"""
        score = 0.0
        
        # 1. 直接专业领域匹配 (40%)
        direct_match_score = self._calculate_direct_match(teacher, course)
        score += direct_match_score * 0.4
        
        # 2. 关键词匹配 (30%)
        keyword_match_score = self._calculate_keyword_match(teacher, course)
        score += keyword_match_score * 0.3
        
        # 3. 学科层次匹配 (20%)
        hierarchy_match_score = self._calculate_hierarchy_match(teacher, course)
        score += hierarchy_match_score * 0.2
        
        # 4. 经验加成 (10%)
        experience_bonus = self._calculate_experience_bonus(teacher, course)
        score += experience_bonus * 0.1
        
        return min(1.0, score)
        
    def _calculate_direct_match(self, teacher: TeacherProfile, course: CourseProfile) -> float:
        """计算直接专业匹配"""
        matches = 0
        total_areas = len(teacher.specialization_areas)
        
        if total_areas == 0:
            return 0.0
            
        for area in teacher.specialization_areas:
            if area.lower() in course.subject_area.lower() or \
               course.subject_area.lower() in area.lower():
                matches += 1
                
        return matches / total_areas
        
    def _calculate_keyword_match(self, teacher: TeacherProfile, course: CourseProfile) -> float:
        """计算关键词匹配"""
        course_text = f"{course.course_name} {course.subject_area}".lower()
        teacher_text = " ".join(teacher.specialization_areas + teacher.research_interests).lower()
        
        total_matches = 0
        total_keywords = 0
        
        for subject, keywords in self.subject_keywords.items():
            subject_matches = 0
            for keyword in keywords:
                total_keywords += 1
                if keyword.lower() in course_text:
                    if keyword.lower() in teacher_text:
                        subject_matches += 1
                        total_matches += 1
                        
        return total_matches / max(1, total_keywords) if total_keywords > 0 else 0.0
        
    def _calculate_hierarchy_match(self, teacher: TeacherProfile, course: CourseProfile) -> float:
        """计算学科层次匹配"""
        teacher_dept = teacher.department.lower()
        course_dept = course.department.lower()
        
        # 同院系加分
        if teacher_dept == course_dept:
            return 1.0
            
        # 相关院系加分
        related_score = 0.0
        for category, disciplines in self.discipline_hierarchy.items():
            teacher_in_category = any(disc in teacher_dept for disc in disciplines.keys())
            course_in_category = any(disc in course_dept for disc in disciplines.keys())
            
            if teacher_in_category and course_in_category:
                related_score = 0.7
                break
                
        return related_score
        
    def _calculate_experience_bonus(self, teacher: TeacherProfile, course: CourseProfile) -> float:
        """计算经验加成"""
        # 教学经验年限加成
        experience_score = min(1.0, teacher.experience_years / 20.0)
        
        # 历史授课记录加成
        if course.course_id in teacher.taught_courses:
            experience_score += 0.5
            
        # 教学评价加成
        avg_evaluation = teacher.get_average_evaluation()
        evaluation_bonus = (avg_evaluation - 3.0) / 2.0  # 基于3.0基准，最高5.0
        
        return min(1.0, experience_score + evaluation_bonus)


class WorkloadBalancer:
    """工作负荷均衡器"""
    
    def __init__(self):
        self.load_weights = {
            'course_count': 0.4,
            'weekly_hours': 0.4,
            'difficulty_factor': 0.2
        }
        
    def calculate_workload_score(self, teacher: TeacherProfile, course: CourseProfile) -> float:
        """计算工作负荷评分 (分数越高表示负荷越轻，越适合分配)"""
        
        # 1. 课程数量负荷
        course_load_ratio = teacher.current_course_load / teacher.max_courses_per_semester
        course_score = 1.0 - course_load_ratio
        
        # 2. 学时负荷
        hours_load_ratio = teacher.current_weekly_hours / teacher.max_weekly_hours
        hours_score = 1.0 - hours_load_ratio
        
        # 3. 难度因子 (高难度课程对有经验教师的负荷相对较轻)
        difficulty_factor = self._calculate_difficulty_factor(teacher, course)
        
        # 综合评分
        total_score = (
            course_score * self.load_weights['course_count'] +
            hours_score * self.load_weights['weekly_hours'] +
            difficulty_factor * self.load_weights['difficulty_factor']
        )
        
        return max(0.0, total_score)
        
    def _calculate_difficulty_factor(self, teacher: TeacherProfile, course: CourseProfile) -> float:
        """计算难度因子"""
        # 教师职称与课程难度的适配性
        title_difficulty_mapping = {
            TeacherTitle.PROFESSOR: {
                DifficultyLevel.GRADUATE: 1.0,
                DifficultyLevel.ADVANCED: 0.9,
                DifficultyLevel.INTERMEDIATE: 0.7,
                DifficultyLevel.BASIC: 0.5
            },
            TeacherTitle.ASSOCIATE_PROFESSOR: {
                DifficultyLevel.GRADUATE: 0.8,
                DifficultyLevel.ADVANCED: 1.0,
                DifficultyLevel.INTERMEDIATE: 0.9,
                DifficultyLevel.BASIC: 0.6
            },
            TeacherTitle.LECTURER: {
                DifficultyLevel.GRADUATE: 0.4,
                DifficultyLevel.ADVANCED: 0.7,
                DifficultyLevel.INTERMEDIATE: 1.0,
                DifficultyLevel.BASIC: 0.9
            },
            TeacherTitle.ASSISTANT: {
                DifficultyLevel.GRADUATE: 0.2,
                DifficultyLevel.ADVANCED: 0.4,
                DifficultyLevel.INTERMEDIATE: 0.7,
                DifficultyLevel.BASIC: 1.0
            }
        }
        
        return title_difficulty_mapping.get(teacher.title, {}).get(course.difficulty_level, 0.5)
        
    def suggest_optimal_distribution(self, teachers: List[TeacherProfile], 
                                   courses: List[CourseProfile]) -> Dict[str, List[str]]:
        """建议最优工作负荷分配"""
        allocation = {teacher.teacher_id: [] for teacher in teachers}
        unassigned_courses = courses.copy()
        
        # 按课程重要性和难度排序
        unassigned_courses.sort(
            key=lambda c: (c.difficulty_level.value, c.course_type == CourseType.REQUIRED),
            reverse=True
        )
        
        for course in unassigned_courses:
            best_teacher = None
            best_score = -1
            
            for teacher in teachers:
                if not teacher.can_teach_more_courses() or \
                   not teacher.can_teach_more_hours(course.weekly_hours):
                    continue
                    
                workload_score = self.calculate_workload_score(teacher, course)
                
                if workload_score > best_score:
                    best_score = workload_score
                    best_teacher = teacher
                    
            if best_teacher:
                allocation[best_teacher.teacher_id].append(course.course_id)
                best_teacher.current_course_load += 1
                best_teacher.current_weekly_hours += course.weekly_hours
                
        return allocation


class TeacherCourseMatchingEngine:
    """教师-课程匹配引擎"""
    
    def __init__(self):
        self.expertise_engine = ExpertiseMatchingEngine()
        self.workload_balancer = WorkloadBalancer()
        
    def calculate_comprehensive_score(self, teacher: TeacherProfile, 
                                    course: CourseProfile,
                                    weight_config: Dict[str, float] = None) -> Tuple[float, Dict[str, float]]:
        """计算综合匹配得分"""
        if weight_config is None:
            weight_config = {
                'expertise': 0.4,
                'workload': 0.3,
                'title_match': 0.2,
                'preference': 0.1
            }
            
        scores = {}
        
        # 1. 专业匹配度
        scores['expertise'] = self.expertise_engine.calculate_expertise_score(teacher, course)
        
        # 2. 工作负荷适宜度
        scores['workload'] = self.workload_balancer.calculate_workload_score(teacher, course)
        
        # 3. 职称匹配度
        scores['title_match'] = self._calculate_title_match_score(teacher, course)
        
        # 4. 个人偏好匹配度
        scores['preference'] = self._calculate_preference_score(teacher, course)
        
        # 计算加权总分
        total_score = sum(
            scores[key] * weight_config.get(key, 0.0) 
            for key in scores
        )
        
        return total_score, scores
        
    def _calculate_title_match_score(self, teacher: TeacherProfile, course: CourseProfile) -> float:
        """计算职称匹配度"""
        preferred_titles = course.preferred_teacher_title
        
        if not preferred_titles:
            return 1.0  # 无特殊要求，任何职称都可以
            
        if teacher.title in preferred_titles:
            return 1.0
            
        # 基于职称等级的部分匹配
        title_hierarchy = {
            TeacherTitle.PROFESSOR: 4,
            TeacherTitle.ASSOCIATE_PROFESSOR: 3,
            TeacherTitle.LECTURER: 2,
            TeacherTitle.ASSISTANT: 1
        }
        
        teacher_level = title_hierarchy.get(teacher.title, 1)
        preferred_levels = [title_hierarchy.get(title, 1) for title in preferred_titles]
        
        min_diff = min(abs(teacher_level - level) for level in preferred_levels)
        
        # 差距越小分数越高
        return max(0.0, 1.0 - min_diff * 0.3)
        
    def _calculate_preference_score(self, teacher: TeacherProfile, course: CourseProfile) -> float:
        """计算个人偏好匹配度"""
        score = 0.0
        
        # 课程类型偏好
        if course.course_type in teacher.preferred_course_types:
            score += 0.5
        elif not teacher.preferred_course_types:  # 无特殊偏好
            score += 0.3
            
        # 难度等级偏好
        if course.difficulty_level in teacher.preferred_difficulty_levels:
            score += 0.5
        elif not teacher.preferred_difficulty_levels:  # 无特殊偏好
            score += 0.3
            
        return min(1.0, score)
        
    def find_best_matches(self, teachers: List[TeacherProfile], 
                         courses: List[CourseProfile],
                         top_n: int = 3) -> Dict[str, List[Tuple[str, float, Dict[str, float]]]]:
        """为每门课程找到最佳教师匹配"""
        course_matches = {}
        
        for course in courses:
            matches = []
            
            for teacher in teachers:
                # 基本可行性检查
                if not teacher.can_teach_more_courses() or \
                   not teacher.can_teach_more_hours(course.weekly_hours):
                    continue
                    
                total_score, detail_scores = self.calculate_comprehensive_score(teacher, course)
                matches.append((teacher.teacher_id, total_score, detail_scores))
                
            # 按分数排序，取前N个
            matches.sort(key=lambda x: x[1], reverse=True)
            course_matches[course.course_id] = matches[:top_n]
            
        return course_matches
        
    def optimize_global_assignment(self, teachers: List[TeacherProfile], 
                                 courses: List[CourseProfile]) -> Dict[str, str]:
        """全局优化分配算法"""
        assignment = {}
        teacher_workloads = {t.teacher_id: {'courses': 0, 'hours': 0} for t in teachers}
        
        # 创建教师ID到对象的映射
        teacher_dict = {t.teacher_id: t for t in teachers}
        
        # 按课程重要性排序
        sorted_courses = sorted(
            courses,
            key=lambda c: (
                c.course_type == CourseType.REQUIRED,  # 必修课优先
                c.difficulty_level.value,              # 高难度课程优先
                -c.student_capacity                     # 大班课程优先
            ),
            reverse=True
        )
        
        for course in sorted_courses:
            best_teacher_id = None
            best_score = -1
            
            for teacher in teachers:
                # 检查工作负荷限制
                current_load = teacher_workloads[teacher.teacher_id]
                if current_load['courses'] >= teacher.max_courses_per_semester or \
                   current_load['hours'] + course.weekly_hours > teacher.max_weekly_hours:
                    continue
                    
                # 计算匹配得分
                score, _ = self.calculate_comprehensive_score(teacher, course)
                
                # 考虑负荷均衡因子
                load_factor = 1.0 - (current_load['courses'] / teacher.max_courses_per_semester)
                adjusted_score = score * (0.7 + 0.3 * load_factor)
                
                if adjusted_score > best_score:
                    best_score = adjusted_score
                    best_teacher_id = teacher.teacher_id
                    
            if best_teacher_id:
                assignment[course.course_id] = best_teacher_id
                teacher_workloads[best_teacher_id]['courses'] += 1
                teacher_workloads[best_teacher_id]['hours'] += course.weekly_hours
                
        return assignment


def generate_realistic_teacher_profiles(count: int, departments: List[str]) -> List[TeacherProfile]:
    """生成真实的教师档案"""
    profiles = []
    
    # 职称分布 (基于真实大学统计)
    title_distribution = [
        (TeacherTitle.PROFESSOR, 0.15),
        (TeacherTitle.ASSOCIATE_PROFESSOR, 0.25),
        (TeacherTitle.LECTURER, 0.45),
        (TeacherTitle.ASSISTANT, 0.15)
    ]
    
    # 专业领域模板
    specialization_templates = {
        '计算机': ['计算机科学', '软件工程', '人工智能', '数据科学', '网络安全'],
        '数学': ['应用数学', '统计学', '运筹学', '数值计算', '数学建模'],
        '物理': ['理论物理', '应用物理', '电子信息', '光电技术'],
        '英语': ['英语语言文学', '翻译学', '应用语言学', '商务英语'],
        '管理': ['工商管理', '项目管理', '人力资源', '市场营销']
    }
    
    for i in range(count):
        # 随机选择职称
        title = random.choices(
            [t[0] for t in title_distribution],
            weights=[t[1] for t in title_distribution]
        )[0]
        
        # 随机选择院系
        department = random.choice(departments)
        
        # 根据院系确定专业领域
        dept_key = None
        for key in specialization_templates:
            if key in department:
                dept_key = key
                break
        
        if dept_key:
            specializations = random.sample(
                specialization_templates[dept_key], 
                random.randint(1, 3)
            )
        else:
            specializations = ['通用专业']
            
        # 根据职称确定经验年限和工作负荷
        if title == TeacherTitle.PROFESSOR:
            experience = random.randint(15, 30)
            max_courses = random.randint(2, 4)
            max_hours = random.randint(8, 12)
        elif title == TeacherTitle.ASSOCIATE_PROFESSOR:
            experience = random.randint(8, 20)
            max_courses = random.randint(3, 5)
            max_hours = random.randint(10, 14)
        elif title == TeacherTitle.LECTURER:
            experience = random.randint(3, 15)
            max_courses = random.randint(4, 6)
            max_hours = random.randint(12, 16)
        else:  # ASSISTANT
            experience = random.randint(1, 8)
            max_courses = random.randint(3, 5)
            max_hours = random.randint(8, 12)
            
        profile = TeacherProfile(
            teacher_id=f"T{i+1:06d}",
            name=f"教师{i+1}",
            title=title,
            department=department,
            specialization_areas=specializations,
            experience_years=experience,
            education_background=random.choice(['博士', '硕士', '学士']),
            research_interests=specializations[:2],
            max_courses_per_semester=max_courses,
            max_weekly_hours=max_hours,
            teaching_evaluations=[random.uniform(3.5, 4.8) for _ in range(random.randint(3, 8))]
        )
        
        profiles.append(profile)
        
    return profiles