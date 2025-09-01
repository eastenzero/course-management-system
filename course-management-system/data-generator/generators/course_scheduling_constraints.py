# file: data-generator/generators/course_scheduling_constraints.py
# 功能: 课程安排合理性标准和约束规则定义

from dataclasses import dataclass
from typing import Dict, List, Set, Tuple, Optional
from enum import Enum
import re


class TimeSlot(Enum):
    """时间段枚举"""
    MORNING_1 = "08:00-08:45"      # 第1节
    MORNING_2 = "08:50-09:35"      # 第2节
    MORNING_3 = "09:50-10:35"      # 第3节
    MORNING_4 = "10:40-11:25"      # 第4节
    MORNING_5 = "11:30-12:15"      # 第5节
    
    AFTERNOON_1 = "14:00-14:45"    # 第6节
    AFTERNOON_2 = "14:50-15:35"    # 第7节
    AFTERNOON_3 = "15:50-16:35"    # 第8节
    AFTERNOON_4 = "16:40-17:25"    # 第9节
    AFTERNOON_5 = "17:30-18:15"    # 第10节
    
    EVENING_1 = "19:00-19:45"      # 第11节
    EVENING_2 = "19:50-20:35"      # 第12节


class CourseType(Enum):
    """课程类型枚举"""
    REQUIRED = "必修课"            # 专业必修课
    ELECTIVE = "选修课"            # 专业选修课
    GENERAL = "通识课"             # 通识教育课
    EXPERIMENT = "实验课"          # 实验实践课
    THESIS = "论文课"              # 毕业论文/设计


class TeacherTitle(Enum):
    """教师职称枚举"""
    PROFESSOR = "教授"
    ASSOCIATE_PROFESSOR = "副教授"
    LECTURER = "讲师"
    ASSISTANT = "助教"


class DifficultyLevel(Enum):
    """课程难度等级"""
    BASIC = 1      # 基础课程
    INTERMEDIATE = 2  # 中级课程
    ADVANCED = 3   # 高级课程
    GRADUATE = 4   # 研究生课程


@dataclass
class TimeConstraint:
    """时间约束定义"""
    
    # 黄金时段定义 (优先安排核心课程)
    GOLDEN_SLOTS = [
        TimeSlot.MORNING_1, TimeSlot.MORNING_2, 
        TimeSlot.MORNING_3, TimeSlot.MORNING_4
    ]
    
    # 下午时段 (适合实践类课程)
    AFTERNOON_SLOTS = [
        TimeSlot.AFTERNOON_1, TimeSlot.AFTERNOON_2,
        TimeSlot.AFTERNOON_3, TimeSlot.AFTERNOON_4
    ]
    
    # 晚间时段 (选修课和补充课程)
    EVENING_SLOTS = [TimeSlot.EVENING_1, TimeSlot.EVENING_2]
    
    # 连续课程最大节数
    MAX_CONTINUOUS_CLASSES = 4
    
    # 同一天最大课时数
    MAX_DAILY_HOURS = 8
    
    # 教师每日最大授课时数
    TEACHER_MAX_DAILY_HOURS = 6


@dataclass
class PrerequisiteRule:
    """先修课程规则"""
    course_id: str
    prerequisites: List[str]
    semester_gap: int = 1  # 与先修课程的最小学期间隔


@dataclass
class TeacherSpecialization:
    """教师专业化定义"""
    teacher_id: str
    title: TeacherTitle
    specialization_areas: List[str]  # 专业领域
    experience_years: int
    max_courses_per_semester: int
    preferred_time_slots: List[TimeSlot]
    max_weekly_hours: int


