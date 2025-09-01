#!/usr/bin/env python
"""
百万级数据生成进度监控器
"""

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
import django
django.setup()

from django.contrib.auth import get_user_model
import time

User = get_user_model()

def monitor_progress():
    print("📊 百万级数据生成进度监控")
    print("=" * 60)
    
    start_time = time.time()
    target = 1000000
    
    while True:
        try:
            total_users = User.objects.count()
            million_users = User.objects.filter(username__startswith='million_').count()
            
            elapsed = time.time() - start_time
            progress = (total_users / target) * 100
            
            print(f"⏰ {time.strftime('%H:%M:%S')} | "
                  f"总用户: {total_users:,} | "
                  f"百万级: {million_users:,} | "
                  f"进度: {progress:.2f}%")
            
            if total_users >= target:
                print("\n🎉 恭喜！已达到百万级数据标准！")
                break
                
            time.sleep(30)  # 每30秒检查一次
            
        except KeyboardInterrupt:
            print("\n⏹️ 监控已停止")
            break
        except Exception as e:
            print(f"❌ 监控错误: {e}")
            time.sleep(10)

if __name__ == '__main__':
    monitor_progress()