#!/usr/bin/env python3
"""
百万级数据生成脚本 - 基于已有数据生成器
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# 不需要Django环境进行数据生成

import random
from faker import Faker
from typing import List, Dict, Any

fake = Faker('zh_CN')

class MillionDataGenerator:
    """百万级数据生成器"""
    
    def __init__(self, target_records: int = 1000000):
        self.target_records = target_records
        self.output_dir = Path("course_data_output")
        self.output_dir.mkdir(exist_ok=True)
        
        # 数据规模配置
        self.calculate_data_distribution()
        
    def calculate_data_distribution(self):
        """计算数据分布"""
        base = int(self.target_records ** 0.5)  # 开平方根作为基数
        
        self.teachers_count = min(base // 10, 50000)  # 教师数量
        self.students_count = min(base * 2, 200000)   # 学生数量
        self.courses_count = min(base // 5, 10000)    # 课程数量
        self.classrooms_count = min(base // 20, 5000) # 教室数量
        
        # 主要记录数来自排课表和选课记录
        remaining = self.target_records - (self.teachers_count + self.students_count + self.courses_count + self.classrooms_count)
        self.schedules_count = remaining // 2
        self.enrollments_count = remaining - self.schedules_count
        
        print(f"📊 数据分布计划:")
        print(f"   教师: {self.teachers_count:,}")
        print(f"   学生: {self.students_count:,}")
        print(f"   课程: {self.courses_count:,}")
        print(f"   教室: {self.classrooms_count:,}")
        print(f"   排课记录: {self.schedules_count:,}")
        print(f"   选课记录: {self.enrollments_count:,}")
        print(f"   总计: {self.target_records:,}")
    
    def generate_departments(self) -> List[Dict]:
        """生成院系数据"""
        departments = [
            {"dept_id": f"DEPT_{i:03d}", "name": f"{fake.company()}学院", "description": fake.text(100)}
            for i in range(1, 21)  # 20个院系
        ]
        return departments
    
    def generate_teachers(self) -> List[Dict]:
        """生成教师数据"""
        print(f"👨‍🏫 生成教师数据 ({self.teachers_count:,} 条)...")
        
        teachers = []
        titles = ["教授", "副教授", "讲师", "助教"]
        departments = [f"DEPT_{i:03d}" for i in range(1, 21)]
        
        for i in range(1, self.teachers_count + 1):
            if i % 10000 == 0:
                print(f"   进度: {i:,}/{self.teachers_count:,}")
            
            teacher = {
                "teacher_id": f"T{i:06d}",
                "name": fake.name(),
                "title": random.choice(titles),
                "department": random.choice(departments),
                "email": f"teacher{i}@university.edu",
                "phone": fake.phone_number(),
                "specialization_areas": [fake.word() for _ in range(random.randint(1, 3))],
                "experience_years": random.randint(1, 35),
                "max_courses_per_semester": random.randint(2, 5)
            }
            teachers.append(teacher)
        
        return teachers
    
    def generate_students(self) -> List[Dict]:
        """生成学生数据"""
        print(f"👨‍🎓 生成学生数据 ({self.students_count:,} 条)...")
        
        students = []
        majors = ["计算机科学", "软件工程", "数据科学", "人工智能", "网络工程", "信息安全"]
        grades = [1, 2, 3, 4]
        
        for i in range(1, self.students_count + 1):
            if i % 10000 == 0:
                print(f"   进度: {i:,}/{self.students_count:,}")
            
            student = {
                "student_id": f"S{i:06d}",
                "name": fake.name(),
                "major": random.choice(majors),
                "grade": random.choice(grades),
                "email": f"student{i}@university.edu",
                "phone": fake.phone_number(),
                "enrollment_year": 2024 - random.randint(0, 3)
            }
            students.append(student)
        
        return students
    
    def generate_courses(self, teachers: List[Dict]) -> List[Dict]:
        """生成课程数据"""
        print(f"📚 生成课程数据 ({self.courses_count:,} 条)...")
        
        courses = []
        course_types = ["必修课", "选修课", "专业课", "通识课"]
        
        for i in range(1, self.courses_count + 1):
            if i % 1000 == 0:
                print(f"   进度: {i:,}/{self.courses_count:,}")
            
            # 随机分配教师
            teacher = random.choice(teachers)
            
            course = {
                "course_id": f"COURSE_{i:06d}",
                "name": f"{fake.word()}课程{i}",
                "code": f"CS{i:04d}",
                "type": random.choice(course_types),
                "credits": random.randint(1, 6),
                "department": teacher["department"],
                "teacher_id": teacher["teacher_id"],
                "weekly_hours": random.randint(2, 6),
                "student_capacity": random.randint(30, 200),
                "semester": random.choice(["2024-1", "2024-2"]),
                "description": fake.text(100)
            }
            courses.append(course)
        
        return courses
    
    def generate_classrooms(self) -> List[Dict]:
        """生成教室数据"""
        print(f"🏫 生成教室数据 ({self.classrooms_count:,} 条)...")
        
        classrooms = []
        buildings = ["A", "B", "C", "D", "E"]
        room_types = ["普通教室", "实验室", "多媒体教室", "大讲堂"]
        
        for i in range(1, self.classrooms_count + 1):
            classroom = {
                "room_id": f"ROOM_{i:04d}",
                "building": random.choice(buildings),
                "floor": random.randint(1, 10),
                "room_number": f"{random.choice(buildings)}{random.randint(100, 999)}",
                "capacity": random.randint(30, 300),
                "room_type": random.choice(room_types),
                "equipment": [fake.word() for _ in range(random.randint(1, 5))],
                "is_available": True
            }
            classrooms.append(classroom)
        
        return classrooms
    
    def generate_schedules(self, courses: List[Dict], classrooms: List[Dict]) -> List[Dict]:
        """生成排课记录"""
        print(f"📅 生成排课记录 ({self.schedules_count:,} 条)...")
        
        schedules = []
        time_slots = [
            "08:00-08:45", "08:55-09:40", "10:00-10:45", "10:55-11:40",
            "14:00-14:45", "14:55-15:40", "16:00-16:45", "16:55-17:40",
            "19:00-19:45", "19:55-20:40"
        ]
        
        for i in range(1, self.schedules_count + 1):
            if i % 10000 == 0:
                print(f"   进度: {i:,}/{self.schedules_count:,}")
            
            course = random.choice(courses)
            classroom = random.choice(classrooms)
            
            schedule = {
                "schedule_id": f"SCHED_{i:08d}",
                "course_id": course["course_id"],
                "teacher_id": course["teacher_id"],
                "classroom_id": classroom["room_id"],
                "week": random.randint(1, 18),
                "weekday": random.randint(1, 5),
                "time_slot": random.choice(time_slots),
                "student_count": random.randint(10, min(course["student_capacity"], classroom["capacity"])),
                "status": "active"
            }
            schedules.append(schedule)
        
        return schedules
    
    def generate_enrollments(self, students: List[Dict], courses: List[Dict]) -> List[Dict]:
        """生成选课记录"""
        print(f"🎯 生成选课记录 ({self.enrollments_count:,} 条)...")
        
        enrollments = []
        statuses = ["已选课", "已退课", "待审核"]
        
        for i in range(1, self.enrollments_count + 1):
            if i % 10000 == 0:
                print(f"   进度: {i:,}/{self.enrollments_count:,}")
            
            student = random.choice(students)
            course = random.choice(courses)
            
            enrollment = {
                "enrollment_id": f"ENROLL_{i:08d}",
                "student_id": student["student_id"],
                "course_id": course["course_id"],
                "semester": course["semester"],
                "status": random.choice(statuses),
                "enrollment_date": fake.date_between(start_date='-30d', end_date='today').isoformat(),
                "grade": random.choice([None, random.randint(60, 100)])
            }
            enrollments.append(enrollment)
        
        return enrollments
    
    def generate_complete_dataset(self) -> Dict[str, Any]:
        """生成完整数据集"""
        print(f"🚀 开始生成百万级数据集 (目标: {self.target_records:,} 条记录)")
        print("=" * 60)
        
        start_time = time.time()
        
        # 生成各类数据
        departments = self.generate_departments()
        teachers = self.generate_teachers()
        students = self.generate_students()
        courses = self.generate_courses(teachers)
        classrooms = self.generate_classrooms()
        schedules = self.generate_schedules(courses, classrooms)
        enrollments = self.generate_enrollments(students, courses)
        
        # 生成先修关系
        print("📋 生成先修关系...")
        prerequisites = []
        for i in range(min(5000, len(courses) // 2)):
            prerequisite = {
                "course_id": courses[i]["course_id"],
                "prerequisite_id": courses[random.randint(0, i)]["course_id"] if i > 0 else None,
                "semester_gap": random.randint(1, 2)
            }
            if prerequisite["prerequisite_id"]:
                prerequisites.append(prerequisite)
        
        # 组装数据集
        dataset = {
            "departments": departments,
            "teachers": teachers,
            "students": students,
            "courses": courses,
            "classrooms": classrooms,
            "schedules": schedules,
            "enrollments": enrollments,
            "prerequisites": prerequisites,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_records": len(departments) + len(teachers) + len(students) + len(courses) + 
                                len(classrooms) + len(schedules) + len(enrollments) + len(prerequisites),
                "generation_time_seconds": 0,  # 将在后面更新
                "target_records": self.target_records,
                "generator_version": "1.0.0"
            }
        }
        
        generation_time = time.time() - start_time
        dataset["metadata"]["generation_time_seconds"] = round(generation_time, 2)
        
        print(f"\n✨ 数据生成完成！")
        print(f"   📊 总计 {dataset['metadata']['total_records']:,} 条记录")
        print(f"   ⏱️  耗时 {generation_time:.2f} 秒")
        print(f"   🚀 生成速度 {dataset['metadata']['total_records']/generation_time:.0f} 条/秒")
        
        return dataset
    
    def save_dataset(self, dataset: Dict[str, Any]) -> str:
        """保存数据集到文件"""
        print("\n💾 保存数据集到文件...")
        
        # 保存主数据文件
        main_file = self.output_dir / "course_dataset.json"
        with open(main_file, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)
        
        # 保存报告文件
        report = {
            "generation_summary": {
                "total_records": dataset["metadata"]["total_records"],
                "generation_time": dataset["metadata"]["generation_time_seconds"],
                "target_records": dataset["metadata"]["target_records"],
                "generated_at": dataset["metadata"]["generated_at"]
            },
            "data_breakdown": {
                "departments": len(dataset["departments"]),
                "teachers": len(dataset["teachers"]),
                "students": len(dataset["students"]),
                "courses": len(dataset["courses"]),
                "classrooms": len(dataset["classrooms"]),
                "schedules": len(dataset["schedules"]),
                "enrollments": len(dataset["enrollments"]),
                "prerequisites": len(dataset["prerequisites"])
            }
        }
        
        report_file = self.output_dir / "generation_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"   ✅ 主数据文件: {main_file}")
        print(f"   ✅ 报告文件: {report_file}")
        
        return str(main_file)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='百万级数据生成器')
    parser.add_argument('--records', '-n', type=int, default=1000000, help='目标记录数')
    
    args = parser.parse_args()
    
    generator = MillionDataGenerator(target_records=args.records)
    dataset = generator.generate_complete_dataset()
    file_path = generator.save_dataset(dataset)
    
    print(f"\n🎉 数据生成完成！")
    print(f"📁 数据文件: {file_path}")
    print(f"📊 记录总数: {dataset['metadata']['total_records']:,}")
    
    return file_path


if __name__ == "__main__":
    main()