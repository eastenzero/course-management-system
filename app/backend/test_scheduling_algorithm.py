#!/usr/bin/env python3
"""
测试排课算法的简化版本，不依赖数据库
"""

import sys
import os
import json
from dataclasses import dataclass
from typing import List, Dict, Set, Tuple
import random

# 添加项目路径
sys.path.append('/root/code/course-management-system/course-management-system/backend')

# 模拟Django模型
class MockUser:
    def __init__(self, id, username, full_name=None):
        self.id = id
        self.username = username
        self.full_name = full_name or username

class MockCourse:
    def __init__(self, id, code, name, course_type='required', max_students=50):
        self.id = id
        self.code = code
        self.name = name
        self.course_type = course_type
        self.max_students = max_students

class MockClassroom:
    def __init__(self, id, name, capacity=50, room_type='lecture'):
        self.id = id
        self.name = name
        self.capacity = capacity
        self.room_type = room_type
    
    def __str__(self):
        return self.name

class MockTimeSlot:
    def __init__(self, id, name, order, start_time="08:00", end_time="08:45"):
        self.id = id
        self.name = name
        self.order = order
        self.start_time = start_time
        self.end_time = end_time

@dataclass
class ScheduleConstraint:
    """排课约束"""
    course: MockCourse
    teacher: MockUser
    preferred_classrooms: List[MockClassroom]
    preferred_time_slots: List[MockTimeSlot]
    preferred_days: List[int]  # 1-7 表示周一到周日
    sessions_per_week: int  # 每周课时数
    avoid_consecutive: bool = False  # 是否避免连续排课
    avoid_noon: bool = False  # 是否避免中午时间
    max_daily_sessions: int = 0  # 每天最大课时数，0表示无限制
    fixed_time_slots: List[Tuple[int, MockTimeSlot]] = None  # 固定时间槽 [(星期, 时间段)]
    priority: int = 1  # 优先级，数字越大优先级越高

    def __post_init__(self):
        if self.fixed_time_slots is None:
            self.fixed_time_slots = []

    def __hash__(self):
        return hash((self.course.id, self.teacher.id, self.sessions_per_week))

    def __eq__(self, other):
        return (self.course.id == other.course.id and
                self.teacher.id == other.teacher.id and
                self.sessions_per_week == other.sessions_per_week)

@dataclass
class ScheduleSlot:
    """排课时间槽"""
    day_of_week: int
    time_slot: MockTimeSlot
    classroom: MockClassroom
    
    def __hash__(self):
        return hash((self.day_of_week, self.time_slot.id, self.classroom.id))
    
    def __eq__(self, other):
        return (self.day_of_week == other.day_of_week and 
                self.time_slot.id == other.time_slot.id and 
                self.classroom.id == other.classroom.id)

