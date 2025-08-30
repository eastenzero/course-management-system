# file: data-generator/generators/facility.py
# 功能: 设施时间数据生成器

import random
from typing import List, Dict, Any, Tuple
from datetime import datetime, time, timedelta
from faker import Faker

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import FACILITY_CONFIG


class FacilityGenerator:
    """设施数据生成器
    
    负责生成教室和时间段数据，包括：
    - 教室基本信息和设备
    - 时间段配置
    - 教室使用规则和限制
    - 设备维护状态
    """
    
    def __init__(self, locale: str = 'zh_CN'):
        """初始化生成器
        
        Args:
            locale: 本地化设置，默认为中文
        """
        self.fake = Faker(locale)
        self.building_names = FACILITY_CONFIG['building_names']
        self.room_types = FACILITY_CONFIG['room_types']
        self.time_slots = FACILITY_CONFIG['time_slots']
        
        # 设置随机种子
        Faker.seed(42)
        random.seed(42)
    
    def generate_classrooms(self, count: int) -> List[Dict[str, Any]]:
        """生成教室数据
        
        Args:
            count: 要生成的教室数量
            
        Returns:
            教室数据列表
        """
        classrooms = []
        
        for i in range(count):
            building = random.choice(self.building_names)
            floor = random.randint(1, 6)
            room_number = f"{floor}{random.randint(10, 99):02d}"
            
            room_type = random.choice(list(self.room_types.keys()))
            type_info = self.room_types[room_type]
            
            capacity = random.randint(*type_info["capacity_range"])
            base_equipment = type_info["equipment"].copy()
            
            # 随机添加额外设备
            extra_equipment = ["空调", "暖气", "窗帘", "WiFi", "监控", "录播设备", "智能黑板"]
            additional_equipment = random.sample(extra_equipment, random.randint(0, 4))
            all_equipment = base_equipment + additional_equipment
            
            classroom = {
                'id': i + 1,
                'building': building,
                'floor': floor,
                'room_number': room_number,
                'full_name': f"{building}{room_number}",
                'room_type': room_type,
                'capacity': capacity,
                'actual_capacity': int(capacity * random.uniform(0.8, 1.0)),  # 实际可用容量
                'area': self._calculate_area(capacity),
                'equipment': all_equipment,
                'equipment_status': self._generate_equipment_status(all_equipment),
                'is_available': random.choices([True, False], weights=[0.95, 0.05])[0],
                'availability_reason': self._generate_availability_reason(),
                'maintenance_status': random.choices(['正常', '维修中', '待维修'], weights=[0.9, 0.05, 0.05])[0],
                'last_maintenance': self.fake.date_between(start_date='-1y', end_date='now'),
                'next_maintenance': self.fake.date_between(start_date='now', end_date='+6m'),
                'booking_rules': self._generate_booking_rules(room_type),
                'usage_restrictions': self._generate_usage_restrictions(room_type),
                'hourly_rate': self._calculate_hourly_rate(room_type, capacity),
                'cleaning_schedule': self._generate_cleaning_schedule(),
                'security_level': random.choices(['普通', '受限', '保密'], weights=[0.8, 0.15, 0.05])[0],
                'accessibility': self._generate_accessibility_features(),
                'environmental_controls': self._generate_environmental_controls(),
                'manager': self.fake.name(),
                'manager_phone': self.fake.phone_number(),
                'manager_email': f"room{i+1}@university.edu.cn",
                'emergency_contact': self.fake.phone_number(),
                'location_description': self._generate_location_description(building, floor),
                'nearby_facilities': self._generate_nearby_facilities(),
                'parking_info': self._generate_parking_info(building),
                'photos': self._generate_photo_urls(i + 1),
                'qr_code': f"QR{i+1:06d}",
                'utilization_rate': round(random.uniform(0.3, 0.9), 2),
                'peak_hours': self._generate_peak_hours(),
                'special_features': self._generate_special_features(room_type),
                'renovation_history': self._generate_renovation_history(),
                'energy_efficiency': random.choices(['A', 'B', 'C', 'D'], weights=[0.3, 0.4, 0.2, 0.1])[0],
                'wifi_ssid': f"University-{building}-{room_number}",
                'wifi_password': self.fake.password(length=12),
                'is_smart_classroom': random.choices([True, False], weights=[0.3, 0.7])[0],
                'created_at': self.fake.date_time_between(start_date='-5y', end_date='now'),
                'updated_at': self.fake.date_time_between(start_date='-1m', end_date='now')
            }
            classrooms.append(classroom)
        
        return classrooms
    
    def generate_time_slots(self) -> List[Dict[str, Any]]:
        """生成时间段数据
        
        Returns:
            时间段数据列表
        """
        time_slots = []
        
        for i, slot in enumerate(self.time_slots):
            start_time = datetime.strptime(slot['start'], '%H:%M').time()
            end_time = datetime.strptime(slot['end'], '%H:%M').time()
            
            # 计算时长（分钟）
            start_minutes = start_time.hour * 60 + start_time.minute
            end_minutes = end_time.hour * 60 + end_time.minute
            duration = end_minutes - start_minutes
            
            time_slot = {
                'id': i + 1,
                'name': slot['name'],
                'start_time': slot['start'],
                'end_time': slot['end'],
                'duration': duration,
                'break_time': self._calculate_break_time(i, len(self.time_slots)),
                'period': self._get_period(slot['start']),
                'is_active': True,
                'is_prime_time': self._is_prime_time(start_time),
                'order': i + 1,
                'day_sequence': (i % 5) + 1,  # 假设一天5个时间段
                'week_pattern': self._generate_week_pattern(),
                'semester_weeks': self._generate_semester_weeks(),
                'holiday_schedule': self._generate_holiday_schedule(),
                'exam_period': self._is_exam_period(i),
                'popularity_score': self._calculate_popularity_score(start_time),
                'conflict_probability': self._calculate_conflict_probability(start_time),
                'teacher_preference': self._calculate_teacher_preference(start_time),
                'student_preference': self._calculate_student_preference(start_time),
                'energy_cost': self._calculate_energy_cost(start_time),
                'description': f"{slot['name']} ({slot['start']}-{slot['end']})",
                'usage_guidelines': self._generate_usage_guidelines(slot['name']),
                'created_at': self.fake.date_time_between(start_date='-2y', end_date='now'),
                'updated_at': self.fake.date_time_between(start_date='-6m', end_date='now')
            }
            time_slots.append(time_slot)
        
        return time_slots
    
    def _calculate_area(self, capacity: int) -> int:
        """根据容量计算面积"""
        # 假设每人需要1.5-2.5平方米
        area_per_person = random.uniform(1.5, 2.5)
        return int(capacity * area_per_person)
    
    def _generate_equipment_status(self, equipment: List[str]) -> Dict[str, str]:
        """生成设备状态"""
        status_options = ['正常', '维修中', '待更换', '已损坏']
        status_weights = [0.85, 0.08, 0.05, 0.02]
        
        equipment_status = {}
        for item in equipment:
            equipment_status[item] = random.choices(status_options, weights=status_weights)[0]
        
        return equipment_status
    
    def _generate_availability_reason(self) -> str:
        """生成可用性原因"""
        reasons = [
            '正常使用', '设备维修', '清洁消毒', '特殊活动',
            '安全检查', '装修改造', '设备升级', '临时占用'
        ]
        return random.choice(reasons)
    
    def _generate_booking_rules(self, room_type: str) -> Dict[str, Any]:
        """生成预订规则"""
        if room_type == '实验室':
            return {
                'advance_booking_days': 7,
                'max_booking_hours': 4,
                'requires_approval': True,
                'approval_level': '院系主任',
                'special_requirements': '需要实验安全培训证书'
            }
        elif room_type == '机房':
            return {
                'advance_booking_days': 3,
                'max_booking_hours': 6,
                'requires_approval': True,
                'approval_level': '实验中心',
                'special_requirements': '需要机房使用许可'
            }
        elif room_type == '阶梯教室':
            return {
                'advance_booking_days': 14,
                'max_booking_hours': 8,
                'requires_approval': True,
                'approval_level': '教务处',
                'special_requirements': '大型活动需要额外审批'
            }
        else:
            return {
                'advance_booking_days': 1,
                'max_booking_hours': 8,
                'requires_approval': False,
                'approval_level': '无',
                'special_requirements': '无'
            }
    
    def _generate_usage_restrictions(self, room_type: str) -> List[str]:
        """生成使用限制"""
        common_restrictions = ['禁止吸烟', '禁止饮食', '保持安静']
        
        if room_type == '实验室':
            return common_restrictions + ['穿戴防护用品', '遵守实验安全规程', '禁止携带易燃易爆物品']
        elif room_type == '机房':
            return common_restrictions + ['禁止安装软件', '禁止修改系统设置', '使用完毕关闭电源']
        elif room_type == '多媒体教室':
            return common_restrictions + ['爱护设备', '使用后归位', '禁止私自调节设备']
        else:
            return common_restrictions
    
    def _calculate_hourly_rate(self, room_type: str, capacity: int) -> float:
        """计算小时费率"""
        base_rates = {
            '普通教室': 0,
            '多媒体教室': 50,
            '实验室': 100,
            '机房': 80,
            '阶梯教室': 200,
            '研讨室': 30
        }
        
        base_rate = base_rates.get(room_type, 0)
        # 根据容量调整费率
        capacity_factor = 1 + (capacity - 50) / 100
        return round(base_rate * capacity_factor, 2)
    
    def _generate_cleaning_schedule(self) -> Dict[str, Any]:
        """生成清洁计划"""
        return {
            'daily_cleaning': '每日晚上',
            'deep_cleaning': '每周末',
            'disinfection': '每月一次',
            'last_cleaned': self.fake.date_time_between(start_date='-3d', end_date='now'),
            'cleaning_staff': self.fake.name(),
            'cleaning_checklist': ['地面清洁', '桌椅整理', '设备擦拭', '垃圾清理', '通风换气']
        }

    def _generate_accessibility_features(self) -> List[str]:
        """生成无障碍设施"""
        features = ['轮椅通道', '无障碍洗手间', '盲文标识', '语音提示', '扶手设施']
        return random.sample(features, random.randint(0, 3))

    def _generate_environmental_controls(self) -> Dict[str, Any]:
        """生成环境控制信息"""
        return {
            'temperature_range': f"{random.randint(18, 22)}-{random.randint(24, 28)}°C",
            'humidity_control': random.choice([True, False]),
            'air_quality_monitor': random.choice([True, False]),
            'noise_level': f"<{random.randint(40, 60)}dB",
            'lighting_type': random.choice(['LED', '荧光灯', '自然光+LED']),
            'lighting_control': random.choice(['手动', '自动感应', '智能调节'])
        }

    def _generate_location_description(self, building: str, floor: int) -> str:
        """生成位置描述"""
        directions = ['东侧', '西侧', '南侧', '北侧', '中央']
        direction = random.choice(directions)
        return f"位于{building}{floor}楼{direction}，靠近电梯/楼梯"

    def _generate_nearby_facilities(self) -> List[str]:
        """生成附近设施"""
        facilities = [
            '洗手间', '饮水机', '复印室', '休息区', '咖啡厅',
            '图书角', '储物柜', '打印机', '自动售货机', '急救箱'
        ]
        return random.sample(facilities, random.randint(2, 5))

    def _generate_parking_info(self, building: str) -> Dict[str, Any]:
        """生成停车信息"""
        return {
            'parking_available': random.choices([True, False], weights=[0.7, 0.3])[0],
            'parking_spaces': random.randint(10, 100) if random.choice([True, False]) else 0,
            'parking_fee': random.choice([0, 5, 10, 15]),
            'parking_location': f"{building}附近停车场",
            'bicycle_parking': random.choices([True, False], weights=[0.9, 0.1])[0]
        }

    def _generate_photo_urls(self, room_id: int) -> List[str]:
        """生成照片URL"""
        num_photos = random.randint(3, 8)
        return [f"http://photos.university.edu.cn/room{room_id}/photo{i+1}.jpg"
                for i in range(num_photos)]

    def _generate_peak_hours(self) -> List[str]:
        """生成高峰使用时间"""
        peak_periods = ['8:00-10:00', '10:00-12:00', '14:00-16:00', '16:00-18:00', '19:00-21:00']
        return random.sample(peak_periods, random.randint(2, 4))

    def _generate_special_features(self, room_type: str) -> List[str]:
        """生成特殊功能"""
        features_map = {
            '多媒体教室': ['高清投影', '环绕音响', '无线话筒', '录播功能'],
            '实验室': ['通风系统', '安全淋浴', '紧急报警', '防爆设施'],
            '机房': ['UPS电源', '防静电地板', '温湿度控制', '网络监控'],
            '阶梯教室': ['阶梯座椅', '大屏幕', '扩音系统', '同声传译'],
            '研讨室': ['圆桌会议', '白板墙面', '视频会议', '茶水设施']
        }

        default_features = ['WiFi覆盖', '电源插座', '空调系统']
        specific_features = features_map.get(room_type, [])

        all_features = default_features + specific_features
        return random.sample(all_features, random.randint(2, len(all_features)))

    def _generate_renovation_history(self) -> List[Dict[str, Any]]:
        """生成装修历史"""
        num_renovations = random.randint(0, 3)
        renovations = []

        for i in range(num_renovations):
            renovation = {
                'date': self.fake.date_between(start_date='-10y', end_date='-1y'),
                'type': random.choice(['全面装修', '设备更新', '局部改造', '维护保养']),
                'cost': random.randint(10000, 500000),
                'contractor': self.fake.company(),
                'description': '教室设施升级改造'
            }
            renovations.append(renovation)

        return renovations

    def _calculate_break_time(self, slot_index: int, total_slots: int) -> int:
        """计算课间休息时间"""
        if slot_index == total_slots - 1:  # 最后一节课
            return 0
        elif slot_index in [1, 3, 5, 7]:  # 某些节次有长休息
            return 20
        else:
            return 10

    def _get_period(self, start_time: str) -> str:
        """根据开始时间确定时段"""
        hour = int(start_time.split(':')[0])
        if hour < 12:
            return "上午"
        elif hour < 18:
            return "下午"
        else:
            return "晚上"

    def _is_prime_time(self, start_time: time) -> bool:
        """判断是否为黄金时间"""
        hour = start_time.hour
        # 上午9-11点，下午2-4点为黄金时间
        return (9 <= hour <= 11) or (14 <= hour <= 16)

    def _generate_week_pattern(self) -> List[bool]:
        """生成周模式（周一到周日是否开放）"""
        # 周一到周五通常开放，周末部分开放
        weekdays = [True] * 5  # 周一到周五
        weekend = [random.choices([True, False], weights=[0.3, 0.7])[0] for _ in range(2)]  # 周末
        return weekdays + weekend

    def _generate_semester_weeks(self) -> List[int]:
        """生成学期周次"""
        # 通常18周的学期，某些周可能不开课
        all_weeks = list(range(1, 19))
        # 随机排除一些周次（如考试周、假期等）
        excluded_weeks = random.sample(all_weeks, random.randint(0, 3))
        return [week for week in all_weeks if week not in excluded_weeks]

    def _generate_holiday_schedule(self) -> Dict[str, bool]:
        """生成节假日安排"""
        holidays = {
            '国庆节': False,
            '春节': False,
            '清明节': random.choice([True, False]),
            '劳动节': random.choice([True, False]),
            '端午节': random.choice([True, False]),
            '中秋节': random.choice([True, False])
        }
        return holidays

    def _is_exam_period(self, slot_index: int) -> bool:
        """判断是否为考试时间段"""
        # 某些时间段更适合考试
        exam_slots = [2, 3, 5, 6]  # 上午第3-4节，下午第1-2节
        return slot_index in exam_slots

    def _calculate_popularity_score(self, start_time: time) -> float:
        """计算时间段受欢迎程度"""
        hour = start_time.hour
        if 9 <= hour <= 11:  # 上午黄金时间
            return random.uniform(0.8, 1.0)
        elif 14 <= hour <= 16:  # 下午黄金时间
            return random.uniform(0.7, 0.9)
        elif hour < 9 or hour > 18:  # 早晚时间
            return random.uniform(0.3, 0.6)
        else:
            return random.uniform(0.6, 0.8)

    def _calculate_conflict_probability(self, start_time: time) -> float:
        """计算冲突概率"""
        hour = start_time.hour
        if 9 <= hour <= 11 or 14 <= hour <= 16:  # 热门时间段
            return random.uniform(0.6, 0.9)
        else:
            return random.uniform(0.2, 0.5)

    def _calculate_teacher_preference(self, start_time: time) -> float:
        """计算教师偏好度"""
        hour = start_time.hour
        if 9 <= hour <= 11:  # 教师偏好上午
            return random.uniform(0.7, 1.0)
        elif 14 <= hour <= 17:  # 下午也可接受
            return random.uniform(0.5, 0.8)
        else:  # 早晚时间偏好较低
            return random.uniform(0.2, 0.5)

    def _calculate_student_preference(self, start_time: time) -> float:
        """计算学生偏好度"""
        hour = start_time.hour
        if 10 <= hour <= 11 or 15 <= hour <= 16:  # 学生偏好时间
            return random.uniform(0.8, 1.0)
        elif hour < 8 or hour > 19:  # 太早或太晚
            return random.uniform(0.1, 0.4)
        else:
            return random.uniform(0.5, 0.8)

    def _calculate_energy_cost(self, start_time: time) -> float:
        """计算能耗成本"""
        hour = start_time.hour
        if 19 <= hour <= 21:  # 晚上需要更多照明
            return random.uniform(1.2, 1.5)
        elif 12 <= hour <= 14:  # 中午可能需要更多空调
            return random.uniform(1.1, 1.3)
        else:
            return random.uniform(0.8, 1.1)

    def _generate_usage_guidelines(self, slot_name: str) -> List[str]:
        """生成使用指南"""
        guidelines = [
            '提前10分钟到达教室',
            '课前检查设备状态',
            '课后整理教室环境',
            '遇到问题及时联系管理员'
        ]

        if '晚' in slot_name:
            guidelines.append('注意教学楼开放时间')
            guidelines.append('确保安全离开')

        if '第1节' in slot_name:
            guidelines.append('注意开门时间')
            guidelines.append('检查教室清洁状况')

        return guidelines
