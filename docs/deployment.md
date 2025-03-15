# StarFall MCP 部署指南

## 部署前准备

### 1. 系统要求

#### 硬件配置
- CPU：2核或以上（推荐4核）
- 内存：4GB或以上（推荐8GB）
- 磁盘空间：20GB或以上（根据数据量增长调整）
- 网络：稳定的网络连接，建议带宽10Mbps以上

#### 软件环境
- 操作系统：Ubuntu 20.04+/CentOS 8+/Windows Server 2019+
- Python 3.10+（必需）
- Redis 6.0+（必需，用于缓存和消息队列）
- PostgreSQL 12+（必需，用于数据持久化）
- Nginx 1.18+（可选，用于反向代理和负载均衡）
- Docker 20.10+（可选，用于容器化部署）
- Docker Compose 2.0+（可选，用于容器编排）

### 2. 环境检查
```bash
# 检查 Python 版本
python --version

# 检查 pip 版本
pip --version

# 检查 PostgreSQL 版本
psql --version

# 检查 Redis 版本
redis-cli --version
```

## 部署方式

### 1. Docker 部署（推荐）

#### 1.1 准备工作
- 安装 Docker：https://docs.docker.com/get-docker/
- 安装 Docker Compose：https://docs.docker.com/compose/install/

#### 1.2 配置文件

创建 `docker-compose.yml`：
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

# 检查服务状态
docker-compose ps
```

### 2. 直接部署

#### 2.1 安装依赖
```bash
# 安装系统依赖
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv postgresql redis-server nginx

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装 Python 依赖
pip install -r requirements.txt
```

#### 2.2 配置数据库
```bash
# 创建数据库和用户
sudo -u postgres psql

CREATE DATABASE starfall;
CREATE USER starfall WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE starfall TO starfall;
```

#### 2.3 配置环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
vim .env
```

#### 2.4 配置系统服务

创建服务文件 `/etc/systemd/system/starfall.service`：
```ini
[Unit]
Description=StarFall MCP
After=network.target

[Service]
User=starfall
WorkingDirectory=/opt/starfall-mcp
EnvironmentFile=/opt/starfall-mcp/.env
ExecStart=/opt/starfall-mcp/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
# 重载服务配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start starfall

# 设置开机自启
sudo systemctl enable starfall

# 查看服务状态
sudo systemctl status starfall
```

## 部署后配置

### 1. Nginx 配置（可选）

创建配置文件 `/etc/nginx/sites-available/starfall`：
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

启用配置：
```bash
# 创建符号链接
sudo ln -s /etc/nginx/sites-available/starfall /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

### 2. SSL 配置（推荐）

使用 Certbot 配置 HTTPS：
```bash
# 安装 Certbot
sudo apt-get install certbot python3-certbot-nginx

# 获取证书并配置 Nginx
sudo certbot --nginx -d your_domain.com
```

## 维护指南

### 1. 日志管理
```bash
# 查看应用日志
tail -f logs/starfall.log

# 查看系统服务日志
journalctl -u starfall -f
```

### 2. 备份恢复
```bash
# 备份数据库
pg_dump -U starfall starfall > backup.sql

# 恢复数据库
psql -U starfall starfall < backup.sql
```

### 3. 更新部署
```bash
# Docker 部署更新
git pull
docker-compose build
docker-compose up -d

# 直接部署更新
git pull
pip install -r requirements.txt
sudo systemctl restart starfall
```

## 常见问题

### 1. 服务无法启动
- 检查环境变量配置
- 验证数据库连接
- 查看错误日志

### 2. 数据库连接失败
- 检查数据库服务状态
- 验证连接字符串
- 确认用户权限

### 3. 性能问题
- 优化数据库配置
- 调整 worker 数量
- 配置缓存策略

## 获取帮助

- 查看[常见问题文档](docs/faq.md)
- 提交 [Issue](https://github.com/StarFall/starfall-mcp/issues)
- 加入运维社区获取支持