class SchedulingAlgorithm:
    """简化版排课算法"""
    
    def __init__(self, semester: str, academic_year: str):
        self.semester = semester
        self.academic_year = academic_year
        self.constraints: List[ScheduleConstraint] = []
        self.available_slots: Set[ScheduleSlot] = set()
        self.assigned_slots: Dict[ScheduleConstraint, List[ScheduleSlot]] = {}
        self.conflicts: List[Dict] = []

        # 优化：使用字典快速查找已分配的时间槽
        self.teacher_schedule: Dict[int, Dict[tuple, ScheduleConstraint]] = {}
        self.classroom_schedule: Dict[int, Dict[tuple, ScheduleConstraint]] = {}
        
    def add_constraint(self, constraint: ScheduleConstraint):
        """添加排课约束"""
        self.constraints.append(constraint)
        
    def initialize_available_slots(self):
        """初始化可用时间槽"""
        # 创建模拟的时间段
        time_slots = [
            MockTimeSlot(1, "第1节", 1),
            MockTimeSlot(2, "第2节", 2),
            MockTimeSlot(3, "第3节", 3),
            MockTimeSlot(4, "第4节", 4),
            MockTimeSlot(5, "第5节", 5),
            MockTimeSlot(6, "第6节", 6),
            MockTimeSlot(7, "第7节", 7),
            MockTimeSlot(8, "第8节", 8),
        ]
        
        # 创建模拟的教室
        classrooms = [
            MockClassroom(1, "教学楼A101", 200),
            MockClassroom(2, "教学楼A102", 180),
            MockClassroom(3, "教学楼A103", 150),
            MockClassroom(4, "教学楼B201", 120),
            MockClassroom(5, "教学楼B202", 100),
            MockClassroom(6, "教学楼B203", 80),
            MockClassroom(7, "教学楼B204", 80),
            MockClassroom(8, "教学楼C301", 60),
            MockClassroom(9, "教学楼C302", 50),
            MockClassroom(10, "教学楼C303", 50),
            MockClassroom(11, "实验楼D401", 70),
            MockClassroom(12, "实验楼D402", 60),
        ]
        
        # 生成所有可能的时间槽
        for day in range(1, 6):  # 周一到周五
            for time_slot in time_slots:
                for classroom in classrooms:
                    slot = ScheduleSlot(
                        day_of_week=day,
                        time_slot=time_slot,
                        classroom=classroom
                    )
                    self.available_slots.add(slot)
    
    def check_teacher_conflict(self, teacher: MockUser, slot: ScheduleSlot) -> bool:
        """检查教师时间冲突（优化版）"""
        teacher_id = teacher.id
        time_key = (slot.day_of_week, slot.time_slot.id)

        # 使用字典快速查找，O(1)时间复杂度
        if teacher_id in self.teacher_schedule:
            return time_key in self.teacher_schedule[teacher_id]
        return False

    def check_classroom_conflict(self, classroom: MockClassroom, slot: ScheduleSlot) -> bool:
        """检查教室冲突（优化版）"""
        classroom_id = classroom.id
        time_key = (slot.day_of_week, slot.time_slot.id)

        # 使用字典快速查找，O(1)时间复杂度
        if classroom_id in self.classroom_schedule:
            return time_key in self.classroom_schedule[classroom_id]
        return False

    def _update_conflict_tracking(self, constraint: ScheduleConstraint, slots: List[ScheduleSlot]):
        """更新冲突跟踪字典"""
        teacher_id = constraint.teacher.id

        # 初始化教师时间表
        if teacher_id not in self.teacher_schedule:
            self.teacher_schedule[teacher_id] = {}

        for slot in slots:
            time_key = (slot.day_of_week, slot.time_slot.id)

            # 更新教师时间表
            self.teacher_schedule[teacher_id][time_key] = constraint

            # 更新教室时间表
            classroom_id = slot.classroom.id
            if classroom_id not in self.classroom_schedule:
                self.classroom_schedule[classroom_id] = {}
            self.classroom_schedule[classroom_id][time_key] = constraint
    
    def calculate_slot_score(self, constraint: ScheduleConstraint, slot: ScheduleSlot) -> float:
        """计算时间槽的适合度分数"""
        score = 0.0
        
        # 优先级权重
        score += constraint.priority * 10
        
        # 偏好教室权重
        if slot.classroom in constraint.preferred_classrooms:
            score += 20
        
        # 偏好时间段权重
        if slot.time_slot in constraint.preferred_time_slots:
            score += 15
        
        # 偏好星期权重
        if slot.day_of_week in constraint.preferred_days:
            score += 10
        
        # 教室容量适合度
        if constraint.course.max_students:
            capacity_ratio = constraint.course.max_students / slot.classroom.capacity
            if 0.5 <= capacity_ratio <= 0.9:  # 理想的容量利用率
                score += 15
            elif capacity_ratio <= 1.0:
                score += 10
            else:
                score -= 20  # 容量不足，大幅减分
        
        # 避免过早或过晚的时间
        if 2 <= slot.time_slot.order <= 6:  # 假设这是比较好的时间段
            score += 5
        
        # 避免中午时间
        if constraint.avoid_noon and self._is_noon_time(slot.time_slot):
            score -= 30
        
        return score
    
    def find_best_slots(self, constraint: ScheduleConstraint) -> List[ScheduleSlot]:
        """为约束找到最佳时间槽"""
        candidate_slots = []
        
        # 处理固定时间槽
        if constraint.fixed_time_slots:
            fixed_slots = []
            for day_of_week, time_slot in constraint.fixed_time_slots:
                # 查找匹配的教室
                for classroom in constraint.preferred_classrooms or self._get_all_classrooms():
                    slot = ScheduleSlot(day_of_week=day_of_week, time_slot=time_slot, classroom=classroom)
                    if slot in self.available_slots:
                        # 检查冲突
                        if (not self.check_teacher_conflict(constraint.teacher, slot) and
                            not self.check_classroom_conflict(slot.classroom, slot)):
                            fixed_slots.append(slot)
            
            # 如果固定时间槽数量满足要求
            if len(fixed_slots) >= constraint.sessions_per_week:
                # 从可用槽中移除
                for slot in fixed_slots[:constraint.sessions_per_week]:
                    self.available_slots.discard(slot)
                return fixed_slots[:constraint.sessions_per_week]
        
        # 筛选可用的时间槽
        for slot in self.available_slots:
            # 检查基本约束
            if (slot.classroom in constraint.preferred_classrooms or 
                not constraint.preferred_classrooms):
                if (slot.time_slot in constraint.preferred_time_slots or 
                    not constraint.preferred_time_slots):
                    if (slot.day_of_week in constraint.preferred_days or 
                        not constraint.preferred_days):
                        # 检查中午时间约束
                        if constraint.avoid_noon and self._is_noon_time(slot.time_slot):
                            continue
                        
                        # 检查冲突
                        if (not self.check_teacher_conflict(constraint.teacher, slot) and
                            not self.check_classroom_conflict(slot.classroom, slot)):
                            score = self.calculate_slot_score(constraint, slot)
                            candidate_slots.append((slot, score))
        
        # 按分数排序
        candidate_slots.sort(key=lambda x: x[1], reverse=True)
        
        # 选择最佳的时间槽
        selected_slots = []
        daily_sessions = {}  # 每天课时计数
        
        for slot, score in candidate_slots:
            if len(selected_slots) >= constraint.sessions_per_week:
                break
                
            # 检查每天最大课时数限制
            if (constraint.max_daily_sessions > 0 and 
                daily_sessions.get(slot.day_of_week, 0) >= constraint.max_daily_sessions):
                continue
                
            # 如果避免连续排课，检查是否在同一天（如果已经排了一天的课）
            if constraint.avoid_consecutive and daily_sessions.get(slot.day_of_week, 0) > 0:
                # 检查是否与已选的同一日课程连续
                if self._would_be_consecutive(slot, selected_slots):
                    continue
                
            selected_slots.append(slot)
            daily_sessions[slot.day_of_week] = daily_sessions.get(slot.day_of_week, 0) + 1
            
            # 从可用槽中移除
            self.available_slots.discard(slot)
        
        return selected_slots
    
    def solve(self, timeout_seconds: int = 300) -> Dict:
        """执行排课算法"""
        print(f"开始执行排课算法，共有 {len(self.constraints)} 个约束")
        self.initialize_available_slots()
        print(f"初始化了 {len(self.available_slots)} 个可用时间槽")
        
        # 按优先级排序约束
        sorted_constraints = sorted(self.constraints, key=lambda x: x.priority, reverse=True)
        
        successful_assignments = 0
        failed_assignments = []
        
        for i, constraint in enumerate(sorted_constraints):
            try:
                best_slots = self.find_best_slots(constraint)
                
                if len(best_slots) >= constraint.sessions_per_week:
                    self.assigned_slots[constraint] = best_slots
                    # 更新冲突跟踪
                    self._update_conflict_tracking(constraint, best_slots)
                    successful_assignments += 1
                    print(f"  约束 {i+1}: {constraint.course.name} - 成功分配 {len(best_slots)} 个时间槽")
                else:
                    failed_assignments.append({
                        'constraint': constraint,
                        'assigned_slots': len(best_slots),
                        'required_slots': constraint.sessions_per_week,
                        'reason': '无法找到足够的合适时间槽'
                    })
                    # 即使部分成功也记录
                    if best_slots:
                        self.assigned_slots[constraint] = best_slots
                        # 更新冲突跟踪
                        self._update_conflict_tracking(constraint, best_slots)
                    print(f"  约束 {i+1}: {constraint.course.name} - 分配失败，只找到 {len(best_slots)} 个时间槽（需要 {constraint.sessions_per_week} 个）")
                        
            except Exception as e:
                failed_assignments.append({
                    'constraint': constraint,
                    'assigned_slots': 0,
                    'required_slots': constraint.sessions_per_week,
                    'reason': f'排课失败: {str(e)}'
                })
                print(f"  约束 {i+1}: {constraint.course.name} - 排课失败: {str(e)}")
        
        success_rate = successful_assignments / len(sorted_constraints) * 100 if sorted_constraints else 0
        
        print(f"排课完成:")
        print(f"  成功分配: {successful_assignments}/{len(sorted_constraints)} ({success_rate:.1f}%)")
        print(f"  失败分配: {len(failed_assignments)}")
        
        return {
            'successful_assignments': successful_assignments,
            'failed_assignments': failed_assignments,
            'total_constraints': len(sorted_constraints),
            'success_rate': success_rate,
            'assigned_slots': self.assigned_slots,
            'optimization_suggestions': self.get_optimization_suggestions()
        }

    def create_schedules(self) -> List[Dict]:
        """根据分配结果创建Schedule对象"""
        schedules = []
        
        for constraint, slots in self.assigned_slots.items():
            for slot in slots:
                schedule = {
                    'course': constraint.course.name,
                    'teacher': constraint.teacher.full_name or constraint.teacher.username,
                    'classroom': str(slot.classroom),
                    'time_slot': slot.time_slot.name,
                    'day_of_week': slot.day_of_week,
                    'semester': self.semester,
                    'academic_year': self.academic_year,
                }
                schedules.append(schedule)
        
        return schedules
    
    def get_optimization_suggestions(self) -> List[Dict]:
        """获取优化建议"""
        suggestions = []
        
        # 分析教室利用率
        classroom_usage = {}
        for slots in self.assigned_slots.values():
            for slot in slots:
                classroom_usage[slot.classroom.id] = classroom_usage.get(slot.classroom.id, 0) + 1
        
        # 找出利用率低的教室
        total_classrooms = len(set(slot.classroom for slots in self.assigned_slots.values() for slot in slots))
        if total_classrooms > 0:
            avg_usage = sum(classroom_usage.values()) / total_classrooms
            for classroom_id, usage in classroom_usage.items():
                if usage < avg_usage * 0.5:
                    suggestions.append({
                        'type': 'classroom_underutilized',
                        'message': f'教室 {classroom_id} 利用率较低，建议调整',
                        'classroom_id': classroom_id,
                        'usage_count': usage
                    })
        
        # 分析时间段分布
        time_slot_usage = {}
        for slots in self.assigned_slots.values():
            for slot in slots:
                time_slot_usage[slot.time_slot.id] = time_slot_usage.get(slot.time_slot.id, 0) + 1
        
        # 建议平衡时间段使用
        if time_slot_usage:
            max_usage = max(time_slot_usage.values())
            min_usage = min(time_slot_usage.values())
            if max_usage > min_usage * 2:
                suggestions.append({
                    'type': 'time_slot_imbalance',
                    'message': '时间段使用不均衡，建议调整课程时间分布',
                    'max_usage': max_usage,
                    'min_usage': min_usage
                })
        
        return suggestions

    def _is_noon_time(self, time_slot: MockTimeSlot) -> bool:
        """判断是否为中午时间（12:00-13:00）"""
        # 简化判断，假设第5-6节是中午时间
        return time_slot.order in [5, 6]
    
    def _would_be_consecutive(self, new_slot: ScheduleSlot, selected_slots: List[ScheduleSlot]) -> bool:
        """检查新时间槽是否与已选时间槽连续"""
        for slot in selected_slots:
            if slot.day_of_week == new_slot.day_of_week:
                # 检查时间是否连续
                if abs(slot.time_slot.order - new_slot.time_slot.order) == 1:
                    return True
        return False
    
    def _get_all_classrooms(self) -> List[MockClassroom]:
        """获取所有可用教室"""
        return list(set(slot.classroom for slot in self.available_slots))


