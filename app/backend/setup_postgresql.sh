#!/bin/bash

# PostgreSQL设置脚本
# 用于配置PostgreSQL数据库

echo "正在设置PostgreSQL数据库..."

# 检查PostgreSQL是否安装
if ! command -v psql &> /dev/null; then
    echo "错误: PostgreSQL未安装"
    echo "请先安装PostgreSQL: sudo apt-get install postgresql postgresql-contrib"
    exit 1
fi

# 启动PostgreSQL服务
echo "启动PostgreSQL服务..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 创建数据库
echo "创建数据库..."
sudo -u postgres createdb course_management

# 创建用户（可选）
echo "是否要创建专用数据库用户? (y/n)"
read -r create_user
if [ "$create_user" = "y" ]; then
    echo "请输入用户名:"
    read -r username
    echo "请输入密码:"
    read -s password
    
    sudo -u postgres psql -c "CREATE USER $username WITH PASSWORD '$password';"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE course_management TO $username;"
    
    echo "用户 $username 已创建并授权"
    echo "请更新.env文件中的DATABASE_URL:"
    echo "DATABASE_URL=postgresql://$username:$password@localhost:5432/course_management"
else
    echo "使用默认postgres用户"
    echo "请更新.env文件中的DATABASE_URL:"
    echo "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/course_management"
fi

echo "PostgreSQL设置完成!"
echo "请运行以下命令应用数据库迁移:"
echo "python manage.py migrate"
