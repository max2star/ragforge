# RAGForge 开发环境

这个目录包含了用于开发的 Docker Compose 配置，使用单机模式的 Elasticsearch，简化了配置并移除了集群相关的复杂性。

## 文件说明

- `docker-compose-dev.yml` - 完整开发环境配置（包含 Infinity 向量数据库）
- `docker-compose-dev-no-infinity.yml` - 简化开发环境配置（不包含 Infinity）
- `start-dev.sh` - 启动开发环境的脚本（提供模式选择）
- `stop-dev.sh` - 停止开发环境的脚本
- `.env` - 环境变量配置文件（首次运行时会自动创建）

## 快速开始

### 1. 启动开发环境

```bash
cd docker
./start-dev.sh
```

启动脚本会询问你选择启动模式：
- **完整模式**: 包含 Infinity 向量数据库（需要 Rosetta 2 支持）
- **简化模式**: 不包含 Infinity，适合 ARM64 Mac 用户

### 2. 停止开发环境

```bash
cd docker
./stop-dev.sh
```

### 3. 手动管理

```bash
# 启动完整模式
docker-compose -f docker-compose-dev.yml up -d

# 启动简化模式
docker-compose -f docker-compose-dev-no-infinity.yml up -d

# 查看服务状态
docker-compose -f docker-compose-dev.yml ps
docker-compose -f docker-compose-dev-no-infinity.yml ps

# 查看日志
docker-compose -f docker-compose-dev.yml logs -f
docker-compose -f docker-compose-dev-no-infinity.yml logs -f

# 停止服务
docker-compose -f docker-compose-dev.yml down
docker-compose -f docker-compose-dev-no-infinity.yml down
```

## 服务配置

### Elasticsearch (单机模式)
- **端口**: 9200
- **认证**: 无密码 (开发模式)
- **访问**: http://localhost:9200

### MySQL
- **端口**: 3306
- **用户名**: root
- **密码**: ragforge123
- **数据库**: ragforge

### MinIO
- **API 端口**: 9000
- **控制台端口**: 9001
- **用户名**: minioadmin
- **密码**: minioadmin
- **访问**: http://localhost:9000 (API), http://localhost:9001 (控制台)

### Redis
- **端口**: 6379
- **密码**: ragforge123

### Infinity (向量数据库) - 仅完整模式
- **Thrift 端口**: 23817
- **HTTP 端口**: 23820
- **PostgreSQL 端口**: 5432
- **访问**: http://localhost:23820
- **注意**: 在 ARM64 Mac 上通过 Rosetta 2 运行

## ARM64 兼容性说明

### Apple Silicon Mac 用户
- **推荐使用简化模式**，不包含 Infinity 向量数据库
- Infinity 镜像不支持 ARM64 架构，需要通过 Rosetta 2 模拟运行
- 如果选择完整模式，确保已安装 Rosetta 2：
  ```bash
  softwareupdate --install-rosetta
  ```

### Intel Mac 用户
- 可以使用完整模式，包含所有服务
- 性能更好，无需模拟层

## 与生产环境的区别

1. **Elasticsearch**: 使用单机模式 (`discovery.type=single-node`)，禁用了 X-Pack 安全功能
2. **简化配置**: 移除了集群配置、SSL 证书、Vault 等复杂组件
3. **开发友好**: 降低了内存限制，简化了网络配置
4. **快速启动**: 减少了服务数量，启动更快
5. **ARM64 支持**: 提供了不包含 Infinity 的简化版本

## 故障排除

### Infinity 启动失败
如果 Infinity 服务启动失败（常见于 ARM64 Mac），请使用简化模式：

```bash
docker-compose -f docker-compose-dev-no-infinity.yml up -d
```

### 端口冲突
如果遇到端口冲突，可以修改 `.env` 文件中的端口配置：

```bash
# 修改端口
ES_PORT=9201
MYSQL_PORT=3307
MINIO_PORT=9002
REDIS_PORT=6380
```

### 内存不足
如果遇到内存不足，可以调整 `.env` 文件中的内存限制：

```bash
MEM_LIMIT=512m
```

### 数据持久化
所有数据都保存在 Docker volumes 中，重启容器数据不会丢失。如果需要清理数据：

```bash
docker-compose -f docker-compose-dev.yml down -v
docker-compose -f docker-compose-dev-no-infinity.yml down -v
```

## 开发建议

1. **ARM64 Mac 用户**: 优先使用简化模式，避免 Infinity 兼容性问题
2. **Intel Mac 用户**: 可以使用完整模式，获得完整的向量数据库功能
3. **生产环境**: 请使用 `docker-compose-base.yml` 的集群模式
4. **定期备份**: 定期备份重要的开发数据
5. **配置调整**: 根据需要调整 `.env` 文件中的配置 