def create_test_data():
    """创建测试数据"""
    # 创建教师
    teachers = [
        MockUser(1, "张伟", "张伟教授"),
        MockUser(2, "李明", "李明教授"),
        MockUser(3, "王芳", "王芳教授"),
        MockUser(4, "赵强", "赵强副教授"),
        MockUser(5, "刘洋", "刘洋讲师"),
        MockUser(6, "陈静", "陈静讲师"),
        MockUser(7, "杨帆", "杨帆教授"),
        MockUser(8, "黄丽", "黄丽副教授"),
        MockUser(9, "孙涛", "孙涛讲师"),
        MockUser(10, "周敏", "周敏副教授"),
    ]
    
    # 创建课程
    courses = [
        MockCourse(1, "CS101", "高等数学A", "required", 200),
        MockCourse(2, "CS102", "高等数学B", "required", 180),
        MockCourse(3, "CS103", "线性代数", "required", 150),
        MockCourse(4, "CS104", "概率论与数理统计", "required", 120),
        MockCourse(5, "CS105", "大学物理A", "required", 100),
        MockCourse(6, "CS106", "大学物理B", "required", 80),
        MockCourse(7, "CS201", "程序设计基础", "required", 70),
        MockCourse(8, "CS202", "数据结构", "required", 60),
        MockCourse(9, "CS203", "计算机组成原理", "required", 80),
        MockCourse(10, "CS204", "操作系统", "required", 60),
        MockCourse(11, "CS205", "数据库系统", "required", 50),
        MockCourse(12, "CS206", "计算机网络", "required", 50),
        MockCourse(13, "CS301", "大学英语1", "public", 50),
        MockCourse(14, "CS302", "大学英语2", "public", 50),
        MockCourse(15, "CS401", "体育1", "public", 200),
    ]
    
    # 创建教室
    classrooms = [
        MockClassroom(1, "教学楼A101", 200),
        MockClassroom(2, "教学楼A102", 180),
        MockClassroom(3, "教学楼A103", 150),
        MockClassroom(4, "教学楼B201", 120),
        MockClassroom(5, "教学楼B202", 100),
        MockClassroom(6, "教学楼B203", 80),
        MockClassroom(7, "教学楼B204", 80),
        MockClassroom(8, "教学楼C301", 60),
        MockClassroom(9, "教学楼C302", 50),
        MockClassroom(10, "教学楼C303", 50),
        MockClassroom(11, "实验楼D401", 70),
        MockClassroom(12, "实验楼D402", 60),
    ]
    
    # 创建时间段
    time_slots = [
        MockTimeSlot(1, "第1节", 1),
        MockTimeSlot(2, "第2节", 2),
        MockTimeSlot(3, "第3节", 3),
        MockTimeSlot(4, "第4节", 4),
        MockTimeSlot(5, "第5节", 5),
        MockTimeSlot(6, "第6节", 6),
        MockTimeSlot(7, "第7节", 7),
        MockTimeSlot(8, "第8节", 8),
    ]
    
    return teachers, courses, classrooms, time_slots