@dataclass
class CourseSchedulingRule:
    """课程排课规则"""
    
    # 课程类型与时间段匹配规则
    COURSE_TIME_PREFERENCES = {
        CourseType.REQUIRED: TimeConstraint.GOLDEN_SLOTS,
        CourseType.EXPERIMENT: TimeConstraint.AFTERNOON_SLOTS,
        CourseType.ELECTIVE: TimeConstraint.AFTERNOON_SLOTS + TimeConstraint.EVENING_SLOTS,
        CourseType.GENERAL: TimeConstraint.GOLDEN_SLOTS + TimeConstraint.AFTERNOON_SLOTS,
        CourseType.THESIS: TimeConstraint.AFTERNOON_SLOTS
    }
    
    # 教师职称与课程类型匹配规则
    TEACHER_COURSE_MATCHING = {
        TeacherTitle.PROFESSOR: [CourseType.REQUIRED, CourseType.ELECTIVE, CourseType.THESIS],
        TeacherTitle.ASSOCIATE_PROFESSOR: [CourseType.REQUIRED, CourseType.ELECTIVE, CourseType.EXPERIMENT],
        TeacherTitle.LECTURER: [CourseType.GENERAL, CourseType.ELECTIVE, CourseType.EXPERIMENT],
        TeacherTitle.ASSISTANT: [CourseType.EXPERIMENT, CourseType.GENERAL]
    }
    
    # 课程难度与教师职称匹配
    DIFFICULTY_TEACHER_MATCHING = {
        DifficultyLevel.GRADUATE: [TeacherTitle.PROFESSOR],
        DifficultyLevel.ADVANCED: [TeacherTitle.PROFESSOR, TeacherTitle.ASSOCIATE_PROFESSOR],
        DifficultyLevel.INTERMEDIATE: [TeacherTitle.ASSOCIATE_PROFESSOR, TeacherTitle.LECTURER],
        DifficultyLevel.BASIC: [TeacherTitle.LECTURER, TeacherTitle.ASSISTANT]
    }


class CourseSchedulingConstraints:
    """课程排课约束验证器"""
    
    def __init__(self):
        self.prerequisite_rules: Dict[str, PrerequisiteRule] = {}
        self.teacher_specializations: Dict[str, TeacherSpecialization] = {}
        self.scheduling_rules = CourseSchedulingRule()
        
    def add_prerequisite_rule(self, rule: PrerequisiteRule):
        """添加先修课程规则"""
        self.prerequisite_rules[rule.course_id] = rule
        
    def add_teacher_specialization(self, spec: TeacherSpecialization):
        """添加教师专业化信息"""
        self.teacher_specializations[spec.teacher_id] = spec
        
    def validate_time_conflict(self, teacher_id: str, time_slot: TimeSlot, 
                             day: str, existing_schedule: Dict) -> bool:
        """验证时间冲突"""
        key = f"{teacher_id}_{day}_{time_slot.value}"
        return key not in existing_schedule
        
    def validate_prerequisite(self, course_id: str, student_completed_courses: Set[str], 
                            current_semester: int, course_semesters: Dict[str, int]) -> bool:
        """验证先修课程要求"""
        if course_id not in self.prerequisite_rules:
            return True
            
        rule = self.prerequisite_rules[course_id]
        
        # 检查所有先修课程是否已完成
        for prereq in rule.prerequisites:
            if prereq not in student_completed_courses:
                return False
                
            # 检查学期间隔
            if prereq in course_semesters:
                prereq_semester = course_semesters[prereq]
                if current_semester - prereq_semester < rule.semester_gap:
                    return False
                    
        return True
        
    def validate_teacher_course_match(self, teacher_id: str, course_type: CourseType, 
                                    difficulty: DifficultyLevel, 
                                    course_subject: str) -> Tuple[bool, float]:
        """验证教师-课程匹配度"""
        if teacher_id not in self.teacher_specializations:
            return False, 0.0
            
        teacher = self.teacher_specializations[teacher_id]
        match_score = 0.0
        
        # 1. 职称与课程类型匹配
        allowed_types = self.scheduling_rules.TEACHER_COURSE_MATCHING.get(teacher.title, [])
        if course_type not in allowed_types:
            return False, 0.0
        match_score += 0.4
        
        # 2. 职称与课程难度匹配
        allowed_titles = self.scheduling_rules.DIFFICULTY_TEACHER_MATCHING.get(difficulty, [])
        if teacher.title not in allowed_titles:
            return False, 0.0
        match_score += 0.3
        
        # 3. 专业领域匹配
        specialization_match = any(
            spec.lower() in course_subject.lower() 
            for spec in teacher.specialization_areas
        )
        if specialization_match:
            match_score += 0.3
        else:
            match_score += 0.1  # 基础分
            
        return True, match_score
        
    def validate_classroom_capacity(self, classroom_capacity: int, 
                                  enrolled_students: int, 
                                  safety_margin: float = 0.1) -> bool:
        """验证教室容量约束"""
        max_allowed = int(classroom_capacity * (1 + safety_margin))
        return enrolled_students <= max_allowed
        
    def validate_weekly_distribution(self, course_schedule: List[Tuple[str, TimeSlot]], 
                                   max_per_day: int = 2) -> bool:
        """验证周内分布合理性"""
        daily_count = {}
        
        for day, time_slot in course_schedule:
            daily_count[day] = daily_count.get(day, 0) + 1
            if daily_count[day] > max_per_day:
                return False
                
        return True
        
    def get_optimal_time_slot(self, course_type: CourseType, 
                            teacher_preferences: List[TimeSlot],
                            available_slots: List[TimeSlot]) -> Optional[TimeSlot]:
        """获取最优时间段"""
        preferred_slots = self.scheduling_rules.COURSE_TIME_PREFERENCES.get(course_type, [])
        
        # 优先考虑课程类型偏好
        for slot in preferred_slots:
            if slot in available_slots:
                return slot
                
        # 其次考虑教师偏好
        for slot in teacher_preferences:
            if slot in available_slots:
                return slot
                
        # 最后选择任意可用时段
        return available_slots[0] if available_slots else None


