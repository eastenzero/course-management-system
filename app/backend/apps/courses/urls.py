from django.urls import path
from . import views
from . import grade_views

app_name = 'courses'

urlpatterns = [
    # 课程管理
    path('', views.CourseListCreateView.as_view(), name='course_list_create'),
    path('<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    
    # 选课管理
    path('enrollments/', views.EnrollmentListCreateView.as_view(), name='enrollment_list_create'),
    path('enrollments/<int:pk>/', views.EnrollmentDetailView.as_view(), name='enrollment_detail'),
    path('<int:course_id>/drop/', views.drop_course, name='drop_course'),
    
    # 统计
    path('statistics/', views.course_statistics, name='course_statistics'),

    # 成绩管理
    path('grades/', views.GradeListCreateView.as_view(), name='grade_list_create'),
    path('grades/<int:pk>/', views.GradeDetailView.as_view(), name='grade_detail'),
    path('<int:course_id>/grade-summary/', views.course_grade_summary, name='course_grade_summary'),

    # 成绩组成配置
    path('grade-components/', grade_views.GradeComponentListCreateView.as_view(), name='grade_component_list_create'),
    path('grade-components/<int:pk>/', grade_views.GradeComponentDetailView.as_view(), name='grade_component_detail'),
    path('grade-components/batch-create/', grade_views.batch_create_grade_components, name='batch_create_grade_components'),
    path('grade-components/copy/', grade_views.copy_grade_components, name='copy_grade_components'),
    path('grade-components/templates/', grade_views.grade_component_templates, name='grade_component_templates'),
    path('grade-components/apply-template/', grade_views.apply_template, name='apply_template'),
    path('grades/recalculate/', grade_views.recalculate_grades, name='recalculate_grades'),

    # 成绩分析
    path('<int:course_id>/grade-distribution/', grade_views.course_grade_distribution, name='course_grade_distribution'),
    path('students/<int:student_id>/grade-trend/', grade_views.student_grade_trend, name='student_grade_trend'),
    path('<int:course_id>/difficulty-analysis/', grade_views.course_difficulty_analysis, name='course_difficulty_analysis'),
    path('class-comparison/', grade_views.class_grade_comparison, name='class_grade_comparison'),

    # 成绩导入导出
    path('<int:course_id>/grades/export/', grade_views.export_grades, name='export_grades'),
    path('<int:course_id>/grades/template/', grade_views.download_grade_template, name='download_grade_template'),
    path('<int:course_id>/grades/import/', grade_views.import_grades, name='import_grades'),

    # 课程评价
    path('evaluations/', views.CourseEvaluationListCreateView.as_view(), name='evaluation_list_create'),
    path('evaluations/<int:pk>/', views.CourseEvaluationDetailView.as_view(), name='evaluation_detail'),
    path('<int:course_id>/evaluation-stats/', views.course_evaluation_statistics, name='course_evaluation_stats'),
]
