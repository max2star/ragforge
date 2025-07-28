#!/bin/bash

# RAGForge 子模块初始化脚本
# 用于初始化所有Git子模块

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

print_header() {
    echo -e "${BLUE}==================================================${NC}"
    echo -e "${BLUE}🔄 RAGForge 子模块初始化脚本${NC}"
    echo -e "${BLUE}==================================================${NC}"
}

# 检查Git
check_git() {
    if ! command -v git &> /dev/null; then
        print_error "❌ Git 未安装，请先安装 Git"
        exit 1
    fi
    print_success "✅ Git 已安装"
}

# 检查是否在Git仓库中
check_git_repo() {
    if [ ! -d ".git" ]; then
        print_error "❌ 当前目录不是Git仓库"
        print_info "请先克隆RAGForge仓库"
        exit 1
    fi
    print_success "✅ 当前目录是Git仓库"
}

# 显示子模块状态
show_submodules() {
    print_info "📋 当前子模块状态:"
    git submodule status
}

# 初始化子模块
init_submodules() {
    print_info "🔄 初始化Git子模块..."
    
    # 更新子模块
    git submodule update --init --recursive
    
    print_success "✅ 子模块初始化完成"
}

# 检查子模块内容
check_submodules() {
    print_info "🔍 检查子模块内容..."
    
    # 检查web目录
    if [ -d "web" ] && [ "$(ls -A web)" ]; then
        print_success "✅ web 子模块已初始化"
        echo "   - 文件数量: $(find web -type f | wc -l)"
        echo "   - 目录大小: $(du -sh web | cut -f1)"
    else
        print_warning "⚠️  web 子模块可能未正确初始化"
    fi
    
    # 检查docs目录
    if [ -d "docs" ] && [ "$(ls -A docs)" ]; then
        print_success "✅ docs 子模块已初始化"
    else
        print_warning "⚠️  docs 子模块可能未正确初始化"
    fi
    
    # 检查ragforge-shell目录
    if [ -d "ragforge-shell" ] && [ "$(ls -A ragforge-shell)" ]; then
        print_success "✅ ragforge-shell 子模块已初始化"
    else
        print_warning "⚠️  ragforge-shell 子模块可能未正确初始化"
    fi
}

# 显示使用说明
show_usage() {
    echo ""
    print_info "📖 使用说明:"
    echo "  1. 确保在RAGForge项目根目录下运行此脚本"
    echo "  2. 脚本会自动初始化所有Git子模块"
    echo "  3. 初始化完成后可以正常使用RAGForge"
    echo ""
    print_info "📁 子模块位置:"
    echo "  - web/: 前端Web界面"
    echo "  - docs/: 文档"
    echo "  - ragforge-shell/: 命令行工具"
    echo ""
}

# 主函数
main() {
    print_header
    
    # 检查Git
    check_git
    
    # 检查Git仓库
    check_git_repo
    
    # 显示子模块状态
    show_submodules
    
    # 初始化子模块
    init_submodules
    
    # 检查子模块内容
    check_submodules
    
    # 显示使用说明
    show_usage
    
    print_success "🎉 子模块初始化完成！"
}

# 如果脚本被直接执行，运行主函数
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 