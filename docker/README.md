# RAGForge Docker 部署指南

## 概述

本目录包含了 RAGForge 的 Docker 部署配置，支持通过环境变量灵活配置各种服务地址和凭据。所有环境变量均需加 RAGFORGE_ 前缀。

## 快速开始

### 1. 完整部署（推荐）

```bash
cd docker
./start.sh -f
```

这将：
- 构建 RAGForge Docker 镜像
- 启动所有必需的服务（MySQL、Elasticsearch、MinIO、Redis）
- 显示服务状态和访问信息

### 2. 分步部署

```bash
# 1. 构建镜像
./start.sh -b

# 2. 启动服务
./start.sh -u

# 3. 查看日志
./start.sh -l

# 4. 停止服务
./start.sh -d
```

## 服务配置

### 默认服务地址

| 服务 | 地址 | 端口 | 用户名 | 密码 |
|------|------|------|--------|------|
| **RAGForge API** | localhost | 9380 | - | - |
| **MySQL** | localhost | 3306 | root | ragforge123 |
| **Elasticsearch** | localhost | 9200 | elastic | (无密码) |
| **MinIO** | localhost | 9000 | minioadmin | minioadmin |
| **MinIO Console** | localhost | 9001 | minioadmin | minioadmin |
| **Redis** | localhost | 6379 | - | ragforge123 |

### 环境变量配置

支持通过环境变量覆盖默认配置，所有变量需加 RAGFORGE_ 前缀：

```bash
# 使用环境变量文件
docker run --env-file .env ragforge-simple:latest

# 直接在命令行设置
docker run \
  -e RAGFORGE_MYSQL_HOST=mysql-server.example.com \
  -e RAGFORGE_ES_HOSTS=http://es-server.example.com:9200 \
  ragforge-simple:latest
```

详细的环境变量说明请参考 [README-env.md](README-env.md)。

## 文件说明

- `docker-compose.yml` - Docker Compose 配置文件
- `env.example` - 环境变量示例文件
- `start.sh` - 快速启动脚本
- `README-env.md` - 环境变量详细说明

## 常用命令

```bash
# 查看帮助
./start.sh -h

# 构建镜像
./start.sh -b

# 启动服务
./start.sh -u

# 查看日志
./start.sh -l

# 重启服务
./start.sh -r

# 停止服务
./start.sh -d

# 清理所有数据
./start.sh -c
```

## 故障排除

### 1. 端口冲突

如果端口被占用，可以修改 `docker-compose.yml` 中的端口映射：

```yaml
ports:
  - "9381:9380"  # 改为 9381
```

### 2. 内存不足

Elasticsearch 需要较多内存，可以调整 JVM 参数：

```yaml
environment:
  - "ES_JAVA_OPTS=-Xms1g -Xmx1g"
```

### 3. 数据持久化

数据会自动保存到 Docker 卷中：

- `mysql_data` - MySQL 数据
- `es_data` - Elasticsearch 数据
- `minio_data` - MinIO 数据
- `redis_data` - Redis 数据
- `ragforge_logs` - RAGForge 日志
- `ragforge_data` - RAGForge 数据

### 4. 查看服务状态

```bash
docker-compose ps
```

### 5. 查看服务日志

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs ragforge
docker-compose logs mysql
```

## 生产环境部署

对于生产环境，建议：

1. **修改默认密码**：更改所有服务的默认密码
2. **使用外部数据库**：连接现有的 MySQL/PostgreSQL 实例
3. **配置 SSL**：为 API 和 MinIO 配置 SSL 证书
4. **设置备份**：配置数据库和文件存储的备份策略
5. **监控**：添加 Prometheus 和 Grafana 监控

## 支持

如果遇到问题，请：

1. 查看服务日志：`./start.sh -l`
2. 检查服务状态：`docker-compose ps`
3. 查看详细文档：[README-env.md](README-env.md)
