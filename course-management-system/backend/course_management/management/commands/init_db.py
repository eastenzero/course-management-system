from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import connection
from django.core.management import call_command
import os

User = get_user_model()

class Command(BaseCommand):
    help = '初始化数据库并创建测试用户'

    def handle(self, *args, **options):
        self.stdout.write('开始初始化数据库...')
        
        # 删除现有数据库文件
        db_path = 'course_management/db.sqlite3'
        if os.path.exists(db_path):
            os.remove(db_path)
            self.stdout.write(f'已删除现有数据库: {db_path}')
        
        # 删除迁移记录
        with connection.cursor() as cursor:
            try:
                cursor.execute("DROP TABLE IF EXISTS django_migrations")
                self.stdout.write('已清除迁移记录表')
            except:
                pass
        
        # 创建数据库表
        try:
            call_command('migrate', '--run-syncdb', verbosity=0)
            self.stdout.write(self.style.SUCCESS('数据库迁移完成'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'迁移失败: {e}'))
            return
        
        # 创建超级用户
        try:
            if not User.objects.filter(username='admin').exists():
                admin_user = User.objects.create_superuser(
                    username='admin',
                    email='admin@example.com',
                    password='admin123',
                    user_type='admin',
                    employee_id='EMP001',
                    first_name='系统',
                    last_name='管理员',
                    department='信息技术部'
                )
                self.stdout.write(self.style.SUCCESS(f'创建超级用户: {admin_user.username}'))
            else:
                self.stdout.write('超级用户已存在')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'创建超级用户失败: {e}'))
        
        # 创建测试教师
        try:
            if not User.objects.filter(username='teacher001').exists():
                teacher_user = User.objects.create_user(
                    username='teacher001',
                    email='teacher001@example.com',
                    password='password123',
                    user_type='teacher',
                    employee_id='T001',
                    first_name='张',
                    last_name='老师',
                    department='计算机科学系'
                )
                self.stdout.write(self.style.SUCCESS(f'创建教师用户: {teacher_user.username}'))
            else:
                self.stdout.write('教师用户已存在')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'创建教师用户失败: {e}'))
        
        # 创建测试学生
        try:
            if not User.objects.filter(username='student001').exists():
                student_user = User.objects.create_user(
                    username='student001',
                    email='student001@example.com',
                    password='password123',
                    user_type='student',
                    student_id='S001',
                    first_name='李',
                    last_name='同学',
                    department='计算机科学系'
                )
                self.stdout.write(self.style.SUCCESS(f'创建学生用户: {student_user.username}'))
            else:
                self.stdout.write('学生用户已存在')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'创建学生用户失败: {e}'))
        
        self.stdout.write(self.style.SUCCESS('数据库初始化完成！'))
        self.stdout.write('测试账号信息：')
        self.stdout.write('管理员: admin / admin123')
        self.stdout.write('教师: teacher001 / password123')
        self.stdout.write('学生: student001 / password123')
