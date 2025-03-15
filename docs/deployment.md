# StarFall MCP 部署指南

## 系统要求

### 硬件要求
- CPU: 2核或以上
- 内存: 4GB或以上
- 磁盘空间: 20GB或以上

### 软件要求
- Python 3.10+
- Redis 6.0+
- PostgreSQL 12+
- Nginx 1.18+

## 部署方法

### 1. Docker 部署

#### 1.1 使用 Docker Compose

创建 `docker-compose.yml` 文件：

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - APP_NAME=StarFall MCP
      - APP_VERSION=1.0.0
      - DEBUG=False
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://user:password@db:5432/starfall
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs

  db:
    image: postgres:12
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=starfall
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6.0
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

#### 1.2 使用 Dockerfile

创建 `Dockerfile`：

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 1.3 启动服务

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 2. 系统服务部署

#### 2.1 安装依赖

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 安装系统依赖
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3-dev postgresql-server-dev-all redis-server nginx

# CentOS/RHEL
sudo yum install -y python3-devel postgresql-devel redis nginx
```

#### 2.2 配置数据库

```bash
# 创建数据库
sudo -u postgres psql
CREATE DATABASE starfall;
CREATE USER starfall WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE starfall TO starfall;
\q
```

#### 2.3 配置 Nginx

创建 `/etc/nginx/conf.d/starfall.conf`：

```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/static;
    }

    location /media {
        alias /path/to/media;
    }
}
```

#### 2.4 创建系统服务

创建 `/etc/systemd/system/starfall.service`：

```ini
[Unit]
Description=StarFall MCP Service
After=network.target

[Service]
User=starfall
Group=starfall
WorkingDirectory=/path/to/starfall
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
# 重新加载 systemd
sudo systemctl daemon-reload

# 启用服务
sudo systemctl enable starfall

# 启动服务
sudo systemctl start starfall

# 查看状态
sudo systemctl status starfall
```

## 配置说明

### 1. 环境变量

复制 `.env.example` 为 `.env` 并修改配置：

```bash
# 应用配置
APP_NAME=StarFall MCP
APP_VERSION=1.0.0
DEBUG=False
ENVIRONMENT=production

# 服务器配置
HOST=0.0.0.0
PORT=8000
WORKERS=4
RELOAD=False

# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/starfall
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10
DATABASE_POOL_TIMEOUT=30

# Redis配置
REDIS_URL=redis://localhost:6379/0
REDIS_POOL_SIZE=5
REDIS_POOL_TIMEOUT=30

# 安全配置
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 2. 日志配置

日志文件位置：`logs/app.log`

```python
# 日志配置
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
LOG_FILE=logs/app.log
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5
```

### 3. 监控配置

```python
# 监控配置
PROMETHEUS_ENABLED=True
PROMETHEUS_PORT=9090
METRICS_ENABLED=True
```

## 维护

### 1. 日志管理

```bash
# 查看实时日志
tail -f logs/app.log

# 查看错误日志
grep ERROR logs/app.log

# 查看警告日志
grep WARNING logs/app.log
```

### 2. 数据库维护

```bash
# 备份数据库
pg_dump -U user starfall > backup.sql

# 恢复数据库
psql -U user starfall < backup.sql

# 优化数据库
VACUUM ANALYZE;
```

### 3. 缓存管理

```bash
# 清理 Redis 缓存
redis-cli FLUSHALL

# 查看 Redis 内存使用
redis-cli INFO memory
```

## 故障排除

### 1. 服务无法启动

检查项：
- 端口是否被占用
- 权限是否正确
- 配置文件是否正确
- 日志文件权限

### 2. 数据库连接失败

检查项：
- 数据库服务是否运行
- 用户名密码是否正确
- 数据库是否创建
- 网络连接是否正常

### 3. Redis 连接失败

检查项：
- Redis 服务是否运行
- 端口是否正确
- 密码是否正确
- 内存是否充足

## 更新流程

### 1. 代码更新

```bash
# 拉取最新代码
git pull origin main

# 安装依赖
pip install -r requirements.txt

# 重启服务
sudo systemctl restart starfall
```

### 2. 数据库迁移

```bash
# 生成迁移文件
alembic revision --autogenerate -m "update"

# 应用迁移
alembic upgrade head
```

## 回滚流程

### 1. 代码回滚

```bash
# 回滚到指定版本
git reset --hard <commit_id>

# 重启服务
sudo systemctl restart starfall
```

### 2. 数据库回滚

```bash
# 回滚到指定版本
alembic downgrade <revision_id>
```

## 联系方式

- 作者：StarFall
- 邮箱：SYC_Hello@163.com
- 项目主页：https://github.com/StarFall/starfall-mcp 