from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    # 学生档案
    path('profile/', views.StudentProfileView.as_view(), name='profile'),
    
    # 仪表板
    path('dashboard/', views.student_dashboard, name='dashboard'),
    
    # 选课相关
    path('available-courses/', views.available_courses, name='available-courses'),
    path('enroll/', views.enroll_course, name='enroll'),
    path('drop/<int:course_id>/', views.drop_course, name='drop'),
    path('check-conflicts/', views.check_conflicts, name='check-conflicts'),
    
    # 我的课程
    path('my-courses/', views.MyCoursesView.as_view(), name='my-courses'),
    
    # 课程表
    path('schedule/', views.course_schedule, name='schedule'),
    
    # 成绩相关
    path('grades/', views.grades_list, name='grades'),
    path('gpa/', views.gpa_statistics, name='gpa'),
]
