#!/bin/bash

# 开发环境停止脚本
echo "停止 RAGForge 开发环境..."

# 停止所有可能的开发环境配置
echo "停止完整模式服务..."
docker-compose -f docker-compose-dev.yml down 2>/dev/null || true

echo "停止简化模式服务..."
docker-compose -f docker-compose-dev-no-infinity.yml down 2>/dev/null || true

echo "开发环境已停止！" 