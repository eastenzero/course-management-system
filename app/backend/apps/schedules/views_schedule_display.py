"""
课程表显示视图
提供课程表的可视化展示功能
"""

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# 添加算法目录到Python路径
algorithms_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'algorithms')
sys.path.insert(0, algorithms_path)

# 导入排课算法
from apps.scheduling_algorithm_integration import SchedulingAlgorithmIntegration


def generate_sample_schedule_data() -> Dict[str, Any]:
    """生成样例课程表数据"""
    
    # 时间段定义 (对应周一到周五，每天8节课)
    time_slots = [
        {'id': 1, 'name': '第1节', 'start_time': '08:00', 'end_time': '08:45'},
        {'id': 2, 'name': '第2节', 'start_time': '08:55', 'end_time': '09:40'},
        {'id': 3, 'name': '第3节', 'start_time': '10:00', 'end_time': '10:45'},
        {'id': 4, 'name': '第4节', 'start_time': '10:55', 'end_time': '11:40'},
        {'id': 5, 'name': '第5节', 'start_time': '14:00', 'end_time': '14:45'},
        {'id': 6, 'name': '第6节', 'start_time': '14:55', 'end_time': '15:40'},
        {'id': 7, 'name': '第7节', 'start_time': '16:00', 'end_time': '16:45'},
        {'id': 8, 'name': '第8节', 'start_time': '16:55', 'end_time': '17:40'},
    ]
    
    # 星期定义
    days = [
        {'id': 1, 'name': '周一', 'short_name': '一'},
        {'id': 2, 'name': '周二', 'short_name': '二'},
        {'id': 3, 'name': '周三', 'short_name': '三'},
        {'id': 4, 'name': '周四', 'short_name': '四'},
        {'id': 5, 'name': '周五', 'short_name': '五'},
    ]
    
    # 生成样例课程数据
    sample_courses = [
        {'id': 1, 'name': '高等数学A', 'code': 'MATH101', 'credits': 4, 'type': 'required', 'color': '#FF6B6B'},
        {'id': 2, 'name': '线性代数', 'code': 'MATH102', 'credits': 3, 'type': 'required', 'color': '#4ECDC4'},
        {'id': 3, 'name': '程序设计基础', 'code': 'CS101', 'credits': 4, 'type': 'professional', 'color': '#45B7D1'},
        {'id': 4, 'name': '数据结构', 'code': 'CS201', 'credits': 3, 'type': 'professional', 'color': '#96CEB4'},
        {'id': 5, 'name': '大学英语', 'code': 'ENG101', 'credits': 2, 'type': 'public', 'color': '#FFEAA7'},
        {'id': 6, 'name': '大学物理', 'code': 'PHY101', 'credits': 4, 'type': 'required', 'color': '#DDA0DD'},
        {'id': 7, 'name': '计算机组成原理', 'code': 'CS202', 'credits': 3, 'type': 'professional', 'color': '#98D8C8'},
    ]
    
    # 生成样例教师数据
    sample_teachers = [
        {'id': 1, 'name': '张教授', 'department': '数学系', 'title': '教授'},
        {'id': 2, 'name': '李老师', 'department': '计算机系', 'title': '副教授'},
        {'id': 3, 'name': '王老师', 'department': '外语系', 'title': '讲师'},
        {'id': 4, 'name': '赵副教授', 'department': '物理系', 'title': '副教授'},
        {'id': 5, 'name': '陈老师', 'department': '计算机系', 'title': '教授'},
    ]
    
    # 生成样例教室数据
    sample_classrooms = [
        {'id': 1, 'name': '教学楼A101', 'building': '教学楼A', 'capacity': 150, 'type': 'lecture'},
        {'id': 2, 'name': '教学楼A102', 'building': '教学楼A', 'capacity': 100, 'type': 'multimedia'},
        {'id': 3, 'name': '教学楼B201', 'building': '教学楼B', 'capacity': 80, 'type': 'computer'},
        {'id': 4, 'name': '教学楼C301', 'building': '教学楼C', 'capacity': 60, 'type': 'seminar'},
        {'id': 5, 'name': '实验楼D401', 'building': '实验楼D', 'capacity': 40, 'type': 'computer'},
    ]
    
    return {
        'time_slots': time_slots,
        'days': days,
        'courses': sample_courses,
        'teachers': sample_teachers,
        'classrooms': sample_classrooms,
    }


