#!/bin/bash

# RAGForge 完整服务启动脚本

set -e

echo "=== RAGForge 服务启动脚本 ==="
echo "1. 启动所有服务（生产环境）"
echo "2. 启动所有服务（开发环境）"
echo "3. 仅启动后端服务"
echo "4. 仅启动数据库服务"
echo "5. 停止所有服务"
echo "6. 查看服务状态"
echo "7. 查看服务日志"
echo "8. 重新构建并启动"
echo ""

read -p "请选择操作 (1-8): " choice

case $choice in
    1)
        echo "启动所有服务（生产环境）..."
        docker-compose up -d
        echo "✅ 所有服务已启动"
        echo "🌐 Web控制台: http://localhost"
        echo "🔧 API服务: http://localhost:9380"
        echo "🗄️ MySQL: localhost:3306"
        echo "🔍 Elasticsearch: localhost:9200"
        echo "📦 MinIO: localhost:9000"
        echo "💾 Redis: localhost:6379"
        ;;
    2)
        echo "启动所有服务（开发环境）..."
        docker-compose --profile dev up -d
        echo "✅ 所有服务已启动（开发模式）"
        echo "🌐 Web控制台: http://localhost:3000"
        echo "🔧 API服务: http://localhost:9380"
        ;;
    3)
        echo "仅启动后端服务..."
        docker-compose up -d ragforge mysql elasticsearch minio redis
        echo "✅ 后端服务已启动"
        echo "🔧 API服务: http://localhost:9380"
        ;;
    4)
        echo "仅启动数据库服务..."
        docker-compose up -d mysql elasticsearch minio redis
        echo "✅ 数据库服务已启动"
        ;;
    5)
        echo "停止所有服务..."
        docker-compose down
        echo "✅ 所有服务已停止"
        ;;
    6)
        echo "查看服务状态..."
        docker-compose ps
        ;;
    7)
        echo "查看服务日志..."
        docker-compose logs -f
        ;;
    8)
        echo "重新构建并启动..."
        docker-compose down
        docker-compose build --no-cache
        docker-compose up -d
        echo "✅ 服务已重新构建并启动"
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "=== 服务信息 ==="
echo "数据库名称: ragforge"
echo "MySQL密码: ragforge123"
echo "Redis密码: ragforge123"
echo "MinIO用户: minioadmin"
echo "MinIO密码: minioadmin"
echo ""
echo "使用 'docker-compose logs -f' 查看实时日志"
echo "使用 'docker-compose down' 停止所有服务" 