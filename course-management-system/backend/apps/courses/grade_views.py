"""
成绩相关视图
"""

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db import transaction
from django.db.models import Avg, Count, Q
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.openapi import OpenApiTypes
from .cache_service import grade_cache, cache_result

from .models import Course, Enrollment, Grade, GradeComponent
from .serializers import GradeComponentSerializer, GradeSerializer
from .analytics import GradeAnalyticsService
from .grade_import_export import GradeImportExportService
from apps.users.permissions import IsTeacherOrAdmin, CanManageCourses
from django.http import HttpResponse


@extend_schema(
    tags=['成绩管理'],
    summary='成绩组成配置',
    description='获取课程的成绩组成配置列表或创建新的成绩组成配置'
)
class GradeComponentListCreateView(generics.ListCreateAPIView):
    """成绩组成列表和创建视图"""

    serializer_class = GradeComponentSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['course', 'is_required']
    search_fields = ['name', 'description']
    ordering_fields = ['order', 'weight', 'created_at']
    ordering = ['order', 'id']
    
    def get_queryset(self):
        """根据用户类型过滤数据"""
        user = self.request.user
        queryset = GradeComponent.objects.all()
        
        if user.user_type == 'teacher':
            # 教师只能看到自己教授的课程的成绩组成
            queryset = queryset.filter(course__teachers=user)
        
        return queryset
    
    def perform_create(self, serializer):
        """创建成绩组成"""
        # 验证用户权限
        course = serializer.validated_data['course']
        if self.request.user.user_type == 'teacher' and self.request.user not in course.teachers.all():
            raise PermissionError('您没有权限为此课程创建成绩组成')
        
        serializer.save()


class GradeComponentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """成绩组成详情视图"""
    
    serializer_class = GradeComponentSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrAdmin]
    
    def get_queryset(self):
        """根据用户类型过滤数据"""
        user = self.request.user
        queryset = GradeComponent.objects.all()
        
        if user.user_type == 'teacher':
            # 教师只能操作自己教授的课程的成绩组成
            queryset = queryset.filter(course__teachers=user)
        
        return queryset


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsTeacherOrAdmin])
def batch_create_grade_components(request):
    """批量创建成绩组成"""
    try:
        course_id = request.data.get('course_id')
        components_data = request.data.get('components', [])
        
        if not course_id or not components_data:
            return Response({
                'error': '请提供课程ID和成绩组成数据'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({
                'error': '课程不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 验证权限
        if request.user.user_type == 'teacher' and request.user not in course.teachers.all():
            return Response({
                'error': '您没有权限为此课程创建成绩组成'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 验证权重总和
        total_weight = sum(component.get('weight', 0) for component in components_data)
        if total_weight > 100:
            return Response({
                'error': f'权重总和不能超过100%，当前为{total_weight}%'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        created_components = []
        errors = []
        
        with transaction.atomic():
            for i, component_data in enumerate(components_data):
                component_data['course'] = course_id
                serializer = GradeComponentSerializer(data=component_data)
                
                if serializer.is_valid():
                    component = serializer.save()
                    created_components.append(GradeComponentSerializer(component).data)
                else:
                    errors.append({
                        'index': i,
                        'errors': serializer.errors
                    })
        
        if errors:
            return Response({
                'error': '部分成绩组成创建失败',
                'created_count': len(created_components),
                'errors': errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'message': f'成功创建{len(created_components)}个成绩组成',
            'created_components': created_components
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': f'批量创建失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsTeacherOrAdmin])
def copy_grade_components(request):
    """复制成绩组成配置"""
    try:
        source_course_id = request.data.get('source_course_id')
        target_course_id = request.data.get('target_course_id')
        
        if not source_course_id or not target_course_id:
            return Response({
                'error': '请提供源课程ID和目标课程ID'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            source_course = Course.objects.get(id=source_course_id)
            target_course = Course.objects.get(id=target_course_id)
        except Course.DoesNotExist:
            return Response({
                'error': '课程不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 验证权限
        user = request.user
        if user.user_type == 'teacher':
            if user not in source_course.teachers.all() or user not in target_course.teachers.all():
                return Response({
                    'error': '您没有权限操作这些课程'
                }, status=status.HTTP_403_FORBIDDEN)
        
        # 获取源课程的成绩组成
        source_components = source_course.grade_components.all()
        
        if not source_components.exists():
            return Response({
                'error': '源课程没有成绩组成配置'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查目标课程是否已有成绩组成
        if target_course.grade_components.exists():
            return Response({
                'error': '目标课程已有成绩组成配置，请先删除现有配置'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 复制成绩组成
        copied_components = []
        with transaction.atomic():
            for component in source_components:
                new_component = GradeComponent.objects.create(
                    course=target_course,
                    name=component.name,
                    weight=component.weight,
                    max_score=component.max_score,
                    is_required=component.is_required,
                    description=component.description,
                    order=component.order
                )
                copied_components.append(new_component)
        
        return Response({
            'message': f'成功复制{len(copied_components)}个成绩组成配置',
            'copied_components': GradeComponentSerializer(copied_components, many=True).data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': f'复制失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def grade_component_templates(request):
    """获取成绩组成模板"""
    templates = {
        'traditional': {
            'name': '传统模式',
            'description': '平时成绩 + 期中考试 + 期末考试',
            'components': [
                {'name': '平时成绩', 'weight': 30, 'max_score': 100, 'is_required': True, 'order': 1},
                {'name': '期中考试', 'weight': 30, 'max_score': 100, 'is_required': True, 'order': 2},
                {'name': '期末考试', 'weight': 40, 'max_score': 100, 'is_required': True, 'order': 3},
            ]
        },
        'comprehensive': {
            'name': '综合评价模式',
            'description': '作业 + 小测验 + 期中考试 + 期末考试 + 课堂参与',
            'components': [
                {'name': '作业', 'weight': 20, 'max_score': 100, 'is_required': True, 'order': 1},
                {'name': '小测验', 'weight': 15, 'max_score': 100, 'is_required': True, 'order': 2},
                {'name': '期中考试', 'weight': 25, 'max_score': 100, 'is_required': True, 'order': 3},
                {'name': '期末考试', 'weight': 30, 'max_score': 100, 'is_required': True, 'order': 4},
                {'name': '课堂参与', 'weight': 10, 'max_score': 100, 'is_required': True, 'order': 5},
            ]
        },
        'project_based': {
            'name': '项目导向模式',
            'description': '项目 + 报告 + 答辩 + 平时表现',
            'components': [
                {'name': '项目实施', 'weight': 40, 'max_score': 100, 'is_required': True, 'order': 1},
                {'name': '项目报告', 'weight': 25, 'max_score': 100, 'is_required': True, 'order': 2},
                {'name': '项目答辩', 'weight': 25, 'max_score': 100, 'is_required': True, 'order': 3},
                {'name': '平时表现', 'weight': 10, 'max_score': 100, 'is_required': True, 'order': 4},
            ]
        },
        'lab_course': {
            'name': '实验课程模式',
            'description': '实验报告 + 实验操作 + 理论考试',
            'components': [
                {'name': '实验报告', 'weight': 40, 'max_score': 100, 'is_required': True, 'order': 1},
                {'name': '实验操作', 'weight': 35, 'max_score': 100, 'is_required': True, 'order': 2},
                {'name': '理论考试', 'weight': 25, 'max_score': 100, 'is_required': True, 'order': 3},
            ]
        }
    }
    
    return Response({
        'templates': templates
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsTeacherOrAdmin])
def apply_template(request):
    """应用成绩组成模板"""
    try:
        course_id = request.data.get('course_id')
        template_name = request.data.get('template_name')
        
        if not course_id or not template_name:
            return Response({
                'error': '请提供课程ID和模板名称'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取模板
        templates_response = grade_component_templates(request)
        templates = templates_response.data['templates']
        
        if template_name not in templates:
            return Response({
                'error': '模板不存在'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        template = templates[template_name]
        
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({
                'error': '课程不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 验证权限
        if request.user.user_type == 'teacher' and request.user not in course.teachers.all():
            return Response({
                'error': '您没有权限为此课程应用模板'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 检查课程是否已有成绩组成
        if course.grade_components.exists():
            return Response({
                'error': '课程已有成绩组成配置，请先删除现有配置'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 应用模板
        created_components = []
        with transaction.atomic():
            for component_data in template['components']:
                component = GradeComponent.objects.create(
                    course=course,
                    **component_data
                )
                created_components.append(component)
        
        return Response({
            'message': f'成功应用模板"{template["name"]}"',
            'created_components': GradeComponentSerializer(created_components, many=True).data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': f'应用模板失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsTeacherOrAdmin])
def recalculate_grades(request):
    """重新计算课程成绩"""
    try:
        course_id = request.data.get('course_id')
        
        if not course_id:
            return Response({
                'error': '请提供课程ID'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({
                'error': '课程不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 验证权限
        if request.user.user_type == 'teacher' and request.user not in course.teachers.all():
            return Response({
                'error': '您没有权限重新计算此课程的成绩'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 重新计算所有选课记录的成绩
        enrollments = course.enrollments.filter(is_active=True)
        updated_count = 0
        
        with transaction.atomic():
            for enrollment in enrollments:
                enrollment.update_final_score()
                updated_count += 1
        
        return Response({
            'message': f'成功重新计算{updated_count}个学生的成绩',
            'updated_count': updated_count
        })
        
    except Exception as e:
        return Response({
            'error': f'重新计算成绩失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 成绩分析API
@extend_schema(
    tags=['数据分析'],
    summary='课程成绩分布分析',
    description='获取指定课程的成绩分布统计数据，包括各等级人数、平均分、及格率等',
    parameters=[
        OpenApiParameter(
            name='course_id',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description='课程ID'
        )
    ],
    responses={
        200: {
            'type': 'object',
            'properties': {
                'message': {'type': 'string'},
                'data': {
                    'type': 'object',
                    'properties': {
                        'course_info': {'type': 'object'},
                        'distribution': {'type': 'object'},
                        'statistics': {'type': 'object'}
                    }
                }
            }
        }
    }
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def course_grade_distribution(request, course_id):
    """获取课程成绩分布"""
    try:
        # 验证权限
        course = Course.objects.get(id=course_id)
        user = request.user

        if user.user_type == 'teacher' and user not in course.teachers.all():
            return Response({
                'error': '您没有权限查看此课程的成绩分布'
            }, status=status.HTTP_403_FORBIDDEN)
        elif user.user_type == 'student':
            # 学生只能查看自己选课的课程
            if not course.enrollments.filter(student=user, is_active=True).exists():
                return Response({
                    'error': '您没有权限查看此课程的成绩分布'
                }, status=status.HTTP_403_FORBIDDEN)

        # 尝试从缓存获取
        cache_key = grade_cache.get_course_grade_distribution_key(course_id)
        result = grade_cache.get(cache_key)

        if result is None:
            result = GradeAnalyticsService.get_course_grade_distribution(course_id)
            if 'error' not in result:
                # 缓存结果（10分钟）
                grade_cache.set(cache_key, result, 600)

        if 'error' in result:
            return Response({
                'error': result['error']
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'message': '获取成绩分布成功',
            'data': result
        })

    except Course.DoesNotExist:
        return Response({
            'error': '课程不存在'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': f'获取成绩分布失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def student_grade_trend(request, student_id):
    """获取学生成绩趋势"""
    try:
        user = request.user

        # 权限验证
        if user.user_type == 'student' and user.id != student_id:
            return Response({
                'error': '您只能查看自己的成绩趋势'
            }, status=status.HTTP_403_FORBIDDEN)
        elif user.user_type == 'teacher':
            # 教师只能查看自己教授课程的学生成绩
            student = User.objects.get(id=student_id, user_type='student')
            taught_courses = Course.objects.filter(teachers=user)
            if not student.enrollments.filter(course__in=taught_courses, is_active=True).exists():
                return Response({
                    'error': '您没有权限查看此学生的成绩趋势'
                }, status=status.HTTP_403_FORBIDDEN)

        semester = request.query_params.get('semester')
        result = GradeAnalyticsService.get_student_grade_trend(student_id, semester)

        if 'error' in result:
            return Response({
                'error': result['error']
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'message': '获取成绩趋势成功',
            'data': result
        })

    except User.DoesNotExist:
        return Response({
            'error': '学生不存在'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': f'获取成绩趋势失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsTeacherOrAdmin])
def course_difficulty_analysis(request, course_id):
    """课程难度分析"""
    try:
        course = Course.objects.get(id=course_id)
        user = request.user

        # 验证权限
        if user.user_type == 'teacher' and user not in course.teachers.all():
            return Response({
                'error': '您没有权限分析此课程的难度'
            }, status=status.HTTP_403_FORBIDDEN)

        result = GradeAnalyticsService.get_course_difficulty_analysis(course_id)

        if 'error' in result:
            return Response({
                'error': result['error']
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'message': '课程难度分析完成',
            'data': result
        })

    except Course.DoesNotExist:
        return Response({
            'error': '课程不存在'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': f'课程难度分析失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsTeacherOrAdmin])
def class_grade_comparison(request):
    """班级成绩对比"""
    try:
        class_name = request.query_params.get('class_name')
        semester = request.query_params.get('semester')

        if not class_name or not semester:
            return Response({
                'error': '请提供班级名称和学期'
            }, status=status.HTTP_400_BAD_REQUEST)

        result = GradeAnalyticsService.get_class_comparison(class_name, semester)

        if 'error' in result:
            return Response({
                'error': result['error']
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'message': '班级成绩对比分析完成',
            'data': result
        })

    except Exception as e:
        return Response({
            'error': f'班级成绩对比分析失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 成绩导入导出API
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsTeacherOrAdmin])
def export_grades(request, course_id):
    """导出成绩"""
    try:
        course = Course.objects.get(id=course_id)
        user = request.user

        # 验证权限
        if user.user_type == 'teacher' and user not in course.teachers.all():
            return Response({
                'error': '您没有权限导出此课程的成绩'
            }, status=status.HTTP_403_FORBIDDEN)

        format_type = request.query_params.get('format', 'excel')
        include_details = request.query_params.get('include_details', 'true').lower() == 'true'
        include_statistics = request.query_params.get('include_statistics', 'true').lower() == 'true'

        export_options = {
            'include_details': include_details,
            'include_statistics': include_statistics
        }

        if format_type == 'excel':
            file_content = GradeImportExportService.export_grades_to_excel(course_id, export_options)
            response = HttpResponse(
                file_content,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{course.name}-成绩单.xlsx"'
            return response

        elif format_type == 'csv':
            file_content = GradeImportExportService.export_grades_to_csv(course_id, export_options)
            response = HttpResponse(file_content, content_type='text/csv; charset=utf-8')
            response['Content-Disposition'] = f'attachment; filename="{course.name}-成绩单.csv"'
            return response

        else:
            return Response({
                'error': '不支持的导出格式'
            }, status=status.HTTP_400_BAD_REQUEST)

    except Course.DoesNotExist:
        return Response({
            'error': '课程不存在'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': f'导出失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsTeacherOrAdmin])
def download_grade_template(request, course_id):
    """下载成绩导入模板"""
    try:
        course = Course.objects.get(id=course_id)
        user = request.user

        # 验证权限
        if user.user_type == 'teacher' and user not in course.teachers.all():
            return Response({
                'error': '您没有权限下载此课程的成绩模板'
            }, status=status.HTTP_403_FORBIDDEN)

        file_content = GradeImportExportService.generate_grade_template(course_id)
        response = HttpResponse(
            file_content,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{course.name}-成绩导入模板.xlsx"'
        return response

    except Course.DoesNotExist:
        return Response({
            'error': '课程不存在'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': f'生成模板失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsTeacherOrAdmin])
def import_grades(request, course_id):
    """导入成绩"""
    try:
        course = Course.objects.get(id=course_id)
        user = request.user

        # 验证权限
        if user.user_type == 'teacher' and user not in course.teachers.all():
            return Response({
                'error': '您没有权限导入此课程的成绩'
            }, status=status.HTTP_403_FORBIDDEN)

        import_data = request.data.get('grades', [])

        if not import_data:
            return Response({
                'error': '请提供成绩数据'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 验证数据
        is_valid, errors = GradeImportExportService.validate_import_data(import_data, course_id)

        if not is_valid:
            return Response({
                'error': '数据验证失败',
                'details': errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # 执行导入
        updated_count, import_errors = GradeImportExportService.import_grades_from_data(import_data, course_id)

        if import_errors:
            return Response({
                'message': f'部分导入成功，更新了{updated_count}条记录',
                'updated_count': updated_count,
                'errors': import_errors
            }, status=status.HTTP_206_PARTIAL_CONTENT)

        return Response({
            'message': f'导入成功，更新了{updated_count}条成绩记录',
            'updated_count': updated_count
        }, status=status.HTTP_200_OK)

    except Course.DoesNotExist:
        return Response({
            'error': '课程不存在'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': f'导入失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
