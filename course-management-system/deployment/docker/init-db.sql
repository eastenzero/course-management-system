-- 课程管理系统数据库初始化脚本
-- 此脚本在PostgreSQL容器首次启动时执行

-- 设置数据库编码和时区
ALTER DATABASE course_management SET timezone TO 'Asia/Shanghai';
ALTER DATABASE course_management SET lc_messages TO 'en_US.UTF-8';
ALTER DATABASE course_management SET lc_monetary TO 'en_US.UTF-8';
ALTER DATABASE course_management SET lc_numeric TO 'en_US.UTF-8';
ALTER DATABASE course_management SET lc_time TO 'en_US.UTF-8';

-- 创建必要的PostgreSQL扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";  -- UUID生成
CREATE EXTENSION IF NOT EXISTS "pg_trgm";    -- 三元语法索引，用于模糊搜索
CREATE EXTENSION IF NOT EXISTS "btree_gin";  -- GIN索引增强
CREATE EXTENSION IF NOT EXISTS "unaccent";   -- 去除重音符号

-- 创建中文全文搜索配置
CREATE TEXT SEARCH CONFIGURATION chinese_utf8 (COPY = simple);
CREATE TEXT SEARCH DICTIONARY chinese_utf8_dict (TEMPLATE = simple);
ALTER TEXT SEARCH CONFIGURATION chinese_utf8 ALTER MAPPING FOR word, asciiword WITH chinese_utf8_dict;

-- 创建索引函数（用于中文全文搜索）
CREATE OR REPLACE FUNCTION f_unaccent(text)
RETURNS text AS
$func$
SELECT unaccent('unaccent', $1)
$func$ LANGUAGE sql IMMUTABLE;

-- 创建课程名称搜索函数
CREATE OR REPLACE FUNCTION course_search_vector(course_name text, course_code text, description text)
RETURNS tsvector AS
$func$
SELECT to_tsvector('chinese_utf8', 
    COALESCE(course_name, '') || ' ' || 
    COALESCE(course_code, '') || ' ' || 
    COALESCE(description, '')
)
$func$ LANGUAGE sql IMMUTABLE;

-- 数据库注释
COMMENT ON DATABASE course_management IS '校园课程管理系统数据库 - 支持智能排课算法';

-- 设置默认权限
GRANT ALL PRIVILEGES ON DATABASE course_management TO postgres;
GRANT CONNECT ON DATABASE course_management TO postgres;

-- 创建应用专用模式（可选，用于更好的组织）
-- CREATE SCHEMA IF NOT EXISTS course_management;
-- COMMENT ON SCHEMA course_management IS '课程管理系统业务数据';

-- 优化PostgreSQL配置（这些设置将在Django迁移后生效）
-- 注意：这些设置主要用于性能优化，实际部署时可根据服务器配置调整
