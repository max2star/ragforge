#!/bin/bash

# RAGForge 安装测试脚本
# 用于测试安装功能是否正常工作

echo "🚀 RAGForge 安装测试脚本"
echo "=================================================="

# 检查系统要求
echo "✅ 检查系统要求..."

# 检查Python
if command -v python3 &> /dev/null; then
    echo "✅ Python3 已安装"
else
    echo "❌ Python3 未安装"
    exit 1
fi

# 检查Docker
if command -v docker &> /dev/null; then
    echo "✅ Docker 已安装"
else
    echo "❌ Docker 未安装"
    exit 1
fi

# 检查Git
if command -v git &> /dev/null; then
    echo "✅ Git 已安装"
else
    echo "❌ Git 未安装"
    exit 1
fi

echo "✅ 所有系统要求检查通过！"
echo ""
echo "📥 现在可以使用以下命令安装 RAGForge:"
echo ""
echo "方法1: curl -fsSL https://raw.githubusercontent.com/zhaozhilong1993/ragforge/main/install.sh | bash"
echo ""
echo "方法2: curl -fsSL https://api.github.com/repos/zhaozhilong1993/ragforge/contents/install.sh | jq -r '.content' | base64 -d | bash"
echo ""
echo "方法3: wget -qO- https://raw.githubusercontent.com/zhaozhilong1993/ragforge/main/install.sh | bash"
echo ""
echo "🎉 安装完成后访问: http://localhost:9380" 