class CourseRealismValidator:
    """课程真实性验证器"""
    
    def __init__(self):
        self.realistic_patterns = self._load_realistic_patterns()
        
    def _load_realistic_patterns(self) -> Dict:
        """加载真实性模式库"""
        return {
            # 课程名称模式
            'course_name_patterns': {
                '数学类': ['高等数学', '线性代数', '概率论与数理统计', '离散数学'],
                '计算机类': ['程序设计', '数据结构', '算法设计', '操作系统', '数据库'],
                '英语类': ['大学英语', '专业英语', '英语听说', '英语写作'],
                '物理类': ['大学物理', '电路分析', '数字电路', '模拟电路']
            },
            
            # 学分分布模式
            'credit_patterns': {
                CourseType.REQUIRED: (2, 4),      # 必修课2-4学分
                CourseType.ELECTIVE: (1, 3),      # 选修课1-3学分
                CourseType.GENERAL: (1, 2),       # 通识课1-2学分
                CourseType.EXPERIMENT: (1, 2),    # 实验课1-2学分
                CourseType.THESIS: (4, 8)         # 论文课4-8学分
            },
            
            # 学时分布模式
            'hour_patterns': {
                CourseType.REQUIRED: (32, 64),    # 必修课32-64学时
                CourseType.ELECTIVE: (16, 48),    # 选修课16-48学时
                CourseType.GENERAL: (16, 32),     # 通识课16-32学时
                CourseType.EXPERIMENT: (16, 32),  # 实验课16-32学时
                CourseType.THESIS: (64, 128)      # 论文课64-128学时
            }
        }
        
    def validate_course_credits(self, course_type: CourseType, credits: int) -> bool:
        """验证学分合理性"""
        min_credits, max_credits = self.realistic_patterns['credit_patterns'][course_type]
        return min_credits <= credits <= max_credits
        
    def validate_course_hours(self, course_type: CourseType, hours: int) -> bool:
        """验证学时合理性"""
        min_hours, max_hours = self.realistic_patterns['hour_patterns'][course_type]
        return min_hours <= hours <= max_hours
        
    def validate_course_name(self, course_name: str, department: str) -> bool:
        """验证课程名称真实性"""
        # 检查是否包含学科相关关键词
        for category, patterns in self.realistic_patterns['course_name_patterns'].items():
            if any(pattern in course_name for pattern in patterns):
                return True
                
        # 检查是否包含院系相关关键词
        if department.lower() in course_name.lower():
            return True
            
        return False
        
    def calculate_realism_score(self, course_data: Dict) -> float:
        """计算课程真实性得分"""
        score = 0.0
        total_checks = 4
        
        # 检查学分合理性
        if self.validate_course_credits(course_data.get('type'), course_data.get('credits', 0)):
            score += 0.25
            
        # 检查学时合理性
        if self.validate_course_hours(course_data.get('type'), course_data.get('hours', 0)):
            score += 0.25
            
        # 检查课程名称真实性
        if self.validate_course_name(course_data.get('name', ''), course_data.get('department', '')):
            score += 0.25
            
        # 检查先修关系合理性
        if course_data.get('prerequisites'):
            # 简单检查：先修课程数量不超过3个
            if len(course_data['prerequisites']) <= 3:
                score += 0.25
        else:
            score += 0.25  # 无先修课程也是合理的
            
        return score


