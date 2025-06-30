#!/bin/bash

# RAGFlow 开发环境检查脚本
# 用于检查所有服务的状态和连接性

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
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
echo "RAGFlow 开发环境检查脚本"
echo "=========================================="
echo

# 1. 检查Docker是否运行
echo "1. 检查Docker服务状态..."
if docker info >/dev/null 2>&1; then
    print_status "OK" "Docker服务运行正常"
else
    print_status "ERROR" "Docker服务未运行或无法访问"
    exit 1
fi
echo

# 2. 检查Docker Compose文件
echo "2. 检查Docker Compose配置..."
if [ -f "docker-compose-dev.yml" ]; then
    print_status "OK" "docker-compose-dev.yml 文件存在"
else
    print_status "ERROR" "docker-compose-dev.yml 文件不存在"
    exit 1
fi

if [ -f ".env" ]; then
    print_status "OK" ".env 环境变量文件存在"
else
    print_status "WARNING" ".env 环境变量文件不存在"
fi
echo

# 3. 检查容器状态
echo "3. 检查容器状态..."
containers=("ragflow-mysql-dev" "ragflow-redis-dev" "ragflow-es-dev" "ragflow-minio-dev")

for container in "${containers[@]}"; do
    if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -q "$container"; then
        status=$(docker ps --format "table {{.Names}}\t{{.Status}}" | grep "$container" | awk '{print $2}')
        if [[ $status == *"healthy"* ]]; then
            print_status "OK" "$container: 运行正常 (健康)"
        elif [[ $status == *"Up"* ]]; then
            print_status "WARNING" "$container: 运行中 (健康检查中)"
        else
            print_status "ERROR" "$container: 状态异常 - $status"
        fi
    else
        print_status "ERROR" "$container: 容器未运行"
    fi
done
echo

# 4. 检查端口连接
echo "4. 检查端口连接..."
ports=(
    "5455:MySQL"
    "16379:Redis"
    "1200:Elasticsearch"
    "19000:MinIO"
    "19001:MinIO Console"
)

for port_info in "${ports[@]}"; do
    port=$(echo $port_info | cut -d: -f1)
    service=$(echo $port_info | cut -d: -f2)
    
    if nc -z localhost $port 2>/dev/null; then
        print_status "OK" "$service (端口 $port): 可连接"
    else
        print_status "ERROR" "$service (端口 $port): 无法连接"
    fi
done
echo

# 5. 检查数据库连接
echo "5. 检查数据库连接..."
if docker exec ragflow-mysql-dev mysql -uroot -pinfini_rag_flow -e "SELECT 1;" >/dev/null 2>&1; then
    print_status "OK" "MySQL数据库连接正常"
else
    print_status "ERROR" "MySQL数据库连接失败"
fi
echo

# 6. 检查Redis连接
echo "6. 检查Redis连接..."
if docker exec ragflow-redis-dev redis-cli ping >/dev/null 2>&1; then
    print_status "OK" "Redis连接正常"
else
    print_status "ERROR" "Redis连接失败"
fi
echo

