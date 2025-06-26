#!/usr/bin/env python3
"""
RAGFlow CLI 测试脚本
测试CLI工具的基本功能
"""

import subprocess
import json
import sys

def test_cli_help():
    """测试CLI帮助功能"""
    print("🔍 测试CLI帮助功能...")
    
    try:
        result = subprocess.run(
            ["python", "ragflow-cli.py", "--help"], 
            capture_output=True, 
            text=True
        )
        
        if result.returncode == 0:
            print("✅ CLI帮助功能正常")
            return True
        else:
            print(f"❌ CLI帮助功能异常: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ CLI帮助功能错误: {e}")
        return False

def test_system_endpoints():
    """测试系统端点（无需认证）"""
    print("\n🔍 测试系统端点...")
    
    endpoints = [
        ("/v1/system/config", "系统配置"),
        ("/v1/system/version", "系统版本"),
    ]
    
    success_count = 0
    for endpoint, name in endpoints:
        try:
            result = subprocess.run(
                ["curl", "-s", f"http://localhost:9380{endpoint}"], 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout)
                    if data.get('code') == 0:
                        print(f"✅ {name} 端点正常")
                        success_count += 1
                    else:
                        print(f"⚠️ {name} 端点返回错误: {data.get('message', '未知错误')}")
                except json.JSONDecodeError:
                    print(f"❌ {name} 端点返回非JSON格式")
            else:
                print(f"❌ {name} 端点请求失败")
        except Exception as e:
            print(f"❌ {name} 端点测试错误: {e}")
    
    return success_count == len(endpoints)

def test_cli_commands():
    """测试CLI命令结构"""
    print("\n🔍 测试CLI命令结构...")
    
    commands = [
        ["python", "ragflow-cli.py", "system", "--help"],
        ["python", "ragflow-cli.py", "dataset", "--help"],
        ["python", "ragflow-cli.py", "document", "--help"],
        ["python", "ragflow-cli.py", "chunk", "--help"],
        ["python", "ragflow-cli.py", "search", "--help"],
        ["python", "ragflow-cli.py", "token", "--help"],
        ["python", "ragflow-cli.py", "user", "--help"],
    ]
    
    success_count = 0
    for cmd in commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {' '.join(cmd[1:])} 命令正常")
                success_count += 1
            else:
                print(f"❌ {' '.join(cmd[1:])} 命令异常")
        except Exception as e:
            print(f"❌ {' '.join(cmd[1:])} 命令错误: {e}")
    
    return success_count == len(commands)

def test_authentication_required():
    """测试需要认证的命令"""
    print("\n🔍 测试需要认证的命令...")
    
    commands = [
        ["python", "ragflow-cli.py", "system", "status"],
        ["python", "ragflow-cli.py", "dataset", "list"],
        ["python", "ragflow-cli.py", "user", "info"],
    ]
    
    success_count = 0
    for cmd in commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # 这些命令应该返回认证错误
            if result.returncode != 0 and "未认证" in result.stderr:
                print(f"✅ {' '.join(cmd[1:])} 正确要求认证")
                success_count += 1
            else:
                print(f"❌ {' '.join(cmd[1:])} 认证检查异常")
        except Exception as e:
            print(f"❌ {' '.join(cmd[1:])} 认证测试错误: {e}")
    
    return success_count == len(commands)

def main():
    """主测试函数"""
    print("🚀 RAGFlow CLI 功能测试")
    print("=" * 50)
    
    tests = [
        ("CLI帮助功能", test_cli_help),
        ("系统端点", test_system_endpoints),
        ("CLI命令结构", test_cli_commands),
        ("认证要求", test_authentication_required),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 测试: {test_name}")
        if test_func():
            passed += 1
            print(f"✅ {test_name} 通过")
        else:
            print(f"❌ {test_name} 失败")
    
    print(f"\n{'='*50}")
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！CLI工具功能正常")
        return 0
    else:
        print("⚠️ 部分测试失败，请检查CLI工具")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 