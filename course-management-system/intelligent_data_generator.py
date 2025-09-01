#!/usr/bin/env python
"""
智能数据生成器 - 基于排课算法约束的大规模数据生成系统
针对80万学生规模，生成匹配的教室、课程、排课和选课数据
"""

# 设置环境变量，禁用有问题的模块
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'course_management.settings'
os.environ['DISABLE_MAGIC'] = '1'  # 禁用magic模块

import sys
import django
import random
import json
from datetime import datetime, time, date
from typing import List, Dict, Any, Set, Tuple
from dataclasses import dataclass
from faker import Faker
import math
# from tqdm import tqdm  # 移除tqdm依赖

# 添加backend目录到Python路径
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.append(backend_path)

# 修改magic模块导入问题
import builtins
original_import = builtins.__import__

def patched_import(name, *args, **kwargs):
    if name == 'magic':
        # 创建一个虚拟magic模块
        class FakeMagic:
            def from_buffer(self, buffer, mime=False):
                return 'application/octet-stream'
        
        class MockMagic:
            Magic = FakeMagic
            
        return MockMagic()
    return original_import(name, *args, **kwargs)

builtins.__import__ = patched_import

try:
    django.setup()
except Exception as e:
    print(f"警告: Django初始化问题: {e}")
    print("尝试继续运行...")

from django.contrib.auth import get_user_model
from apps.classrooms.models import Building, Classroom
from apps.courses.models import Course
from apps.schedules.models import Schedule, TimeSlot
from apps.courses.models import Enrollment
from django.db import transaction
from django.utils import timezone

User = get_user_model()
fake = Faker('zh_CN')

@dataclass
class GenerationConfig:
    """数据生成配置"""
    # 目标数量
    target_buildings: int = 50
    target_classrooms: int = 3500
    target_courses: int = 15000
    target_schedules: int = 180000
    target_enrollments: int = 5607049
    
    # 约束参数
    classroom_utilization_rate: float = 0.75  # 教室利用率
    student_course_avg: int = 7  # 学生平均选课数
    teacher_max_weekly_hours: int = 20  # 教师最大周学时
    teacher_max_daily_hours: int = 8   # 教师最大日学时
    
    # 批处理参数
    batch_size: int = 5000
    progress_update_interval: int = 1000

