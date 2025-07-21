#!/bin/bash

# RAGForge 稳定构建脚本
# 解决网络连接问题，使用更稳定的构建方法

set -e

echo "=== RAGForge 稳定构建脚本 ==="

# 检查 Docker 是否运行
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker 未运行，请启动 Docker 后重试。"
    exit 1
fi

# 清理旧的构建缓存
echo "🧹 清理构建缓存..."
docker builder prune -f

# 设置构建参数
BUILD_ARGS=""
DOCKERFILE="Dockerfile"

# 检查是否使用稳定版本
if [ "$1" = "--stable" ]; then
    DOCKERFILE="Dockerfile.stable"
    echo "📦 使用稳定版本 Dockerfile"
fi

echo "🔨 开始构建镜像..."
echo "使用 Dockerfile: $DOCKERFILE"

# 构建镜像，使用多阶段构建和更好的网络配置
if docker build \
    --network=host \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    --build-arg DOCKER_BUILDKIT=1 \
    -f "$DOCKERFILE" \
    -t ragforge:latest \
    -t ragforge:stable \
    ..; then
    echo "✅ 构建成功！"
    echo ""
    echo "📋 镜像信息："
    docker images ragforge:latest
    echo ""
    echo "🚀 可以使用以下命令运行："
    echo "  docker run -p 9380:9380 ragforge:latest"
    echo ""
    echo "🔧 或者使用 Docker Compose："
    echo "  cd docker && ./start-isolated.sh"
else
    echo "❌ 构建失败！"
    echo ""
    echo "🔧 常见解决方案："
    echo "1. 检查网络连接"
    echo "2. 清理 Docker 缓存：docker system prune -a"
    echo "3. 使用稳定版本：./build-stable.sh --stable"
    echo "4. 检查磁盘空间"
    exit 1
fi 