def format_schedule_for_display(schedule_data: Dict[str, Any]) -> Dict[str, Any]:
    """格式化课程表数据用于显示"""
    
    # 创建时间表格子
    schedule_grid = {}
    
    # 初始化网格
    for day in schedule_data['days']:
        schedule_grid[day['id']] = {}
        for slot in schedule_data['time_slots']:
            schedule_grid[day['id']][slot['id']] = None
    
    # 填充课程安排
    assignments = schedule_data.get('assignments', [])
    
    for assignment in assignments:
        if hasattr(assignment, 'day_of_week'):
            day_id = assignment.day_of_week
            slot_id = assignment.time_slot
            
            # 查找对应的课程、教师和教室
            course = next((c for c in schedule_data['courses'] if c['id'] == assignment.course_id), None)
            teacher = next((t for t in schedule_data['teachers'] if t['id'] == assignment.teacher_id), None)
            classroom = next((r for r in schedule_data['classrooms'] if r['id'] == assignment.classroom_id), None)
            
            if course and teacher and classroom:
                schedule_grid[day_id][slot_id] = {
                    'course': course,
                    'teacher': teacher,
                    'classroom': classroom,
                    'fitness_score': getattr(assignment, 'fitness_score', 0.7)
                }
    
    return {
        'grid': schedule_grid,
        'time_slots': schedule_data['time_slots'],
        'days': schedule_data['days'],
        'total_assignments': len(assignments),
        'success_rate': schedule_data.get('success_rate', 0),
        'execution_time': schedule_data.get('execution_time', 0)
    }


def generate_schedule_with_algorithm() -> Dict[str, Any]:
    """使用算法生成课程表"""
    
    print("🚀 使用智能排课算法生成课程表...")
    
    # 创建算法集成实例
    integration = SchedulingAlgorithmIntegration()
    
    # 运行排课算法
    result = integration.run_scheduling_algorithm('simple')
    
    if result and result.get('assignments'):
        print(f"✅ 算法运行成功！成功率: {result.get('success_rate', 0):.1%}")
        
        # 获取基础数据
        base_data = generate_sample_schedule_data()
        
        # 合并算法结果
        base_data['assignments'] = result.get('assignments', [])
        base_data['success_rate'] = result.get('success_rate', 0)
        base_data['execution_time'] = result.get('execution_time', 0)
        base_data['algorithm_used'] = result.get('algorithm', 'simplified')
        base_data['timestamp'] = result.get('timestamp', '')
        
        return base_data
    else:
        print("❌ 算法运行失败，使用预设数据")
        base_data = generate_sample_schedule_data()
        base_data['assignments'] = []
        base_data['success_rate'] = 0
        base_data['execution_time'] = 0
        base_data['algorithm_used'] = 'none'
        base_data['timestamp'] = ''
        
        return base_data


