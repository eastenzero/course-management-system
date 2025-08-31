#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.courses.models import Course, Enrollment
from apps.schedules.models import TimeSlot

User = get_user_model()

print('📊 当前数据库状态检查:')
print('学生用户:', User.objects.filter(user_type='student').count())
print('教师用户:', User.objects.filter(user_type='teacher').count())
print('课程数量:', Course.objects.count())
print('选课记录:', Enrollment.objects.count())
print('时间段数量:', TimeSlot.objects.count())