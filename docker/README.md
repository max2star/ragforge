# RAGForge 完整服务部署指南

本项目包含了 RAGForge 的完整服务栈，包括后端 API、Web 控制台和所有必要的数据库服务。

## 🚀 快速启动

### 方法一：使用启动脚本（推荐）

```bash
cd docker
./start.sh
```

然后选择相应的选项：
- `1` - 启动所有服务（生产环境）
- `2` - 启动所有服务（开发环境）
- `3` - 仅启动后端服务
- `4` - 仅启动数据库服务

### 方法二：直接使用 docker-compose

```bash
cd docker

# 启动所有服务（生产环境）
docker-compose up -d

# 启动所有服务（开发环境）
docker-compose --profile dev up -d

# 仅启动后端服务
docker-compose up -d ragforge mysql elasticsearch minio redis

# 仅启动数据库服务
docker-compose up -d mysql elasticsearch minio redis
```

## 📋 服务列表

| 服务 | 端口 | 描述 | 访问地址 |
|------|------|------|----------|
| **web** | 80 | Web 控制台（生产环境） | http://localhost |
| **web-dev** | 3000 | Web 控制台（开发环境） | http://localhost:3000 |
| **ragforge** | 9380 | RAGForge API 服务 | http://localhost:9380 |
| **mysql** | 3306 | MySQL 数据库 | localhost:3306 |
| **elasticsearch** | 9200 | Elasticsearch 搜索引擎 | http://localhost:9200 |
| **minio** | 9000 | MinIO 对象存储 | http://localhost:9000 |
| **minio-console** | 9001 | MinIO 管理控制台 | http://localhost:9001 |
| **redis** | 6379 | Redis 缓存 | localhost:6379 |

## 🔐 默认凭据

| 服务 | 用户名 | 密码 | 数据库 |
|------|--------|------|--------|
| **MySQL** | root | ragforge123 | ragforge |
| **MinIO** | minioadmin | minioadmin | - |
| **Redis** | - | ragforge123 | - |
| **Elasticsearch** | elastic | (无密码) | - |

## 🛠️ 常用命令

### 服务管理

```bash
# 查看服务状态
docker-compose ps

# 查看服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f ragforge

# 停止所有服务
docker-compose down

# 重启服务
docker-compose restart

# 重新构建并启动
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 数据库操作

```bash
# 连接到 MySQL
docker exec -it docker-mysql-1 mysql -u root -pragforge123

# 查看 MySQL 日志
docker-compose logs mysql

# 备份 MySQL 数据
docker exec docker-mysql-1 mysqldump -u root -pragforge123 ragforge > backup.sql

# 恢复 MySQL 数据
docker exec -i docker-mysql-1 mysql -u root -pragforge123 ragforge < backup.sql
```

### 存储管理

```bash
# 访问 MinIO 控制台
# 浏览器打开: http://localhost:9001
# 用户名: minioadmin
# 密码: minioadmin

# 查看 MinIO 日志
docker-compose logs minio
```

## 🔧 环境变量配置

所有服务都支持通过环境变量进行配置。主要的环境变量包括：

### RAGForge API 服务

```bash
# 数据库配置
RAGFORGE_MYSQL_HOST=mysql
RAGFORGE_MYSQL_PORT=3306
RAGFORGE_MYSQL_USER=root
RAGFORGE_MYSQL_PASSWORD=ragforge123
RAGFORGE_MYSQL_DBNAME=ragforge

# Elasticsearch 配置
RAGFORGE_ES_HOSTS=http://elasticsearch:9200
RAGFORGE_ES_USERNAME=elastic
RAGFORGE_ES_PASSWORD=

# MinIO 配置
RAGFORGE_MINIO_HOST=minio:9000
RAGFORGE_MINIO_USER=minioadmin
RAGFORGE_MINIO_PASSWORD=minioadmin

# Redis 配置
RAGFORGE_REDIS_HOST=redis
RAGFORGE_REDIS_PORT=6379
RAGFORGE_REDIS_PASSWORD=ragforge123
```

### Web 控制台

```bash
# 生产环境
NODE_ENV=production

# 开发环境
NODE_ENV=development
```

## 📁 数据持久化

所有数据都通过 Docker 卷进行持久化：

- `mysql_data` - MySQL 数据
- `es_data` - Elasticsearch 数据
- `minio_data` - MinIO 数据
- `redis_data` - Redis 数据
- `ragforge_logs` - RAGForge 日志
- `ragforge_data` - RAGForge 数据

## 🔍 故障排除

### 常见问题

1. **端口冲突**
   ```bash
   # 检查端口占用
   lsof -i :80
   lsof -i :9380
   lsof -i :3306
   ```

2. **服务启动失败**
   ```bash
   # 查看详细日志
   docker-compose logs ragforge
   docker-compose logs mysql
   ```

3. **数据库连接失败**
   ```bash
   # 检查 MySQL 状态
   docker-compose ps mysql
   docker-compose logs mysql
   ```

4. **Web 控制台无法访问**
   ```bash
   # 检查 Web 服务状态
   docker-compose ps web
   docker-compose logs web
   ```

### 清理和重置

```bash
# 停止所有服务
docker-compose down

# 删除所有数据（谨慎操作）
docker-compose down -v

# 清理所有容器和镜像
docker system prune -a

# 重新构建
docker-compose build --no-cache
docker-compose up -d
```

## 🌐 网络配置

所有服务都在 `ragforge_network` 网络中运行，服务间可以通过服务名进行通信：

- `ragforge` - API 服务
- `mysql` - MySQL 数据库
- `elasticsearch` - Elasticsearch
- `minio` - MinIO 存储
- `redis` - Redis 缓存
- `web` - Web 控制台

## 📝 开发模式

开发模式下，Web 控制台会运行在端口 3000，支持热重载：

```bash
# 启动开发环境
docker-compose --profile dev up -d

# 访问开发环境
# http://localhost:3000
```

## 🔄 更新服务

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 📞 支持

如果遇到问题，请检查：

1. Docker 和 Docker Compose 是否正确安装
2. 端口是否被其他服务占用
3. 系统资源是否充足
4. 网络连接是否正常

更多信息请参考项目文档或提交 Issue。
