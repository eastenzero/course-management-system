# 课程管理系统 - 配置指南

## 📋 概述

本文档说明了课程管理系统后端的配置结构和最佳实践。

## 🏗️ 配置文件结构

### 主配置文件
- **`course_management/settings.py`** - 主要配置文件（推荐使用）
  - 智能Redis/内存缓存切换
  - 完整的Celery配置
  - 开发和生产环境兼容
  - 详细的日志配置
  - 性能监控支持

### 备用配置文件
- **`course_management/settings/base.py`** - 基础配置模板
- **`simple_settings.py`** - 简化配置（仅开发用）

## ⚙️ 主要功能

### 1. 智能缓存配置
系统会自动检测Redis连接状态：
- ✅ **Redis可用时**: 使用高性能Redis缓存
- ❌ **Redis不可用时**: 自动降级到内存缓存

```python
# 自动检测Redis连接
try:
    redis.Redis(host=REDIS_HOST, port=REDIS_PORT).ping()
    USE_REDIS = True
except:
    USE_REDIS = False  # 降级到内存缓存
```

### 2. 环境自适应数据库
- **Docker环境**: 自动使用PostgreSQL
- **本地开发**: 默认使用SQLite（开发方便）
- **生产环境**: 支持DATABASE_URL环境变量

### 3. CORS 支持
支持多端口前端开发：
- `localhost:3000` - 默认端口
- `localhost:3001` - 备用端口（解决端口冲突）
- 局域网IP访问支持

### 4. Celery 异步任务
- **Redis可用**: 使用Redis作为消息队列
- **Redis不可用**: 降级到Django数据库队列

### 5. 完善的日志系统
- 文件日志: `logs/course_management.log`
- 控制台日志: 开发环境实时查看
- 分级日志: DEBUG/INFO/WARNING/ERROR

## 🔧 配置优化

### Redis 配置优化
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'OPTIONS': {
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'IGNORE_EXCEPTIONS': True,  # 容错机制
        }
    }
}
```

### 性能监控
开发环境自动启用Django Debug Toolbar（如果已安装）

## 🚀 使用指南

### 启动服务
```bash
# 激活虚拟环境
source venv/bin/activate

# 检查配置
python manage.py check

# 启动开发服务器
python manage.py runserver 8001
```

### 环境变量配置
```bash
# Redis配置
export REDIS_HOST=localhost
export REDIS_PORT=6379

# 数据库配置（可选）
export DATABASE_URL=postgresql://user:password@host:port/database

# Docker标识
export IN_DOCKER=true
```

## 📊 监控和调试

### 缓存状态检查
```bash
python manage.py shell
>>> from django.core.cache import cache
>>> cache.get('test_key')  # 测试缓存连接
```

### API健康检查
```bash
curl http://localhost:8001/api/health/
```

### 查看日志
```bash
tail -f logs/course_management.log
```

## 🎯 最佳实践

### 1. 开发环境
- 使用SQLite数据库（快速启动）
- 内存缓存作为备用方案
- 启用Debug模式和详细日志

### 2. 生产环境
- 使用PostgreSQL数据库
- Redis缓存和队列
- 禁用Debug模式
- 配置proper SECRET_KEY

### 3. 部署注意事项
- 设置环境变量 `IN_DOCKER=true`
- 配置 `DATABASE_URL`
- 确保Redis服务可用
- 创建logs目录权限

## 🔍 故障排除

### Redis连接问题
1. 检查Redis服务状态
2. 验证端口和主机配置
3. 系统会自动降级到内存缓存

### 数据库连接问题
1. 检查DATABASE_URL格式
2. 验证数据库服务状态
3. 确认用户权限

### 端口冲突
- 前端: 3000 → 3001
- 后端: 8000 → 8001
- CORS已配置支持多端口

## 📝 更新记录

### v2.0 (2025-01-08)
- ✅ 修复Redis兼容性问题
- ✅ 智能缓存降级机制
- ✅ 完善的日志系统
- ✅ 多端口CORS支持
- ✅ 环境自适应配置

---

**维护者**: 课程管理系统开发团队  
**最后更新**: 2025-01-08  
**版本**: 2.0