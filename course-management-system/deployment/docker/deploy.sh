#!/bin/bash

# 课程管理系统Docker部署脚本
# 使用方法: ./deploy.sh [dev|prod|stop|clean]

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

# 检查Docker和Docker Compose
check_requirements() {
    log_info "检查系统要求..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    log_success "系统要求检查通过"
}

# 创建环境变量文件
setup_env() {
    log_info "设置环境变量..."
    
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            cp .env.example .env
            log_warning "已创建.env文件，请根据需要修改配置"
        else
            log_error ".env.example文件不存在"
            exit 1
        fi
    else
        log_info ".env文件已存在"
    fi
}

# 构建镜像
build_images() {
    log_info "构建Docker镜像..."
    
    sudo docker-compose build --no-cache
    
    log_success "镜像构建完成"
}

# 启动开发环境
start_dev() {
    log_info "启动开发环境..."
    
    # 启动数据库和Redis
    sudo docker-compose up -d db redis

    # 等待数据库启动
    log_info "等待数据库启动..."
    sleep 10

    # 运行数据库迁移
    sudo docker-compose run --rm backend python manage.py migrate

    # 创建超级用户（如果不存在）
    sudo docker-compose run --rm backend python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('超级用户已创建: admin/admin123')
else:
    print('超级用户已存在')
"

    # 启动所有服务
    sudo docker-compose up -d
    
    log_success "开发环境启动完成"
    log_info "前端地址: http://localhost"
    log_info "后端API: http://localhost:8000"
    log_info "管理后台: http://localhost:8000/admin"
}

# 启动生产环境
start_prod() {
    log_info "启动生产环境..."
    
    # 使用生产配置
    sudo docker-compose --profile production up -d

    # 等待服务启动
    sleep 15

    # 运行数据库迁移
    sudo docker-compose exec backend python manage.py migrate

    # 收集静态文件
    sudo docker-compose exec backend python manage.py collectstatic --noinput
    
    log_success "生产环境启动完成"
}

# 停止服务
stop_services() {
    log_info "停止所有服务..."
    
    sudo docker-compose down
    
    log_success "服务已停止"
}

# 清理环境
clean_env() {
    log_warning "这将删除所有容器、镜像和数据卷！"
    read -p "确定要继续吗？(y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "清理Docker环境..."
        
        # 停止并删除容器
        sudo docker-compose down -v --remove-orphans

        # 删除镜像
        sudo docker-compose down --rmi all

        # 删除未使用的卷
        sudo docker volume prune -f
        
        log_success "环境清理完成"
    else
        log_info "取消清理操作"
    fi
}

# 显示日志
show_logs() {
    log_info "显示服务日志..."
    sudo docker-compose logs -f
}

# 显示状态
show_status() {
    log_info "服务状态:"
    sudo docker-compose ps

    echo
    log_info "资源使用情况:"
    sudo docker stats --no-stream
}

# 备份数据
backup_data() {
    log_info "备份数据库..."
    
    BACKUP_DIR="./backups"
    mkdir -p $BACKUP_DIR
    
    BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql"
    
    sudo docker-compose exec -T db pg_dump -U postgres course_management > $BACKUP_FILE
    
    log_success "数据库备份完成: $BACKUP_FILE"
}

# 恢复数据
restore_data() {
    if [ -z "$1" ]; then
        log_error "请指定备份文件路径"
        exit 1
    fi
    
    if [ ! -f "$1" ]; then
        log_error "备份文件不存在: $1"
        exit 1
    fi
    
    log_warning "这将覆盖现有数据库！"
    read -p "确定要继续吗？(y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "恢复数据库..."
        
        sudo docker-compose exec -T db psql -U postgres -d course_management < "$1"
        
        log_success "数据库恢复完成"
    else
        log_info "取消恢复操作"
    fi
}

# 主函数
main() {
    cd "$(dirname "$0")/../.."
    
    case "$1" in
        "dev")
            check_requirements
            setup_env
            build_images
            start_dev
            ;;
        "prod")
            check_requirements
            setup_env
            build_images
            start_prod
            ;;
        "stop")
            stop_services
            ;;
        "clean")
            clean_env
            ;;
        "logs")
            show_logs
            ;;
        "status")
            show_status
            ;;
        "backup")
            backup_data
            ;;
        "restore")
            restore_data "$2"
            ;;
        "rebuild")
            stop_services
            build_images
            start_dev
            ;;
        *)
            echo "使用方法: $0 {dev|prod|stop|clean|logs|status|backup|restore|rebuild}"
            echo ""
            echo "命令说明:"
            echo "  dev     - 启动开发环境"
            echo "  prod    - 启动生产环境"
            echo "  stop    - 停止所有服务"
            echo "  clean   - 清理所有容器和数据"
            echo "  logs    - 显示服务日志"
            echo "  status  - 显示服务状态"
            echo "  backup  - 备份数据库"
            echo "  restore - 恢复数据库"
            echo "  rebuild - 重新构建并启动"
            exit 1
            ;;
    esac
}

main "$@"
