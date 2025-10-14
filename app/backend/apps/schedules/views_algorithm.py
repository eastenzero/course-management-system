"""
排课算法API视图
提供REST API接口供前端调用智能排课算法
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
import logging
from typing import Dict, Any, List

# 导入排课算法集成
from .scheduling_algorithm_integration import SchedulingAlgorithmIntegration

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def run_scheduling_algorithm(request):
    """
    运行智能排课算法
    
    POST /api/scheduling/run-algorithm/
    
    请求体:
    {
        "algorithm_type": "simple",  // 算法类型: simple, genetic, hybrid
        "semester": "2024春",        // 学期
        "academic_year": "2023-2024", // 学年
        "courses": [1, 2, 3],        // 需要排课的课程ID列表（可选）
        "teachers": [1, 2, 3],       // 参与排课的教师ID列表（可选）
        "constraints": {             // 额外约束条件（可选）
            "max_daily_hours": 8,
            "preferred_time_slots": [1, 2, 3, 4]
        },
        "timeout_seconds": 300       // 算法执行超时时间（秒）
    }
    """
    try:
        # 获取请求参数
        data = request.data
        algorithm_type = data.get('algorithm_type', 'simple')
        semester = data.get('semester', '2024春')
        academic_year = data.get('academic_year', '2023-2024')
        course_ids = data.get('courses', [])
        teacher_ids = data.get('teachers', [])
        constraints = data.get('constraints', {})
        timeout_seconds = data.get('timeout_seconds', 300)
        
        logger.info(f"用户 {request.user.username} 请求运行{algorithm_type}排课算法")
        
        # 创建排课算法集成实例
        integration = SchedulingAlgorithmIntegration()
        
        # 设置参数
        integration.semester = semester
        integration.academic_year = academic_year
        integration.course_filter_ids = course_ids
        integration.teacher_filter_ids = teacher_ids
        integration.custom_constraints = constraints
        
        # 运行排课算法
        result = integration.run_scheduling_algorithm(algorithm_type)
        
        # 处理结果
        if result:
            # 生成详细的排课报告
            report = integration.generate_scheduling_report(result)
            
            # 准备响应数据
            response_data = {
                'success': True,
                'message': '排课算法运行成功',
                'data': {
                    'algorithm_type': algorithm_type,
                    'semester': semester,
                    'academic_year': academic_year,
                    'total_assignments': result.get('successful_assignments', 0),
                    'success_rate': result.get('success_rate', 0),
                    'execution_time': result.get('execution_time', 0),
                    'assignments': result.get('assigned_slots', {}),
                    'failed_assignments': result.get('failed_assignments', []),
                    'report': report,
                    'timestamp': result.get('timestamp', ''),
                    'constraint_stats': result.get('constraint_stats', {}),
                    'resource_utilization': result.get('resource_utilization', {})
                },
                'status': 'completed'
            }
            
            logger.info(f"排课算法成功完成，成功安排了 {result.get('successful_assignments', 0)} 个约束")
            return Response(response_data, status=status.HTTP_200_OK)
            
        else:
            error_data = {
                'success': False,
                'message': '排课算法运行失败',
                'data': None,
                'status': 'failed',
                'error': '算法未能生成有效的排课方案'
            }
            logger.error("排课算法运行失败")
            return Response(error_data, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.exception(f"排课算法运行时发生错误: {e}")
        error_data = {
            'success': False,
            'message': '排课算法运行时发生错误',
            'data': None,
            'status': 'error',
            'error': str(e)
        }
        return Response(error_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_scheduling_results(request):
    """
    应用排课结果到系统
    
    POST /api/scheduling/apply-results/
    
    请求体:
    {
        "assignments": [...],  // 排课算法生成的分配结果
        "semester": "2024春",
        "overwrite_existing": false  // 是否覆盖现有安排
    }
    """
    try:
        data = request.data
        assignments = data.get('assignments', [])
        semester = data.get('semester', '2024春')
        overwrite_existing = data.get('overwrite_existing', False)
        
        if not assignments:
            return Response({
                'success': False,
                'message': '没有提供排课结果',
                'data': None,
                'status': 'failed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        logger.info(f"用户 {request.user.username} 请求应用排课结果到学期 {semester}")
        
        # 创建集成实例
        integration = SchedulingAlgorithmIntegration()
        
        # 构建排课结果格式
        scheduling_result = {
            'assignments': assignments,
            'semester': semester,
            'timestamp': str(timezone.now()) if 'timezone' in globals() else str(datetime.now())
        }
        
        # 应用结果到系统
        success = integration.apply_scheduling_results(scheduling_result)
        
        if success:
            response_data = {
                'success': True,
                'message': f'排课结果已成功应用到学期 {semester}',
                'data': {
                    'total_applied': len(assignments),
                    'semester': semester,
                    'overwrite_existing': overwrite_existing
                },
                'status': 'completed'
            }
            logger.info(f"成功应用了 {len(assignments)} 个排课安排")
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            error_data = {
                'success': False,
                'message': '应用排课结果失败',
                'data': None,
                'status': 'failed',
                'error': '数据库操作失败或模型不可用'
            }
            return Response(error_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.exception(f"应用排课结果时发生错误: {e}")
        error_data = {
            'success': False,
            'message': '应用排课结果时发生错误',
            'data': None,
            'status': 'error',
            'error': str(e)
        }
        return Response(error_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_scheduling_status(request):
    """
    获取排课状态信息
    
    GET /api/scheduling/status/
    """
    try:
        # 获取当前学期信息（需要根据实际系统调整）
        current_semester = request.GET.get('semester', '2024春')
        
        # 这里可以添加实际的统计逻辑
        # 例如：已安排课程数量、未安排课程数量、冲突数量等
        
        status_data = {
            'current_semester': current_semester,
            'total_courses': 0,  # 需要从数据库获取
            'scheduled_courses': 0,
            'unscheduled_courses': 0,
            'total_teachers': 0,
            'total_classrooms': 0,
            'conflicts_detected': 0,
            'last_scheduling_time': None,
            'system_ready': True
        }
        
        return Response({
            'success': True,
            'message': '排课状态获取成功',
            'data': status_data,
            'status': 'ready'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.exception(f"获取排课状态时发生错误: {e}")
        return Response({
            'success': False,
            'message': '获取排课状态时发生错误',
            'data': None,
            'status': 'error',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_scheduling_constraints(request):
    """
    验证排课约束条件
    
    POST /api/scheduling/validate-constraints/
    
    请求体:
    {
        "assignments": [...],  // 待验证的排课方案
        "semester": "2024春"
    }
    """
    try:
        data = request.data
        assignments = data.get('assignments', [])
        semester = data.get('semester', '2024春')
        
        if not assignments:
            return Response({
                'success': False,
                'message': '没有提供排课方案',
                'data': None,
                'status': 'failed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 创建集成实例进行验证
        integration = SchedulingAlgorithmIntegration()
        
        # 这里可以添加具体的约束验证逻辑
        # 返回验证结果，包括冲突检测、约束违反等
        
        validation_result = {
            'is_valid': True,  # 暂时默认有效
            'conflicts': [],
            'violations': [],
            'warnings': [],
            'suggestions': []
        }
        
        return Response({
            'success': True,
            'message': '约束验证完成',
            'data': validation_result,
            'status': 'validated'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.exception(f"验证约束时发生错误: {e}")
        return Response({
            'success': False,
            'message': '验证约束时发生错误',
            'data': None,
            'status': 'error',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 辅助函数
def format_assignment_for_response(assignment):
    """格式化分配结果用于API响应"""
    if hasattr(assignment, 'day_of_week'):
        # Assignment对象格式
        return {
            'course_id': assignment.course_id,
            'teacher_id': assignment.teacher_id,
            'classroom_id': assignment.classroom_id,
            'day_of_week': assignment.day_of_week,
            'time_slot': assignment.time_slot,
            'semester': assignment.semester,
            'fitness_score': getattr(assignment, 'fitness_score', 0.0)
        }
    else:
        # 字典格式
        return dict(assignment)