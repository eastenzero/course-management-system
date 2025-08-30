from django.urls import path
from . import views

app_name = 'teachers'

urlpatterns = [
    # 教师档案
    path('profile/', views.TeacherProfileView.as_view(), name='profile'),
    
    # 仪表板
    path('dashboard/', views.teacher_dashboard, name='dashboard'),
    
    # 我的课程
    path('my-courses/', views.MyCoursesView.as_view(), name='my-courses'),
    
    # 学生管理
    path('course/<int:course_id>/students/', views.course_students, name='course-students'),
    
    # 成绩管理
    path('grades/batch/', views.batch_grade_entry, name='batch-grade-entry'),
    path('grade/<int:enrollment_id>/', views.update_grade, name='update-grade'),
    path('course/<int:course_id>/grade-stats/', views.course_grade_statistics, name='course-grade-stats'),
    
    # 教学安排
    path('schedule/', views.teaching_schedule, name='schedule'),
    
    # 通知管理
    path('notices/', views.TeacherNoticeListCreateView.as_view(), name='notices'),
    path('notice/<int:pk>/', views.TeacherNoticeDetailView.as_view(), name='notice-detail'),
    path('notice/<int:notice_id>/publish/', views.publish_notice, name='publish-notice'),
]
