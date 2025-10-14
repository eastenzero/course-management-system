from django.urls import path, include
from . import views

app_name = 'schedules'

urlpatterns = [
    # 时间段管理
    path('timeslots/', views.TimeSlotListCreateView.as_view(), name='timeslot_list_create'),
    path('timeslots/<int:pk>/', views.TimeSlotDetailView.as_view(), name='timeslot_detail'),
    path('timeslots/simple/', views.get_time_slots, name='simple_timeslots'),  # 简化版本
    
    # 课程安排管理
    path('', views.ScheduleListCreateView.as_view(), name='schedule_list_create'),
    path('<int:pk>/', views.ScheduleDetailView.as_view(), name='schedule_detail'),
    
    # 排课功能
    path('check-conflicts/', views.check_schedule_conflicts, name='check_conflicts'),
    path('batch-create/', views.batch_create_schedules, name='batch_create'),
    
    # 课程表查询
    path('table/', views.get_schedule_table, name='schedule_table'),
    
    # 统计
    path('statistics/', views.schedule_statistics, name='schedule_statistics'),

    # 智能排课
    path('auto-schedule/', views.auto_schedule, name='auto_schedule'),
    path('optimize/', views.optimize_schedule, name='optimize_schedule'),

    # 导入导出
    path('import/', views.import_schedules, name='import_schedules'),
    path('export/', views.export_schedules, name='export_schedules'),
    
    # 教师课程表
    path('teacher/', views.get_teacher_schedules, name='teacher_schedules'),
    
    # 算法相关API
    path('', include('apps.schedules.urls_algorithm')),
]
