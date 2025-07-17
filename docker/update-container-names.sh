#!/bin/bash

# RAGForge 容器名称统一更新脚本
# 为所有容器添加 ragforge 前缀，避免与其他项目冲突

set -e

echo "=== RAGForge 容器名称统一更新脚本 ==="

# 备份原始文件
backup_dir="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$backup_dir"

echo "📁 创建备份目录: $backup_dir"

# 备份原始文件
cp docker-compose.yml "$backup_dir/"
cp docker-compose-dev.yml "$backup_dir/"
cp docker-compose-base.yml "$backup_dir/"
cp start.sh "$backup_dir/"

echo "✅ 已备份原始文件到 $backup_dir"

# 更新 docker-compose.yml 中的服务名称
echo "🔄 更新 docker-compose.yml..."

# 检查是否已经更新过
if grep -q "ragforge-ragforge" docker-compose.yml; then
    echo "⚠️  docker-compose.yml 已经更新过，跳过"
else
    # 更新服务名称
    sed -i '' 's/^  ragforge:/  ragforge-ragforge:/' docker-compose.yml
    sed -i '' 's/^  web:/  ragforge-web:/' docker-compose.yml
    sed -i '' 's/^  web-dev:/  ragforge-web-dev:/' docker-compose.yml
    sed -i '' 's/^  mysql:/  ragforge-mysql:/' docker-compose.yml
    sed -i '' 's/^  elasticsearch:/  ragforge-elasticsearch:/' docker-compose.yml
    sed -i '' 's/^  minio:/  ragforge-minio:/' docker-compose.yml
    sed -i '' 's/^  redis:/  ragforge-redis:/' docker-compose.yml
    
    # 更新依赖关系
    sed -i '' 's/- mysql/- ragforge-mysql/g' docker-compose.yml
    sed -i '' 's/- elasticsearch/- ragforge-elasticsearch/g' docker-compose.yml
    sed -i '' 's/- minio/- ragforge-minio/g' docker-compose.yml
    sed -i '' 's/- redis/- ragforge-redis/g' docker-compose.yml
    sed -i '' 's/- ragforge/- ragforge-ragforge/g' docker-compose.yml
    
    # 更新环境变量中的服务名称
    sed -i '' 's/ragforge:9380/ragforge-ragforge:9380/g' docker-compose.yml
    
    echo "✅ docker-compose.yml 更新完成"
fi

# 更新 start.sh 中的服务名称
echo "🔄 更新 start.sh..."

if grep -q "ragforge-ragforge" start.sh; then
    echo "⚠️  start.sh 已经更新过，跳过"
else
    sed -i '' 's/ragforge mysql elasticsearch minio redis/ragforge-ragforge ragforge-mysql ragforge-elasticsearch ragforge-minio ragforge-redis/g' start.sh
    sed -i '' 's/mysql elasticsearch minio redis/ragforge-mysql ragforge-elasticsearch ragforge-minio ragforge-redis/g' start.sh
    
    echo "✅ start.sh 更新完成"
fi

# 检查其他 Docker Compose 文件
echo "🔍 检查其他 Docker Compose 文件..."

# 检查 docker-compose-dev.yml
if grep -q "container_name: ragforge-" docker-compose-dev.yml; then
    echo "✅ docker-compose-dev.yml 已经使用 ragforge 前缀"
else
    echo "⚠️  docker-compose-dev.yml 需要手动检查"
fi

# 检查 docker-compose-base.yml
if grep -q "container_name: ragforge-" docker-compose-base.yml; then
    echo "✅ docker-compose-base.yml 已经使用 ragforge 前缀"
else
    echo "⚠️  docker-compose-base.yml 需要手动检查"
fi

echo ""
echo "=== 更新完成 ==="
echo "📋 更新内容："
echo "- 主服务: ragforge → ragforge-ragforge"
echo "- Web服务: web → ragforge-web"
echo "- 开发Web服务: web-dev → ragforge-web-dev"
echo "- MySQL: mysql → ragforge-mysql"
echo "- Elasticsearch: elasticsearch → ragforge-elasticsearch"
echo "- MinIO: minio → ragforge-minio"
echo "- Redis: redis → ragforge-redis"
echo ""
echo "📁 备份文件位置: $backup_dir"
echo ""
echo "🚀 现在可以使用以下命令启动服务："
echo "  ./start.sh"
echo ""
echo "🔧 如果需要恢复原始配置："
echo "  cp $backup_dir/* ." 