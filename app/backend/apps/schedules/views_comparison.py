"""
算法性能对比API视图
提供REST API接口用于比较不同排课算法的性能
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import logging

from .performance_comparison import run_performance_comparison

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def compare_scheduling_algorithms(request):
    """
    比较不同排课算法的性能
    
    POST /api/scheduling/compare-algorithms/
    
    请求体:
    {
        "semester": "2024春",        // 学期
        "academic_year": "2023-2024", // 学年
        "courses": [1, 2, 3],        // 需要排课的课程ID列表（可选）
        "timeout_seconds": 300       // 算法执行超时时间（秒）
    }
    """
    try:
        # 获取请求参数
        data = request.data
        semester = data.get('semester', '2024春')
        academic_year = data.get('academic_year', '2023-2024')
        course_ids = data.get('courses', [])
        timeout_seconds = data.get('timeout_seconds', 300)
        
        logger.info(f"用户 {request.user.username} 请求比较排课算法性能")
        
        # 运行性能对比
        comparison_results = run_performance_comparison(
            semester, academic_year, course_ids, timeout_seconds
        )
        
        # 准备响应数据
        response_data = {
            'success': True,
            'message': '算法性能对比完成',
            'data': comparison_results,
            'status': 'completed'
        }
        
        logger.info("算法性能对比成功完成")
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.exception(f"算法性能对比时发生错误: {e}")
        error_data = {
            'success': False,
            'message': '算法性能对比时发生错误',
            'data': None,
            'status': 'error',
            'error': str(e)
        }
        return Response(error_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)