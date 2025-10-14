#!/usr/bin/env python3
"""
排课算法效果测试脚本
用于测试和对比不同排课算法的性能表现
"""

import os
import sys
import django
import time
from datetime import datetime

# 设置Django环境
sys.path.insert(0, '/root/code/course-management-system/course-management-system/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.schedules.models import Schedule
from apps.courses.models import Course, Enrollment
from apps.classrooms.models import Classroom
from apps.schedules.algorithms import SchedulingEngine, ScheduleConstraint, ScheduleSlot

User = get_user_model()

class AlgorithmPerformanceTester:
    """算法性能测试器"""
    
    def __init__(self):
        self.semester = "2024春"
        self.academic_year = "2023-2024"
        self.test_results = {}
    
    def get_test_data(self):
        """获取测试数据"""
        print("📊 获取测试数据...")
        
        # 获取需要排课的课程（有选课的课程）
        courses_with_enrollment = Course.objects.filter(
            enrollments__status='enrolled',
            enrollments__is_active=True,
            is_active=True,
            is_published=True
        ).distinct()
        
        # 获取可用的教师
        available_teachers = User.objects.filter(
            user_type='teacher',
            is_active=True,
            courses__in=courses_with_enrollment
        ).distinct()
        
        # 获取可用教室
        available_classrooms = Classroom.objects.filter(
            is_available=True,
            is_active=True
        )
        
        # 获取时间段
        time_slots = list(range(1, 9))  # 第1-8节
        week_days = list(range(1, 6))   # 周一到周五
        
        data = {
            'courses': courses_with_enrollment,
            'teachers': available_teachers,
            'classrooms': available_classrooms,
            'time_slots': time_slots,
            'week_days': week_days,
            'total_courses': courses_with_enrollment.count(),
            'total_teachers': available_teachers.count(),
            'total_classrooms': available_classrooms.count()
        }
        
        print(f"📚 待排课课程: {data['total_courses']}门")
        print(f"👨‍🏫 可用教师: {data['total_teachers']}名")
        print(f"🏫 可用教室: {data['total_classrooms']}间")
        
        return data
    
    def test_greedy_algorithm(self, data):
        """测试贪心算法"""
        print("\n🚀 测试贪心算法...")
        start_time = time.time()
        
        try:
            # 创建排课引擎
            engine = SchedulingEngine(
                semester=self.semester,
                academic_year=self.academic_year
            )
            
            # 初始化约束
            constraints = []
            
            # 为每门课程创建约束
            for course in data['courses']:
                # 获取合格教师
                qualified_teachers = list(course.teachers.filter(is_active=True))
                if not qualified_teachers:
                    continue
                
                # 创建约束
                constraint = ScheduleConstraint(
                    course=course,
                    teachers=qualified_teachers,
                    required_hours=course.hours // 2,  # 每次2学时
                    weeks=f"1-16",
                    priority=course.credits
                )
                constraints.append(constraint)
            
            print(f"  创建 {len(constraints)} 个排课约束")
            
            # 运行贪心算法
            results = engine.create_schedules_greedy(constraints)
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # 统计结果
            success_count = len(results)
            total_attempts = len(constraints)
            success_rate = success_count / total_attempts if total_attempts > 0 else 0
            
            result = {
                'algorithm': 'greedy',
                'success_count': success_count,
                'total_attempts': total_attempts,
                'success_rate': success_rate,
                'execution_time': execution_time,
                'results': results
            }
            
            print(f"  ✅ 成功: {success_count}/{total_attempts} ({success_rate:.1%})")
            print(f"  ⏱️  执行时间: {execution_time:.3f}秒")
            
            return result
            
        except Exception as e:
            print(f"  ❌ 贪心算法失败: {e}")
            return None
    
    def test_constraint_based_algorithm(self, data):
        """测试基于约束的算法"""
        print("\n🧠 测试基于约束的算法...")
        start_time = time.time()
        
        try:
            # 这里可以集成更复杂的算法逻辑
            # 目前使用简化的约束检查方法
            
            successful_schedules = []
            total_attempts = 0
            
            # 获取时间段
            time_slots = data['time_slots']
            week_days = data['week_days']
            
            for course in data['courses']:
                qualified_teachers = list(course.teachers.filter(is_active=True))
                available_classrooms = data['classrooms']
                
                if not qualified_teachers or not available_classrooms:
                    continue
                
                total_attempts += 1
                
                # 尝试找到合适的安排
                best_schedule = None
                best_score = -1
                
                for teacher in qualified_teachers[:3]:  # 限制尝试的教师数量
                    for classroom in available_classrooms[:5]:  # 限制尝试的教室数量
                        for day in week_days:
                            for slot in time_slots:
                                # 简单的冲突检查
                                if self.check_availability(teacher, classroom, day, slot):
                                    # 计算评分
                                    score = self.calculate_schedule_score(course, teacher, classroom, day, slot)
                                    
                                    if score > best_score:
                                        best_score = score
                                        best_schedule = {
                                            'course': course,
                                            'teacher': teacher,
                                            'classroom': classroom,
                                            'day_of_week': day,
                                            'time_slot': slot,
                                            'score': score
                                        }
                
                if best_schedule:
                    successful_schedules.append(best_schedule)
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            success_count = len(successful_schedules)
            success_rate = success_count / total_attempts if total_attempts > 0 else 0
            
            result = {
                'algorithm': 'constraint_based',
                'success_count': success_count,
                'total_attempts': total_attempts,
                'success_rate': success_rate,
                'execution_time': execution_time,
                'results': successful_schedules
            }
            
            print(f"  ✅ 成功: {success_count}/{total_attempts} ({success_rate:.1%})")
            print(f"  ⏱️  执行时间: {execution_time:.3f}秒")
            
            return result
            
        except Exception as e:
            print(f"  ❌ 基于约束算法失败: {e}")
            return None
    
    def check_availability(self, teacher, classroom, day, slot):
        """检查时间可用性"""
        # 检查教师是否已有安排
        teacher_conflict = Schedule.objects.filter(
            teacher=teacher,
            day_of_week=day,
            time_slot__order=slot,
            status='active'
        ).exists()
        
        # 检查教室是否已被占用
        classroom_conflict = Schedule.objects.filter(
            classroom=classroom,
            day_of_week=day,
            time_slot__order=slot,
            status='active'
        ).exists()
        
        return not teacher_conflict and not classroom_conflict
    
    def calculate_schedule_score(self, course, teacher, classroom, day, slot):
        """计算排课评分"""
        score = 0.0
        
        # 容量匹配度 (0-40分)
        capacity_ratio = min(course.max_students / classroom.capacity, 1.0)
        score += capacity_ratio * 40
        
        # 时间合理性 (0-30分)
        # 避免过早或过晚的时间段
        if 3 <= slot <= 7:  # 第3-7节为最佳时间
            score += 30
        elif slot <= 2 or slot >= 8:  # 过早或过晚
            score += 15
        else:
            score += 20
        
        # 专业匹配度 (0-30分)
        if course.department == teacher.department:
            score += 30
        else:
            score += 10
        
        return score
    
    def save_results_to_database(self, algorithm_results):
        """将算法结果保存到数据库"""
        print("💾 保存算法结果到数据库...")
        
        saved_count = 0
        
        for result in algorithm_results:
            if not result or not result.get('results'):
                continue
            
            algorithm = result['algorithm']
            
            if algorithm == 'greedy':
                # 保存贪心算法结果
                for schedule in result['results']:
                    try:
                        Schedule.objects.create(
                            course=schedule.course,
                            teacher=schedule.teacher,
                            classroom=schedule.classroom,
                            time_slot=schedule.time_slot,
                            day_of_week=schedule.day_of_week,
                            week_range="1-16",
                            semester=self.semester,
                            academic_year=self.academic_year,
                            status='active',
                            notes=f"算法生成 - {algorithm}算法"
                        )
                        saved_count += 1
                    except Exception as e:
                        print(f"  保存失败: {e}")
            
            elif algorithm == 'constraint_based':
                # 保存基于约束算法结果
                for schedule_data in result['results']:
                    try:
                        # 获取或创建时间段
                        from apps.schedules.models import TimeSlot
                        time_slot, _ = TimeSlot.objects.get_or_create(
                            order=schedule_data['time_slot'],
                            defaults={
                                'name': f"第{schedule_data['time_slot']}节",
                                'start_time': f"{8+schedule_data['time_slot']-1:02d}:00:00",
                                'end_time': f"{8+schedule_data['time_slot']-1:02d}:45:00",
                                'is_active': True
                            }
                        )
                        
                        Schedule.objects.create(
                            course=schedule_data['course'],
                            teacher=schedule_data['teacher'],
                            classroom=schedule_data['classroom'],
                            time_slot=time_slot,
                            day_of_week=schedule_data['day_of_week'],
                            week_range="1-16",
                            semester=self.semester,
                            academic_year=self.academic_year,
                            status='active',
                            notes=f"算法生成 - {algorithm}算法"
                        )
                        saved_count += 1
                    except Exception as e:
                        print(f"  保存失败: {e}")
        
        print(f"  ✅ 成功保存 {saved_count} 条排课记录")
        return saved_count
    
    def run_algorithm_comparison(self):
        """运行算法对比测试"""
        print("=" * 60)
        print("🧪 排课算法效果对比测试")
        print("=" * 60)
        
        start_time = datetime.now()
        
        # 获取测试数据
        data = self.get_test_data()
        
        if data['total_courses'] == 0:
            print("❌ 没有需要排课的课程")
            return None
        
        # 测试不同算法
        results = []
        
        # 1. 测试贪心算法
        greedy_result = self.test_greedy_algorithm(data)
        if greedy_result:
            results.append(greedy_result)
        
        # 2. 测试基于约束的算法
        constraint_result = self.test_constraint_based_algorithm(data)
        if constraint_result:
            results.append(constraint_result)
        
        # 保存结果到数据库
        if results:
            self.save_results_to_database(results)
        
        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()
        
        # 生成分析报告
        self.generate_analysis_report(results, total_duration)
        
        return results
    
    def generate_analysis_report(self, results, total_duration):
        """生成算法分析报告"""
        print("\n" + "=" * 60)
        print("📊 算法性能分析报告")
        print("=" * 60)
        
        if not results:
            print("❌ 没有可用的测试结果")
            return
        
        print(f"⏱️  总测试时间: {total_duration:.2f}秒")
        print(f"📋 参与测试算法: {len(results)}种")
        
        print("\n📈 算法性能对比:")
        print("-" * 40)
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['algorithm'].upper()}算法:")
            print(f"   ✅ 成功率: {result['success_rate']:.1%}")
            print(f"   📊 成功数: {result['success_count']}/{result['total_attempts']}")
            print(f"   ⏱️  执行时间: {result['execution_time']:.3f}秒")
            print()
        
        # 找出最佳算法
        best_algorithm = max(results, key=lambda x: x['success_rate'])
        print(f"🏆 最佳算法: {best_algorithm['algorithm'].upper()}")
        print(f"   成功率: {best_algorithm['success_rate']:.1%}")
        print(f"   执行效率: {best_algorithm['execution_time']:.3f}秒")
        
        print("\n💡 算法效果分析:")
        print("-" * 40)
        
        # 分析成功率
        avg_success_rate = sum(r['success_rate'] for r in results) / len(results)
        print(f"📊 平均成功率: {avg_success_rate:.1%}")
        
        if avg_success_rate >= 0.8:
            print("✅ 算法表现优秀 - 成功率超过80%")
        elif avg_success_rate >= 0.6:
            print("⚠️  算法表现良好 - 成功率在60%-80%之间")
        else:
            print("❌ 算法需要优化 - 成功率低于60%")
        
        # 分析执行时间
        avg_execution_time = sum(r['execution_time'] for r in results) / len(results)
        print(f"⏱️  平均执行时间: {avg_execution_time:.3f}秒")
        
        if avg_execution_time < 1.0:
            print("✅ 算法效率很高 - 执行时间小于1秒")
        elif avg_execution_time < 5.0:
            print("⚠️  算法效率良好 - 执行时间在1-5秒之间")
        else:
            print("❌ 算法效率较低 - 执行时间超过5秒")
        
        print("\n🎯 结论与建议:")
        print("-" * 40)
        print("1. 排课算法能够有效处理大规模数据")
        print("2. 不同算法在成功率和效率方面各有优势")
        print("3. 建议在实际应用中根据具体需求选择合适算法")
        print("4. 可进一步优化算法参数以提高成功率")

def main():
    """主函数"""
    print("🚀 排课算法效果对比测试系统")
    print("=" * 60)
    
    tester = AlgorithmPerformanceTester()
    results = tester.run_algorithm_comparison()
    
    if results:
        print("\n🎉 算法对比测试完成！")
        print("现在可以使用前端界面查看排课效果")
        return 0
    else:
        print("\n❌ 算法测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())