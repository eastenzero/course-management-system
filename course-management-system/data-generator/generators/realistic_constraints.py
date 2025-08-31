# file: data-generator/generators/realistic_constraints.py
# 功能: 真实性约束模块 - 提升数据生成的真实性

import random
import numpy as np
from typing import List, Dict, Any, Tuple
from datetime import datetime, time, timedelta
from dataclasses import dataclass


@dataclass
class TimePreferenceProfile:
    """教师时间偏好配置文件"""
    age_group: str  # "young", "middle", "senior"
    title: str     # "教授", "副教授", "讲师", "助教"
    morning_preference: float    # 0-1
    afternoon_preference: float  # 0-1
    evening_preference: float    # 0-1
    continuous_preference: float # 连续授课偏好 0-1
    max_daily_hours: int        # 每日最大授课时数
    preferred_break_duration: int # 偏好的课间休息时长(分钟)


class RealisticConstraintsEngine:
    """真实性约束引擎
    
    基于真实大学运营规律生成符合实际的数据分布和约束
    """
    
    def __init__(self):
        self.setup_realistic_distributions()
        self.setup_teacher_profiles()
        self.setup_course_patterns()
        
    def setup_realistic_distributions(self):
        """设置真实的概率分布"""
        
        # 时间偏好分布 - 基于真实大学作息调研
        self.time_preference_weights = {
            '8:00-10:00': 0.75,   # 黄金时间段
            '10:00-12:00': 0.85,  # 最佳时间段
            '14:00-16:00': 0.80,  # 良好时间段
            '16:00-18:00': 0.65,  # 一般时间段
            '19:00-21:00': 0.35   # 晚间时间段
        }
        
        # 课程热度分布 - 帕累托分布(80-20法则)
        self.course_popularity_alpha = 1.16  # 形状参数
        
        # 教室利用率分布 - 正态分布
        self.classroom_utilization_mean = 0.75
        self.classroom_utilization_std = 0.15
        
        # 学生选课行为分布
        self.student_course_load_mean = 18  # 平均学分
        self.student_course_load_std = 3
        
    def setup_teacher_profiles(self):
        """设置教师偏好配置文件"""
        
        self.teacher_profiles = {
            "young_lecturer": TimePreferenceProfile(
                age_group="young",
                title="讲师",
                morning_preference=0.6,
                afternoon_preference=0.8,
                evening_preference=0.7,
                continuous_preference=0.4,
                max_daily_hours=6,
                preferred_break_duration=15
            ),
            "middle_associate": TimePreferenceProfile(
                age_group="middle", 
                title="副教授",
                morning_preference=0.8,
                afternoon_preference=0.7,
                evening_preference=0.3,
                continuous_preference=0.6,
                max_daily_hours=5,
                preferred_break_duration=20
            ),
            "senior_professor": TimePreferenceProfile(
                age_group="senior",
                title="教授", 
                morning_preference=0.9,
                afternoon_preference=0.5,
                evening_preference=0.1,
                continuous_preference=0.8,
                max_daily_hours=4,
                preferred_break_duration=30
            )
        }
        
    def setup_course_patterns(self):
        """设置课程模式"""
        
        # 课程类型与时间偏好映射
        self.course_time_patterns = {
            "理论课": {"preferred_duration": 2, "preferred_times": ["10:00-12:00", "14:00-16:00"]},
            "实验课": {"preferred_duration": 3, "preferred_times": ["14:00-17:00", "16:00-19:00"]},
            "讨论课": {"preferred_duration": 1, "preferred_times": ["16:00-17:00", "19:00-20:00"]},
            "大班课": {"preferred_duration": 2, "preferred_times": ["10:00-12:00", "14:00-16:00"]}
        }
        
        # 学科与教室类型匹配
        self.subject_classroom_mapping = {
            "计算机": ["机房", "多媒体教室"],
            "化学": ["实验室", "多媒体教室"],
            "物理": ["实验室", "多媒体教室"], 
            "数学": ["普通教室", "多媒体教室"],
            "文科": ["普通教室", "研讨室"],
            "艺术": ["专业教室", "工作室"]
        }

    def generate_realistic_teacher_preferences(self, teacher: Dict[str, Any]) -> Dict[str, Any]:
        """基于教师特征生成真实的时间偏好
        
        Args:
            teacher: 教师基本信息
            
        Returns:
            真实的时间偏好数据
        """
        # 确定教师类型
        birth_year = teacher.get('birth_year')
        if birth_year is None:
            # 如果没有birth_year，使用默认值
            age = 35
        else:
            try:
                if isinstance(birth_year, str):
                    birth_year = int(birth_year)
                age = 2024 - birth_year
            except (ValueError, TypeError):
                age = 35  # 默认年龄
                
        title = teacher.get('title', '讲师')
        
        if age < 35:
            profile_key = "young_lecturer"
        elif age < 50:
            profile_key = "middle_associate" 
        else:
            profile_key = "senior_professor"
            
        profile = self.teacher_profiles[profile_key]
        
        # 生成每日每时段的偏好分数
        weekly_preferences = {}
        
        for day in range(1, 6):  # 周一到周五
            daily_prefs = {}
            daily_load = 0
            
            for hour in range(8, 21):  # 8:00-21:00
                time_slot = f"{hour:02d}:00"
                
                # 基础偏好分数
                base_score = self._calculate_base_preference(hour, profile)
                
                # 连续性调整
                continuity_bonus = self._calculate_continuity_bonus(hour, daily_prefs, profile)
                
                # 日负荷调整  
                load_penalty = self._calculate_load_penalty(daily_load, profile.max_daily_hours)
                
                # 随机波动
                random_factor = np.random.normal(0, 0.1)
                
                final_score = max(0, min(1, base_score + continuity_bonus - load_penalty + random_factor))
                
                daily_prefs[time_slot] = {
                    "preference_score": round(final_score, 3),
                    "is_available": final_score > 0.3,
                    "max_continuous_hours": self._calculate_max_continuous(hour, profile)
                }
                
                if final_score > 0.5:
                    daily_load += 1
                    
            weekly_preferences[f"day_{day}"] = daily_prefs
            
        return {
            "teacher_id": teacher['id'],
            "profile_type": profile_key,
            "weekly_preferences": weekly_preferences,
            "constraints": {
                "max_daily_hours": profile.max_daily_hours,
                "min_break_minutes": profile.preferred_break_duration,
                "no_back_to_back_days": title == "教授"  # 教授避免连续两天
            }
        }

    def _calculate_base_preference(self, hour: int, profile: TimePreferenceProfile) -> float:
        """计算基础时间偏好分数"""
        if 8 <= hour < 12:  # 上午
            return profile.morning_preference
        elif 14 <= hour < 18:  # 下午
            return profile.afternoon_preference  
        elif 19 <= hour <= 21:  # 晚上
            return profile.evening_preference
        else:
            return 0.1  # 其他时间很低偏好
            
    def _calculate_continuity_bonus(self, hour: int, daily_prefs: Dict, profile: TimePreferenceProfile) -> float:
        """计算连续性奖励"""
        if not daily_prefs:
            return 0
            
        prev_hour_key = f"{hour-1:02d}:00"
        if prev_hour_key in daily_prefs and daily_prefs[prev_hour_key]["preference_score"] > 0.5:
            return profile.continuous_preference * 0.2
        return 0
        
    def _calculate_load_penalty(self, current_load: int, max_hours: int) -> float:
        """计算日负荷惩罚"""
        if current_load >= max_hours:
            return 0.8  # 严重惩罚
        elif current_load >= max_hours * 0.8:
            return 0.3  # 中等惩罚
        return 0
        
    def _calculate_max_continuous(self, hour: int, profile: TimePreferenceProfile) -> int:
        """计算最大连续授课时数"""
        if profile.title == "教授":
            return 2  # 教授最多连续2小时
        elif profile.title == "副教授":
            return 3  # 副教授最多连续3小时
        else:
            return 4  # 讲师可以连续4小时

    def generate_realistic_course_distribution(self, courses: List[Dict], departments: List[Dict]) -> List[Dict]:
        """生成真实的课程分布特征
        
        Args:
            courses: 课程列表
            departments: 院系列表
            
        Returns:
            增强了真实性的课程列表
        """
        enhanced_courses = []
        
        # 生成课程热度分布(帕累托分布)
        popularities = np.random.pareto(self.course_popularity_alpha, len(courses))
        popularities = (popularities / popularities.max()) * 100  # 标准化到0-100
        
        for i, course in enumerate(courses):
            enhanced_course = course.copy()
            
            # 设置课程热度
            popularity = min(100, max(10, popularities[i]))
            enhanced_course['popularity_score'] = round(popularity, 1)
            
            # 基于热度调整最大选课人数
            base_capacity = enhanced_course.get('max_students', 50)
            if popularity > 80:  # 热门课程
                enhanced_course['max_students'] = int(base_capacity * 1.5)
                enhanced_course['difficulty_multiplier'] = 1.3  # 增加排课难度
            elif popularity < 30:  # 冷门课程
                enhanced_course['max_students'] = int(base_capacity * 0.7)
                enhanced_course['difficulty_multiplier'] = 0.8
            else:
                enhanced_course['difficulty_multiplier'] = 1.0
                
            # 设置课程时间模式偏好
            course_type = self._determine_course_type(enhanced_course['name'])
            enhanced_course['time_pattern'] = self.course_time_patterns.get(course_type, 
                                                                          self.course_time_patterns['理论课'])
            
            # 设置教室需求
            subject = self._extract_subject(enhanced_course['name'])
            enhanced_course['preferred_classroom_types'] = self.subject_classroom_mapping.get(subject, 
                                                                                             ["普通教室"])
            
            enhanced_courses.append(enhanced_course)
            
        return enhanced_courses

    def _determine_course_type(self, course_name: str) -> str:
        """根据课程名称确定课程类型"""
        if any(keyword in course_name for keyword in ["实验", "实践", "上机"]):
            return "实验课"
        elif any(keyword in course_name for keyword in ["讨论", "研讨", "seminar"]):
            return "讨论课"
        elif any(keyword in course_name for keyword in ["导论", "概论", "基础"]):
            return "大班课"
        else:
            return "理论课"
            
    def _extract_subject(self, course_name: str) -> str:
        """从课程名称提取学科类别"""
        if any(keyword in course_name for keyword in ["计算机", "编程", "算法", "软件", "网络"]):
            return "计算机"
        elif any(keyword in course_name for keyword in ["化学", "有机", "无机"]):
            return "化学"
        elif any(keyword in course_name for keyword in ["物理", "力学", "电磁"]):
            return "物理"
        elif any(keyword in course_name for keyword in ["数学", "微积分", "线性代数", "概率"]):
            return "数学"
        elif any(keyword in course_name for keyword in ["文学", "语言", "历史", "哲学"]):
            return "文科"
        else:
            return "通用"

    def generate_realistic_student_enrollment_patterns(self, students: List[Dict], courses: List[Dict]) -> List[Dict]:
        """生成真实的学生选课模式
        
        Args:
            students: 学生列表
            courses: 课程列表
            
        Returns:
            真实的选课记录列表
        """
        enrollments = []
        enrollment_id = 1
        
        for student in students:
            # 确定学生选课负荷(正态分布)
            target_credits = max(12, min(25, int(np.random.normal(self.student_course_load_mean, 
                                                                 self.student_course_load_std))))
            
            selected_courses = self._select_courses_realistically(student, courses, target_credits)
            
            for course in selected_courses:
                enrollment = {
                    'id': enrollment_id,
                    'student_id': student['id'],
                    'course_id': course['id'], 
                    'selection_priority': course.get('selection_priority', 1),
                    'selection_reason': self._generate_selection_reason(student, course),
                    'enrollment_timestamp': self._generate_realistic_enrollment_time(),
                    'is_major_required': self._is_major_required(student, course),
                    'expected_grade': self._predict_expected_grade(student, course)
                }
                enrollments.append(enrollment)
                enrollment_id += 1
                
        return enrollments
        
    def _select_courses_realistically(self, student: Dict, courses: List[Dict], target_credits: int) -> List[Dict]:
        """为学生真实地选择课程"""
        available_courses = []
        student_major = student.get('major', '')
        student_year = student.get('year', 1)
        
        # 筛选适合的课程
        for course in courses:
            # 专业匹配性检查
            major_match_score = self._calculate_major_match_score(student_major, course)
            
            # 年级适配性检查
            year_suitable = self._is_year_suitable(student_year, course)
            
            # 热度影响(热门课程更容易被选择)
            popularity_bonus = course.get('popularity_score', 50) / 100
            
            if year_suitable and major_match_score > 0.2:
                course['selection_weight'] = major_match_score + popularity_bonus
                available_courses.append(course)
        
        # 按权重排序并选择
        available_courses.sort(key=lambda x: x['selection_weight'], reverse=True)
        
        selected_courses = []
        current_credits = 0
        
        for course in available_courses:
            if current_credits + course.get('credits', 3) <= target_credits:
                selected_courses.append(course)
                current_credits += course.get('credits', 3)
                
                if current_credits >= target_credits * 0.9:  # 达到90%目标即可
                    break
                    
        return selected_courses
        
    def _calculate_major_match_score(self, student_major: str, course: Dict) -> float:
        """计算专业匹配分数"""
        course_name = course.get('name', '')
        
        # 必修课程匹配度最高
        if course.get('course_type') == '必修':
            return 0.9
            
        # 专业相关课程
        if student_major in course_name or any(keyword in course_name 
                                              for keyword in student_major.split()):
            return 0.8
            
        # 通识课程
        if course.get('course_type') == '通识':
            return 0.4
            
        # 其他选修课程
        return 0.3
        
    def _is_year_suitable(self, student_year: int, course: Dict) -> bool:
        """检查年级适配性"""
        course_level = course.get('difficulty_level', 1)
        
        # 确保course_level是数字类型
        if isinstance(course_level, str):
            try:
                course_level = int(course_level)
            except (ValueError, TypeError):
                course_level = 1
        
        # 基础课程适合低年级
        if course_level <= 2 and student_year <= 2:
            return True
        # 高级课程适合高年级    
        elif course_level > 2 and student_year >= 2:
            return True
        # 通识课程适合所有年级
        elif course.get('course_type') == '通识':
            return True
        else:
            return False
            
    def _generate_selection_reason(self, student: Dict, course: Dict) -> str:
        """生成选课原因"""
        reasons = []
        
        if course.get('course_type') == '必修':
            reasons.append("专业必修")
        elif self._calculate_major_match_score(student.get('major', ''), course) > 0.7:
            reasons.append("专业相关")
        elif course.get('popularity_score', 0) > 80:
            reasons.append("热门课程")
        else:
            reasons.append("兴趣选择")
            
        return random.choice(reasons)
        
    def _generate_realistic_enrollment_time(self) -> datetime:
        """生成真实的选课时间(集中在选课时间段)"""
        # 模拟选课高峰期
        base_time = datetime(2024, 8, 15, 9, 0)  # 选课开始时间
        
        # 80%的选课发生在前3天
        if random.random() < 0.8:
            offset_hours = random.randint(0, 72)
        else:
            offset_hours = random.randint(0, 168)  # 一周内
            
        return base_time + timedelta(hours=offset_hours)
        
    def _is_major_required(self, student: Dict, course: Dict) -> bool:
        """判断是否为专业必修课"""
        return (course.get('course_type') == '必修' and 
                self._calculate_major_match_score(student.get('major', ''), course) > 0.7)
                
    def _predict_expected_grade(self, student: Dict, course: Dict) -> float:
        """预测期望成绩"""
        base_grade = 75  # 基础分数
        
        # 专业匹配度影响
        major_match = self._calculate_major_match_score(student.get('major', ''), course)
        base_grade += major_match * 10
        
        # 课程难度影响
        difficulty = course.get('difficulty_level', 1)
        base_grade -= (difficulty - 1) * 5
        
        # 学生能力影响(随机因素)
        ability_factor = random.uniform(-10, 15)
        
        return max(60, min(100, base_grade + ability_factor))