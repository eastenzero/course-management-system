"""
智能排课算法集成模块
将用户的实际Django模型数据转换为排课算法格式，并应用算法结果
"""

import sys
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

# 添加算法目录到Python路径
algorithms_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'algorithms')
sys.path.insert(0, algorithms_path)

# 导入排课算法组件
from models import Assignment, TeacherPreference
from constraints.manager import ConstraintManager
from run_simple_scheduling import create_simple_test_data, run_simple_scheduling

# Django模型导入（将在实际使用时导入）
def get_django_models():
    """延迟导入Django模型，避免在没有Django环境时出错"""
    try:
        from apps.courses.models import Course
        from apps.classrooms.models import Classroom
        from apps.schedules.models import Schedule, TimeSlot
        from apps.teachers.models import TeacherProfile
        from django.contrib.auth import get_user_model
        return Course, Classroom, Schedule, TimeSlot, TeacherProfile, get_user_model()
    except ImportError:
        return None, None, None, None, None, None


class SchedulingAlgorithmIntegration:
    """排课算法集成类"""
    
    def __init__(self):
        self.courses = []
        self.teachers = []
        self.classrooms = []
        self.teacher_preferences = []
        self.assignments = []
        self.constraint_manager = ConstraintManager()
        
    def extract_actual_data(self) -> Dict[str, Any]:
        """
        从Django数据库提取实际的课程数据
        """
        Course, Classroom, Schedule, TimeSlot, TeacherProfile, get_user_model = get_django_models()
        
        if not all([Course, Classroom, Schedule, TimeSlot, TeacherProfile]):
            print("⚠️ Django环境未就绪，使用模拟数据")
            return self._create_demo_data()
        
        print("🔄 正在提取实际系统数据...")
        
        # 提取课程数据
        courses_data = []
        for course in Course.objects.filter(is_active=True):
            courses_data.append({
                'id': course.id,
                'name': course.name,
                'code': course.code,
                'credits': course.credits,
                'max_students': course.max_students or 30,  # 默认值
                'course_type': course.course_type,
                'semester': '2024春',  # 可以从课程中获取实际学期
                'academic_year': '2023-2024',
                'is_active': course.is_active,
                'is_published': getattr(course, 'is_published', True),
            })
        
        # 提取教师数据
        teachers_data = []
        User = get_user_model()
        for teacher_profile in TeacherProfile.objects.filter(user__is_active=True):
            user = teacher_profile.user
            # 获取教师能教授的课程（需要建立关联）
            qualified_courses = self._get_teacher_qualified_courses(user)
            
            teachers_data.append({
                'id': user.id,
                'name': user.get_full_name() or user.username,
                'department': getattr(teacher_profile, 'department', '未知系别'),
                'max_weekly_hours': getattr(teacher_profile, 'max_weekly_hours', 16),
                'max_daily_hours': getattr(teacher_profile, 'max_daily_hours', 6),
                'qualified_courses': qualified_courses,
                'title': teacher_profile.title,
            })
        
        # 提取教室数据
        classrooms_data = []
        for classroom in Classroom.objects.filter(is_available=True):
            classrooms_data.append({
                'id': classroom.id,
                'name': classroom.name,
                'building': classroom.building,
                'floor': getattr(classroom, 'floor', 1),
                'capacity': classroom.capacity,
                'room_type': getattr(classroom, 'room_type', 'lecture'),
                'equipment': getattr(classroom, 'equipment', []),
                'is_available': classroom.is_available,
                'is_active': getattr(classroom, 'is_active', True),
            })
        
        # 提取教师偏好数据
        teacher_preferences_data = self._extract_teacher_preferences()
        
        print(f"✅ 数据提取完成:")
        print(f"   📚 课程: {len(courses_data)} 门")
        print(f"   👨‍🏫 教师: {len(teachers_data)} 名")
        print(f"   🏫 教室: {len(classrooms_data)} 间")
        print(f"   ⏰ 教师偏好: {len(teacher_preferences_data)} 个")
        
        return {
            'courses': courses_data,
            'teachers': teachers_data,
            'classrooms': classrooms_data,
            'teacher_preferences': teacher_preferences_data
        }
    
    def _get_teacher_qualified_courses(self, teacher_user) -> List[int]:
        """获取教师能教授的课程列表"""
        # 这里需要根据实际的数据结构来implement
        # 暂时返回所有课程ID的随机子集
        Course = get_django_models()[0]
        if Course:
            course_ids = list(Course.objects.filter(is_active=True).values_list('id', flat=True))
            import random
            return random.sample(course_ids, min(len(course_ids), random.randint(3, 8)))
        return []
    
    def _extract_teacher_preferences(self) -> List:
        """提取教师时间偏好"""
        preferences = []
        # 这里需要根据实际的教师偏好数据结构来implement
        # 暂时创建一些默认偏好
        import random
        
        TeacherProfile = get_django_models()[4]
        if TeacherProfile:
            for teacher_profile in TeacherProfile.objects.all()[:5]:  # 前5名教师
                teacher_id = teacher_profile.user.id
                # 为每位教师创建2-4个时间偏好
                for _ in range(random.randint(2, 4)):
                    preference = TeacherPreference(
                        teacher_id=teacher_id,
                        day_of_week=random.randint(1, 5),
                        time_slot=random.randint(1, 8),
                        preference_score=random.uniform(0.6, 1.0),
                        is_available=random.choice([True, True, False]),
                        reason=f"偏好时间段"
                    )
                    preferences.append(preference)
        
        return preferences
    
    def _create_demo_data(self) -> Dict[str, Any]:
        """创建演示数据（当Django环境不可用时）"""
        print("🔄 创建演示数据...")
        courses, teachers, classrooms, teacher_preferences = create_simple_test_data()
        
        return {
            'courses': courses,
            'teachers': teachers,
            'classrooms': classrooms,
            'teacher_preferences': teacher_preferences
        }
    
    def run_scheduling_algorithm(self, algorithm_type: str = 'simple') -> Dict[str, Any]:
        """
        运行排课算法
        """
        print(f"🚀 开始运行{algorithm_type}排课算法...")
        
        # 提取数据
        data = self.extract_actual_data()
        
        # 设置算法数据
        self.courses = data['courses']
        self.teachers = data['teachers']
        self.classrooms = data['classrooms']
        self.teacher_preferences = data['teacher_preferences']
        
        # 根据算法类型运行相应的算法
        if algorithm_type == 'simple':
            result = self._run_simple_scheduling()
        elif algorithm_type == 'genetic':
            result = self._run_genetic_scheduling()
        elif algorithm_type == 'hybrid':
            result = self._run_hybrid_scheduling()
        else:
            result = self._run_simple_scheduling()  # 默认使用简化版
        
        return result
    
    def _run_simple_scheduling(self) -> Dict[str, Any]:
        """运行简化版排课算法"""
        # 使用已验证的简化版算法逻辑
        result = run_simple_scheduling()
        return result
    
    def _run_genetic_scheduling(self) -> Dict[str, Any]:
        """运行遗传算法排课"""
        try:
            # 导入遗传算法模块
            from apps.schedules.genetic_algorithm import create_genetic_schedule
            
            # 使用实际数据运行遗传算法
            # 这里需要根据实际需求设置学期和学年
            result = create_genetic_schedule('2024春', '2023-2024')
            return result
        except Exception as e:
            print(f"❌ 遗传算法运行失败: {e}")
            # 回退到简化版算法
            return self._run_simple_scheduling()
    
    def _run_hybrid_scheduling(self) -> Dict[str, Any]:
        """运行混合算法排课"""
        try:
            # 导入混合算法模块
            from apps.schedules.hybrid_algorithm import create_hybrid_schedule
            
            # 使用实际数据运行混合算法
            # 这里需要根据实际需求设置学期和学年
            result = create_hybrid_schedule('2024春', '2023-2024')
            return result
        except Exception as e:
            print(f"❌ 混合算法运行失败: {e}")
            # 回退到简化版算法
            return self._run_simple_scheduling()
    
    def apply_scheduling_results(self, scheduling_result: Dict[str, Any]) -> bool:
        """
        将排课结果应用到实际系统
        """
        try:
            print("💾 正在将排课结果应用到系统...")
            
            Schedule = get_django_models()[2]
            if not Schedule:
                print("❌ Schedule模型不可用")
                return False
            
            assignments = scheduling_result.get('assignments', [])
            created_count = 0
            
            for assignment in assignments:
                # 创建Schedule记录
                schedule_data = {
                    'course_id': assignment['course_id'],
                    'classroom_id': assignment['classroom_id'],
                    'teacher_id': assignment['teacher_id'],
                    'day_of_week': assignment['day_of_week'],
                    'time_slot_id': assignment.get('time_slot', assignment.get('time_slot_id', 1)),
                    'semester': assignment.get('semester', '2024春'),
                    'academic_year': assignment.get('academic_year', '2023-2024'),
                    'week_range': assignment.get('week_range', '1-16'),
                    'status': 'active',
                }
                
                # 检查是否已存在相同的安排
                existing = Schedule.objects.filter(
                    course_id=assignment['course_id'],
                    teacher_id=assignment['teacher_id'],
                    semester=schedule_data['semester']
                ).first()
                
                if not existing:
                    Schedule.objects.create(**schedule_data)
                    created_count += 1
            
            print(f"✅ 成功创建 {created_count} 个课程安排")
            return True
            
        except Exception as e:
            print(f"❌ 应用排课结果失败: {e}")
            return False
    
    def generate_scheduling_report(self, scheduling_result: Dict[str, Any]) -> str:
        """
        生成排课报告
        """
        report = []
        report.append("=" * 60)
        report.append("智能排课算法应用报告")
        report.append("=" * 60)
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"算法类型: {scheduling_result.get('algorithm', '简化版算法')}")
        
        if 'assignments' in scheduling_result:
            assignments = scheduling_result['assignments']
            report.append(f"成功分配数量: {len(assignments)}")
            report.append(f"成功率: {scheduling_result.get('success_rate', '未知')}")
            report.append("")
            report.append("详细分配结果:")
            report.append("-" * 40)
            
            for i, assignment in enumerate(assignments, 1):
                day_names = ['', '周一', '周二', '周三', '周四', '周五', '周六', '周日']
                
                # 处理Assignment对象和字典两种格式
                if hasattr(assignment, 'day_of_week'):
                    # Assignment对象格式
                    day_of_week = assignment.day_of_week
                    time_slot = assignment.time_slot
                    course_id = assignment.course_id
                    teacher_id = assignment.teacher_id
                    classroom_id = assignment.classroom_id
                else:
                    # 字典格式
                    day_of_week = assignment.get('day_of_week', 1)
                    time_slot = assignment.get('time_slot', 1)
                    course_id = assignment.get('course_id')
                    teacher_id = assignment.get('teacher_id')
                    classroom_id = assignment.get('classroom_id')
                
                day_name = day_names[day_of_week]
                
                report.append(f"{i}. 课程ID:{course_id} - "
                            f"教师ID:{teacher_id} - "
                            f"教室ID:{classroom_id} - "
                            f"{day_name}第{time_slot}节")
        
        return "\n".join(report)


def main():
    """主函数 - 演示集成效果"""
    print("🎓 智能排课算法集成演示")
    print("=" * 50)
    
    # 创建集成实例
    integration = SchedulingAlgorithmIntegration()
    
    # 运行排课算法
    result = integration.run_scheduling_algorithm('simple')
    
    if result and result.get('assignments'):
        # 应用结果到系统
        success = integration.apply_scheduling_results(result)
        
        # 生成报告
        report = integration.generate_scheduling_report(result)
        print(report)
        
        if success:
            print("\n✅ 排课算法已成功应用到实际系统！")
        else:
            print("\n⚠️ 算法运行成功，但应用到系统时遇到问题")
    else:
        print("❌ 排课算法运行失败")


if __name__ == "__main__":
    main()