class ConstraintAwareGenerator:
    """基于约束的智能数据生成器"""
    
    def __init__(self, config: GenerationConfig):
        self.config = config
        self.fake = Faker('zh_CN')
        
        # 教学楼配置
        self.building_types = [
            "文科教学楼", "理科教学楼", "工科实验楼", "综合教学楼", 
            "图书馆", "实验中心", "艺术楼", "体育馆", "学生活动中心", "行政楼"
        ]
        
        # 教室类型配置（符合排课算法约束）
        self.room_types = {
            'lecture': {
                'name': '普通教室',
                'capacity_range': (30, 150),
                'equipment': ['投影仪', '音响', '黑板', '网络接口'],
                'weight': 0.6  # 60%的教室是普通教室
            },
            'multimedia': {
                'name': '多媒体教室', 
                'capacity_range': (50, 200),
                'equipment': ['投影仪', '音响', '电脑', '网络', '智能黑板'],
                'weight': 0.15
            },
            'lab': {
                'name': '实验室',
                'capacity_range': (20, 60),
                'equipment': ['实验台', '仪器设备', '通风系统', '安全设备'],
                'weight': 0.15
            },
            'computer': {
                'name': '机房',
                'capacity_range': (30, 80),
                'equipment': ['电脑', '网络', '投影仪', '空调', '打印机'],
                'weight': 0.05
            },
            'seminar': {
                'name': '研讨室',
                'capacity_range': (10, 30),
                'equipment': ['白板', '投影仪', '圆桌', '网络'],
                'weight': 0.03
            },
            'auditorium': {
                'name': '阶梯教室',
                'capacity_range': (100, 500),
                'equipment': ['投影仪', '音响', '话筒', '灯光', '录播设备'],
                'weight': 0.02
            }
        }
        
        # 院系与专业配置
        self.departments = {
            "计算机学院": ["计算机科学与技术", "软件工程", "网络工程", "数据科学与大数据技术", "人工智能"],
            "数学学院": ["数学与应用数学", "信息与计算科学", "统计学", "金融数学"],
            "物理学院": ["物理学", "应用物理学", "光电信息科学与工程", "材料物理"],
            "化学学院": ["化学", "应用化学", "材料化学", "化学工程与工艺"],
            "生物学院": ["生物科学", "生物技术", "生物信息学", "生态学"],
            "外国语学院": ["英语", "日语", "法语", "德语", "俄语"],
            "经济管理学院": ["经济学", "金融学", "国际经济与贸易", "工商管理", "市场营销", "会计学"],
            "文学院": ["汉语言文学", "新闻学", "广告学", "历史学"],
            "艺术学院": ["音乐学", "美术学", "舞蹈学", "设计学"],
            "体育学院": ["体育教育", "运动训练", "社会体育"],
            "医学院": ["临床医学", "预防医学", "护理学", "药学"],
            "法学院": ["法学", "政治学", "社会学"],
            "教育学院": ["教育学", "心理学", "学前教育"],
            "工学院": ["机械工程", "电气工程", "土木工程", "建筑学", "环境工程"],
            "材料学院": ["材料科学与工程", "冶金工程", "高分子材料"]
        }
        
        # 课程类型配置
        self.course_types = {
            'required': {'weight': 0.4, 'credits_range': (3, 6)},
            'elective': {'weight': 0.35, 'credits_range': (2, 4)},
            'public': {'weight': 0.15, 'credits_range': (1, 3)},
            'professional': {'weight': 0.1, 'credits_range': (2, 5)}
        }

    def generate_buildings(self) -> List[Dict]:
        """生成教学楼数据"""
        print(f"🏢 生成教学楼数据 ({self.config.target_buildings} 栋)...")
        
        buildings = []
        # 确保建筑名称唯一
        building_names = set()
        
        for i in range(self.config.target_buildings):
            building_type = random.choice(self.building_types)
            
            # 确保名称唯一
            counter = 1
            while True:
                name = f"{building_type}{chr(65 + (i + counter - 1) % 26)}栋"
                code = f"BUILD_{i+1:03d}"
                if name not in building_names:
                    building_names.add(name)
                    break
                counter += 1
            
            building = {
                'name': name,
                'code': code,
                'address': f"校园{random.choice(['东', '西', '南', '北', '中'])}区",
                'description': f"{building_type}，共{random.randint(3, 12)}层",
                'is_active': True
            }
            buildings.append(building)
        
        return buildings

    def generate_classrooms(self, buildings: List[Dict]) -> List[Dict]:
        """生成教室数据（满足排课算法约束）"""
        print(f"🏫 生成教室数据 ({self.config.target_classrooms} 间)...")
        
        classrooms = []
        rooms_per_building = math.ceil(self.config.target_classrooms / len(buildings))
        
        for idx, building in enumerate(buildings):
            print(f"\r生成教室进度: {idx+1}/{len(buildings)} ({(idx+1)/len(buildings)*100:.1f}%)", end="")
            building_rooms = 0
            floors = random.randint(3, 12)
            
            for floor in range(1, floors + 1):
                rooms_on_floor = random.randint(8, 20)
                
                for room_num in range(1, rooms_on_floor + 1):
                    if building_rooms >= rooms_per_building:
                        break
                    
                    # 随机选择教室类型（按权重）
                    room_type = random.choices(
                        list(self.room_types.keys()),
                        weights=[config['weight'] for config in self.room_types.values()]
                    )[0]
                    
                    type_config = self.room_types[room_type]
                    capacity = random.randint(*type_config['capacity_range'])
                    
                    # 生成教室号
                    room_number = f"{floor}{room_num:02d}"
                    
                    classroom = {
                        'building_id': building['code'],  # 将与Building关联
                        'room_number': room_number,
                        'name': f"{building['name']}{room_number}",
                        'capacity': capacity,
                        'room_type': room_type,
                        'floor': floor,
                        'area': self._calculate_area(capacity),
                        'equipment': self._generate_equipment(type_config['equipment']),
                        'location_description': f"位于{building['name']}{floor}楼",
                        'is_available': random.choices([True, False], weights=[0.95, 0.05])[0],
                        'is_active': True,
                        'maintenance_notes': self._generate_maintenance_notes()
                    }
                    
                    classrooms.append(classroom)
                    building_rooms += 1
                    
                    if len(classrooms) >= self.config.target_classrooms:
                        return classrooms
                
                if building_rooms >= rooms_per_building:
                    break
        
        return classrooms

    def generate_time_slots(self) -> List[Dict]:
        """生成时间段数据（符合排课算法）"""
        print("⏰ 生成时间段数据...")
        
        # 标准时间段配置（每节课45分钟）
        standard_slots = [
            {"name": "第1节", "start": "08:00", "end": "08:45", "period": "上午"},
            {"name": "第2节", "start": "08:55", "end": "09:40", "period": "上午"},
            {"name": "第3节", "start": "10:00", "end": "10:45", "period": "上午"},
            {"name": "第4节", "start": "10:55", "end": "11:40", "period": "上午"},
            {"name": "第5节", "start": "14:00", "end": "14:45", "period": "下午"},
            {"name": "第6节", "start": "14:55", "end": "15:40", "period": "下午"},
            {"name": "第7节", "start": "16:00", "end": "16:45", "period": "下午"},
            {"name": "第8节", "start": "16:55", "end": "17:40", "period": "下午"},
            {"name": "第9节", "start": "19:00", "end": "19:45", "period": "晚上"},
            {"name": "第10节", "start": "19:55", "end": "20:40", "period": "晚上"},
        ]
        
        time_slots = []
        for i, slot in enumerate(standard_slots):
            time_slot = {
                'name': slot['name'],
                'start_time': slot['start'],
                'end_time': slot['end'],
                'order': i + 1,
                'is_active': True,
                'description': f"{slot['name']} ({slot['start']}-{slot['end']})",
                'period': slot['period']
            }
            time_slots.append(time_slot)
        
        return time_slots

    def _calculate_area(self, capacity: int) -> float:
        """根据容量计算教室面积"""
        # 按每人1.5-2.5平方米计算
        return round(capacity * random.uniform(1.5, 2.5), 2)

    def _generate_equipment(self, base_equipment: List[str]) -> Dict:
        """生成设备信息"""
        equipment = {}
        for item in base_equipment:
            equipment[item] = random.choice([True, False]) if item not in ['投影仪'] else True
        
        # 随机添加额外设备
        extra_equipment = ["空调", "暖气", "窗帘", "WiFi", "监控", "录播设备"]
        for item in random.sample(extra_equipment, random.randint(0, 4)):
            equipment[item] = True
        
        return equipment

    def _generate_maintenance_notes(self) -> str:
        """生成维护备注"""
        notes = [
            "设备状态良好", "需定期清洁", "投影仪需要更换灯泡", 
            "空调制冷效果待检查", "网络连接正常", "桌椅完好"
        ]
        return random.choice(notes) if random.random() < 0.3 else ""

