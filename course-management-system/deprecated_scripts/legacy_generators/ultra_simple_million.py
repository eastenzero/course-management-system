#!/usr/bin/env python
"""
超简化百万级数据生成器 - 确保能够运行
目标：快速生成确实的百万级数据
"""

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
import django
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction
from django.contrib.auth.hashers import make_password
import time
import random

User = get_user_model()

def main():
    print("🚀 超简化百万级数据生成器")
    print("=" * 60)
    
    # 预先计算密码
    password_hash = make_password('password123')
    
    # 简化的名字和部门
    names = ['张三', '李四', '王五', '赵六', '钱七', '孙八', '周九', '吴十']
    depts = ['计算机学院', '软件学院', '信息学院']
    
    # 目标：生成100万用户
    TARGET = 1000000
    BATCH_SIZE = 2000
    
    print(f"目标生成 {TARGET:,} 个用户...")
    
    # 清理现有的million用户
    User.objects.filter(username__startswith='million_').delete()
    print("清理完成")
    
    created = 0
    start_time = time.time()
    
    for batch_start in range(0, TARGET, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, TARGET)
        users = []
        
        for i in range(batch_start, batch_end):
            user_num = i + 1
            name = random.choice(names)
            
            users.append(User(
                username=f"million_{user_num:07d}",
                email=f"u{user_num:07d}@test.com",
                first_name=name[:1],
                last_name=name[1:] if len(name) > 1 else 'X',
                user_type='student',
                department=random.choice(depts),
                student_id=f"S{user_num:07d}",
                password=password_hash,
                is_active=True
            ))
        
        try:
            User.objects.bulk_create(users, ignore_conflicts=True)
            created += len(users)
        except Exception as e:
            print(f"批次 {batch_start} 失败: {e}")
            continue
        
        # 每10万显示一次进度
        if batch_start % 100000 == 0:
            elapsed = time.time() - start_time
            speed = created / elapsed if elapsed > 0 else 0
            progress = (created / TARGET) * 100
            print(f"进度: {created:,}/{TARGET:,} ({progress:.1f}%) | 速度: {speed:.0f} 条/秒")
    
    total_elapsed = time.time() - start_time
    
    print("\n" + "=" * 60)
    print("生成完成！")
    print(f"实际创建: {created:,} 条记录")
    print(f"总耗时: {total_elapsed/60:.1f} 分钟")
    print(f"平均速度: {created/total_elapsed:.0f} 条/秒")
    
    # 验证
    final_count = User.objects.count()
    million_count = User.objects.filter(username__startswith='million_').count()
    
    print(f"\n验证结果:")
    print(f"数据库总用户: {final_count:,}")
    print(f"百万级用户: {million_count:,}")
    
    if final_count >= 1000000:
        print("✅ 成功达到百万级数据标准！")
    else:
        print(f"距离百万级还需: {1000000 - final_count:,}")

if __name__ == '__main__':
    main()