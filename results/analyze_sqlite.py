#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析SQLite数据库结构
"""

import sqlite3

def analyze_database():
    """分析SQLite数据库结构"""
    try:
        # 连接SQLite数据库
        conn = sqlite3.connect('university_data.db')
        cursor = conn.cursor()
        
        print("🗄️ SQLite数据库分析")
        print("=" * 50)
        
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = cursor.fetchall()
        
        print(f"📊 发现 {len(tables)} 张表:")
        for table in tables:
            table_name = table[0]
            print(f"\n📋 表名: {table_name}")
            
            # 获取表结构
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            print("  字段结构:")
            for col in columns:
                col_id, col_name, col_type, notnull, default, pk = col
                null_str = "NOT NULL" if notnull else "NULL"
                pk_str = " PRIMARY KEY" if pk else ""
                print(f"    - {col_name}: {col_type} {null_str}{pk_str}")
            
            # 获取记录数
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"  📈 记录数: {count:,}")
            
            # 获取前3条样本数据
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
            samples = cursor.fetchall()
            if samples:
                print("  📝 样本数据:")
                for i, sample in enumerate(samples, 1):
                    print(f"    {i}: {sample}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 数据库分析失败: {e}")

if __name__ == "__main__":
    analyze_database()