class DatabaseManager:
    """数据库操作管理器"""
    
    def __init__(self, config: GenerationConfig):
        self.config = config

    def save_buildings(self, buildings: List[Dict]) -> Dict[str, Building]:
        """保存教学楼数据"""
        print("💾 保存教学楼数据到数据库...")
        
        building_map = {}
        created_count = 0
        
        with transaction.atomic():
            for idx, building_data in enumerate(buildings):
                if idx % 10 == 0:
                    print(f"\r保存教学楼进度: {idx+1}/{len(buildings)} ({(idx+1)/len(buildings)*100:.1f}%)", end="")
                
                try:
                    building, created = Building.objects.get_or_create(
                        name=building_data['name'],
                        defaults={
                            'code': building_data['code'],
                            'address': building_data['address'],
                            'description': building_data['description'],
                            'is_active': building_data['is_active']
                        }
                    )
                    building_map[building_data['code']] = building
                    if created:
                        created_count += 1
                except Exception as e:
                    print(f"\n⚠️  跳过重复教学楼: {building_data['name']} - {e}")
                    continue
        
        print(f"✅ 教学楼保存完成：新增 {created_count} 栋，总计 {len(buildings)} 栋")
        return building_map

    def save_classrooms(self, classrooms: List[Dict], building_map: Dict[str, Building]) -> int:
        """保存教室数据"""
        print("💾 保存教室数据到数据库...")
        
        created_count = 0
        batch = []
        
        for i, classroom_data in enumerate(classrooms):
            if i % 500 == 0:
                print(f"\r保存教室进度: {i+1}/{len(classrooms)} ({(i+1)/len(classrooms)*100:.1f}%)", end="")
            building = building_map.get(classroom_data['building_id'])
            if not building:
                continue
            
            # 检查是否已存在
            existing = Classroom.objects.filter(
                building=building,
                room_number=classroom_data['room_number']
            ).exists()
            
            if not existing:
                classroom = Classroom(
                    building=building,
                    room_number=classroom_data['room_number'],
                    name=classroom_data['name'],
                    capacity=classroom_data['capacity'],
                    room_type=classroom_data['room_type'],
                    floor=classroom_data['floor'],
                    area=classroom_data['area'],
                    equipment=classroom_data['equipment'],
                    location_description=classroom_data['location_description'],
                    is_available=classroom_data['is_available'],
                    is_active=classroom_data['is_active'],
                    maintenance_notes=classroom_data['maintenance_notes']
                )
                batch.append(classroom)
                created_count += 1
            
            # 批量保存
            if len(batch) >= self.config.batch_size or i == len(classrooms) - 1:
                if batch:
                    Classroom.objects.bulk_create(batch, ignore_conflicts=True)
                    batch = []
        
        print(f"✅ 教室保存完成：新增 {created_count} 间教室")
        return created_count

    def save_time_slots(self, time_slots: List[Dict]) -> int:
        """保存时间段数据"""
        print("💾 保存时间段数据到数据库...")
        
        created_count = 0
        
        with transaction.atomic():
            for slot_data in time_slots:
                time_slot, created = TimeSlot.objects.get_or_create(
                    name=slot_data['name'],
                    defaults={
                        'start_time': datetime.strptime(slot_data['start_time'], '%H:%M').time(),
                        'end_time': datetime.strptime(slot_data['end_time'], '%H:%M').time(),
                        'order': slot_data['order'],
                        'is_active': slot_data['is_active']
                    }
                )
                if created:
                    created_count += 1
        
        print(f"✅ 时间段保存完成：新增 {created_count} 个时间段")
        return created_count

