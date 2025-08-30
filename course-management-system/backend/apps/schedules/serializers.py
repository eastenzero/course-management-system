from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import TimeSlot, Schedule
from apps.courses.models import Course
from apps.classrooms.models import Classroom

User = get_user_model()


class TimeSlotSerializer(serializers.ModelSerializer):
    """时间段序列化器"""
    
    class Meta:
        model = TimeSlot
        fields = [
            'id', 'name', 'start_time', 'end_time', 'order',
            'duration_minutes', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'duration_minutes', 'created_at', 'updated_at']


class ScheduleSerializer(serializers.ModelSerializer):
    """课程安排序列化器"""
    
    course_info = serializers.SerializerMethodField()
    teacher_info = serializers.SerializerMethodField()
    classroom_info = serializers.SerializerMethodField()
    time_slot_info = serializers.SerializerMethodField()
    time_display = serializers.ReadOnlyField()
    location_display = serializers.ReadOnlyField()
    day_of_week_display = serializers.CharField(source='get_day_of_week_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Schedule
        fields = [
            'id', 'course', 'course_info', 'teacher', 'teacher_info',
            'classroom', 'classroom_info', 'time_slot', 'time_slot_info',
            'day_of_week', 'day_of_week_display', 'week_range',
            'semester', 'academic_year', 'status', 'status_display',
            'time_display', 'location_display', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'time_display', 'location_display', 'created_at', 'updated_at']
    
    def get_course_info(self, obj):
        """获取课程信息"""
        return {
            'id': obj.course.id,
            'code': obj.course.code,
            'name': obj.course.name,
            'credits': obj.course.credits,
            'department': obj.course.department
        }
    
    def get_teacher_info(self, obj):
        """获取教师信息"""
        return {
            'id': obj.teacher.id,
            'username': obj.teacher.username,
            'name': f"{obj.teacher.first_name} {obj.teacher.last_name}".strip() or obj.teacher.username,
            'department': obj.teacher.department
        }
    
    def get_classroom_info(self, obj):
        """获取教室信息"""
        return {
            'id': obj.classroom.id,
            'room_number': obj.classroom.room_number,
            'building_name': obj.classroom.building.name,
            'capacity': obj.classroom.capacity,
            'full_name': obj.classroom.full_name
        }
    
    def get_time_slot_info(self, obj):
        """获取时间段信息"""
        return {
            'id': obj.time_slot.id,
            'name': obj.time_slot.name,
            'start_time': obj.time_slot.start_time,
            'end_time': obj.time_slot.end_time,
            'order': obj.time_slot.order
        }
    
    def validate(self, attrs):
        """验证排课数据"""
        course = attrs.get('course')
        teacher = attrs.get('teacher')
        classroom = attrs.get('classroom')
        day_of_week = attrs.get('day_of_week')
        time_slot = attrs.get('time_slot')
        semester = attrs.get('semester')
        status = attrs.get('status', 'active')
        
        # 只对active状态的排课进行冲突检测
        if status != 'active':
            return attrs
        
        # 检查教师是否是该课程的授课教师
        if teacher and course and not course.teachers.filter(id=teacher.id).exists():
            raise serializers.ValidationError('该教师不是此课程的授课教师')
        
        # 检查教室容量
        if classroom and course and classroom.capacity < course.max_students:
            raise serializers.ValidationError(f'教室容量({classroom.capacity})小于课程最大选课人数({course.max_students})')
        
        # 检查时间冲突（排除当前实例）
        existing_schedules = Schedule.objects.filter(
            day_of_week=day_of_week,
            time_slot=time_slot,
            semester=semester,
            status='active'
        )
        
        # 如果是更新操作，排除当前实例
        if self.instance:
            existing_schedules = existing_schedules.exclude(id=self.instance.id)
        
        # 检查教室冲突
        if existing_schedules.filter(classroom=classroom).exists():
            raise serializers.ValidationError('该时间段教室已被占用')
        
        # 检查教师冲突
        if existing_schedules.filter(teacher=teacher).exists():
            raise serializers.ValidationError('该时间段教师已有课程安排')
        
        return attrs


class ScheduleListSerializer(serializers.ModelSerializer):
    """课程安排列表序列化器（简化版）"""
    
    course_code = serializers.CharField(source='course.code', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    teacher_name = serializers.SerializerMethodField()
    classroom_name = serializers.CharField(source='classroom.full_name', read_only=True)
    time_slot_name = serializers.CharField(source='time_slot.name', read_only=True)
    day_of_week_display = serializers.CharField(source='get_day_of_week_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Schedule
        fields = [
            'id', 'course_code', 'course_name', 'teacher_name',
            'classroom_name', 'time_slot_name', 'day_of_week',
            'day_of_week_display', 'semester', 'status', 'status_display'
        ]
    
    def get_teacher_name(self, obj):
        """获取教师姓名"""
        return f"{obj.teacher.first_name} {obj.teacher.last_name}".strip() or obj.teacher.username


class ScheduleCreateSerializer(serializers.ModelSerializer):
    """排课创建序列化器"""
    
    class Meta:
        model = Schedule
        fields = [
            'course', 'teacher', 'classroom', 'time_slot',
            'day_of_week', 'week_range', 'semester', 'academic_year',
            'notes'
        ]
    
    def validate(self, attrs):
        """验证排课数据"""
        # 使用ScheduleSerializer的验证逻辑
        schedule_serializer = ScheduleSerializer()
        return schedule_serializer.validate(attrs)


class ScheduleConflictSerializer(serializers.Serializer):
    """排课冲突序列化器"""
    
    conflict_type = serializers.CharField()  # 'teacher' 或 'classroom'
    conflicting_schedule = ScheduleListSerializer()
    message = serializers.CharField()


class ScheduleBatchCreateSerializer(serializers.Serializer):
    """批量排课序列化器"""
    
    course_id = serializers.IntegerField()
    teacher_id = serializers.IntegerField()
    classroom_id = serializers.IntegerField()
    semester = serializers.CharField()
    academic_year = serializers.CharField()
    week_range = serializers.CharField()
    time_slots = serializers.ListField(
        child=serializers.DictField(child=serializers.IntegerField()),
        help_text='格式：[{"day_of_week": 1, "time_slot_id": 1}, ...]'
    )
    
    def validate(self, attrs):
        """验证批量排课数据"""
        course_id = attrs['course_id']
        teacher_id = attrs['teacher_id']
        classroom_id = attrs['classroom_id']
        
        # 验证课程存在
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            raise serializers.ValidationError('课程不存在')
        
        # 验证教师存在且是该课程的授课教师
        try:
            teacher = User.objects.get(id=teacher_id, user_type='teacher')
            if not course.teachers.filter(id=teacher_id).exists():
                raise serializers.ValidationError('该教师不是此课程的授课教师')
        except User.DoesNotExist:
            raise serializers.ValidationError('教师不存在')
        
        # 验证教室存在
        try:
            classroom = Classroom.objects.get(id=classroom_id)
            if classroom.capacity < course.max_students:
                raise serializers.ValidationError(f'教室容量({classroom.capacity})小于课程最大选课人数({course.max_students})')
        except Classroom.DoesNotExist:
            raise serializers.ValidationError('教室不存在')
        
        # 验证时间段
        time_slots = attrs['time_slots']
        for slot in time_slots:
            try:
                TimeSlot.objects.get(id=slot['time_slot_id'])
            except TimeSlot.DoesNotExist:
                raise serializers.ValidationError(f'时间段{slot["time_slot_id"]}不存在')
        
        attrs['course'] = course
        attrs['teacher'] = teacher
        attrs['classroom'] = classroom
        
        return attrs
