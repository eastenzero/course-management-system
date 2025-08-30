# file: data-generator/generators/scenario.py
# 功能: 复杂场景数据生成器

import random
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date, timedelta
from faker import Faker


class ComplexScenarioGenerator:
    """复杂场景数据生成器
    
    负责生成复杂的业务场景数据，包括：
    - 选课数据和冲突
    - 教师时间偏好
    - 各种约束和冲突场景
    - 排课难点模拟
    """
    
    def __init__(self, locale: str = 'zh_CN'):
        """初始化生成器
        
        Args:
            locale: 本地化设置，默认为中文
        """
        self.fake = Faker(locale)
        
        # 设置随机种子
        Faker.seed(42)
        random.seed(42)
    
    def generate_enrollment_data(self, students: List[Dict[str, Any]], 
                               courses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成选课数据 - 创造复杂的选课场景
        
        Args:
            students: 学生数据列表
            courses: 课程数据列表
            
        Returns:
            选课数据列表
        """
        enrollments = []
        enrollment_id = 1
        
        # 创建专业-课程映射，便于筛选合适课程
        major_course_map = self._create_major_course_mapping(students, courses)
        
        for student in students:
            # 每个学生选择5-8门课程
            num_courses = random.randint(5, 8)
            
            # 根据学生专业和年级选择合适的课程
            suitable_courses = self._filter_suitable_courses(student, courses, major_course_map)
            
            if len(suitable_courses) < num_courses:
                # 如果合适课程不够，添加一些通识课程
                general_courses = [c for c in courses if c['course_type'] == '通识']
                suitable_courses.extend(random.sample(general_courses, 
                                                    min(num_courses - len(suitable_courses), 
                                                        len(general_courses))))
            
            if len(suitable_courses) >= num_courses:
                selected_courses = random.sample(suitable_courses, num_courses)
            else:
                selected_courses = suitable_courses
            
            for course in selected_courses:
                enrollment = {
                    'id': enrollment_id,
                    'student_id': student['id'],
                    'course_id': course['id'],
                    'semester': f"{random.randint(2023, 2024)}-{random.randint(1, 2)}",
                    'academic_year': f"{random.randint(2023, 2024)}-{random.randint(2024, 2025)}",
                    'enrollment_type': random.choices(['正常选课', '补选', '重修', '旁听'], weights=[0.8, 0.1, 0.08, 0.02])[0],
                    'status': random.choices(['已选', '待审核', '已退课', '已完成'], weights=[0.7, 0.15, 0.1, 0.05])[0],
                    'priority': random.randint(1, 5),  # 选课优先级
                    'selection_time': self.fake.date_time_between(start_date='-3m', end_date='-1m'),
                    'grade': self._generate_course_grade(enrollment_id),
                    'attendance_rate': round(random.uniform(0.6, 1.0), 2),
                    'midterm_score': random.randint(60, 100) if random.random() < 0.8 else None,
                    'final_score': random.randint(60, 100) if random.random() < 0.9 else None,
                    'total_score': None,  # 将根据其他分数计算
                    'gpa_points': None,  # 将根据总分计算
                    'is_retake': random.choices([True, False], weights=[0.1, 0.9])[0],
                    'retake_count': random.randint(0, 2) if random.random() < 0.1 else 0,
                    'withdrawal_reason': self._generate_withdrawal_reason() if random.random() < 0.05 else None,
                    'special_notes': self._generate_special_notes(),
                    'created_at': self.fake.date_time_between(start_date='-1y', end_date='now'),
                    'updated_at': self.fake.date_time_between(start_date='-1m', end_date='now')
                }
                
                # 计算总分和GPA
                enrollment['total_score'] = self._calculate_total_score(enrollment)
                enrollment['gpa_points'] = self._calculate_gpa_points(enrollment['total_score'])
                
                enrollments.append(enrollment)
                enrollment_id += 1
        
        return enrollments
    
    def generate_teacher_preferences(self, teachers: List[Dict[str, Any]], 
                                   time_slots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成教师时间偏好数据
        
        Args:
            teachers: 教师数据列表
            time_slots: 时间段数据列表
            
        Returns:
            教师偏好数据列表
        """
        preferences = []
        preference_id = 1
        
        for teacher in teachers:
            # 为每个教师生成一周的时间偏好
            for day in range(1, 6):  # 周一到周五
                for time_slot in time_slots:
                    
                    # 生成偏好分数 (0-1之间)
                    preference_score = self._calculate_teacher_preference_score(
                        day, time_slot, teacher
                    )
                    
                    preference = {
                        'id': preference_id,
                        'teacher_id': teacher['id'],
                        'day_of_week': day,
                        'time_slot_id': time_slot['id'],
                        'preference_score': preference_score,
                        'preference_level': self._score_to_level(preference_score),
                        'reason': self._generate_preference_reason(preference_score, teacher),
                        'is_available': preference_score > 0.2,  # 低于0.2认为不可用
                        'max_courses': self._calculate_max_courses_per_slot(preference_score),
                        'preferred_course_types': self._generate_preferred_course_types(teacher),
                        'avoid_back_to_back': random.choices([True, False], weights=[0.3, 0.7])[0],
                        'travel_time_needed': random.randint(0, 30),  # 换教室需要的时间（分钟）
                        'special_requirements': self._generate_special_requirements(teacher),
                        'flexibility': random.uniform(0.1, 0.9),  # 时间灵活性
                        'created_at': self.fake.date_time_between(start_date='-1y', end_date='now'),
                        'updated_at': self.fake.date_time_between(start_date='-1m', end_date='now')
                    }
                    preferences.append(preference)
                    preference_id += 1
        
        return preferences
    
    def generate_conflict_scenarios(self, courses: List[Dict[str, Any]], 
                                  teachers: List[Dict[str, Any]], 
                                  classrooms: List[Dict[str, Any]],
                                  students: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成冲突场景数据
        
        Args:
            courses: 课程数据列表
            teachers: 教师数据列表
            classrooms: 教室数据列表
            students: 学生数据列表
            
        Returns:
            冲突场景数据列表
        """
        conflicts = []
        conflict_id = 1
        
        # 1. 教师时间冲突
        teacher_conflicts = self._generate_teacher_conflicts(teachers, courses)
        for conflict in teacher_conflicts:
            conflict['id'] = conflict_id
            conflicts.append(conflict)
            conflict_id += 1
        
        # 2. 教室资源冲突
        classroom_conflicts = self._generate_classroom_conflicts(classrooms, courses)
        for conflict in classroom_conflicts:
            conflict['id'] = conflict_id
            conflicts.append(conflict)
            conflict_id += 1
        
        # 3. 学生选课冲突
        student_conflicts = self._generate_student_conflicts(students, courses)
        for conflict in student_conflicts:
            conflict['id'] = conflict_id
            conflicts.append(conflict)
            conflict_id += 1
        
        # 4. 课程依赖冲突
        dependency_conflicts = self._generate_dependency_conflicts(courses)
        for conflict in dependency_conflicts:
            conflict['id'] = conflict_id
            conflicts.append(conflict)
            conflict_id += 1
        
        # 5. 资源容量冲突
        capacity_conflicts = self._generate_capacity_conflicts(courses, classrooms)
        for conflict in capacity_conflicts:
            conflict['id'] = conflict_id
            conflicts.append(conflict)
            conflict_id += 1
        
        return conflicts
    
    def generate_scheduling_constraints(self, courses: List[Dict[str, Any]], 
                                      teachers: List[Dict[str, Any]], 
                                      classrooms: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成排课约束数据
        
        Args:
            courses: 课程数据列表
            teachers: 教师数据列表
            classrooms: 教室数据列表
            
        Returns:
            约束数据列表
        """
        constraints = []
        constraint_id = 1
        
        # 硬约束
        hard_constraints = [
            {
                'id': constraint_id,
                'type': 'hard',
                'category': 'teacher_conflict',
                'description': '同一教师不能在同一时间段教授多门课程',
                'priority': 1,
                'violation_penalty': 1000,
                'is_active': True
            },
            {
                'id': constraint_id + 1,
                'type': 'hard',
                'category': 'classroom_conflict',
                'description': '同一教室不能在同一时间段安排多门课程',
                'priority': 1,
                'violation_penalty': 1000,
                'is_active': True
            },
            {
                'id': constraint_id + 2,
                'type': 'hard',
                'category': 'student_conflict',
                'description': '学生不能在同一时间段选修多门课程',
                'priority': 1,
                'violation_penalty': 1000,
                'is_active': True
            }
        ]
        
        constraints.extend(hard_constraints)
        constraint_id += len(hard_constraints)
        
        # 软约束
        soft_constraints = [
            {
                'id': constraint_id,
                'type': 'soft',
                'category': 'teacher_preference',
                'description': '尽量满足教师时间偏好',
                'priority': 2,
                'violation_penalty': 50,
                'is_active': True
            },
            {
                'id': constraint_id + 1,
                'type': 'soft',
                'category': 'classroom_capacity',
                'description': '教室容量应满足课程需求',
                'priority': 2,
                'violation_penalty': 30,
                'is_active': True
            },
            {
                'id': constraint_id + 2,
                'type': 'soft',
                'category': 'time_distribution',
                'description': '课程时间分布应均匀',
                'priority': 3,
                'violation_penalty': 20,
                'is_active': True
            }
        ]
        
        constraints.extend(soft_constraints)
        
        return constraints

    def _create_major_course_mapping(self, students: List[Dict[str, Any]],
                                   courses: List[Dict[str, Any]]) -> Dict[int, List[int]]:
        """创建专业-课程映射"""
        major_course_map = {}

        # 获取所有专业ID
        major_ids = set(student['major_id'] for student in students)

        for major_id in major_ids:
            # 为每个专业找到相关课程
            related_courses = []
            for course in courses:
                # 同院系课程或通识课程
                if course['course_type'] == '通识':
                    related_courses.append(course['id'])
                # 这里简化处理，实际应该根据专业-院系关系判断
                elif random.random() < 0.7:  # 70%概率相关
                    related_courses.append(course['id'])

            major_course_map[major_id] = related_courses

        return major_course_map

    def _filter_suitable_courses(self, student: Dict[str, Any],
                               courses: List[Dict[str, Any]],
                               major_course_map: Dict[int, List[int]]) -> List[Dict[str, Any]]:
        """根据学生情况筛选合适的课程"""
        suitable_courses = []
        student_grade = 2024 - student['grade'] + 1  # 当前年级

        # 获取该专业相关课程
        related_course_ids = major_course_map.get(student['major_id'], [])

        for course in courses:
            # 检查课程是否相关
            if course['id'] not in related_course_ids and course['course_type'] != '通识':
                continue

            # 检查学期匹配（简化：假设学期对应年级）
            if course['semester'] <= student_grade * 2:  # 每年级2个学期
                # 检查先修课程（简化处理）
                if not course.get('prerequisites') or random.random() < 0.8:
                    suitable_courses.append(course)

        return suitable_courses

    def _generate_course_grade(self, enrollment_id: int) -> Optional[int]:
        """生成课程成绩"""
        if random.random() < 0.3:  # 30%的课程还没有成绩
            return None

        # 成绩分布：优秀(85-100) 20%, 良好(75-84) 30%, 中等(65-74) 35%, 及格(60-64) 15%
        grade_ranges = [(85, 100), (75, 84), (65, 74), (60, 64)]
        weights = [0.2, 0.3, 0.35, 0.15]

        selected_range = random.choices(grade_ranges, weights=weights)[0]
        return random.randint(*selected_range)

    def _calculate_total_score(self, enrollment: Dict[str, Any]) -> Optional[float]:
        """计算总分"""
        midterm = enrollment.get('midterm_score')
        final = enrollment.get('final_score')

        if midterm is None or final is None:
            return None

        # 期中30%，期末70%
        return round(midterm * 0.3 + final * 0.7, 1)

    def _calculate_gpa_points(self, total_score: Optional[float]) -> Optional[float]:
        """计算GPA点数"""
        if total_score is None:
            return None

        if total_score >= 90:
            return 4.0
        elif total_score >= 85:
            return 3.7
        elif total_score >= 82:
            return 3.3
        elif total_score >= 78:
            return 3.0
        elif total_score >= 75:
            return 2.7
        elif total_score >= 72:
            return 2.3
        elif total_score >= 68:
            return 2.0
        elif total_score >= 64:
            return 1.5
        elif total_score >= 60:
            return 1.0
        else:
            return 0.0

    def _generate_withdrawal_reason(self) -> str:
        """生成退课原因"""
        reasons = [
            '时间冲突', '课程难度过大', '个人原因', '专业调整',
            '身体健康', '家庭原因', '实习安排', '出国交流'
        ]
        return random.choice(reasons)

    def _generate_special_notes(self) -> Optional[str]:
        """生成特殊备注"""
        if random.random() < 0.1:  # 10%概率有特殊备注
            notes = [
                '需要特殊照顾', '学习困难', '优秀学生', '交换生',
                '重修学生', '旁听生', '免修申请', '缓考申请'
            ]
            return random.choice(notes)
        return None

    def _calculate_teacher_preference_score(self, day: int, time_slot: Dict[str, Any],
                                          teacher: Dict[str, Any]) -> float:
        """计算教师时间偏好分数"""
        base_score = 0.5

        # 年龄因素：年长教师偏好上午时间
        birth_year = teacher['birth_date'].year if hasattr(teacher['birth_date'], 'year') else 1980
        age = 2024 - birth_year

        slot_hour = int(time_slot['start_time'].split(':')[0])

        if age > 50 and slot_hour <= 11:  # 上午时间
            base_score += 0.3
        elif age < 35 and slot_hour >= 19:  # 年轻教师可以接受晚上
            base_score += 0.2

        # 职称因素：教授偏好较少的课时
        if teacher['title'] == '教授' and random.random() < 0.3:
            base_score -= 0.2

        # 周几因素：周一周五稍微不受欢迎
        if day in [1, 5]:  # 周一、周五
            base_score -= 0.1

        # 随机因素
        base_score += random.uniform(-0.2, 0.2)

        return max(0.0, min(1.0, base_score))

    def _score_to_level(self, score: float) -> str:
        """将分数转换为偏好等级"""
        if score >= 0.8:
            return '非常喜欢'
        elif score >= 0.6:
            return '喜欢'
        elif score >= 0.4:
            return '一般'
        elif score >= 0.2:
            return '不喜欢'
        else:
            return '不可用'

    def _generate_preference_reason(self, score: float, teacher: Dict[str, Any]) -> str:
        """生成偏好原因"""
        if score > 0.8:
            return random.choice(["最佳时间", "精力充沛", "学生注意力集中", "个人习惯"])
        elif score > 0.6:
            return random.choice(["较好时间", "可以接受", "时间合适", "教学效果好"])
        elif score > 0.4:
            return random.choice(["一般时间", "勉强可以", "需要调整", "中性时间"])
        elif score > 0.2:
            return random.choice(["不太理想", "尽量避免", "影响效果", "个人不便"])
        else:
            return random.choice(["不可用", "有其他安排", "身体原因", "家庭原因"])

    def _calculate_max_courses_per_slot(self, preference_score: float) -> int:
        """根据偏好分数计算该时段最多可安排课程数"""
        if preference_score >= 0.8:
            return random.randint(2, 3)
        elif preference_score >= 0.6:
            return random.randint(1, 2)
        elif preference_score >= 0.4:
            return 1
        else:
            return 0

    def _generate_preferred_course_types(self, teacher: Dict[str, Any]) -> List[str]:
        """生成教师偏好的课程类型"""
        all_types = ['必修', '选修', '限选', '通识']

        # 根据教师职称和经验确定偏好
        if teacher['title'] == '教授':
            # 教授更愿意教高级课程
            return random.sample(['必修', '选修'], random.randint(1, 2))
        elif teacher['title'] == '副教授':
            return random.sample(all_types, random.randint(2, 3))
        else:
            # 讲师和助教更多教基础课程
            return random.sample(['必修', '通识'], random.randint(1, 2))

    def _generate_special_requirements(self, teacher: Dict[str, Any]) -> List[str]:
        """生成特殊要求"""
        requirements = []

        if random.random() < 0.2:  # 20%概率有特殊要求
            possible_requirements = [
                '需要多媒体教室', '需要实验室', '需要大教室',
                '避免连续上课', '需要助教', '需要特殊设备'
            ]
            requirements = random.sample(possible_requirements, random.randint(1, 2))

        return requirements

    def _generate_teacher_conflicts(self, teachers: List[Dict[str, Any]],
                                  courses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成教师冲突场景"""
        conflicts = []

        # 找出课程较多的热门教师
        teacher_course_count = {}
        for course in courses:
            for teacher_id in course.get('teacher_ids', []):
                teacher_course_count[teacher_id] = teacher_course_count.get(teacher_id, 0) + 1

        # 选择课程数量前20%的教师作为热门教师
        sorted_teachers = sorted(teacher_course_count.items(), key=lambda x: x[1], reverse=True)
        top_20_percent = max(1, len(sorted_teachers) // 5)
        popular_teacher_ids = [tid for tid, _ in sorted_teachers[:top_20_percent]]

        for teacher_id in popular_teacher_ids:
            teacher = next((t for t in teachers if t['id'] == teacher_id), None)
            if teacher:
                course_count = teacher_course_count[teacher_id]
                conflicts.append({
                    'type': 'teacher_overload',
                    'severity': 'high' if course_count > 8 else 'medium',
                    'teacher_id': teacher_id,
                    'teacher_name': teacher['name'],
                    'course_count': course_count,
                    'max_recommended': teacher.get('max_weekly_hours', 16) // 2,
                    'description': f"教师{teacher['name']}课程安排过多，共{course_count}门课程",
                    'impact_score': min(100, course_count * 10),
                    'suggested_solution': '分配部分课程给其他教师或调整课程安排',
                    'created_at': self.fake.date_time_between(start_date='-1m', end_date='now')
                })

        return conflicts

    def _generate_classroom_conflicts(self, classrooms: List[Dict[str, Any]],
                                    courses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成教室冲突场景"""
        conflicts = []

        # 找出热门教室（容量大的教室）
        popular_classrooms = sorted(classrooms, key=lambda x: x['capacity'], reverse=True)[:10]

        for classroom in popular_classrooms:
            # 模拟该教室的需求量
            demand_courses = [c for c in courses if c['max_students'] <= classroom['capacity']]
            demand_level = len(demand_courses)

            if demand_level > 20:  # 如果需求课程超过20门
                conflicts.append({
                    'type': 'classroom_high_demand',
                    'severity': 'high' if demand_level > 30 else 'medium',
                    'classroom_id': classroom['id'],
                    'classroom_name': classroom['full_name'],
                    'capacity': classroom['capacity'],
                    'demand_courses': demand_level,
                    'utilization_rate': min(1.0, demand_level / 40),
                    'description': f"教室{classroom['full_name']}需求量大，有{demand_level}门课程适合",
                    'impact_score': min(100, demand_level * 2),
                    'suggested_solution': '增加类似容量教室或调整课程时间分布',
                    'created_at': self.fake.date_time_between(start_date='-1m', end_date='now')
                })

        return conflicts

    def _generate_student_conflicts(self, students: List[Dict[str, Any]],
                                  courses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成学生冲突场景"""
        conflicts = []

        # 模拟热门课程冲突
        popular_courses = random.sample(courses, min(10, len(courses)))

        for course in popular_courses:
            # 模拟选课人数超过容量
            interested_students = random.randint(course['max_students'],
                                               int(course['max_students'] * 1.5))

            if interested_students > course['max_students']:
                conflicts.append({
                    'type': 'course_oversubscription',
                    'severity': 'high' if interested_students > course['max_students'] * 1.3 else 'medium',
                    'course_id': course['id'],
                    'course_name': course['name'],
                    'max_capacity': course['max_students'],
                    'interested_students': interested_students,
                    'overflow_count': interested_students - course['max_students'],
                    'description': f"课程{course['name']}选课人数超出容量",
                    'impact_score': min(100, (interested_students - course['max_students']) * 5),
                    'suggested_solution': '增开班级或调整选课规则',
                    'created_at': self.fake.date_time_between(start_date='-1m', end_date='now')
                })

        return conflicts

    def _generate_dependency_conflicts(self, courses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成课程依赖冲突场景"""
        conflicts = []

        for course in courses:
            prerequisites = course.get('prerequisites', [])
            if prerequisites:
                # 检查先修课程是否在合适的学期
                for prereq_id in prerequisites:
                    prereq_course = next((c for c in courses if c['id'] == prereq_id), None)
                    if prereq_course:
                        # 如果先修课程学期不早于当前课程
                        if prereq_course['semester'] >= course['semester']:
                            conflicts.append({
                                'type': 'prerequisite_scheduling',
                                'severity': 'high',
                                'course_id': course['id'],
                                'course_name': course['name'],
                                'course_semester': course['semester'],
                                'prerequisite_id': prereq_id,
                                'prerequisite_name': prereq_course['name'],
                                'prerequisite_semester': prereq_course['semester'],
                                'description': f"课程{course['name']}的先修课程{prereq_course['name']}学期安排不当",
                                'impact_score': 80,
                                'suggested_solution': '调整课程学期安排或修改先修关系',
                                'created_at': self.fake.date_time_between(start_date='-1m', end_date='now')
                            })

        return conflicts

    def _generate_capacity_conflicts(self, courses: List[Dict[str, Any]],
                                   classrooms: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成容量冲突场景"""
        conflicts = []

        for course in courses:
            # 找到容量合适的教室
            suitable_classrooms = [
                c for c in classrooms
                if c['capacity'] >= course['max_students'] and c['is_available']
            ]

            if len(suitable_classrooms) < 3:  # 如果合适教室少于3个
                conflicts.append({
                    'type': 'insufficient_classroom_capacity',
                    'severity': 'high' if len(suitable_classrooms) == 0 else 'medium',
                    'course_id': course['id'],
                    'course_name': course['name'],
                    'required_capacity': course['max_students'],
                    'suitable_classrooms': len(suitable_classrooms),
                    'available_classrooms': [c['id'] for c in suitable_classrooms],
                    'description': f"课程{course['name']}缺少合适容量的教室",
                    'impact_score': 90 if len(suitable_classrooms) == 0 else 50,
                    'suggested_solution': '增加教室容量或分班教学',
                    'created_at': self.fake.date_time_between(start_date='-1m', end_date='now')
                })

        return conflicts
