#!/bin/bash

# RAGFlow开发环境自动修复脚本
# 用于修复常见的配置问题和连接问题

set -e

echo "🔧 开始修复RAGFlow开发环境..."

# 检查是否在正确的目录
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ 请在RAGFlow项目根目录运行此脚本"
    exit 1
fi

# 停止所有容器
echo "=== 停止所有容器 ==="
docker-compose down 2>/dev/null || true
echo "✅ 容器已停止"

# 修复.env文件
echo "=== 修复.env文件 ==="
if [ -f ".env" ]; then
    # 备份原文件
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    
    # 修复MySQL配置
    echo "   修复MySQL配置..."
    sed -i.bak 's/MYSQL_HOST=.*/MYSQL_HOST=ragflow-mysql-dev/' .env
    sed -i.bak 's/MYSQL_PORT=.*/MYSQL_PORT=13306/' .env
    sed -i.bak 's/MYSQL_USER=.*/MYSQL_USER=root/' .env
    sed -i.bak 's/MYSQL_PASSWORD=.*/MYSQL_PASSWORD=infini_rag_flow/' .env
    sed -i.bak 's/MYSQL_DATABASE=.*/MYSQL_DATABASE=ragflow/' .env
    
    # 修复Redis配置
    echo "   修复Redis配置..."
    sed -i.bak 's/REDIS_HOST=.*/REDIS_HOST=localhost/' .env
    sed -i.bak 's/REDIS_PORT=.*/REDIS_PORT=16379/' .env
    sed -i.bak 's/REDIS_PASSWORD=.*/REDIS_PASSWORD=infini_rag_flow/' .env
    
    # 修复MinIO配置
    echo "   修复MinIO配置..."
    sed -i.bak 's/MINIO_HOST=.*/MINIO_HOST=localhost/' .env
    sed -i.bak 's/MINIO_PORT=.*/MINIO_PORT=19000/' .env
    sed -i.bak 's/MINIO_ACCESS_KEY=.*/MINIO_ACCESS_KEY=infini_rag_flow/' .env
    sed -i.bak 's/MINIO_SECRET_KEY=.*/MINIO_SECRET_KEY=infini_rag_flow/' .env
    
    # 修复Elasticsearch配置
    echo "   修复Elasticsearch配置..."
    sed -i.bak 's/ELASTICSEARCH_HOST=.*/ELASTICSEARCH_HOST=localhost/' .env
    sed -i.bak 's/ELASTICSEARCH_PORT=.*/ELASTICSEARCH_PORT=19200/' .env
    
    echo "✅ .env文件已修复"
else
    echo "❌ 未找到.env文件"
fi

# 修复service_conf.yaml文件
echo "=== 修复service_conf.yaml文件 ==="
if [ -f "service_conf.yaml" ]; then
    # 备份原文件
    cp service_conf.yaml service_conf.yaml.backup.$(date +%Y%m%d_%H%M%S)
    
    # 修复Redis配置
    echo "   修复Redis配置..."
    sed -i.bak 's/host:.*redis.*/host: localhost:16379/' service_conf.yaml
    
    # 修复MySQL配置
    echo "   修复MySQL配置..."
    sed -i.bak 's/host:.*mysql.*/host: ragflow-mysql-dev:3306/' service_conf.yaml
    
    # 修复MinIO配置
    echo "   修复MinIO配置..."
    sed -i.bak 's/host:.*minio.*/host: localhost:19000/' service_conf.yaml
    
    # 修复Elasticsearch配置
    echo "   修复Elasticsearch配置..."
    sed -i.bak 's/host:.*elasticsearch.*/host: localhost:19200/' service_conf.yaml
    
    echo "✅ service_conf.yaml文件已修复"
else
    echo "❌ 未找到service_conf.yaml文件"
fi

# 清理数据卷（可选）
echo "=== 清理数据卷 ==="
read -p "是否要清理数据卷？这将删除所有数据！(y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "   清理MySQL数据卷..."
    docker volume rm ragflow_mysql_data 2>/dev/null || true
    
    echo "   清理Elasticsearch数据卷..."
    docker volume rm ragflow_elasticsearch_data 2>/dev/null || true
    
    echo "   清理MinIO数据卷..."
    docker volume rm ragflow_minio_data 2>/dev/null || true
    
    echo "✅ 数据卷已清理"
else
    echo "⏭️  跳过数据卷清理"
fi

# 启动服务
echo "=== 启动服务 ==="
echo "   启动基础服务..."
docker-compose up -d mysql redis minio elasticsearch

echo "   等待服务启动..."
sleep 10

echo "   启动后端服务..."
docker-compose up -d ragflow-server

echo "✅ 服务启动完成"

# 检查服务状态
echo "=== 检查服务状态 ==="
docker-compose ps

echo ""
echo "🎉 修复完成！"
echo "请运行 ./check-dev-env.sh 检查服务状态" 