def schedule_display_view(request):
    """
    课程表显示视图
    """
    context = {
        'title': '智能课程表',
        'semester': '2024年春季学期',
        'academic_year': '2023-2024',
    }
    
    # 检查是否有算法生成的数据
    use_algorithm = request.GET.get('use_algorithm', 'true') == 'true'
    
    if use_algorithm:
        # 使用算法生成课程表
        schedule_data = generate_schedule_with_algorithm()
    else:
        # 使用预设样例数据
        schedule_data = generate_sample_schedule_data()
        # 添加一些预设的课程安排用于演示
        preset_assignments = [
            type('Assignment', (), {
                'course_id': 1, 'teacher_id': 1, 'classroom_id': 1, 'day_of_week': 1, 'time_slot': 1, 'fitness_score': 0.8
            })(),
            type('Assignment', (), {
                'course_id': 2, 'teacher_id': 2, 'classroom_id': 2, 'day_of_week': 2, 'time_slot': 3, 'fitness_score': 0.75
            })(),
            type('Assignment', (), {
                'course_id': 3, 'teacher_id': 3, 'classroom_id': 3, 'day_of_week': 3, 'time_slot': 5, 'fitness_score': 0.85
            })(),
        ]
        schedule_data['assignments'] = preset_assignments
        schedule_data['success_rate'] = 1.0
        schedule_data['execution_time'] = 0.0
        schedule_data['algorithm_used'] = 'preset'
    
    # 格式化数据用于显示
    formatted_data = format_schedule_for_display(schedule_data)
    
    # 添加到上下文
    context.update(formatted_data)
    context.update({
        'algorithm_info': {
            'used': schedule_data.get('algorithm_used', 'none'),
            'success_rate': schedule_data.get('success_rate', 0),
            'execution_time': schedule_data.get('execution_time', 0),
            'total_assignments': len(schedule_data.get('assignments', [])),
        },
        'use_algorithm': use_algorithm,
    })
    
    return render(request, 'schedules/schedule_display.html', context)


@csrf_exempt
def generate_schedule_api(request):
    """
    API接口：生成新的课程表
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            algorithm_type = data.get('algorithm_type', 'simple')
            semester = data.get('semester', '2024春')
            
            print(f"🔄 API请求：使用{algorithm_type}算法生成{semester}课程表")
            
            # 运行排课算法
            integration = SchedulingAlgorithmIntegration()
            result = integration.run_scheduling_algorithm(algorithm_type)
            
            if result and result.get('assignments'):
                # 格式化数据
                base_data = generate_sample_schedule_data()
                base_data['assignments'] = result.get('assignments', [])
                base_data['success_rate'] = result.get('success_rate', 0)
                base_data['execution_time'] = result.get('execution_time', 0)
                base_data['algorithm_used'] = result.get('algorithm', algorithm_type)
                base_data['timestamp'] = result.get('timestamp', '')
                
                formatted_data = format_schedule_for_display(base_data)
                
                return JsonResponse({
                    'success': True,
                    'message': '课程表生成成功',
                    'data': formatted_data,
                    'algorithm_info': {
                        'used': algorithm_type,
                        'success_rate': result.get('success_rate', 0),
                        'execution_time': result.get('execution_time', 0),
                        'total_assignments': len(result.get('assignments', [])),
                    }
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': '课程表生成失败',
                    'data': None,
                    'error': '算法未能生成有效的排课方案'
                })
                
        except Exception as e:
            print(f"❌ API错误: {e}")
            return JsonResponse({
                'success': False,
                'message': '生成课程表时发生错误',
                'data': None,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'message': '只支持POST请求',
        'data': None
    })


def schedule_json_api(request):
    """
    API接口：获取课程表JSON数据
    """
    use_algorithm = request.GET.get('use_algorithm', 'true') == 'true'
    
    if use_algorithm:
        schedule_data = generate_schedule_with_algorithm()
    else:
        schedule_data = generate_sample_schedule_data()
        # 添加预设安排
        preset_assignments = [
            type('Assignment', (), {
                'course_id': 1, 'teacher_id': 1, 'classroom_id': 1, 'day_of_week': 1, 'time_slot': 1, 'fitness_score': 0.8
            })(),
        ]
        schedule_data['assignments'] = preset_assignments
    
    formatted_data = format_schedule_for_display(schedule_data)
    
    return JsonResponse({
        'success': True,
        'message': '课程表数据获取成功',
        'data': formatted_data,
        'algorithm_info': {
            'used': schedule_data.get('algorithm_used', 'none'),
            'success_rate': schedule_data.get('success_rate', 0),
            'execution_time': schedule_data.get('execution_time', 0),
        }
    })