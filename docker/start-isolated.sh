#!/bin/bash

# RAGForge 隔离环境启动脚本
# 使用 ragforge- 前缀的容器名称，避免与其他项目冲突

set -e

# 设置项目名称前缀
PROJECT_PREFIX="ragforge"
COMPOSE_PROJECT_NAME="ragforge"

function check_port() {
  local port=$1
  if lsof -i :$port | grep LISTEN >/dev/null; then
    echo "❌ 端口 $port 已被占用，请关闭占用该端口的进程后重试。"
    lsof -i :$port | grep LISTEN
    exit 1
  fi
}

function check_docker_running() {
  if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker 未运行，请启动 Docker 后重试。"
    exit 1
  fi
}

function cleanup_orphans() {
  echo "🧹 清理孤立的容器和网络..."
  docker-compose -p $COMPOSE_PROJECT_NAME down --remove-orphans 2>/dev/null || true
  docker network prune -f 2>/dev/null || true
}

echo "=== RAGForge 隔离环境启动脚本 ==="
echo "使用项目前缀: $PROJECT_PREFIX"
echo "Docker Compose 项目名: $COMPOSE_PROJECT_NAME"
echo ""
echo "1. 启动所有服务（生产环境）"
echo "2. 启动所有服务（开发环境）"
echo "3. 仅启动后端服务"
echo "4. 仅启动数据库服务"
echo "5. 停止所有服务"
echo "6. 查看服务状态"
echo "7. 查看服务日志"
echo "8. 重新构建并启动"
echo "9. 清理所有 ragforge 相关容器"
echo ""

read -p "请选择操作 (1-9): " choice

# 检查 Docker 是否运行
check_docker_running

case $choice in
    1)
        cleanup_orphans
        check_port 80
        check_port 9380
        echo "🚀 启动所有服务（生产环境）..."
        if ! docker-compose -p $COMPOSE_PROJECT_NAME up -d; then
          echo "❌ 启动失败。常见原因："
          echo "- 端口被占用"
          echo "- 残留容器或网络冲突"
          echo "建议执行：docker-compose -p $COMPOSE_PROJECT_NAME down --remove-orphans && docker container prune -f && docker network prune -f"
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
        cleanup_orphans
        check_port 3000
        check_port 9380
        echo "🚀 启动所有服务（开发环境）..."
        if ! docker-compose -p $COMPOSE_PROJECT_NAME --profile dev up -d; then
          echo "❌ 启动失败。常见原因："
          echo "- 端口被占用"
          echo "- 残留容器或网络冲突"
          echo "建议执行：docker-compose -p $COMPOSE_PROJECT_NAME down --remove-orphans && docker container prune -f && docker network prune -f"
          exit 1
        fi
        echo "✅ 所有服务已启动（开发模式）"
        echo "🌐 Web控制台: http://localhost:3000"
        echo "🔧 API服务: http://localhost:9380"
        ;;
    3)
        cleanup_orphans
        check_port 9380
        echo "🔧 仅启动后端服务..."
        if ! docker-compose -p $COMPOSE_PROJECT_NAME up -d ragforge-ragforge ragforge-mysql ragforge-elasticsearch ragforge-minio ragforge-redis; then
          echo "❌ 启动失败。常见原因："
          echo "- 端口被占用"
          echo "- 残留容器或网络冲突"
          echo "建议执行：docker-compose -p $COMPOSE_PROJECT_NAME down --remove-orphans && docker container prune -f && docker network prune -f"
          exit 1
        fi
        echo "✅ 后端服务已启动"
        echo "🔧 API服务: http://localhost:9380"
        ;;
    4)
        cleanup_orphans
        echo "🗄️ 仅启动数据库服务..."
        if ! docker-compose -p $COMPOSE_PROJECT_NAME up -d ragforge-mysql ragforge-elasticsearch ragforge-minio ragforge-redis; then
          echo "❌ 启动失败。常见原因："
          echo "- 端口被占用"
          echo "- 残留容器或网络冲突"
          echo "建议执行：docker-compose -p $COMPOSE_PROJECT_NAME down --remove-orphans && docker container prune -f && docker network prune -f"
          exit 1
        fi
        echo "✅ 数据库服务已启动"
        ;;
    5)
        echo "🛑 停止所有服务..."
        docker-compose -p $COMPOSE_PROJECT_NAME down
        echo "✅ 所有服务已停止"
        ;;
    6)
        echo "📊 查看服务状态..."
        docker-compose -p $COMPOSE_PROJECT_NAME ps
        ;;
    7)
        echo "📋 查看服务日志..."
        docker-compose -p $COMPOSE_PROJECT_NAME logs -f
        ;;
    8)
        cleanup_orphans
        echo "🔨 重新构建并启动..."
        docker-compose -p $COMPOSE_PROJECT_NAME down
        if ! docker-compose -p $COMPOSE_PROJECT_NAME build --no-cache; then
          echo "❌ 构建失败，请检查Dockerfile和依赖。"
          exit 1
        fi
        if ! docker-compose -p $COMPOSE_PROJECT_NAME up -d; then
          echo "❌ 启动失败。常见原因："
          echo "- 端口被占用"
          echo "- 残留容器或网络冲突"
          echo "建议执行：docker-compose -p $COMPOSE_PROJECT_NAME down --remove-orphans && docker container prune -f && docker network prune -f"
          exit 1
        fi
        echo "✅ 服务已重新构建并启动"
        ;;
    9)
        echo "🧹 清理所有 ragforge 相关容器..."
        echo "⚠️  这将停止并删除所有 ragforge 相关的容器、网络和卷"
        read -p "确认继续？(y/N): " confirm
        if [[ $confirm =~ ^[Yy]$ ]]; then
          docker-compose -p $COMPOSE_PROJECT_NAME down -v --remove-orphans
          docker container prune -f
          docker network prune -f
          docker volume prune -f
          echo "✅ 清理完成"
        else
          echo "❌ 操作已取消"
        fi
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "=== 服务信息 ==="
echo "项目前缀: $PROJECT_PREFIX"
echo "Docker Compose 项目名: $COMPOSE_PROJECT_NAME"
echo "数据库名称: ragforge"
echo "MySQL密码: ragforge123"
echo "Redis密码: ragforge123"
echo "MinIO用户: minioadmin"
echo "MinIO密码: minioadmin"
echo ""
echo "🔍 查看容器状态："
echo "  docker-compose -p $COMPOSE_PROJECT_NAME ps"
echo ""
echo "📋 查看日志："
echo "  docker-compose -p $COMPOSE_PROJECT_NAME logs -f"
echo ""
echo "🛑 停止服务："
echo "  docker-compose -p $COMPOSE_PROJECT_NAME down"
echo ""
echo "🧹 清理所有资源："
echo "  docker-compose -p $COMPOSE_PROJECT_NAME down -v --remove-orphans"
echo ""
echo "常见问题排查："
echo "- 如果遇到端口占用，请关闭相关进程后重试。"
echo "- 如果遇到容器/网络冲突，请执行选项 9 进行清理。"
echo "- 使用 'docker-compose -p $COMPOSE_PROJECT_NAME logs -f' 查看实时日志" 