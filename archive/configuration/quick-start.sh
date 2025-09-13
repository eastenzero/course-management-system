#!/bin/bash

# 校园课程管理系统 - 快速启动脚本
# 基于Docker部署文档的简化版本

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 校园课程管理系统 - 启动中...${NC}"

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo "请先安装Docker"
    exit 1
fi

# 启动服务
echo -e "${YELLOW}📦 启动Docker服务...${NC}"
docker-compose up -d

# 等待服务启动
echo -e "${YELLOW}⏳ 等待服务启动...${NC}"
sleep 10

# 运行数据库迁移
echo -e "${YELLOW}🗄️  运行数据库迁移...${NC}"
docker-compose exec -T backend python manage.py migrate

# 创建测试数据（可选）
echo -e "${YELLOW}📝 创建测试数据...${NC}"
docker-compose exec -T backend python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123', user_type='admin')
    print('✅ 超级用户已创建: admin/admin123')
if not User.objects.filter(username='teacher1').exists():
    User.objects.create_user('teacher1', 'teacher1@example.com', 'teacher123', user_type='teacher', first_name='张', last_name='老师')
    print('✅ 教师账号已创建: teacher1/teacher123')
if not User.objects.filter(username='student1').exists():
    User.objects.create_user('student1', 'student1@example.com', 'student123', user_type='student', first_name='李', last_name='同学')
    print('✅ 学生账号已创建: student1/student123')
"

echo -e "${GREEN}🎉 部署完成！${NC}"
echo
echo -e "${BLUE}📋 访问信息:${NC}"
echo -e "  前端应用: ${GREEN}http://localhost${NC}"
echo -e "  后端API: ${GREEN}http://localhost:8000${NC}"
echo -e "  API文档: ${GREEN}http://localhost:8000/api/docs/${NC}"
echo -e "  管理后台: ${GREEN}http://localhost:8000/admin${NC}"
echo
echo -e "${BLUE}👤 测试账号:${NC}"
echo -e "  管理员: ${GREEN}admin / admin123${NC}"
echo -e "  教师: ${GREEN}teacher1 / teacher123${NC}"
echo -e "  学生: ${GREEN}student1 / student123${NC}"
echo
echo -e "${YELLOW}🔍 查看服务状态: ${GREEN}docker-compose ps${NC}"
echo -e "${YELLOW}📊 查看日志: ${GREEN}docker-compose logs -f${NC}"
echo -e "${YELLOW}🛑 停止服务: ${GREEN}docker-compose down${NC}"