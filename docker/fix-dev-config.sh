#!/bin/bash

# RAGForge 开发环境配置修复脚本
# 用于快速修复常见的配置问题

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    local status=$1
    local message=$2
    case $status in
        "OK")
            echo -e "${GREEN}✓ $message${NC}"
            ;;
        "ERROR")
            echo -e "${RED}✗ $message${NC}"
            ;;
        "WARNING")
            echo -e "${YELLOW}⚠ $message${NC}"
            ;;
        "INFO")
            echo -e "${BLUE}ℹ $message${NC}"
            ;;
    esac
}

echo "=========================================="
echo "RAGForge 开发环境配置修复脚本"
echo "=========================================="
echo

# 1. 检查并修复环境变量文件
echo "1. 检查并修复环境变量配置..."
if [ -f ".env" ]; then
    # 修复MYSQL_HOST
    if grep -q "MYSQL_HOST=mysql-ragforge" .env; then
        sed -i '' 's/MYSQL_HOST=mysql-ragforge/MYSQL_HOST=ragforge-mysql-dev/' .env
        print_status "OK" "已修复 MYSQL_HOST 配置"
    fi
    
    # 检查STACK_VERSION
    if grep -q "STACK_VERSION=8.11.3" .env; then
        print_status "OK" "Elasticsearch版本配置正确"
    else
        sed -i '' 's/STACK_VERSION=.*/STACK_VERSION=8.11.3/' .env
        print_status "OK" "已修复 Elasticsearch版本配置"
    fi
else
    print_status "ERROR" ".env 文件不存在"
    exit 1
fi
echo

# 2. 检查并修复主配置文件
echo "2. 检查并修复主配置文件..."
CONFIG_FILE="../conf/service_conf.yaml"
if [ -f "$CONFIG_FILE" ]; then
    # 备份原文件
    cp "$CONFIG_FILE" "$CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    print_status "INFO" "已备份原配置文件"
    
    # 修复MySQL密码
    sed -i '' "s/password: 'ragforge123'/password: 'infini_rag_flow'/" "$CONFIG_FILE"
    print_status "OK" "已修复 MySQL 密码配置"
    
    # 修复Elasticsearch端口
    sed -i '' "s/hosts: 'http:\/\/localhost:9200'/hosts: 'http:\/\/localhost:1200'/" "$CONFIG_FILE"
    print_status "OK" "已修复 Elasticsearch 端口配置"
    
    # 修复Redis密码
    sed -i '' "s/password: 'ragforge123'/password: 'infini_rag_flow'/" "$CONFIG_FILE"
    print_status "OK" "已修复 Redis 密码配置"
    
    # 修复MySQL端口
    sed -i '' "s/port: 3306/port: 5455/" "$CONFIG_FILE"
    print_status "OK" "已修复 MySQL 端口配置"
else
    print_status "ERROR" "主配置文件不存在: $CONFIG_FILE"
    exit 1
fi
echo

# 3. 重启服务
echo "3. 重启服务..."
print_status "INFO" "停止所有服务..."
docker-compose -f docker-compose-dev.yml down

print_status "INFO" "启动所有服务..."
docker-compose -f docker-compose-dev.yml up -d

print_status "INFO" "等待服务启动..."
sleep 30
echo

# 4. 验证修复结果
echo "4. 验证修复结果..."
print_status "INFO" "运行环境检查..."

# 检查MySQL连接
if docker exec ragforge-mysql-dev mysql -uroot -pinfini_rag_flow -e "SELECT 1;" >/dev/null 2>&1; then
    print_status "OK" "MySQL连接正常"
else
    print_status "ERROR" "MySQL连接失败"
fi

# 检查Redis连接
if docker exec ragforge-redis-dev redis-cli ping >/dev/null 2>&1; then
    print_status "OK" "Redis连接正常"
else
    print_status "ERROR" "Redis连接失败"
fi

# 检查Elasticsearch连接
if curl -s http://localhost:1200/_cluster/health >/dev/null 2>&1; then
    health=$(curl -s http://localhost:1200/_cluster/health | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    print_status "OK" "Elasticsearch连接正常 (状态: $health)"
else
    print_status "ERROR" "Elasticsearch连接失败"
fi

# 检查MinIO连接
if curl -s http://localhost:9001 >/dev/null 2>&1; then
    print_status "OK" "MinIO连接正常"
else
    print_status "WARNING" "MinIO连接失败"
fi
echo

# 5. 显示服务状态
echo "5. 当前服务状态..."
docker ps --filter "name=ragforge" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo

echo "=========================================="
echo "修复完成！"
echo "=========================================="
echo
echo "如果仍有问题，请检查:"
echo "1. 容器日志: docker logs <container_name>"
echo "2. 运行检查脚本: ./check-dev-env.sh"
echo "3. 手动重启服务: docker-compose -f docker-compose-dev.yml restart" 