# 预定义的课程依赖关系模板
STANDARD_PREREQUISITE_CHAINS = {
    # 数学课程链
    'math_chain': [
        PrerequisiteRule('高等数学A2', ['高等数学A1'], 1),
        PrerequisiteRule('线性代数', ['高等数学A1'], 1),
        PrerequisiteRule('概率论与数理统计', ['高等数学A2', '线性代数'], 1),
    ],
    
    # 计算机课程链
    'cs_chain': [
        PrerequisiteRule('数据结构', ['程序设计基础'], 1),
        PrerequisiteRule('算法设计与分析', ['数据结构'], 1),
        PrerequisiteRule('操作系统', ['数据结构'], 1),
        PrerequisiteRule('数据库系统', ['数据结构'], 1),
        PrerequisiteRule('编译原理', ['算法设计与分析'], 1),
    ],
    
    # 物理课程链
    'physics_chain': [
        PrerequisiteRule('电路分析', ['大学物理'], 1),
        PrerequisiteRule('数字电路', ['电路分析'], 1),
        PrerequisiteRule('模拟电路', ['电路分析'], 1),
        PrerequisiteRule('计算机组成原理', ['数字电路'], 1),
    ]
}


# 预定义的教师专业化模板
STANDARD_TEACHER_SPECIALIZATIONS = {
    'math_professor': TeacherSpecialization(
        teacher_id='',  # 动态分配
        title=TeacherTitle.PROFESSOR,
        specialization_areas=['数学', '统计学', '应用数学'],
        experience_years=15,
        max_courses_per_semester=3,
        preferred_time_slots=TimeConstraint.GOLDEN_SLOTS,
        max_weekly_hours=12
    ),
    
    'cs_associate_prof': TeacherSpecialization(
        teacher_id='',
        title=TeacherTitle.ASSOCIATE_PROFESSOR,
        specialization_areas=['计算机科学', '软件工程', '人工智能'],
        experience_years=8,
        max_courses_per_semester=4,
        preferred_time_slots=TimeConstraint.GOLDEN_SLOTS + TimeConstraint.AFTERNOON_SLOTS[:2],
        max_weekly_hours=14
    ),
    
    'experiment_lecturer': TeacherSpecialization(
        teacher_id='',
        title=TeacherTitle.LECTURER,
        specialization_areas=['实验教学', '工程实践'],
        experience_years=5,
        max_courses_per_semester=5,
        preferred_time_slots=TimeConstraint.AFTERNOON_SLOTS,
        max_weekly_hours=16
    )
}