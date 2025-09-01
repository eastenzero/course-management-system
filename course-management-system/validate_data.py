#!/usr/bin/env python3
"""验证数据文件的脚本"""
import json
import os
from pathlib import Path

def validate_data_file(file_path: str):
    """验证数据文件"""
    try:
        print(f"🔍 验证数据文件: {file_path}")
        
        # 检查文件是否存在
        if not Path(file_path).exists():
            print("❌ 文件不存在")
            return False
        
        # 获取文件大小
        file_size = Path(file_path).stat().st_size
        print(f"📁 文件大小: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
        
        # 加载JSON数据
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("✅ JSON格式验证通过")
        
        # 验证数据结构
        print("\n📊 数据统计:")
        total_records = 0
        for key, value in data.items():
            if isinstance(value, list):
                count = len(value)
                total_records += count
                print(f"   {key}: {count:,} 条记录")
            elif key == "metadata":
                print(f"   元数据:")
                for meta_key, meta_value in value.items():
                    print(f"     {meta_key}: {meta_value}")
        
        print(f"\n📈 总记录数: {total_records:,}")
        
        # 验证数据样本
        print("\n🔍 数据样本验证:")
        if "teachers" in data and data["teachers"]:
            teacher = data["teachers"][0]
            print(f"   教师样本: {teacher.get('name', 'N/A')} - {teacher.get('title', 'N/A')}")
        
        if "students" in data and data["students"]:
            student = data["students"][0]
            print(f"   学生样本: {student.get('name', 'N/A')} - {student.get('major', 'N/A')}")
        
        if "courses" in data and data["courses"]:
            course = data["courses"][0]
            print(f"   课程样本: {course.get('name', 'N/A')} - {course.get('credits', 'N/A')}学分")
        
        print("\n✅ 数据文件验证完成")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON格式错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

def main():
    """主函数"""
    # 验证主数据文件
    data_file = "course_data_output/course_dataset.json"
    validate_data_file(data_file)
    
    # 验证报告文件
    report_file = "course_data_output/generation_report.json"
    print(f"\n🔍 验证报告文件: {report_file}")
    if Path(report_file).exists():
        with open(report_file, 'r', encoding='utf-8') as f:
            report = json.load(f)
        print("📋 生成报告:")
        for key, value in report.items():
            print(f"   {key}: {value}")
        print("✅ 报告文件验证通过")
    else:
        print("❌ 报告文件不存在")

if __name__ == "__main__":
    main()