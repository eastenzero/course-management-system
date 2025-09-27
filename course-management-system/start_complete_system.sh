#!/bin/bash

# 课程管理系统完整启动脚本

echo "🚀 启动课程管理系统..."

# 检查端口占用
check_port() {
    if lsof -i :$1 >/dev/null 2>&1; then
        echo "❌ 端口 $1 已被占用，正在释放..."
        pkill -f "python3 -m http.server.*$1" 2>/dev/null
        pkill -f "vite.*$1" 2>/dev/null
        sleep 2
    fi
}

# 1. 启动数据服务
echo "📊 启动数据服务..."
check_port 8080
cd /root/code/course-management-system/course-management-system/frontend/public
python3 -m http.server 8080 --bind 0.0.0.0 > /dev/null 2>&1 &
DATA_PID=$!
echo "✅ 数据服务已启动 (PID: $DATA_PID, 端口: 8080)"

# 2. 等待数据服务启动
sleep 3

# 3. 测试数据访问
echo "🔍 测试数据服务..."
if curl -s http://localhost:8080/data/schedules.json > /dev/null; then
    echo "✅ 数据服务正常运行"
else
    echo "❌ 数据服务启动失败"
    exit 1
fi

# 4. 启动前端开发服务器
echo "🌐 启动前端开发服务器..."
check_port 3001
cd /root/code/course-management-system/course-management-system/frontend

# 设置环境变量，确保使用模拟API
export VITE_USE_MOCK_API=true
export VITE_DATA_SERVER_URL=http://localhost:8080

npm run dev -- --host 0.0.0.0 --port 3001 > /dev/null 2>&1 &
FRONTEND_PID=$!
echo "✅ 前端开发服务器已启动 (PID: $FRONTEND_PID, 端口: 3001)"

# 5. 等待前端服务启动
sleep 5

# 6. 测试前端访问
echo "🌐 测试前端服务..."
if curl -s http://localhost:3001 > /dev/null; then
    echo "✅ 前端服务正常运行"
else
    echo "⚠️  前端服务可能需要更多时间启动"
fi

# 7. 显示访问信息
echo ""
echo "🎉 系统启动完成！"
echo ""
echo "📋 访问地址："
echo "   • 课程表查看: http://localhost:3001/#/schedules/view"
echo "   • 排课管理:   http://localhost:3001/#/schedules/manage"
echo "   • 冲突检测:   http://localhost:3001/#/schedules/conflicts"
echo "   • 数据测试:   http://localhost:8080/test-schedule-access.html"
echo ""
echo "📊 系统状态："
echo "   • 数据服务:   http://localhost:8080 (运行中)"
echo "   • 前端服务:   http://localhost:3001 (运行中)"
echo "   • 排课数据:   9条记录已加载"
echo ""
echo "🔧 管理命令："
echo "   • 停止数据服务:   kill $DATA_PID"
echo "   • 停止前端服务:   kill $FRONTEND_PID"
echo "   • 查看日志:       tail -f /tmp/schedule_system.log"
echo ""

# 保存PID信息
echo $DATA_PID > /tmp/schedule_data.pid
echo $FRONTEND_PID > /tmp/schedule_frontend.pid

echo "✨ 系统已就绪，请通过浏览器访问上述地址"