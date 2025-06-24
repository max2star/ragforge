# RAGFlow 开发环境设置指南

这个指南将帮助你设置完整的 RAGFlow 开发环境，包括 Docker 服务和 API 配置。

## 🚀 快速开始

### 1. 启动 Docker 服务

```bash
cd docker
./start-dev.sh
```

选择启动模式：
- **选项 1**: 完整模式（包含 Infinity 向量数据库）
- **选项 2**: 简化模式（推荐给 ARM64 Mac 用户）

### 2. 切换 API 配置

```bash
cd conf
./switch-to-dev.sh
```

### 3. 启动 API 服务器

```bash
# 回到项目根目录
cd ..

# 设置环境变量
export PYTHONPATH=/Users/zhaozhilong/Desktop/cursor/Test/ragflow

# 启动 API 服务器
python api/main.py
```

## 📋 详细步骤

### 第一步：启动 Docker 服务

1. **进入 docker 目录**：
   ```bash
   cd docker
   ```

2. **运行启动脚本**：
   ```bash
   ./start-dev.sh
   ```

3. **选择启动模式**：
   - 对于 Apple Silicon Mac，推荐选择 **选项 2（简化模式）**
   - 对于 Intel Mac，可以选择 **选项 1（完整模式）**

4. **验证服务状态**：
   ```bash
   docker-compose -f docker-compose-dev.yml ps
   # 或
   docker-compose -f docker-compose-dev-no-infinity.yml ps
   ```

### 第二步：配置 API 连接

1. **进入 conf 目录**：
   ```bash
   cd conf
   ```

2. **切换到开发环境配置**：
   ```bash
   ./switch-to-dev.sh
   ```

3. **验证配置**：
   ```bash
   cat service_conf.yaml | grep -A 5 "mysql:"
   cat service_conf.yaml | grep -A 5 "es:"
   cat service_conf.yaml | grep -A 5 "minio:"
   cat service_conf.yaml | grep -A 5 "redis:"
   ```

### 第三步：启动 API 服务器

1. **回到项目根目录**：
   ```bash
   cd ..
   ```

2. **设置 Python 环境**：
   ```bash
   # 激活虚拟环境（如果有）
   source .venv/bin/activate
   
   # 设置 PYTHONPATH
   export PYTHONPATH=/Users/zhaozhilong/Desktop/cursor/Test/ragflow
   ```

3. **启动 API 服务器**：
   ```bash
   python api/main.py
   ```

## 🔧 服务配置详情

### Docker 服务地址

| 服务 | 地址 | 端口 | 用户名 | 密码 |
|------|------|------|--------|------|
| **Elasticsearch** | http://localhost | 9200 | elastic | changeme |
| **MySQL** | localhost | 3306 | root | ragflow123 |
| **MinIO** | http://localhost | 9000 | minioadmin | minioadmin |
| **MinIO Console** | http://localhost | 9001 | minioadmin | minioadmin |
| **Redis** | localhost | 6379 | - | ragflow123 |
| **Infinity** | http://localhost | 23820 | - | - |

### API 配置

配置文件：`conf/service_conf.yaml`

主要修改：
- MySQL: `localhost:3306` (root/ragflow123)
- Elasticsearch: `http://localhost:9200` (elastic/changeme)
- MinIO: `localhost:9000` (minioadmin/minioadmin)
- Redis: `localhost:6379` (ragflow123)

## 🛠️ 环境变量

### 数据库类型
```bash
export DATABASE_TYPE=mysql  # 默认使用 MySQL
# export DATABASE_TYPE=dm   # 使用达梦数据库
```

### 文档引擎
```bash
export DOC_ENGINE=elasticsearch  # 默认使用 Elasticsearch
# export DOC_ENGINE=infinity     # 使用 Infinity 向量数据库
```

### 存储实现
```bash
export STORAGE_IMPL=MINIO  # 默认使用 MinIO
# export STORAGE_IMPL=AWS_S3  # 使用 AWS S3
```

## 🔍 故障排除

### 1. Docker 服务启动失败

**问题**：Infinity 镜像不支持 ARM64
```bash
# 解决方案：使用简化模式
cd docker
./start-dev.sh
# 选择选项 2
```

**问题**：端口冲突
```bash
# 解决方案：修改端口
cd docker
# 编辑 .env 文件，修改端口
ES_PORT=9201
MYSQL_PORT=3307
MINIO_PORT=9002
REDIS_PORT=6380
```

### 2. API 连接失败

**问题**：无法连接到数据库
```bash
# 检查 Docker 服务状态
cd docker
docker-compose -f docker-compose-dev.yml ps

# 检查服务日志
docker-compose -f docker-compose-dev.yml logs mysql-ragflow
```

**问题**：配置未生效
```bash
# 重新应用配置
cd conf
./switch-to-dev.sh
```

### 3. Python 环境问题

**问题**：模块导入错误
```bash
# 设置 PYTHONPATH
export PYTHONPATH=/Users/zhaozhilong/Desktop/cursor/Test/ragflow

# 安装依赖
pip install -r requirements.txt
# 或
uv sync --python 3.10 --all-extras
```

## 📝 常用命令

### Docker 管理
```bash
# 启动服务
cd docker
./start-dev.sh

# 停止服务
./stop-dev.sh

# 查看状态
docker-compose -f docker-compose-dev.yml ps

# 查看日志
docker-compose -f docker-compose-dev.yml logs -f

# 重启服务
docker-compose -f docker-compose-dev.yml restart
```

### 配置管理
```bash
# 切换到开发配置
cd conf
./switch-to-dev.sh

# 恢复原配置
./restore-original.sh

# 查看当前配置
cat service_conf.yaml
```

### API 管理
```bash
# 启动 API 服务器
python api/main.py

# 后台运行
nohup python api/main.py > api.log 2>&1 &

# 查看 API 日志
tail -f api.log
```

## 🔄 开发工作流

### 日常开发流程

1. **启动开发环境**：
   ```bash
   cd docker && ./start-dev.sh
   cd conf && ./switch-to-dev.sh
   ```

2. **开发调试**：
   ```bash
   cd ..
   export PYTHONPATH=/Users/zhaozhilong/Desktop/cursor/Test/ragflow
   python api/main.py
   ```

3. **停止开发环境**：
   ```bash
   cd docker && ./stop-dev.sh
   cd conf && ./restore-original.sh
   ```

### 数据管理

```bash
# 清理所有数据
cd docker
docker-compose -f docker-compose-dev.yml down -v

# 备份数据
docker exec ragflow-mysql-dev mysqldump -u root -pragflow123 rag_flow > backup.sql

# 恢复数据
docker exec -i ragflow-mysql-dev mysql -u root -pragflow123 rag_flow < backup.sql
```

## 📚 相关文档

- [Docker 开发环境说明](docker/README-dev.md)
- [配置管理说明](conf/README-dev-config.md)
- [API 开发指南](docs/api-development.md)

## 🆘 获取帮助

如果遇到问题：

1. 检查 Docker 服务状态
2. 查看服务日志
3. 验证配置文件
4. 检查环境变量
5. 参考故障排除部分

---

**注意**：开发环境配置仅用于本地开发和测试，不要在生产环境中使用。 