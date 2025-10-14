# 数据库配置指南

## 当前配置

系统当前使用 **SQLite** 数据库，适合开发和测试环境。

## 切换到 PostgreSQL

### 1. 自动设置（推荐）

运行提供的设置脚本：

```bash
cd backend
./setup_postgresql.sh
```

### 2. 手动设置

#### 安装 PostgreSQL

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql
```

#### 启动服务

```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### 创建数据库

```bash
sudo -u postgres createdb course_management
```

#### 设置用户（可选）

```bash
sudo -u postgres psql
```

在 PostgreSQL 命令行中：

```sql
CREATE USER course_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE course_management TO course_user;
\q
```

#### 更新环境变量

创建 `.env` 文件（基于 `.env.example`）：

```bash
cp .env.example .env
```

编辑 `.env` 文件，设置数据库URL：

```
# 使用默认 postgres 用户
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/course_management

# 或使用自定义用户
DATABASE_URL=postgresql://course_user:your_password@localhost:5432/course_management
```

#### 应用迁移

```bash
source venv/bin/activate
python manage.py migrate
python create_test_data.py  # 重新创建测试数据
```

## 数据库对比

| 特性 | SQLite | PostgreSQL |
|------|--------|------------|
| 适用环境 | 开发/测试 | 生产环境 |
| 并发性能 | 有限 | 优秀 |
| 数据完整性 | 基本 | 强大 |
| 扩展性 | 有限 | 优秀 |
| 维护复杂度 | 简单 | 中等 |

## 故障排除

### PostgreSQL 连接问题

1. 检查服务状态：
   ```bash
   sudo systemctl status postgresql
   ```

2. 检查端口占用：
   ```bash
   sudo netstat -tlnp | grep 5432
   ```

3. 重启服务：
   ```bash
   sudo systemctl restart postgresql
   ```

### 权限问题

确保 PostgreSQL 用户有正确的权限：

```sql
GRANT ALL PRIVILEGES ON DATABASE course_management TO your_user;
GRANT ALL ON SCHEMA public TO your_user;
```
