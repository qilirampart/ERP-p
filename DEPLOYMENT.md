# 印刷ERP系统 - Docker部署文档

## 📋 目录

- [系统要求](#系统要求)
- [部署前准备](#部署前准备)
- [快速部署](#快速部署)
- [详细配置](#详细配置)
- [常用命令](#常用命令)
- [故障排查](#故障排查)
- [备份与恢复](#备份与恢复)
- [安全建议](#安全建议)

---

## 系统要求

### 硬件要求
- **CPU**: 2核及以上
- **内存**: 4GB及以上（推荐8GB）
- **磁盘**: 20GB可用空间

### 软件要求
- Docker 20.10+
- Docker Compose 2.0+
- 操作系统：Linux/Windows/macOS

---

## 部署前准备

### 1. 安装Docker和Docker Compose

#### Linux (Ubuntu/Debian)
```bash
# 安装Docker
curl -fsSL https://get.docker.com | sh

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 安装Docker Compose
sudo apt-get update
sudo apt-get install docker-compose-plugin

# 验证安装
docker --version
docker compose version
```

#### Windows
1. 下载并安装 [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)
2. 启动Docker Desktop
3. 验证安装：打开PowerShell运行 `docker --version`

### 2. 克隆项目代码

```bash
git clone <your-repo-url>
cd ERP-p
```

---

## 快速部署

### 1. 配置环境变量

```bash
# 复制环境配置文件
cp .env.example .env

# 编辑配置文件
nano .env  # Linux/Mac
notepad .env  # Windows
```

**必须修改的配置项：**
```env
MYSQL_ROOT_PASSWORD=your_secure_root_password  # MySQL root密码
MYSQL_PASSWORD=your_secure_password            # 应用数据库密码
SECRET_KEY=your_secret_key_here                # JWT密钥（至少32字符）
```

**生成安全的SECRET_KEY：**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. 初始化数据库

确保 `backend/init.sql` 包含初始化脚本（如果需要）。

### 3. 构建并启动服务

```bash
# 构建所有服务
docker compose build

# 启动所有服务（后台运行）
docker compose up -d

# 查看启动日志
docker compose logs -f
```

### 4. 访问系统

- **前端界面**：http://localhost （或服务器IP）
- **后端API**：http://localhost:8000
- **API文档**：http://localhost:8000/docs

**默认管理员账号：**
- 用户名：`admin`
- 密码：`admin123`

⚠️ **首次登录后请立即修改密码！**

---

## 详细配置

### 端口配置

在 `docker-compose.yml` 中修改端口映射：

```yaml
services:
  frontend:
    ports:
      - "80:80"      # HTTP端口
      - "443:443"    # HTTPS端口（需要SSL证书）

  backend:
    ports:
      - "8000:8000"  # API端口

  mysql:
    ports:
      - "3306:3306"  # MySQL端口
```

### SSL/HTTPS配置

#### 1. 准备SSL证书

将证书文件放置在以下位置：
```
frontend/
  ├── ssl/
  │   ├── cert.pem    # 证书文件
  │   └── key.pem     # 私钥文件
```

#### 2. 修改Nginx配置

编辑 `frontend/nginx.conf`，添加HTTPS配置：

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    # SSL配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # ... 其他配置保持不变
}
```

#### 3. 修改docker-compose.yml

```yaml
frontend:
  volumes:
    - ./frontend/ssl:/etc/nginx/ssl:ro
```

#### 4. 重启服务

```bash
docker compose restart frontend
```

---

## 常用命令

### 服务管理

```bash
# 启动所有服务
docker compose up -d

# 停止所有服务
docker compose down

# 重启所有服务
docker compose restart

# 重启单个服务
docker compose restart backend
docker compose restart frontend
docker compose restart mysql

# 查看服务状态
docker compose ps

# 查看服务日志
docker compose logs -f
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f mysql
```

### 数据库管理

```bash
# 进入MySQL容器
docker compose exec mysql bash

# 连接数据库
docker compose exec mysql mysql -u root -p

# 导出数据库
docker compose exec mysql mysqldump -u root -p erp_db > backup.sql

# 导入数据库
docker compose exec -T mysql mysql -u root -p erp_db < backup.sql
```

### 更新部署

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker compose up -d --build

# 或者分步操作
docker compose build
docker compose down
docker compose up -d
```

---

## 故障排查

### 1. 服务无法启动

**检查日志：**
```bash
docker compose logs backend
docker compose logs frontend
docker compose logs mysql
```

**常见问题：**
- 端口被占用：修改docker-compose.yml中的端口映射
- 内存不足：增加Docker内存限制或升级服务器
- 环境变量错误：检查.env文件配置

### 2. 数据库连接失败

```bash
# 检查MySQL健康状态
docker compose ps mysql

# 查看MySQL日志
docker compose logs mysql

# 测试数据库连接
docker compose exec backend python -c "
from sqlalchemy import create_engine
from app.core.config import settings
engine = create_engine(settings.DATABASE_URL.replace('+aiomysql', ''))
engine.connect()
print('Database connected!')
"
```

### 3. 前端无法访问后端API

**检查网络：**
```bash
# 进入前端容器
docker compose exec frontend sh

# 测试后端连接
wget -O- http://backend:8000/health
```

### 4. 清理并重新部署

```bash
# 停止并删除所有容器、网络
docker compose down

# 删除数据卷（⚠️ 会清除数据库数据）
docker compose down -v

# 清理Docker缓存
docker system prune -a

# 重新部署
docker compose up -d --build
```

---

## 备份与恢复

### 数据库备份

#### 手动备份

```bash
# 创建备份目录
mkdir -p backups

# 导出数据库
docker compose exec mysql mysqldump \
  -u root -p${MYSQL_ROOT_PASSWORD} \
  --databases ${MYSQL_DATABASE} \
  --single-transaction \
  --quick \
  --lock-tables=false \
  > backups/erp_db_$(date +%Y%m%d_%H%M%S).sql
```

#### 自动备份脚本

创建 `backup.sh`：

```bash
#!/bin/bash
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 导出数据库
docker compose exec -T mysql mysqldump \
  -u root -p${MYSQL_ROOT_PASSWORD} \
  --databases ${MYSQL_DATABASE} \
  --single-transaction \
  --quick \
  --lock-tables=false \
  > $BACKUP_DIR/erp_db_$DATE.sql

# 压缩备份文件
gzip $BACKUP_DIR/erp_db_$DATE.sql

# 删除7天前的备份
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Backup completed: erp_db_$DATE.sql.gz"
```

设置定时任务（Linux）：
```bash
# 编辑crontab
crontab -e

# 每天凌晨2点执行备份
0 2 * * * cd /path/to/ERP-p && ./backup.sh
```

### 数据库恢复

```bash
# 停止后端服务
docker compose stop backend

# 恢复数据库
gunzip < backups/erp_db_YYYYMMDD_HHMMSS.sql.gz | \
  docker compose exec -T mysql mysql -u root -p${MYSQL_ROOT_PASSWORD}

# 启动后端服务
docker compose start backend
```

### 文件备份

```bash
# 备份上传文件
tar -czf backups/uploads_$(date +%Y%m%d).tar.gz backend/uploads/

# 恢复上传文件
tar -xzf backups/uploads_YYYYMMDD.tar.gz
```

---

## 安全建议

### 1. 密码安全

- ✅ 使用强密码（至少16字符，包含大小写字母、数字、特殊字符）
- ✅ 定期更换密码
- ✅ 不要在代码或文档中硬编码密码
- ✅ 不要将.env文件提交到版本控制

### 2. 网络安全

- ✅ 使用防火墙限制端口访问
- ✅ 只暴露必要的端口（80/443）
- ✅ 内网部署时不要暴露8000和3306端口到公网
- ✅ 启用HTTPS加密传输

### 3. 数据库安全

```bash
# 修改MySQL root密码
docker compose exec mysql mysql -u root -p
ALTER USER 'root'@'%' IDENTIFIED BY 'new_secure_password';
FLUSH PRIVILEGES;
```

### 4. 定期更新

```bash
# 更新Docker镜像
docker compose pull
docker compose up -d

# 更新系统依赖
docker compose build --no-cache
```

### 5. 日志管理

设置日志轮转，防止磁盘被日志占满：

编辑 `docker-compose.yml`：

```yaml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

---

## 监控与维护

### 健康检查

```bash
# 检查所有服务健康状态
docker compose ps

# 手动触发健康检查
curl http://localhost/health
curl http://localhost:8000/health
```

### 资源监控

```bash
# 查看容器资源使用
docker stats

# 查看磁盘使用
df -h
docker system df
```

### 清理无用数据

```bash
# 清理未使用的镜像、容器、网络
docker system prune -a

# 清理未使用的数据卷（⚠️谨慎操作）
docker volume prune
```

---

## 生产环境检查清单

部署到生产环境前，请确认：

- [ ] 所有密码已修改为强密码
- [ ] SECRET_KEY已生成并配置
- [ ] 数据库备份策略已设置
- [ ] 防火墙规则已配置
- [ ] HTTPS已启用（如需公网访问）
- [ ] 日志轮转已配置
- [ ] 监控告警已设置
- [ ] 默认admin密码已修改
- [ ] 不必要的端口已关闭
- [ ] 定期备份任务已设置

---

## 技术支持

如遇到问题，请：
1. 查看本文档的故障排查章节
2. 检查服务日志：`docker compose logs -f`
3. 联系技术支持团队

---

**最后更新时间**：2025-12-27