def main():
    """主函数"""
    print("🚀 智能数据生成器启动")
    print("=" * 60)
    
    # 检查当前数据状况
    current_students = User.objects.filter(user_type='student').count()
    current_teachers = User.objects.filter(user_type='teacher').count()
    current_classrooms = Classroom.objects.count()
    current_courses = Course.objects.count()
    
    print(f"📊 当前数据状况：")
    print(f"   学生数量: {current_students:,}")
    print(f"   教师数量: {current_teachers:,}")
    print(f"   教室数量: {current_classrooms:,}")
    print(f"   课程数量: {current_courses:,}")
    print()
    
    if current_students == 0:
        print("❌ 错误：数据库中没有学生数据，请先确保有基础用户数据")
        return
    
    # 初始化配置和生成器
    config = GenerationConfig()
    generator = ConstraintAwareGenerator(config)
    db_manager = DatabaseManager(config)
    
    start_time = datetime.now()
    
    try:
        # 1. 生成并保存教学楼
        print("🏢 第一阶段：生成教学楼数据")
        buildings = generator.generate_buildings()
        building_map = db_manager.save_buildings(buildings)
        
        # 2. 生成并保存教室
        print("\n🏫 第二阶段：生成教室数据")
        classrooms = generator.generate_classrooms(buildings)
        created_classrooms = db_manager.save_classrooms(classrooms, building_map)
        
        # 3. 生成并保存时间段
        print("\n⏰ 第三阶段：生成时间段数据")
        time_slots = generator.generate_time_slots()
        created_time_slots = db_manager.save_time_slots(time_slots)
        
        # 计算用时
        end_time = datetime.now()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print("🎉 教室和基础设施数据生成完成！")
        print(f"⏱️  总用时: {duration}")
        print(f"🏢 教学楼: {len(buildings)} 栋")
        print(f"🏫 教室: {created_classrooms} 间")
        print(f"⏰ 时间段: {created_time_slots} 个")
        print()
        print("📋 下一步：运行课程数据生成器")
        print("   python intelligent_course_generator.py")
        
    except Exception as e:
        print(f"❌ 生成过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()