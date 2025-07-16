#!/usr/bin/env python3
"""
RAGForge 服务器启动脚本
用于从源码启动RAGForge服务
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_environment():
    """设置环境变量"""
    # 获取项目根目录
    project_root = Path(__file__).parent.absolute()
    
    # 设置PYTHONPATH
    os.environ['PYTHONPATH'] = str(project_root)
    
    # 设置工作目录
    os.chdir(project_root)
    
    print(f"项目根目录: {project_root}")
    print(f"PYTHONPATH: {os.environ['PYTHONPATH']}")

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import uv
        print("✅ uv 已安装")
    except ImportError:
        print("❌ uv 未安装，请先运行: pip install uv")
        return False
    
    # 检查虚拟环境是否存在
    venv_path = Path(".venv")
    if not venv_path.exists():
        print("❌ 虚拟环境不存在，请先运行: uv sync --python 3.10")
        return False
    
    print("✅ 虚拟环境存在")
    return True

def activate_venv():
    """激活虚拟环境"""
    if sys.platform == "win32":
        activate_script = ".venv\\Scripts\\activate"
    else:
        activate_script = ".venv/bin/activate"
    
    if os.path.exists(activate_script):
        print(f"激活虚拟环境: {activate_script}")
        return True
    else:
        print(f"❌ 虚拟环境激活脚本不存在: {activate_script}")
        return False

def start_server():
    """启动RAGForge服务器"""
    try:
        # 设置环境
        setup_environment()
        
        # 检查依赖
        if not check_dependencies():
            return False
        
        # 激活虚拟环境
        if not activate_venv():
            return False
        
        print("🚀 启动RAGForge服务器...")
        print("📝 提示: 确保已启动数据库服务 (MySQL, Redis, Elasticsearch, MinIO)")
        print("🌐 服务启动后访问: http://localhost:9380")
        print("📚 API文档: http://localhost:9380/apidocs/")
        print("=" * 50)
        
        # 启动服务器
        server_script = "api/ragforge_server.py"
        if not os.path.exists(server_script):
            print(f"❌ 服务器脚本不存在: {server_script}")
            return False
        
        # 使用虚拟环境中的Python执行
        if sys.platform == "win32":
            python_path = ".venv\\Scripts\\python.exe"
        else:
            python_path = ".venv/bin/python"
        
        if not os.path.exists(python_path):
            print(f"❌ Python解释器不存在: {python_path}")
            return False
        
        # 启动服务器
        subprocess.run([python_path, server_script], check=True)
        
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 服务器启动失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 启动过程中出现错误: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = start_server()
    if not success:
        sys.exit(1) 