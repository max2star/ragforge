#!/bin/bash

# 开发环境启动脚本
echo "启动 RAGFlow 开发环境..."

# 检查 .env 文件是否存在
if [ ! -f ".env" ]; then
    echo "创建默认的 .env 文件..."
    cat > .env << EOF
# 开发环境配置文件

# 时区设置
TIMEZONE=Asia/Shanghai

# Elasticsearch 配置
STACK_VERSION=8.11.0
ES_PORT=9200
ELASTIC_PASSWORD=changeme

# MySQL 配置
MYSQL_PORT=3306
MYSQL_PASSWORD=ragflow123

# MinIO 配置
MINIO_PORT=9000
MINIO_CONSOLE_PORT=9001
MINIO_USER=minioadmin
MINIO_PASSWORD=minioadmin

# Redis 配置
REDIS_PORT=6379
REDIS_PASSWORD=ragflow123

# Infinity 配置
INFINITY_THRIFT_PORT=23817
INFINITY_HTTP_PORT=23820
INFINITY_PSQL_PORT=5432

# 内存限制
MEM_LIMIT=1g
EOF
    echo ".env 文件已创建"
fi

# 询问用户是否包含 Infinity
echo ""
echo "选择启动模式："
echo "1) 完整模式 (包含 Infinity 向量数据库)"
echo "2) 简化模式 (不包含 Infinity，适合 ARM64 Mac)"
echo ""
read -p "请选择 (1 或 2): " choice

case $choice in
    1)
        echo "启动完整模式..."
        COMPOSE_FILE="docker-compose-dev.yml"
        ;;
    2)
        echo "启动简化模式..."
        COMPOSE_FILE="docker-compose-dev-no-infinity.yml"
        ;;
    *)
        echo "无效选择，默认使用简化模式..."
        COMPOSE_FILE="docker-compose-dev-no-infinity.yml"
        ;;
esac

# 启动开发环境服务
echo "启动 Docker 服务..."
docker-compose -f $COMPOSE_FILE up -d

echo "等待服务启动..."
sleep 10

# 检查服务状态
echo "检查服务状态..."
docker-compose -f $COMPOSE_FILE ps

echo "开发环境启动完成！"
echo ""
echo "服务访问地址："
echo "- Elasticsearch: http://localhost:9200"
echo "- MySQL: localhost:3306"
echo "- MinIO: http://localhost:9000 (Console: http://localhost:9001)"
echo "- Redis: localhost:6379"

if [ "$COMPOSE_FILE" = "docker-compose-dev.yml" ]; then
    echo "- Infinity: http://localhost:23820"
fi

echo ""
echo "默认凭据："
echo "- Elasticsearch: 无密码 (开发模式)"
echo "- MySQL: root/ragflow123"
echo "- MinIO: minioadmin/minioadmin"
echo "- Redis: ragflow123" 