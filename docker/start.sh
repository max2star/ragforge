#!/bin/bash

# RAGForge Docker 快速启动脚本
# 使用方法: ./start.sh [选项]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助信息
show_help() {
    echo "RAGForge Docker 快速启动脚本"
    echo ""
    echo "使用方法:"
    echo "  $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help              显示此帮助信息"
    echo "  -b, --build             构建 Docker 镜像"
    echo "  -u, --up                启动所有服务"
    echo "  -d, --down              停止所有服务"
    echo "  -r, --restart           重启所有服务"
    echo "  -l, --logs              查看服务日志"
    echo "  -c, --clean             清理所有容器和卷"
    echo "  -f, --full              完整部署 (构建 + 启动)"
    echo ""
    echo "示例:"
    echo "  $0 -f                   完整部署"
    echo "  $0 -u                   仅启动服务"
    echo "  $0 -l                   查看日志"
    echo "  $0 -d                   停止服务"
}

# 检查 Docker 是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
}

# 构建镜像
build_image() {
    print_info "构建 RAGForge Docker 镜像..."
    cd ..
    docker build -f Dockerfile.simple -t ragforge-simple:latest .
    cd docker
    print_success "镜像构建完成"
}

# 启动服务
start_services() {
    print_info "启动 RAGForge 服务..."
    docker-compose up -d
    print_success "服务启动完成"
    
    print_info "等待服务启动..."
    sleep 10
    
    # 检查服务状态
    check_services_status
}

# 停止服务
stop_services() {
    print_info "停止 RAGForge 服务..."
    docker-compose down
    print_success "服务已停止"
}

# 重启服务
restart_services() {
    print_info "重启 RAGForge 服务..."
    docker-compose restart
    print_success "服务重启完成"
}

# 查看日志
show_logs() {
    print_info "显示服务日志..."
    docker-compose logs -f
}

# 清理所有容器和卷
clean_all() {
    print_warning "这将删除所有容器、网络和卷，数据将丢失！"
    read -p "确定要继续吗？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "清理所有容器和卷..."
        docker-compose down -v --remove-orphans
        docker system prune -f
        print_success "清理完成"
    else
        print_info "取消清理操作"
    fi
}

# 检查服务状态
check_services_status() {
    print_info "检查服务状态..."
    
    # 检查 MySQL
    if docker-compose ps mysql | grep -q "Up"; then
        print_success "MySQL: 运行中"
    else
        print_error "MySQL: 未运行"
    fi
    
    # 检查 Elasticsearch
    if docker-compose ps elasticsearch | grep -q "Up"; then
        print_success "Elasticsearch: 运行中"
    else
        print_error "Elasticsearch: 未运行"
    fi
    
    # 检查 MinIO
    if docker-compose ps minio | grep -q "Up"; then
        print_success "MinIO: 运行中"
    else
        print_error "MinIO: 未运行"
    fi
    
    # 检查 Redis
    if docker-compose ps redis | grep -q "Up"; then
        print_success "Redis: 运行中"
    else
        print_error "Redis: 未运行"
    fi
    
    # 检查 RAGForge
    if docker-compose ps ragforge | grep -q "Up"; then
        print_success "RAGForge: 运行中"
    else
        print_error "RAGForge: 未运行"
    fi
    
    echo ""
    print_info "服务访问地址："
    echo "  - RAGForge API: http://localhost:9380"
    echo "  - MySQL: localhost:3306"
    echo "  - Elasticsearch: http://localhost:9200"
    echo "  - MinIO: http://localhost:9000"
    echo "  - MinIO Console: http://localhost:9001"
    echo "  - Redis: localhost:6379"
    echo ""
    print_info "默认凭据："
    echo "  - MySQL: root/ragforge123"
    echo "  - MinIO: minioadmin/minioadmin"
    echo "  - Redis: ragforge123"
    echo "  - Elasticsearch: elastic/(无密码)"
}

# 完整部署
full_deploy() {
    print_info "开始完整部署..."
    build_image
    start_services
}

# 主函数
main() {
    # 检查是否在正确的目录
    if [ ! -f "docker-compose.yml" ]; then
        print_error "请在 docker 目录下运行此脚本"
        exit 1
    fi
    
    # 检查 Docker
    check_docker
    
    # 如果没有参数，显示帮助
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi
    
    # 处理参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -b|--build)
                build_image
                ;;
            -u|--up)
                start_services
                ;;
            -d|--down)
                stop_services
                ;;
            -r|--restart)
                restart_services
                ;;
            -l|--logs)
                show_logs
                ;;
            -c|--clean)
                clean_all
                ;;
            -f|--full)
                full_deploy
                ;;
            *)
                print_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
        shift
    done
}

# 运行主函数
main "$@" 