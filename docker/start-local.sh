#!/bin/bash

# RAGForge 本地开发启动脚本
# 避免 Docker 构建问题，使用本地 Python 环境

set -e

echo "=== RAGForge 本地开发启动脚本 ==="

# 检查数据库服务是否运行
echo "检查数据库服务状态..."
if ! docker-compose ps | grep -q "ragforge-mysql.*Up"; then
    echo "❌ MySQL 服务未运行，请先启动数据库服务"
    exit 1
fi

echo "✅ 数据库服务运行正常"

# 启动 API 服务（本地模式）
echo "🚀 启动 RAGForge API 服务（本地模式）..."
cd ..

# 检查 Python 环境
if ! command -v python &> /dev/null; then
    echo "❌ Python 未安装"
    exit 1
fi

# 设置环境变量
export RAGFORGE_MYSQL_HOST=localhost
export RAGFORGE_MYSQL_PORT=3306
export RAGFORGE_MYSQL_USER=ragforge
export RAGFORGE_MYSQL_PASSWORD=ragforge123
export RAGFORGE_MYSQL_DATABASE=ragforge
export RAGFORGE_REDIS_HOST=localhost
export RAGFORGE_REDIS_PORT=6379
export RAGFORGE_REDIS_PASSWORD=ragforge123
export RAGFORGE_ES_HOSTS=localhost:9200
export RAGFORGE_MINIO_HOST=localhost
export RAGFORGE_MINIO_PORT=9000
export RAGFORGE_MINIO_ACCESS_KEY=minioadmin
export RAGFORGE_MINIO_SECRET_KEY=minioadmin

# 启动 API 服务
echo "启动 API 服务..."
python -m api.ragforge_server &
API_PID=$!

# 等待 API 服务启动
sleep 10

# 启动 Web 服务（本地模式）
echo "🌐 启动 Web 服务（本地模式）..."
cd web

# 检查 Node.js 环境
if ! command -v npm &> /dev/null; then
    echo "❌ Node.js 未安装，请先安装 Node.js"
    kill $API_PID 2>/dev/null || true
    exit 1
fi

# 安装依赖
echo "安装 Web 依赖..."
npm install

# 启动开发服务器
echo "启动 Web 开发服务器..."
npm run dev &
WEB_PID=$!

echo ""
echo "✅ RAGForge 本地开发环境启动完成！"
echo ""
echo "=== 服务信息 ==="
echo "🌐 Web 界面: http://localhost:3000"
echo "🔧 API 服务: http://localhost:9380"
echo "🗄️  MySQL: localhost:3306"
echo "🔍 Elasticsearch: localhost:9200"
echo "📦 MinIO: localhost:9000"
echo "💾 Redis: localhost:6379"
echo ""
echo "按 Ctrl+C 停止服务"

# 等待用户中断
trap "echo '正在停止服务...'; kill $API_PID $WEB_PID 2>/dev/null || true; exit 0" INT

wait 