def create_auto_schedule(semester: str, academic_year: str) -> Dict:
    """
    自动排课主函数
    
    Args:
        semester: 学期
        academic_year: 学年
    
    Returns:
        排课结果字典
    """
    print(f"开始自动排课: {semester} {academic_year}")
    
    # 创建算法实例
    algorithm = SchedulingAlgorithm(semester, academic_year)
    
    # 获取测试数据
    teachers, courses, classrooms, time_slots = create_test_data()
    
    # 为每个课程创建约束
    for i, course in enumerate(courses):
        # 获取课程的主要教师（轮询分配）
        main_teacher = teachers[i % len(teachers)]
        
        # 根据课程类型设置偏好
        preferred_classrooms = classrooms
        preferred_time_slots = time_slots
        preferred_days = list(range(1, 6))  # 周一到周五
        
        # 根据课程类型调整偏好
        if course.course_type == 'lab':
            # 实验课偏好实验室
            preferred_classrooms = [c for c in classrooms if '实验' in c.name or 'D' in c.name]
        elif course.course_type == 'lecture':
            # 理论课偏好大教室
            preferred_classrooms = [c for c in classrooms if c.capacity >= 50]
        
        # 计算每周课时数
        sessions_per_week = min(course.max_students // 30, 4)  # 简化计算
        if sessions_per_week == 0:
            sessions_per_week = 1
        
        constraint = ScheduleConstraint(
            course=course,
            teacher=main_teacher,
            preferred_classrooms=preferred_classrooms,
            preferred_time_slots=preferred_time_slots,
            preferred_days=preferred_days,
            sessions_per_week=sessions_per_week,
            avoid_consecutive=course.course_type == 'lecture',  # 理论课避免连续
            avoid_noon=False,  # 默认不禁用中午时间
            max_daily_sessions=0,  # 默认无每日限制
            priority=3 if course.course_type == 'required' else 2  # 必修课优先级高
        )
        
        algorithm.add_constraint(constraint)
    
    # 执行排课算法
    result = algorithm.solve()
    
    # 生成优化建议
    suggestions = algorithm.get_optimization_suggestions()
    
    # 准备返回结果
    result.update({
        'suggestions': suggestions,
        'algorithm_instance': algorithm,  # 用于后续创建Schedule对象
    })
    
    return result


def main():
    """主函数"""
    print("🚀 开始运行排课算法测试...")
    print("=" * 50)
    
    # 运行排课算法
    result = create_auto_schedule("2024-1", "2023-2024")
    
    if result:
        print()
        print("=" * 50)
        print("🎉 排课算法运行完成!")
        
        # 显示一些关键统计信息
        print(f"📊 排课统计:")
        print(f"   成功率: {result.get('success_rate', 0):.1f}%")
        print(f"   成功分配: {result.get('successful_assignments', 0)}")
        print(f"   总约束数: {result.get('total_constraints', 0)}")
        
        # 显示失败的分配
        if result.get('failed_assignments'):
            print(f"   失败分配: {len(result['failed_assignments'])}")
            for failed in result['failed_assignments'][:3]:  # 只显示前3个
                constraint = failed['constraint']
                print(f"     - {constraint.course.name}: {failed['reason']}")
            if len(result['failed_assignments']) > 3:
                print(f"     ... 还有 {len(result['failed_assignments']) - 3} 个失败分配")
        
        # 显示优化建议
        if result.get('suggestions'):
            print(f"💡 优化建议:")
            for suggestion in result['suggestions'][:3]:  # 只显示前3个
                print(f"   - {suggestion['message']}")
            if len(result['suggestions']) > 3:
                print(f"   ... 还有 {len(result['suggestions']) - 3} 个优化建议")
        
        # 保存结果到文件
        schedules = result['algorithm_instance'].create_schedules() if 'algorithm_instance' in result else []
        output_data = {
            'statistics': {
                'success_rate': result.get('success_rate', 0),
                'successful_assignments': result.get('successful_assignments', 0),
                'total_constraints': result.get('total_constraints', 0),
                'failed_assignments': len(result.get('failed_assignments', [])),
            },
            'suggestions': result.get('suggestions', []),
            'schedules': schedules
        }
        
        with open('scheduling_result_test.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 排课结果已保存到 scheduling_result_test.json")
        
        # 显示部分排课结果
        if schedules:
            print(f"📋 部分排课结果:")
            for schedule in schedules[:10]:  # 只显示前10个
                print(f"   {schedule['course']} - {schedule['teacher']} - 周{schedule['day_of_week']} {schedule['time_slot']} - {schedule['classroom']}")
            if len(schedules) > 10:
                print(f"   ... 还有 {len(schedules) - 10} 个排课结果")
    else:
        print()
        print("=" * 50)
        print("❌ 排课算法运行失败!")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)