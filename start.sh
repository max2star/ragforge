#!/bin/bash

# RAGForge 服务器启动脚本
# 用于从源码启动RAGForge服务

set -e

echo "=== RAGForge 服务器启动脚本 ==="

# 检查是否在项目根目录
if [ ! -f "pyproject.toml" ]; then
    echo "❌ 错误: 请在RAGForge项目根目录下运行此脚本"
    exit 1
fi

# 检查虚拟环境是否存在
if [ ! -d ".venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行: uv sync --python 3.10"
    exit 1
fi

# 设置环境变量
export PYTHONPATH=$(pwd)
echo "✅ 设置PYTHONPATH: $PYTHONPATH"

# 激活虚拟环境
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi

echo "✅ 虚拟环境已激活"

# 检查服务器脚本是否存在
if [ ! -f "api/ragforge_server.py" ]; then
    echo "❌ 服务器脚本不存在: api/ragforge_server.py"
    exit 1
fi

echo "🚀 启动RAGForge服务器..."
echo "📝 提示: 确保已启动数据库服务 (MySQL, Redis, Elasticsearch, MinIO)"
echo "🌐 服务启动后访问: http://localhost:9380"
echo "📚 API文档: http://localhost:9380/apidocs/"
echo "=" * 50

# 启动服务器
python api/ragforge_server.py 