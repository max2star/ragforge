#!/bin/bash

# RAGForge 完整服务启动脚本

set -e

function check_port() {
  local port=$1
  if lsof -i :$port | grep LISTEN >/dev/null; then
    echo "❌ 端口 $port 已被占用，请关闭占用该端口的进程后重试。"
    lsof -i :$port | grep LISTEN
    exit 1
  fi
}

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
        # 只停止 ragforge 相关的容器，不影响其他项目
        docker-compose down
        check_port 80
        check_port 9380
        echo "启动所有服务（生产环境）..."
        if ! docker-compose up -d; then
          echo "❌ 启动失败。常见原因："
          echo "- 端口被占用"
          echo "- 残留容器或网络冲突"
          echo "建议执行：docker-compose down && docker container prune -f"
          exit 1
        fi
        echo "✅ 所有服务已启动"
        echo "🌐 Web控制台: http://localhost"
        echo "🔧 API服务: http://localhost:9380"
        echo "🗄️ MySQL: localhost:3306"
        echo "🔍 Elasticsearch: localhost:9200"
        echo "📦 MinIO: localhost:9000"
        echo "💾 Redis: localhost:6379"
        ;;
    2)
        # 只停止 ragforge 相关的容器，不影响其他项目
        docker-compose down
        check_port 3000
        check_port 9380
        echo "启动所有服务（开发环境）..."
        if ! docker-compose --profile dev up -d; then
          echo "❌ 启动失败。常见原因："
          echo "- 端口被占用"
          echo "- 残留容器或网络冲突"
          echo "建议执行：docker-compose down && docker container prune -f"
          exit 1
        fi
        echo "✅ 所有服务已启动（开发模式）"
        echo "🌐 Web控制台: http://localhost:3000"
        echo "🔧 API服务: http://localhost:9380"
        ;;
    3)
        # 只停止 ragforge 相关的容器，不影响其他项目
        docker-compose down
        check_port 9380
        echo "仅启动后端服务..."
        if ! docker-compose up -d ragforge-ragforge ragforge-mysql ragforge-elasticsearch ragforge-minio ragforge-redis; then
          echo "❌ 启动失败。常见原因："
          echo "- 端口被占用"
          echo "- 残留容器或网络冲突"
          echo "建议执行：docker-compose down && docker container prune -f"
          exit 1
        fi
        echo "✅ 后端服务已启动"
        echo "🔧 API服务: http://localhost:9380"
        ;;
    4)
        # 只停止 ragforge 相关的容器，不影响其他项目
        docker-compose down
        echo "仅启动数据库服务..."
        if ! docker-compose up -d ragforge-mysql ragforge-elasticsearch ragforge-minio ragforge-redis; then
          echo "❌ 启动失败。常见原因："
          echo "- 端口被占用"
          echo "- 残留容器或网络冲突"
          echo "建议执行：docker-compose down && docker container prune -f"
          exit 1
        fi
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
        # 只停止 ragforge 相关的容器，不影响其他项目
        docker-compose down
        echo "重新构建并启动..."
        if ! docker-compose build --no-cache; then
          echo "❌ 构建失败，请检查Dockerfile和依赖。"
          exit 1
        fi
        if ! docker-compose up -d; then
          echo "❌ 启动失败。常见原因："
          echo "- 端口被占用"
          echo "- 残留容器或网络冲突"
          echo "建议执行：docker-compose down && docker container prune -f"
          exit 1
        fi
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
echo "常见问题排查："
echo "- 如果遇到端口占用，请关闭相关进程后重试。"
echo "- 如果遇到容器/网络冲突或not connected to the network错误，请执行："
echo "    docker-compose down --remove-orphans && docker container prune -f && docker network prune -f"
echo "- 使用 'docker-compose logs -f' 查看实时日志"
echo "- 使用 'docker-compose down' 停止所有服务" 