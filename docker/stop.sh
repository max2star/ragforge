#!/bin/bash

# RAGForge 服务停止脚本

set -e

echo "=== RAGForge 服务停止脚本 ==="
echo "1. 停止所有服务"
echo "2. 停止并删除所有容器"
echo "3. 停止并删除所有容器和卷"
echo "4. 停止并删除所有容器、卷和镜像"
echo "5. 仅停止后端服务"
echo "6. 仅停止数据库服务"
echo "7. 查看服务状态"
echo ""

read -p "请选择操作 (1-7): " choice

case $choice in
    1)
        echo "停止所有服务..."
        # 先停止所有profiles的服务
        docker-compose --profile dev down
        # 再停止默认服务
        docker-compose down
        echo "✅ 所有服务已停止"
        ;;
    2)
        echo "停止并删除所有容器..."
        # 先停止所有profiles的服务并移除孤儿容器
        docker-compose --profile dev down --remove-orphans
        # 再停止默认服务并移除孤儿容器
        docker-compose down --remove-orphans
        echo "✅ 所有容器已停止并删除"
        ;;
    3)
        echo "停止并删除所有容器和卷..."
        read -p "⚠️  这将删除所有数据，确定继续吗？(y/N): " confirm
        if [[ $confirm =~ ^[Yy]$ ]]; then
            # 先停止所有profiles的服务并删除卷
            docker-compose --profile dev down -v --remove-orphans
            # 再停止默认服务并删除卷
            docker-compose down -v --remove-orphans
            echo "✅ 所有容器和卷已删除"
        else
            echo "❌ 操作已取消"
        fi
        ;;
    4)
        echo "停止并删除所有容器、卷和镜像..."
        read -p "⚠️  这将删除所有数据、卷和镜像，确定继续吗？(y/N): " confirm
        if [[ $confirm =~ ^[Yy]$ ]]; then
            # 先停止所有profiles的服务并删除卷
            docker-compose --profile dev down -v --remove-orphans
            # 再停止默认服务并删除卷
            docker-compose down -v --remove-orphans
            # 删除所有相关镜像
            docker-compose down --rmi all
            echo "✅ 所有容器、卷和镜像已删除"
        else
            echo "❌ 操作已取消"
        fi
        ;;
    5)
        echo "仅停止后端服务..."
        docker-compose stop ragforge
        echo "✅ 后端服务已停止"
        ;;
    6)
        echo "仅停止数据库服务..."
        docker-compose stop mysql elasticsearch minio redis
        echo "✅ 数据库服务已停止"
        ;;
    7)
        echo "查看服务状态..."
        docker-compose ps
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "=== 服务状态 ==="
docker-compose ps

echo ""
echo "使用 'docker-compose logs -f' 查看实时日志"
echo "使用 './start.sh' 重新启动服务" 