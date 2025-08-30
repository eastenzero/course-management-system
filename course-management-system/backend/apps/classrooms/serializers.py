from rest_framework import serializers
from .models import Building, Classroom


class BuildingSerializer(serializers.ModelSerializer):
    """教学楼序列化器"""
    
    classrooms_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Building
        fields = [
            'id', 'name', 'code', 'address', 'description',
            'classrooms_count', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_classrooms_count(self, obj):
        """获取教室数量"""
        return obj.classrooms.filter(is_active=True).count()


class ClassroomSerializer(serializers.ModelSerializer):
    """教室序列化器"""
    
    building_info = serializers.SerializerMethodField()
    full_name = serializers.ReadOnlyField()
    equipment_list = serializers.ReadOnlyField()
    room_type_display = serializers.CharField(source='get_room_type_display', read_only=True)
    
    class Meta:
        model = Classroom
        fields = [
            'id', 'building', 'building_info', 'room_number', 'name', 'full_name',
            'capacity', 'room_type', 'room_type_display', 'floor', 'area',
            'equipment', 'equipment_list', 'location_description',
            'is_available', 'is_active', 'maintenance_notes', 'last_maintenance',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'full_name', 'equipment_list', 'created_at', 'updated_at']
    
    def get_building_info(self, obj):
        """获取教学楼信息"""
        return {
            'id': obj.building.id,
            'name': obj.building.name,
            'code': obj.building.code
        }


class ClassroomListSerializer(serializers.ModelSerializer):
    """教室列表序列化器（简化版）"""
    
    building_name = serializers.CharField(source='building.name', read_only=True)
    building_code = serializers.CharField(source='building.code', read_only=True)
    full_name = serializers.ReadOnlyField()
    room_type_display = serializers.CharField(source='get_room_type_display', read_only=True)
    
    class Meta:
        model = Classroom
        fields = [
            'id', 'building', 'building_name', 'building_code',
            'room_number', 'name', 'full_name', 'capacity',
            'room_type', 'room_type_display', 'floor',
            'is_available', 'is_active'
        ]


class ClassroomAvailabilitySerializer(serializers.Serializer):
    """教室可用性序列化器"""
    
    classroom_id = serializers.IntegerField()
    classroom_name = serializers.CharField()
    day_of_week = serializers.IntegerField()
    time_slot_id = serializers.IntegerField()
    time_slot_name = serializers.CharField()
    is_available = serializers.BooleanField()
    occupied_by = serializers.CharField(required=False, allow_null=True)


class ClassroomUtilizationSerializer(serializers.Serializer):
    """教室利用率序列化器"""
    
    classroom_id = serializers.IntegerField()
    classroom_name = serializers.CharField()
    total_time_slots = serializers.IntegerField()
    occupied_time_slots = serializers.IntegerField()
    utilization_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    week_number = serializers.IntegerField()
    semester = serializers.CharField()