# 7. 检查Elasticsearch连接
echo "7. 检查Elasticsearch连接..."
if curl -s http://localhost:1200/_cluster/health >/dev/null 2>&1; then
    health=$(curl -s http://localhost:1200/_cluster/health | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    if [ "$health" = "green" ] || [ "$health" = "yellow" ]; then
        print_status "OK" "Elasticsearch连接正常 (状态: $health)"
    else
        print_status "WARNING" "Elasticsearch连接正常但状态异常 (状态: $health)"
    fi
else
    print_status "ERROR" "Elasticsearch连接失败"
fi
echo

# 8. 检查MinIO连接
echo "8. 检查MinIO连接..."
if curl -s http://localhost:19001 >/dev/null 2>&1; then
    print_status "OK" "MinIO Console连接正常"
else
    print_status "WARNING" "MinIO Console连接失败"
fi
echo

# 9. 检查网络配置
echo "9. 检查Docker网络..."
if docker network ls | grep -q "docker_ragflow"; then
    print_status "OK" "ragflow网络存在"
    network_info=$(docker network inspect docker_ragflow --format '{{.IPAM.Config}}')
    print_status "INFO" "网络配置: $network_info"
else
    print_status "ERROR" "ragflow网络不存在"
fi
echo

# 10. 检查配置文件
echo "10. 检查配置文件..."
config_files=(
    "../conf/service_conf.yaml"
    "service_conf.yaml.template"
    ".env"
)

for config_file in "${config_files[@]}"; do
    if [ -f "$config_file" ]; then
        print_status "OK" "$config_file 存在"
    else
        print_status "WARNING" "$config_file 不存在"
    fi
done
echo

# 11. 检查环境变量
echo "11. 检查关键环境变量..."
if [ -f ".env" ]; then
    source .env
    vars=("MYSQL_PASSWORD" "MYSQL_HOST" "STACK_VERSION" "REDIS_PASSWORD")
    for var in "${vars[@]}"; do
        if [ -n "${!var}" ]; then
            print_status "OK" "$var: 已设置"
        else
            print_status "WARNING" "$var: 未设置"
        fi
    done
fi
echo

# 12. 检查服务版本兼容性
echo "12. 检查服务版本兼容性..."
mysql_version=$(docker exec ragflow-mysql-dev mysql --version | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+')
es_version=$(docker exec ragflow-es-dev elasticsearch --version | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+')

print_status "INFO" "MySQL版本: $mysql_version"
print_status "INFO" "Elasticsearch版本: $es_version"

# 检查版本兼容性
if [[ "$es_version" == "8.11.3" ]]; then
    print_status "OK" "Elasticsearch版本正确 (8.11.3)"
else
    print_status "WARNING" "Elasticsearch版本可能不匹配 (当前: $es_version, 期望: 8.11.3)"
fi
echo

# 13. 检查后端API配置
echo "13. 检查后端API配置..."
API_CONFIG_FILE="../conf/service_conf.yaml"
if [ -f "$API_CONFIG_FILE" ]; then
    print_status "OK" "后端API配置文件存在"
    
    # 检查MySQL配置
    mysql_host=$(grep -A 5 "mysql:" "$API_CONFIG_FILE" | grep "host:" | awk '{print $2}' | tr -d "'")
    mysql_port=$(grep -A 5 "mysql:" "$API_CONFIG_FILE" | grep "port:" | awk '{print $2}')
    mysql_user=$(grep -A 5 "mysql:" "$API_CONFIG_FILE" | grep "user:" | awk '{print $2}' | tr -d "'")
    mysql_password=$(grep -A 5 "mysql:" "$API_CONFIG_FILE" | grep "password:" | awk '{print $2}' | tr -d "'")
    
    print_status "INFO" "MySQL配置: host=$mysql_host, port=$mysql_port, user=$mysql_user"
    
    # 验证MySQL配置
    if [ "$mysql_host" = "localhost" ] && [ "$mysql_port" = "5455" ]; then
        print_status "OK" "MySQL端口配置正确 (5455)"
    else
        print_status "ERROR" "MySQL端口配置错误 (当前: $mysql_port, 期望: 5455)"
    fi
    
    if [ "$mysql_user" = "root" ]; then
        print_status "OK" "MySQL用户名配置正确"
    else
        print_status "ERROR" "MySQL用户名配置错误 (当前: $mysql_user, 期望: root)"
    fi
    
    if [ "$mysql_password" = "infini_rag_flow" ]; then
        print_status "OK" "MySQL密码配置正确"
    else
        print_status "ERROR" "MySQL密码配置错误 (当前: $mysql_password, 期望: infini_rag_flow)"
    fi
    
    # 检查Redis配置
    redis_host=$(grep -A 4 "redis:" "$API_CONFIG_FILE" | grep "host:" | awk '{print $2}' | tr -d "'")
    redis_password=$(grep -A 4 "redis:" "$API_CONFIG_FILE" | grep "password:" | awk '{print $2}' | tr -d "'")
    redis_port=$(grep -A 4 "redis:" "$API_CONFIG_FILE" | grep "port:" | awk '{print $2}')
    
    print_status "INFO" "Redis配置: host=$redis_host, port=$redis_port"
    
    if [ "$redis_host" = "localhost" ] && [ "$redis_port" = "16379" ]; then
        print_status "OK" "Redis配置正确"
    else
        print_status "ERROR" "Redis配置错误 (当前: $redis_host:$redis_port, 期望: localhost:16379)"
    fi
    
    if [ "$redis_password" = "infini_rag_flow" ]; then
        print_status "OK" "Redis密码配置正确"
    else
        print_status "ERROR" "Redis密码配置错误 (当前: $redis_password, 期望: infini_rag_flow)"
    fi
    
    # 检查Elasticsearch配置
    es_hosts=$(grep -A 2 "es:" "$API_CONFIG_FILE" | grep "hosts:" | awk '{print $2}' | tr -d "'")
    
    print_status "INFO" "Elasticsearch配置: hosts=$es_hosts"
    
    if [ "$es_hosts" = "http://localhost:1200" ]; then
        print_status "OK" "Elasticsearch配置正确"
    else
        print_status "ERROR" "Elasticsearch配置错误 (当前: $es_hosts, 期望: http://localhost:1200)"
    fi
    
else
    print_status "ERROR" "后端API配置文件不存在: $API_CONFIG_FILE"
fi
echo

echo "=========================================="
echo "检查完成！"
echo "=========================================="

# 总结
echo
echo "服务状态总结:"
healthy_count=$(docker ps --filter "name=ragflow" --filter "health=healthy" --format "table {{.Names}}" | wc -l)
total_count=$(docker ps --filter "name=ragflow" --format "table {{.Names}}" | wc -l)

if [ $healthy_count -eq $total_count ]; then
    print_status "OK" "所有服务运行正常 ($healthy_count/$total_count)"
else
    print_status "WARNING" "部分服务可能有问题 ($healthy_count/$total_count 健康)"
fi

echo
echo "如果发现问题，请检查:"
echo "1. 容器日志: docker logs <container_name>"
echo "2. 网络连接: docker network inspect docker_ragflow"
echo "3. 配置文件: 检查 .env 和 service_conf.yaml"
echo "4. 重启服务: docker-compose -f docker-compose-dev.yml restart" 