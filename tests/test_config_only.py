#!/usr/bin/env python3
"""
只测试配置加载，不连接数据库
"""

import subprocess

def test_config_loading():
    """测试配置加载功能"""
    print("=== 配置加载测试 ===")
    
    # 环境变量
    env_vars = {
        'RAGFORGE_MYSQL_HOST': '172.16.1.50',
        'RAGFORGE_MYSQL_PORT': '5455',
        'RAGFORGE_ES_HOSTS': 'http://172.16.1.50:1200',
        'RAGFORGE_MINIO_HOST': '172.16.1.50:19000',
        'RAGFORGE_REDIS_HOST': '172.16.1.50',
        'RAGFORGE_REDIS_PORT': '16379'
    }
    
    # 构建命令
    env_args = []
    for key, value in env_vars.items():
        env_args.extend(['-e', f'{key}={value}'])
    
    # 只测试配置加载，不启动服务
    cmd = [
        'docker', 'run', '--rm',
        *env_args,
        'ragforge-simple:latest',
        'python', '-c', 
        '''
import os
import sys
sys.path.append("/ragforge")
from api.utils import read_config, show_configs

print("=== 开始加载配置 ===")
config = read_config()
show_configs()

print("\\n=== 验证环境变量覆盖 ===")
mysql_config = config.get("mysql", {})
es_config = config.get("es", {})
minio_config = config.get("minio", {})
redis_config = config.get("redis", {})

print(f"MySQL host: {mysql_config.get('host')}")
print(f"MySQL port: {mysql_config.get('port')}")
print(f"ES hosts: {es_config.get('hosts')}")
print(f"MinIO host: {minio_config.get('host')}")
print(f"Redis host: {redis_config.get('host')}")
print(f"Redis port: {redis_config.get('port')}")

print("\\n=== 配置加载测试完成 ===")
'''
    ]
    
    print("启动配置测试容器...")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ 配置加载测试成功")
            print("\n=== 输出日志 ===")
            print(result.stdout)
        else:
            print(f"❌ 配置加载测试失败，返回码: {result.returncode}")
            print("\n=== 错误输出 ===")
            print(result.stderr)
            print("\n=== 标准输出 ===")
            print(result.stdout)
            
    except subprocess.TimeoutExpired:
        print("❌ 配置加载测试超时")
    except Exception as e:
        print(f"❌ 配置加载测试失败: {e}")

def test_env_vars():
    """测试环境变量是否正确传递"""
    print("\n=== 环境变量传递测试 ===")
    
    cmd = [
        'docker', 'run', '--rm',
        '-e', 'RAGFORGE_MYSQL_HOST=test-host',
        '-e', 'RAGFORGE_ES_HOSTS=http://test-es:9200',
        'ragforge-simple:latest',
        'env', '|', 'grep', 'RAGFORGE'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ 环境变量传递成功")
            print("环境变量列表:")
            print(result.stdout)
        else:
            print("❌ 环境变量传递失败")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ 环境变量测试失败: {e}")

def main():
    """主函数"""
    print("开始配置加载测试...")
    
    # 1. 环境变量传递测试
    test_env_vars()
    
    # 2. 配置加载测试
    test_config_loading()
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main() 