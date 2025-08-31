-- 数据库初始化脚本
-- 用于 PostgreSQL 数据库的基础配置

-- 创建数据库（如果不存在）
-- 注意：在 docker-compose 中，数据库已经通过环境变量创建

-- 设置字符编码
ALTER DATABASE course_management SET timezone TO 'Asia/Shanghai';

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 授权设置
GRANT ALL PRIVILEGES ON DATABASE course_management TO postgres;

-- 创建索引优化查询性能
-- 注意：具体的表索引将在 Django migrations 中创建

-- 设置连接限制
ALTER DATABASE course_management CONNECTION LIMIT 100;

-- 日志记录设置
-- 这些设置有助于性能监控和调试
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- 记录执行时间超过1秒的查询

-- 性能优化设置
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

-- 重载配置
SELECT pg_reload_conf();

-- 输出初始化完成信息
DO $$
BEGIN
    RAISE NOTICE '数据库初始化完成 - 课程管理系统';
    RAISE NOTICE '时区设置: Asia/Shanghai';
    RAISE NOTICE '字符编码: UTF-8';
    RAISE NOTICE '最大连接数: 200';
END $$;