#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据迁移脚本 - 从SQLite到PostgreSQL
将results目录中的SQLite数据导入到现有的PostgreSQL课程管理系统
"""

import sqlite3
import psycopg2
import psycopg2.extras
from psycopg2 import sql
import json
from datetime import datetime, date, time
import re

class DataMigration:
    def __init__(self, sqlite_path, postgres_config):
        """
        初始化数据迁移器
        
        Args:
            sqlite_path: SQLite数据库路径
            postgres_config: PostgreSQL连接配置字典
        """
        self.sqlite_path = sqlite_path
        self.postgres_config = postgres_config
        self.sqlite_conn = None
        self.postgres_conn = None
        
        # 数据映射配置
        self.building_mapping = {}  # SQLite building_id -> PostgreSQL building_id
        self.room_mapping = {}      # SQLite room_id -> PostgreSQL classroom_id
        self.course_mapping = {}    # SQLite course_id -> PostgreSQL course_id
        self.teacher_mapping = {}   # SQLite teacher_id -> PostgreSQL teacher_id
        self.time_slot_mapping = {} # SQLite slot_id -> PostgreSQL time_slot_id
        
    def connect_databases(self):
        """连接SQLite和PostgreSQL数据库"""
        try:
            # 连接SQLite
            self.sqlite_conn = sqlite3.connect(self.sqlite_path)
            self.sqlite_conn.row_factory = sqlite3.Row
            print("✅ 成功连接SQLite数据库")
            
            # 连接PostgreSQL
            self.postgres_conn = psycopg2.connect(**self.postgres_config)
            print("✅ 成功连接PostgreSQL数据库")
            
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            raise
    
    def get_sqlite_data(self, table_name, limit=None):
        """从SQLite获取数据"""
        cursor = self.sqlite_conn.cursor()
        query = f"SELECT * FROM {table_name}"
        if limit:
            query += f" LIMIT {limit}"
        cursor.execute(query)
        return cursor.fetchall()
    
    def execute_postgres_query(self, query, params=None):
        """执行PostgreSQL查询"""
        cursor = self.postgres_conn.cursor()
        try:
            cursor.execute(query, params)
            self.postgres_conn.commit()
            return cursor
        except Exception as e:
            self.postgres_conn.rollback()
            print(f"❌ PostgreSQL查询失败: {query} - {e}")
            raise
    
    def migrate_buildings(self):
        """迁移教学楼数据"""
        print("\n🏢 开始迁移教学楼数据...")
        
        buildings = self.get_sqlite_data("buildings")
        migrated_count = 0
        
        for building in buildings:
            try:
                # 检查是否已存在
                cursor = self.execute_postgres_query(
                    "SELECT id FROM classrooms_building WHERE code = %s",
                    (building['building_code'],)
                )
                existing = cursor.fetchone()
                
                if existing:
                    self.building_mapping[building['building_id']] = existing[0]
                    print(f"  📝 教学楼已存在: {building['building_name']} (ID: {existing[0]})")
                    continue
                
                # 检查是否已存在（通过name）
                cursor = self.execute_postgres_query(
                    "SELECT id FROM classrooms_building WHERE name = %s",
                    (building['building_name'],)
                )
                existing = cursor.fetchone()
                
                if existing:
                    self.building_mapping[building['building_id']] = existing[0]
                    print(f"  📝 教学楼已存在: {building['building_name']} (ID: {existing[0]})")
                    continue
            
                # 插入新数据
                cursor = self.execute_postgres_query(
                    """INSERT INTO classrooms_building 
                       (name, code, address, description, is_active, created_at, updated_at)
                       VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id""",
                    (
                        building['building_name'],
                        building['building_code'],
                        building['location'] or f"教学楼{building['building_name']}",
                        f"{building['building_name']} - {building['floors']}层",
                        True,
                        building['created_at'] or datetime.now(),
                        datetime.now()
                    )
                )
                new_id = cursor.fetchone()[0]
                self.building_mapping[building['building_id']] = new_id
                migrated_count += 1
                print(f"  ✅ 迁移教学楼: {building['building_name']} (ID: {new_id})")
                    
            except Exception as e:
                print(f"  ❌ 迁移失败: {building['building_name']} - {e}")
        
        print(f"🏢 教学楼迁移完成: {migrated_count} 条新记录")
        return migrated_count
    
    def migrate_rooms(self):
        """迁移教室数据"""
        print("\n🚪 开始迁移教室数据...")
        
        rooms = self.get_sqlite_data("rooms")
        migrated_count = 0
        
        for room in rooms:
            try:
                # 检查是否已存在
                cursor = self.execute_postgres_query(
                    "SELECT id FROM classrooms_classroom WHERE room_number = %s",
                    (room['room_code'],)
                )
                existing = cursor.fetchone()
                
                if existing:
                    self.room_mapping[room['room_id']] = existing[0]
                    print(f"  📝 教室已存在: {room['room_name']} (ID: {existing[0]})")
                else:
                    # 获取对应教学楼ID
                    building_id = self.building_mapping.get(room['building_id'])
                    if not building_id:
                        print(f"  ⚠️  跳过教室: {room['room_name']} - 未找到对应教学楼")
                        continue
                    
                    # 设备信息转换为JSON
                    equipment = {
                        "multimedia": bool(room['has_multimedia']),
                        "air_conditioner": bool(room['has_air_conditioner']),
                        "original_type": room['room_type']
                    }
                    
                    # 插入新数据
                    cursor = self.execute_postgres_query(
                        """INSERT INTO classrooms_classroom 
                           (room_number, name, capacity, room_type, floor, equipment, 
                            location_description, is_available, is_active, created_at, updated_at, building_id,
                            maintenance_notes, area, last_maintenance)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
                        (
                            room['room_code'],
                            room['room_name'],
                            room['capacity'],
                            room['room_type'] or '普通教室',
                            room['floor_number'] or 1,
                            json.dumps(equipment),
                            f"{room['room_name']} - 容量{room['capacity']}人",
                            room['status'] == '可用' if room['status'] else True,
                            True,
                            room['created_at'] or datetime.now(),
                            datetime.now(),
                            building_id,
                            '',  # maintenance_notes - 非空字段
                            50.0,  # area - 默认面积
                            datetime.now()  # last_maintenance
                        )
                    )
                    new_id = cursor.fetchone()[0]
                    self.room_mapping[room['room_id']] = new_id
                    migrated_count += 1
                    print(f"  ✅ 迁移教室: {room['room_name']} (ID: {new_id})")
                    
            except Exception as e:
                print(f"  ❌ 迁移失败: {room['room_name']} - {e}")
        
        print(f"🚪 教室迁移完成: {migrated_count} 条新记录")
        return migrated_count
    
    def migrate_courses(self):
        """迁移课程数据"""
        print("\n📚 开始迁移课程数据...")
        
        courses = self.get_sqlite_data("courses")
        migrated_count = 0
        
        for course in courses:
            try:
                # 检查是否已存在
                cursor = self.execute_postgres_query(
                    "SELECT id FROM courses_course WHERE code = %s",
                    (course['course_code'],)
                )
                existing = cursor.fetchone()
                
                if existing:
                    self.course_mapping[course['course_id']] = existing[0]
                    print(f"  📝 课程已存在: {course['course_name']} (ID: {existing[0]})")
                else:
                    # 确定课程类型
                    course_type_map = {
                        '理论课': 'theory',
                        '实验课': 'lab',
                        '实践课': 'practice',
                        '体育课': 'sports'
                    }
                    course_type = course_type_map.get(course['course_type'], 'theory')
                    
                    # 插入新数据 - 修复所有非空字段
                    cursor = self.execute_postgres_query(
                        """INSERT INTO courses_course 
                           (code, name, english_name, credits, hours, course_type, 
                            department, semester, academic_year, description, objectives,
                            max_students, min_students, 
                            is_active, is_published, created_at, updated_at)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
                        (
                            course['course_code'],
                            course['course_name'],
                            course['course_name'],  # 英文名称暂用中文
                            int(course['credits']),
                            course['total_hours'],
                            course_type,
                            '待定',  # 部门信息后续补充
                            'all',  # 学期，默认为全年
                            '2023-2024',  # 学年
                            course['description'] or f"课程{course['course_name']}",
                            f"学习{course['course_name']}的基本理论和方法",  # objectives
                            course['max_students'] or 120,
                            10,  # 最少学生数默认10
                            course['status'] == '启用' if course['status'] else True,
                            True,
                            course['created_at'] or datetime.now(),
                            datetime.now()
                        )
                    )
                    new_id = cursor.fetchone()[0]
                    self.course_mapping[course['course_id']] = new_id
                    migrated_count += 1
                    print(f"  ✅ 迁移课程: {course['course_name']} (ID: {new_id})")
                    
            except Exception as e:
                print(f"  ❌ 迁移失败: {course['course_name']} - {e}")
        
        print(f"📚 课程迁移完成: {migrated_count} 条新记录")
        return migrated_count
    
    def migrate_teachers(self):
        """迁移教师数据"""
        print("\n👨‍🏫 开始迁移教师数据...")
        
        teachers = self.get_sqlite_data("teachers")
        migrated_count = 0
        
        for teacher in teachers:
            try:
                # 检查是否已存在（通过邮箱）
                cursor = self.execute_postgres_query(
                    "SELECT id FROM users_user WHERE email = %s",
                    (teacher['email'],)
                )
                existing = cursor.fetchone()
                
                if existing:
                    self.teacher_mapping[teacher['teacher_id']] = existing[0]
                    print(f"  📝 教师已存在: {teacher['teacher_name']} (ID: {existing[0]})")
                else:
                    # 生成用户名
                    username = teacher['email'].split('@')[0] if teacher['email'] else f"teacher_{teacher['teacher_id']}"
                    
                    # 插入用户基础信息
                    cursor = self.execute_postgres_query(
                        """INSERT INTO users_user 
                           (username, email, first_name, last_name, is_active, 
                            is_staff, is_superuser, date_joined, created_at, updated_at)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
                        (
                            username,
                            teacher['email'],
                            teacher['teacher_name'][:1],  # 姓
                            teacher['teacher_name'][1:],  # 名
                            teacher['employment_status'] == '在职' if teacher['employment_status'] else True,
                            True,  # is_staff
                            False,  # is_superuser
                            datetime.now(),
                            datetime.now(),
                            datetime.now()
                        )
                    )
                    user_id = cursor.fetchone()[0]
                    
                    # 插入教师详细信息
                    cursor = self.execute_postgres_query(
                        """INSERT INTO teachers_profile 
                           (user_id, employee_id, department, title, office, 
                            max_weekly_hours, employment_status, created_at, updated_at)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (
                            user_id,
                            teacher['teacher_code'],
                            teacher['department'] or '待定',
                            teacher['title'] or '讲师',
                            teacher['office'] or '待定',
                            teacher['max_weekly_hours'] or 16,
                            teacher['employment_status'] or '在职',
                            datetime.now(),
                            datetime.now()
                        )
                    )
                    
                    self.teacher_mapping[teacher['teacher_id']] = user_id
                    migrated_count += 1
                    print(f"  ✅ 迁移教师: {teacher['teacher_name']} (ID: {user_id})")
                    
            except Exception as e:
                print(f"  ❌ 迁移失败: {teacher['teacher_name']} - {e}")
        
        print(f"👨‍🏫 教师迁移完成: {migrated_count} 条新记录")
        return migrated_count
    
    def migrate_time_slots(self):
        """迁移时间段数据"""
        print("\n⏰ 开始迁移时间段数据...")
        
        time_slots = self.get_sqlite_data("time_slots")
        migrated_count = 0
        
        for slot in time_slots:
            try:
                # 解析时间段信息
                day_map = {'周一': 1, '周二': 2, '周三': 3, '周四': 4, '周五': 5, '周六': 6, '周日': 7}
                day_num = day_map.get(slot['day_of_week'], 1)
                
                # 检查是否已存在
                cursor = self.execute_postgres_query(
                    "SELECT id FROM schedules_timeslot WHERE name = %s",
                    (slot['slot_code'],)
                )
                existing = cursor.fetchone()
                
                if existing:
                    self.time_slot_mapping[slot['slot_id']] = existing[0]
                    print(f"  📝 时间段已存在: {slot['slot_code']} (ID: {existing[0]})")
                else:
                    # 计算持续时间
                    start_time = datetime.strptime(slot['start_time'], '%H:%M').time()
                    end_time = datetime.strptime(slot['end_time'], '%H:%M').time()
                    duration = (datetime.combine(date.min, end_time) - 
                               datetime.combine(date.min, start_time)).seconds // 60
                    
                    # 插入新数据
                    cursor = self.execute_postgres_query(
                        """INSERT INTO schedules_timeslot 
                           (name, start_time, end_time, order, duration_minutes, is_active, created_at, updated_at)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
                        (
                            slot['slot_code'],
                            start_time,
                            end_time,
                            slot['period_number'],
                            duration,
                            slot['is_available'] if slot['is_available'] is not None else True,
                            datetime.now(),
                            datetime.now()
                        )
                    )
                    new_id = cursor.fetchone()[0]
                    self.time_slot_mapping[slot['slot_id']] = new_id
                    migrated_count += 1
                    print(f"  ✅ 迁移时间段: {slot['slot_code']} (ID: {new_id})")
                    
            except Exception as e:
                print(f"  ❌ 迁移失败: {slot['slot_code']} - {e}")
        
        print(f"⏰ 时间段迁移完成: {migrated_count} 条新记录")
        return migrated_count
    
    def migrate_schedule_data(self):
        """迁移排课数据（核心功能）"""
        print("\n📅 开始迁移排课数据...")
        
        # 获取教学任务和排课记录
        teaching_tasks = self.get_sqlite_data("teaching_tasks")
        timetable_records = self.get_sqlite_data("timetable")
        
        migrated_count = 0
        error_count = 0
        
        print(f"📊 待处理数据: {len(teaching_tasks)} 个教学任务, {len(timetable_records)} 条排课记录")
        
        # 先处理教学任务，建立映射
        task_mapping = {}  # SQLite task_id -> PostgreSQL schedule_ids
        
        for task in teaching_tasks:
            try:
                # 获取映射ID
                course_id = self.course_mapping.get(task['course_id'])
                teacher_id = self.teacher_mapping.get(task['teacher_id'])
                
                if not course_id or not teacher_id:
                    print(f"  ⚠️  跳过教学任务: 未找到对应的课程或教师 (任务ID: {task['task_id']})")
                    continue
                
                # 查找对应的排课记录
                task_timetable = [tt for tt in timetable_records if tt['task_id'] == task['task_id']]
                
                if not task_timetable:
                    print(f"  ⚠️  教学任务无排课记录: 任务ID {task['task_id']}")
                    continue
                
                schedule_ids = []
                
                for tt_record in task_timetable:
                    room_id = self.room_mapping.get(tt_record['room_id'])
                    slot_id = self.time_slot_mapping.get(tt_record['slot_id'])
                    
                    if not room_id or not slot_id:
                        print(f"  ⚠️  跳过排课记录: 未找到对应的教室或时间段 (记录ID: {tt_record['timetable_id']})")
                        continue
                    
                    # 检查是否已存在相同的排课记录
                    cursor = self.execute_postgres_query(
                        """SELECT id FROM schedules_schedule 
                           WHERE classroom_id = %s AND course_id = %s AND teacher_id = %s 
                           AND time_slot_id = %s AND semester = %s AND day_of_week = %s""",
                        (room_id, course_id, teacher_id, slot_id, f"学期{task['semester_id']}", 1)
                    )
                    existing = cursor.fetchone()
                    
                    if existing:
                        schedule_ids.append(existing[0])
                        print(f"  📝 排课记录已存在: ID {existing[0]}")
                    else:
                        # 生成周范围字符串
                        week_range = f"{tt_record['week_number']}"
                        
                        # 插入排课记录
                        cursor = self.execute_postgres_query(
                            """INSERT INTO schedules_schedule 
                               (day_of_week, week_range, semester, academic_year, status, notes, 
                                created_at, updated_at, classroom_id, course_id, teacher_id, time_slot_id)
                               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
                            (
                                1,  # day_of_week，需要根据时间段解析
                                week_range,
                                f"学期{task['semester_id']}",
                                "2023-2024",  # 学年，需要根据实际情况调整
                                tt_record['status'] or 'active',
                                f"从SQLite导入 - 原ID: {tt_record['timetable_id']}",
                                tt_record['created_at'] or datetime.now(),
                                datetime.now(),
                                room_id,
                                course_id,
                                teacher_id,
                                slot_id
                            )
                        )
                        new_id = cursor.fetchone()[0]
                        schedule_ids.append(new_id)
                        migrated_count += 1
                        print(f"  ✅ 迁移排课记录: ID {new_id} (原ID: {tt_record['timetable_id']})")
                
                task_mapping[task['task_id']] = schedule_ids
                
            except Exception as e:
                error_count += 1
                print(f"  ❌ 教学任务迁移失败: 任务ID {task['task_id']} - {e}")
        
        print(f"📅 排课数据迁移完成: {migrated_count} 条新记录, {error_count} 个错误")
        return migrated_count
    
    def verify_migration(self):
        """验证数据迁移结果"""
        print("\n🔍 开始验证数据迁移结果...")
        
        verification_results = {}
        
        try:
            # 验证各表数据量
            tables_to_check = [
                ('classrooms_building', '教学楼'),
                ('classrooms_classroom', '教室'),
                ('courses_course', '课程'),
                ('schedules_schedule', '排课记录'),
                ('schedules_timeslot', '时间段')
            ]
            
            for table_name, description in tables_to_check:
                cursor = self.execute_postgres_query(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                verification_results[table_name] = count
                print(f"  📊 {description}: {count} 条记录")
            
            # 验证关键业务查询
            print("\n🔍 验证关键业务查询:")
            
            # 1. 按学期查询课程表
            cursor = self.execute_postgres_query(
                """SELECT COUNT(*) FROM schedules_schedule 
                   WHERE semester LIKE %s""",
                ("%学期1",)
            )
            semester1_count = cursor.fetchone()[0]
            print(f"  📅 学期1排课记录: {semester1_count} 条")
            
            # 2. 检查数据一致性
            cursor = self.execute_postgres_query(
                """SELECT COUNT(*) FROM schedules_schedule s
                   JOIN courses_course c ON s.course_id = c.id
                   JOIN classrooms_classroom r ON s.classroom_id = r.id
                   JOIN users_user u ON s.teacher_id = u.id"""
            )
            consistent_count = cursor.fetchone()[0]
            print(f"  ✅ 数据一致性: {consistent_count} 条完整记录")
            
            # 3. 样本数据展示
            print("\n📝 样本数据展示:")
            cursor = self.execute_postgres_query(
                """SELECT s.semester, c.name as course_name, u.first_name || u.last_name as teacher_name,
                          r.name as room_name, s.day_of_week, s.week_range
                   FROM schedules_schedule s
                   JOIN courses_course c ON s.course_id = c.id
                   JOIN users_user u ON s.teacher_id = u.id
                   JOIN classrooms_classroom r ON s.classroom_id = r.id
                   LIMIT 3"""
            )
            samples = cursor.fetchall()
            for i, sample in enumerate(samples, 1):
                semester, course, teacher, room, day, week = sample
                print(f"    {i}. {semester}: {course} - {teacher} - {room} (周{day}, 第{week}周)")
            
            print(f"\n✅ 数据迁移验证完成!")
            return verification_results
            
        except Exception as e:
            print(f"❌ 验证失败: {e}")
            return None
    
    def run_migration(self):
        """执行完整的数据迁移流程"""
        print("🚀 开始执行数据迁移流程...")
        start_time = datetime.now()
        
        try:
            # 连接数据库
            self.connect_databases()
            
            # 迁移基础数据
            buildings_count = self.migrate_buildings()
            rooms_count = self.migrate_rooms()
            courses_count = self.migrate_courses()
            teachers_count = self.migrate_teachers()
            time_slots_count = self.migrate_time_slots()
            
            # 迁移业务数据
            schedule_count = self.migrate_schedule_data()
            
            # 验证结果
            verification_results = self.verify_migration()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print(f"\n🎉 数据迁移完成!")
            print(f"⏱️  总耗时: {duration:.2f} 秒")
            print(f"📊 迁移统计:")
            print(f"   🏢 教学楼: {buildings_count} 条")
            print(f"   🚪 教室: {rooms_count} 条")
            print(f"   📚 课程: {courses_count} 条")
            print(f"   👨‍🏫 教师: {teachers_count} 条")
            print(f"   ⏰ 时间段: {time_slots_count} 条")
            print(f"   📅 排课记录: {schedule_count} 条")
            
            return True
            
        except Exception as e:
            print(f"❌ 数据迁移失败: {e}")
            return False
            
        finally:
            # 关闭数据库连接
            if self.sqlite_conn:
                self.sqlite_conn.close()
            if self.postgres_conn:
                self.postgres_conn.close()

def main():
    """主函数"""
    print("🎓 智能大学课程表调度系统 - 数据迁移工具")
    print("=" * 60)
    
    # PostgreSQL连接配置
    postgres_config = {
        'host': 'localhost',
        'port': 15432,
        'database': 'course_management',
        'user': 'postgres',
        'password': 'postgres123'
    }
    
    # 创建迁移器并执行
    migration = DataMigration('university_data.db', postgres_config)
    
    success = migration.run_migration()
    
    if success:
        print("\n✅ 所有数据迁移完成！课程表现在应该可以正确显示了。")
    else:
        print("\n❌ 数据迁移失败，请检查错误信息。")

if __name__ == "__main__":
    main()