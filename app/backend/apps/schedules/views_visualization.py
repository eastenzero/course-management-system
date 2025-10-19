"""
排课结果可视化API视图
提供REST API接口用于可视化排课结果
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import logging

from .visualization import generate_visualization_data

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_schedule_table(request):
    """
    获取课程表数据
    
    GET /api/scheduling/visualization/schedule-table/
    
    查询参数:
    - semester: 学期
    - academic_year: 学年
    - user_type: 用户类型 (student, teacher, classroom, general)
    - user_id: 用户ID
    """
    try:
        # 获取查询参数
        semester = request.GET.get('semester')
        academic_year = request.GET.get('academic_year')
        user_type = request.GET.get('user_type', 'general')
        user_id = request.GET.get('user_id')
        
        if not semester or not academic_year:
            return Response({
                'success': False,
                'message': '缺少必要参数：semester 和 academic_year',
                'data': None,
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 转换user_id为整数
        if user_id:
            try:
                user_id = int(user_id)
            except ValueError:
                user_id = None
        
        logger.info(f"用户 {request.user.username} 请求获取课程表数据")
        
        # 生成课程表数据
        schedule_data = generate_visualization_data(
            semester, academic_year, 'schedule_table', user_type, user_id
        )
        
        # 准备响应数据
        response_data = {
            'success': True,
            'message': '课程表数据获取成功',
            'data': schedule_data,
            'status': 'completed'
        }
        
        logger.info("课程表数据获取成功")
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.exception(f"获取课程表数据时发生错误: {e}")
        error_data = {
            'success': False,
            'message': '获取课程表数据时发生错误',
            'data': None,
            'status': 'error',
            'error': str(e)
        }
        return Response(error_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_statistics_chart(request):
    """
    获取统计图表数据
    
    GET /api/scheduling/visualization/statistics/
    
    查询参数:
    - semester: 学期
    - academic_year: 学年
    """
    try:
        # 获取查询参数
        semester = request.GET.get('semester')
        academic_year = request.GET.get('academic_year')
        
        if not semester or not academic_year:
            return Response({
                'success': False,
                'message': '缺少必要参数：semester 和 academic_year',
                'data': None,
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        logger.info(f"用户 {request.user.username} 请求获取统计图表数据")
        
        # 生成统计图表数据
        statistics_data = generate_visualization_data(
            semester, academic_year, 'statistics'
        )
        
        # 准备响应数据
        response_data = {
            'success': True,
            'message': '统计图表数据获取成功',
            'data': statistics_data,
            'status': 'completed'
        }
        
        logger.info("统计图表数据获取成功")
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.exception(f"获取统计图表数据时发生错误: {e}")
        error_data = {
            'success': False,
            'message': '获取统计图表数据时发生错误',
            'data': None,
            'status': 'error',
            'error': str(e)
        }
        return Response(error_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_conflict_report(request):
    """
    获取冲突报告数据
    
    GET /api/scheduling/visualization/conflicts/
    
    查询参数:
    - semester: 学期
    - academic_year: 学年
    """
    try:
        # 获取查询参数
        semester = request.GET.get('semester')
        academic_year = request.GET.get('academic_year')
        
        if not semester or not academic_year:
            return Response({
                'success': False,
                'message': '缺少必要参数：semester 和 academic_year',
                'data': None,
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        logger.info(f"用户 {request.user.username} 请求获取冲突报告数据")
        
        # 生成冲突报告数据
        conflict_data = generate_visualization_data(
            semester, academic_year, 'conflicts'
        )
        
        # 准备响应数据
        response_data = {
            'success': True,
            'message': '冲突报告数据获取成功',
            'data': conflict_data,
            'status': 'completed'
        }
        
        logger.info("冲突报告数据获取成功")
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.exception(f"获取冲突报告数据时发生错误: {e}")
        error_data = {
            'success': False,
            'message': '获取冲突报告数据时发生错误',
            'data': None,
            'status': 'error',
            'error': str(e)
        }
        return Response(error_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)