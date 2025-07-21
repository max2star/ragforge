# RAGForge 容器隔离配置

## 概述

为了避免与其他项目的 Docker 容器冲突，RAGForge 现在使用 `ragforge-` 前缀来命名所有容器。

## 更改内容

### 容器名称映射

| 原名称 | 新名称 | 说明 |
|--------|--------|------|
| `ragforge` | `ragforge-ragforge` | 主后端服务 |
| `web` | `ragforge-web` | Web 控制台（生产环境） |
| `web-dev` | `ragforge-web-dev` | Web 控制台（开发环境） |
| `mysql` | `ragforge-mysql` | MySQL 数据库 |
| `elasticsearch` | `ragforge-elasticsearch` | Elasticsearch 搜索引擎 |
| `minio` | `ragforge-minio` | MinIO 对象存储 |
| `redis` | `ragforge-redis` | Redis 缓存 |

### 配置文件更改

1. **docker-compose.yml**
   - 所有服务名称添加 `ragforge-` 前缀
   - 更新服务间的依赖关系
   - 更新环境变量中的服务名称引用

2. **start.sh**
   - 更新服务启动命令中的服务名称
   - 保持原有的功能不变

## 使用方法

### 使用启动脚本（推荐）

```bash
cd docker
./start.sh
```

这个脚本提供了以下功能：
- 使用 `ragforge` 作为 Docker Compose 项目名
- 只管理 ragforge 相关容器，不影响其他项目
- 提供完整的服务管理功能
- 避免与其他项目的容器冲突

### 手动使用 Docker Compose

```bash
cd docker
# 启动所有服务
docker-compose -p ragforge up -d

# 查看服务状态
docker-compose -p ragforge ps

# 查看日志
docker-compose -p ragforge logs -f

# 停止服务
docker-compose -p ragforge down
```

## 脚本说明

### start.sh
- **功能**：RAGForge 服务启动脚本
- **特点**：只管理 ragforge 相关容器，不影响其他项目
- **选项**：
  1. 启动所有服务（生产环境）
  2. 启动所有服务（开发环境）
  3. 仅启动后端服务
  4. 仅启动数据库服务
  5. 停止所有服务
  6. 查看服务状态
  7. 查看服务日志
  8. 重新构建并启动

### update-container-names.sh
- **功能**：自动更新容器名称
- **特点**：备份原始文件，安全更新
- **使用**：`./update-container-names.sh`

## 故障排除

### 1. 端口冲突
如果遇到端口被占用的情况：
```bash
# 检查端口占用
lsof -i :9380
lsof -i :80
lsof -i :3000

# 停止占用端口的进程
kill -9 <PID>
```

### 2. 容器冲突
如果遇到容器名称冲突：
```bash
# 清理所有 ragforge 相关容器
docker-compose -p ragforge down -v --remove-orphans
docker container prune -f
docker network prune -f
```

### 3. Redis 认证错误
如果遇到 Redis 认证错误：
1. 检查 Redis 密码配置
2. 确保 Redis 容器使用正确的密码
3. 更新 `conf/service_conf.yaml` 中的 Redis 密码

## 环境变量

### Docker Compose 项目名
- `COMPOSE_PROJECT_NAME=ragforge`

### 容器名称前缀
- `PROJECT_PREFIX=ragforge`

## 网络配置

所有 ragforge 容器使用独立的网络：
- 网络名称：`ragforge_ragforge`
- 子网：自动分配

## 数据持久化

所有数据卷都使用 `ragforge_` 前缀：
- `ragforge_mysql_data`
- `ragforge_es_data`
- `ragforge_minio_data`
- `ragforge_redis_data`
- `ragforge_ragforge_logs`
- `ragforge_ragforge_data`

## 迁移指南

### 从旧版本迁移

1. **备份现有数据**
```bash
# 备份数据库
docker exec ragforge-mysql mysqldump -u root -p ragforge > backup.sql

# 备份 MinIO 数据
# 使用 MinIO 客户端下载数据
```

2. **停止旧服务**
```bash
docker-compose down
```

3. **使用新配置启动**
```bash
./start-isolated.sh
```

4. **恢复数据**
```bash
# 恢复数据库
docker exec -i ragforge-mysql mysql -u root -p ragforge < backup.sql

# 恢复 MinIO 数据
# 使用 MinIO 客户端上传数据
```

## 注意事项

1. **容器名称**：所有容器名称都以 `ragforge-` 开头
2. **网络隔离**：使用独立的 Docker 网络
3. **数据卷**：使用独立的 Docker 卷
4. **端口映射**：保持原有的端口映射不变
5. **环境变量**：更新了服务间的引用

## 验证

启动服务后，可以使用以下命令验证：

```bash
# 查看所有 ragforge 容器
docker ps --filter "name=ragforge"

# 查看网络
docker network ls --filter "name=ragforge"

# 查看数据卷
docker volume ls --filter "name=ragforge"
``` 