#!/bin/bash

# 课程管理系统后端启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 等待数据库就绪
wait_for_db() {
    log_info "等待数据库连接..."
    
    # 从DATABASE_URL中提取数据库信息
    if [ -n "$DATABASE_URL" ]; then
        # 解析DATABASE_URL
        DB_HOST=$(echo $DATABASE_URL | sed 's/.*@\([^:]*\):.*/\1/')
        DB_PORT=$(echo $DATABASE_URL | sed 's/.*:\([0-9]*\)\/.*/\1/')
    else
        DB_HOST=${DB_HOST:-db}
        DB_PORT=${DB_PORT:-5432}
    fi
    
    # 等待数据库端口可用
    while ! nc -z $DB_HOST $DB_PORT; do
        log_info "数据库 $DB_HOST:$DB_PORT 尚未就绪，等待中..."
        sleep 2
    done
    
    log_success "数据库连接成功"
}

# 等待Redis就绪
wait_for_redis() {
    log_info "等待Redis连接..."
    
    # 从REDIS_URL中提取Redis信息
    if [ -n "$REDIS_URL" ]; then
        REDIS_HOST=$(echo $REDIS_URL | sed 's/.*@\([^:]*\):.*/\1/')
        REDIS_PORT=$(echo $REDIS_URL | sed 's/.*:\([0-9]*\)\/.*/\1/')
    else
        REDIS_HOST=${REDIS_HOST:-redis}
        REDIS_PORT=${REDIS_PORT:-6379}
    fi
    
    # 等待Redis端口可用
    while ! nc -z $REDIS_HOST $REDIS_PORT; do
        log_info "Redis $REDIS_HOST:$REDIS_PORT 尚未就绪，等待中..."
        sleep 2
    done
    
    log_success "Redis连接成功"
}

# 运行数据库迁移
run_migrations() {
    log_info "运行数据库迁移..."
    
    # 检查是否需要迁移
    if python manage.py showmigrations --plan | grep -q '\[ \]'; then
        log_info "发现未应用的迁移，开始迁移..."
        python manage.py migrate --noinput
        log_success "数据库迁移完成"
    else
        log_info "数据库已是最新状态"
    fi
}

# 收集静态文件
collect_static() {
    log_info "收集静态文件..."
    
    python manage.py collectstatic --noinput --clear
    
    log_success "静态文件收集完成"
}

# 创建超级用户
create_superuser() {
    log_info "检查超级用户..."
    
    # 检查是否已存在超级用户
    if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then
        python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
    print('超级用户已创建')
else:
    print('超级用户已存在')
"
        log_success "超级用户检查完成"
    else
        log_warning "未设置超级用户环境变量，跳过创建"
    fi
}

# 编译翻译文件
compile_messages() {
    log_info "编译翻译文件..."
    
    if [ -d "locale" ]; then
        python manage.py compilemessages
        log_success "翻译文件编译完成"
    else
        log_info "未找到翻译文件，跳过编译"
    fi
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    # 检查Django应用是否正常
    python manage.py check --deploy
    
    log_success "健康检查通过"
}

# 清理临时文件
cleanup() {
    log_info "清理临时文件..."
    
    # 清理Python缓存
    find . -type f -name "*.pyc" -delete
    find . -type d -name "__pycache__" -delete
    
    # 清理临时文件
    rm -rf /tmp/*
    
    log_success "清理完成"
}

# 主函数
main() {
    log_info "启动课程管理系统后端服务..."
    
    # 等待依赖服务
    wait_for_db
    wait_for_redis
    
    # 初始化应用
    run_migrations
    collect_static
    create_superuser
    compile_messages
    
    # 健康检查
    health_check
    
    # 清理
    cleanup
    
    log_success "初始化完成，启动应用服务..."
    
    # 执行传入的命令
    exec "$@"
}

# 信号处理
trap 'log_info "收到停止信号，正在关闭..."; exit 0' SIGTERM SIGINT

# 如果是Django管理命令，直接执行
if [ "$1" = "python" ] && [ "$2" = "manage.py" ]; then
    log_info "执行Django管理命令: $*"
    exec "$@"
fi

# 如果是Celery命令，等待依赖服务后执行
if [ "$1" = "celery" ]; then
    log_info "启动Celery服务: $*"
    wait_for_db
    wait_for_redis
    exec "$@"
fi

# 其他情况执行完整初始化
main "$@"
