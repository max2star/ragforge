# 开发环境配置说明

这个目录包含了用于开发环境的配置文件，用于将 RAGFlow API 连接到开发环境的 Docker 服务。

## 文件说明

- `service_conf-dev.yaml` - 开发环境配置文件
- `switch-to-dev.sh` - 切换到开发环境配置的脚本
- `restore-original.sh` - 恢复原配置的脚本
- `service_conf.yaml.backup` - 原配置的备份文件（运行 switch-to-dev.sh 后生成）

## 配置对比

### 原配置 vs 开发环境配置

| 服务 | 原配置 | 开发环境配置 |
|------|--------|--------------|
| **MySQL** | localhost:5455 (root/infini_rag_flow) | localhost:3306 (root/ragflow123) |
| **Elasticsearch** | https://localhost:1200 (elastic/EPPso10r8Ja) | http://localhost:9200 (elastic/changeme) |
| **MinIO** | localhost:9000 (rag_flow/infini_rag_flow) | localhost:9000 (minioadmin/minioadmin) |
| **Redis** | localhost:6379 (infini_rag_flow) | localhost:6379 (ragflow123) |
| **Infinity** | localhost:23817 | localhost:23817 |

## 使用方法

### 1. 切换到开发环境配置

```bash
cd conf
./switch-to-dev.sh
```

这个脚本会：
- 备份当前的 `service_conf.yaml` 为 `service_conf.yaml.backup`
- 将 `service_conf-dev.yaml` 复制为 `service_conf.yaml`

### 2. 恢复原配置

```bash
cd conf
./restore-original.sh
```

这个脚本会从备份文件恢复原配置。

### 3. 手动配置

你也可以手动编辑 `service_conf.yaml` 文件，将服务地址修改为：

```yaml
mysql:
  host: 'localhost'
  port: 3306
  password: 'ragflow123'

es:
  hosts: 'http://localhost:9200'
  password: 'changeme'

minio:
  user: 'minioadmin'
  password: 'minioadmin'
  host: 'localhost:9000'

redis:
  password: 'ragflow123'
  host: 'localhost:6379'
```

## 重要说明

### 1. 数据库类型
- 默认使用 MySQL 数据库
- 如需使用达梦数据库，请确保 `DATABASE_TYPE=dm` 环境变量已设置

### 2. 文档引擎
- 默认使用 Elasticsearch (`DOC_ENGINE=elasticsearch`)
- 如需使用 Infinity，请设置 `DOC_ENGINE=infinity`

### 3. 存储类型
- 默认使用 MinIO (`STORAGE_IMPL=MINIO`)
- 支持的其他选项：AWS_S3, AZURE_SPN, AZURE_SAS, OSS

### 4. 安全配置
- 开发环境禁用了 Elasticsearch 的 X-Pack 安全功能
- 使用 HTTP 而不是 HTTPS 连接
- 移除了 SSL 证书配置

## 环境变量

你还可以通过环境变量来覆盖配置：

```bash
# 数据库类型
export DATABASE_TYPE=mysql  # 或 dm

# 文档引擎
export DOC_ENGINE=elasticsearch  # 或 infinity

# 存储实现
export STORAGE_IMPL=MINIO  # 或 AWS_S3, AZURE_SPN, AZURE_SAS, OSS
```

## 故障排除

### 1. 连接失败
确保 Docker 服务正在运行：
```bash
cd docker
docker-compose -f docker-compose-dev.yml ps
```

### 2. 端口冲突
如果遇到端口冲突，可以修改 Docker 配置中的端口映射，然后相应地更新 `service_conf-dev.yaml`。

### 3. 权限问题
确保脚本有执行权限：
```bash
chmod +x conf/switch-to-dev.sh conf/restore-original.sh
```

## 开发建议

1. **开发前**：运行 `switch-to-dev.sh` 切换到开发环境配置
2. **开发中**：确保 Docker 服务正常运行
3. **部署前**：运行 `restore-original.sh` 恢复生产环境配置
4. **定期备份**：重要配置修改前先备份 