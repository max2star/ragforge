# 检查Redis连接
echo "=== 检查Redis连接 ==="
if docker exec ragflow-redis-dev redis-cli -a infini_rag_flow ping 2>/dev/null | grep -q "PONG"; then
    echo "✅ Redis连接正常"
else
    echo "❌ Redis连接失败"
    echo "   尝试检查Redis容器状态..."
    docker ps | grep redis || echo "   未找到Redis容器"
fi

# 检查Redis配置
echo "=== 检查Redis配置 ==="
if [ -f ".env" ]; then
    echo "Redis配置:"
    grep -E "REDIS|redis" .env | grep -v "^#" || echo "   未找到Redis配置"
fi 