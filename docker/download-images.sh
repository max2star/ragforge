#!/bin/bash

# Docker 镜像下载脚本
# 解决网络连接问题

set -e

echo "=== Docker 镜像下载脚本 ==="

# 定义镜像列表
IMAGES=(
    "mysql:8.0"
    "redis:7-alpine"
    "elasticsearch:8.11.0"
    "minio/minio:latest"
    "python:3.10-slim"
    "node:18"
    "nginx:alpine"
)

# 定义镜像加速器
MIRRORS=(
    "mirror.ccs.tencentyun.com"
    "registry.docker-cn.com"
    "docker.mirrors.ustc.edu.cn"
    "hub-mirror.c.163.com"
    "mirror.baidubce.com"
    "dockerproxy.com"
    "docker.m.daocloud.io"
)

echo "开始下载镜像..."

for image in "${IMAGES[@]}"; do
    echo "正在下载: $image"
    
    # 尝试不同的镜像源
    for mirror in "${MIRRORS[@]}"; do
        echo "尝试从 $mirror 下载..."
        if docker pull "$mirror/library/${image#*/}" 2>/dev/null; then
            echo "✅ 从 $mirror 下载成功: $image"
            # 重新标记镜像
            docker tag "$mirror/library/${image#*/}" "$image"
            break
        elif docker pull "$mirror/${image}" 2>/dev/null; then
            echo "✅ 从 $mirror 下载成功: $image"
            # 重新标记镜像
            docker tag "$mirror/${image}" "$image"
            break
        else
            echo "❌ 从 $mirror 下载失败"
        fi
    done
    
    # 如果所有镜像源都失败，尝试直接下载
    if ! docker images | grep -q "$image"; then
        echo "尝试直接下载: $image"
        if docker pull "$image"; then
            echo "✅ 直接下载成功: $image"
        else
            echo "❌ 所有下载方式都失败: $image"
        fi
    fi
done

echo ""
echo "=== 下载完成 ==="
echo "已下载的镜像:"
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" 