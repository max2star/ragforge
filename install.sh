#!/bin/bash

# RAGForge 一键安装脚本
# 使用方法: curl -fsSL https://raw.githubusercontent.com/zhaozhilong1993/ragforge/main/install.sh | bash

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
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

print_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

print_header() {
    echo -e "${CYAN}==================================================${NC}"
    echo -e "${CYAN}🚀 RAGForge 一键安装脚本${NC}"
    echo -e "${CYAN}==================================================${NC}"
}

# 检查系统要求
check_requirements() {
    print_step "检查系统要求..."
    
    # 检查操作系统
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        print_success "✅ 操作系统: Linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        print_success "✅ 操作系统: macOS"
    else
        print_warning "⚠️  操作系统: $OSTYPE (可能不完全支持)"
    fi
    
    # 检查Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "✅ Python版本: $PYTHON_VERSION"
    else
        print_error "❌ Python3 未安装"
        print_info "请先安装 Python 3.10+: https://python.org"
        exit 1
    fi
    
    # 检查Docker
    if command -v docker &> /dev/null; then
        print_success "✅ Docker 已安装"
    else
        print_error "❌ Docker 未安装"
        print_info "请先安装 Docker: https://docker.com"
        exit 1
    fi
    
    # 检查Docker Compose
    if command -v docker-compose &> /dev/null; then
        print_success "✅ Docker Compose 已安装"
    else
        print_error "❌ Docker Compose 未安装"
        print_info "请先安装 Docker Compose"
        exit 1
    fi
    
    # 检查Git
    if command -v git &> /dev/null; then
        print_success "✅ Git 已安装"
    else
        print_error "❌ Git 未安装"
        print_info "请先安装 Git"
        exit 1
    fi
}

# 创建项目目录
setup_project() {
    print_step "设置项目目录..."
    
    PROJECT_DIR="$HOME/ragforge"
    
    if [ -d "$PROJECT_DIR" ]; then
        print_warning "⚠️  项目目录已存在: $PROJECT_DIR"
        read -p "是否删除现有目录并重新安装? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "删除现有目录..."
            rm -rf "$PROJECT_DIR"
        else
            print_info "使用现有目录"
            cd "$PROJECT_DIR"
            return
        fi
    fi
    
    mkdir -p "$PROJECT_DIR"
    cd "$PROJECT_DIR"
    print_success "✅ 项目目录: $PROJECT_DIR"
}

# 下载源码
download_source() {
    print_step "下载RAGForge源码..."
    
    if [ ! -d ".git" ]; then
        git clone https://github.com/zhaozhilong1993/ragforge.git .
        print_success "✅ 源码下载完成"
    else
        print_info "📦 源码已存在，跳过下载"
    fi
}

# 安装Python依赖
install_python_deps() {
    print_step "安装Python依赖..."
    
    # 检查uv
    if ! command -v uv &> /dev/null; then
        print_info "📦 安装 uv 包管理器..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        source ~/.cargo/env
        print_success "✅ uv 安装完成"
    fi
    
    # 安装依赖
    print_info "📦 安装Python依赖..."
    uv sync --python 3.10
    print_success "✅ Python依赖安装完成"
}

# 启动Docker服务
start_docker_services() {
    print_step "启动Docker服务..."
    
    cd docker
    
    if [ ! -f "docker-compose.yml" ]; then
        print_error "❌ docker-compose.yml 文件不存在"
        exit 1
    fi
    
    print_info "🐳 启动Docker容器..."
    docker-compose up -d
    
    print_info "⏳ 等待服务启动 (30秒)..."
    sleep 30
    
    print_info "📊 检查服务状态..."
    docker-compose ps
    
    print_success "✅ Docker服务启动完成"
}

# 启动RAGForge服务器
start_server() {
    print_step "启动RAGForge服务器..."
    
    cd ..
    
    # 设置环境变量
    export PYTHONPATH=$(pwd)
    
    # 激活虚拟环境
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source .venv/Scripts/activate
    else
        source .venv/bin/activate
    fi
    
    print_success "✅ 虚拟环境已激活"
    
    echo ""
    print_info "🚀 启动RAGForge服务器..."
    print_info "📝 提示: Docker服务已启动"
    print_info "🌐 服务启动后访问: http://localhost:9380"
    print_info "📚 API文档: http://localhost:9380/apidocs/"
    print_info "🛑 按 Ctrl+C 停止服务器"
    echo ""
    echo -e "${CYAN}==================================================${NC}"
    
    # 启动服务器
    python api/ragforge_server.py
}

# 显示使用说明
show_usage() {
    echo ""
    print_info "📖 使用说明:"
    echo "  1. 访问 Web 界面: http://localhost:9380"
    echo "  2. 查看 API 文档: http://localhost:9380/apidocs/"
    echo "  3. 停止服务器: 按 Ctrl+C"
    echo "  4. 重新启动: cd ~/ragforge && ./start.sh"
    echo ""
    print_info "📁 项目位置: $HOME/ragforge"
    print_info "🐳 Docker服务: cd ~/ragforge/docker && docker-compose up -d"
    echo ""
}

# 主函数
main() {
    print_header
    
    # 检查系统要求
    check_requirements
    
    # 设置项目
    setup_project
    
    # 下载源码
    download_source
    
    # 安装依赖
    install_python_deps
    
    # 启动Docker服务
    start_docker_services
    
    # 显示使用说明
    show_usage
    
    # 启动服务器
    start_server
}

# 如果脚本被直接执行，运行主函数
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 