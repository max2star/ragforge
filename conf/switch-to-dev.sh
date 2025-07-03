#!/bin/bash

# 切换到开发环境配置脚本
echo "切换到开发环境配置..."

# 备份原配置文件
if [ -f "service_conf.yaml" ]; then
    echo "备份原配置文件为 service_conf.yaml.backup"
    cp service_conf.yaml service_conf.yaml.backup
fi

# 复制开发环境配置
echo "应用开发环境配置..."
cp service_conf-dev.yaml service_conf.yaml

echo "配置切换完成！"
echo ""
echo "开发环境配置详情："
echo "- MySQL: localhost:3306 (root/ragforge123)"
echo "- Elasticsearch: http://localhost:9200 (elastic/changeme)"
echo "- MinIO: http://localhost:9000 (minioadmin/minioadmin)"
echo "- Redis: localhost:6379 (ragforge123)"
echo "- Infinity: localhost:23817 (如果使用完整模式)"
echo ""
echo "如需恢复原配置，请运行："
echo "cp service_conf.yaml.backup service_conf.yaml" 