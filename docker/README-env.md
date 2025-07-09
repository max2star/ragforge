# RAGForge Docker 环境变量配置指南

## 概述

RAGForge 现在支持通过环境变量来覆盖配置文件中的服务地址和凭据。所有环境变量均需加 RAGFORGE_ 前缀，以避免与其他业务冲突。

## 默认服务配置

| 服务 | 地址 | 端口 | 用户名 | 密码 |
|------|------|------|--------|------|
| **Elasticsearch** | localhost | 9200 | elastic | (无密码) |
| **MySQL** | localhost | 3306 | root | ragforge123 |
| **MinIO** | localhost | 9000 | minioadmin | minioadmin |
| **Redis** | localhost | 6379 | - | ragforge123 |

## 环境变量列表

### 数据库配置

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| `RAGFORGE_MYSQL_HOST` | localhost | MySQL 主机地址 |
| `RAGFORGE_MYSQL_PORT` | 3306 | MySQL 端口 |
| `RAGFORGE_MYSQL_USER` | root | MySQL 用户名 |
| `RAGFORGE_MYSQL_PASSWORD` | ragforge123 | MySQL 密码 |
| `RAGFORGE_MYSQL_DBNAME` | rag_flow | MySQL 数据库名 |

### Elasticsearch 配置

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| `RAGFORGE_ES_HOSTS` | http://localhost:9200 | Elasticsearch 地址 |
| `RAGFORGE_ES_USERNAME` | elastic | Elasticsearch 用户名 |
| `RAGFORGE_ES_PASSWORD` | (空) | Elasticsearch 密码 |

### MinIO 配置

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| `RAGFORGE_MINIO_HOST` | localhost:9000 | MinIO 地址和端口 |
| `RAGFORGE_MINIO_USER` | minioadmin | MinIO 用户名 |
| `RAGFORGE_MINIO_PASSWORD` | minioadmin | MinIO 密码 |
| `RAGFORGE_MINIO_BUCKET_ENCRYPTION` | false | MinIO 存储桶加密 |

### Redis 配置

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| `RAGFORGE_REDIS_HOST` | localhost | Redis 主机地址 |
| `RAGFORGE_REDIS_PORT` | 6379 | Redis 端口 |
| `RAGFORGE_REDIS_PASSWORD` | ragforge123 | Redis 密码 |

### LLM 配置

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| `RAGFORGE_LLM_FACTORY` | OpenAI-API-Compatible | LLM 工厂类型 |
| `RAGFORGE_LLM_API_KEY` | gpustack_xxx | LLM API 密钥 |
| `RAGFORGE_LLM_BASE_URL` | http://101.52.216.178:890/v1 | LLM 基础 URL |

## 使用方法

### 方法 1: 使用环境变量文件

1. 复制示例文件：
```bash
cp docker/env.example docker/.env
```

2. 编辑 `.env` 文件，修改为你的环境配置：
```bash
# 示例：连接到远程 MySQL
RAGFORGE_MYSQL_HOST=mysql-server.example.com
RAGFORGE_MYSQL_PORT=3306
RAGFORGE_MYSQL_USER=ragforge_user
RAGFORGE_MYSQL_PASSWORD=your_password
```

3. 启动容器：
```bash
docker run --env-file docker/.env ragforge-simple:latest
```

### 方法 2: 直接在命令行中设置

```bash
docker run \
  -e RAGFORGE_MYSQL_HOST=mysql-server.example.com \
  -e RAGFORGE_MYSQL_PORT=3306 \
  -e RAGFORGE_ES_HOSTS=http://es-server.example.com:9200 \
  -e RAGFORGE_MINIO_HOST=minio-server.example.com:9000 \
  ragforge-simple:latest
```

### 方法 3: 使用 docker-compose

创建 `docker-compose.yml` 文件：

```yaml
version: '3.8'
services:
  ragforge:
    image: ragforge-simple:latest
    ports:
      - "9380:9380"
    environment:
      - RAGFORGE_MYSQL_HOST=mysql
      - RAGFORGE_MYSQL_PORT=3306
      - RAGFORGE_ES_HOSTS=http://elasticsearch:9200
      - RAGFORGE_MINIO_HOST=minio:9000
      - RAGFORGE_REDIS_HOST=redis
    depends_on:
      - mysql
      - elasticsearch
      - minio
      - redis

  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ragforge123
      MYSQL_DATABASE: rag_flow
    ports:
      - "3306:3306"

  elasticsearch:
    image: elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"

  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ragforge123
    ports:
      - "6379:6379"
```

## 配置优先级

环境变量的优先级高于配置文件：

1. **RAGFORGE_ 环境变量** (最高优先级)
2. **local.service_conf.yaml** (本地配置)
3. **service_conf.yaml** (默认配置)

## 验证配置

启动容器后，可以在日志中看到配置信息：

```
Current configs, from /ragforge/conf/service_conf.yaml:
	mysql: {'name': 'rag_flow', 'user': 'root', 'password': '********', 'host': 'mysql-server.example.com', 'port': 3306, 'max_connections': 100, 'stale_timeout': 30}
	es: {'hosts': 'http://es-server.example.com:9200', 'username': 'elastic', 'password': ''}
	minio: {'user': 'minioadmin', 'password': '********', 'host': 'minio-server.example.com:9000', 'bucket_encryption': False}
```

## 故障排除

### 1. 检查环境变量是否正确设置

```bash
docker run --rm ragforge-simple:latest env | grep RAGFORGE_
```

### 2. 查看配置加载日志

启动容器时，会显示所有配置项（密码会被隐藏）：

```
Current configs, from /ragforge/conf/service_conf.yaml:
	...
```

### 3. 常见问题

- **连接被拒绝**: 检查服务地址和端口是否正确
- **认证失败**: 检查用户名和密码是否正确
- **配置未生效**: 确保环境变量名称正确（区分大小写）

## 示例场景

### 场景 1: 开发环境

使用本地服务，直接使用默认配置：

```bash
docker run -p 9380:9380 ragforge-simple:latest
```

### 场景 2: 生产环境

连接到远程服务：

```bash
docker run \
  -p 9380:9380 \
  -e RAGFORGE_MYSQL_HOST=prod-mysql.company.com \
  -e RAGFORGE_MYSQL_PASSWORD=prod_password \
  -e RAGFORGE_ES_HOSTS=https://prod-es.company.com:9200 \
  -e RAGFORGE_ES_PASSWORD=prod_es_password \
  -e RAGFORGE_MINIO_HOST=prod-minio.company.com:9000 \
  -e RAGFORGE_MINIO_PASSWORD=prod_minio_password \
  ragforge-simple:latest
```

### 场景 3: 容器化部署

使用 docker-compose 进行完整部署，参考上面的 docker-compose.yml 示例。 