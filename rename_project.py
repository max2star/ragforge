#!/usr/bin/env python3
"""
项目重命名脚本：将ragflow相关名字替换成ragforge
注意：此脚本会修改项目文件，请在运行前备份项目
"""

import os
import re
import shutil
import time
from pathlib import Path
import argparse

def should_skip_file(file_path):
    """判断是否应该跳过某个文件"""
    skip_patterns = [
        r'\.git/',
        r'\.venv/',
        r'venv/',
        r'__pycache__/',
        r'\.pyc$',
        r'\.pyo$',
        r'\.pyd$',
        r'\.so$',
        r'\.egg-info/',
        r'\.gitignore',
        r'rename_project\.py',  # 跳过脚本本身
        r'\.lock$',  # 跳过lock文件
        r'node_modules/',
        r'\.DS_Store$',
        r'\.idea/',
        r'\.vscode/',
    ]
    
    file_str = str(file_path)
    for pattern in skip_patterns:
        if re.search(pattern, file_str):
            return True
    return False

def should_skip_directory(dir_path):
    """判断是否应该跳过某个目录"""
    skip_dirs = {
        '.git', '.venv', 'venv', '__pycache__', 
        'node_modules', '.idea', '.vscode', '.DS_Store'
    }
    return dir_path.name in skip_dirs

def replace_in_file(file_path, old_name, new_name):
    """在文件中替换文本"""
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 执行替换
        original_content = content
        
        # 替换各种形式的ragflow和NewRAGflow
        replacements = [
            ('ragflow', 'ragforge'),
            ('RAGFlow', 'RAGForge'),
            ('RAGFLOW', 'RAGFORGE'),
            ('Ragflow', 'Ragforge'),
            ('NewRAGflow', 'RAGForge'),
            ('NewRAGFlow', 'RAGForge'),
            ('newragflow', 'ragforge'),
            ('NEWRAGFLOW', 'RAGFORGE'),
        ]
        
        for old, new in replacements:
            content = content.replace(old, new)
        
        # 如果内容有变化，写回文件
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
        
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {e}")
        return False

def rename_file_or_directory(path, old_name, new_name):
    """重命名文件或目录"""
    try:
        if path.exists():
            new_path = path.parent / str(path.name).replace(old_name, new_name)
            if new_path != path:
                path.rename(new_path)
                return new_path
    except Exception as e:
        print(f"重命名 {path} 时出错: {e}")
    return path

def process_directory(root_dir, old_name, new_name, dry_run=False):
    """处理目录中的所有文件和子目录"""
    root_path = Path(root_dir)
    processed_files = 0
    renamed_items = []
    
    print(f"开始处理目录: {root_path}")
    print(f"将 '{old_name}' 替换为 '{new_name}'")
    if dry_run:
        print("DRY RUN 模式 - 不会实际修改文件")
    print("-" * 50)
    
    # 首先处理文件内容
    for file_path in root_path.rglob('*'):
        if file_path.is_file() and not should_skip_file(file_path):
            if dry_run:
                # 检查文件是否包含需要替换的内容
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    if any(old in content for old in ['ragflow', 'RAGFlow', 'RAGFLOW', 'Ragflow', 'NewRAGflow', 'NewRAGFlow', 'newragflow', 'NEWRAGFLOW']):
                        print(f"将修改文件: {file_path}")
                        processed_files += 1
                except Exception as e:
                    print(f"读取文件 {file_path} 时出错: {e}")
            else:
                if replace_in_file(file_path, old_name, new_name):
                    print(f"已修改文件: {file_path}")
                    processed_files += 1
    
    # 然后处理文件和目录名
    if not dry_run:
        # 从最深层开始，避免路径变化影响
        all_items = list(root_path.rglob('*'))
        all_items.sort(key=lambda x: len(str(x).split(os.sep)), reverse=True)
        
        for item_path in all_items:
            if should_skip_file(item_path) or should_skip_directory(item_path):
                continue
                
            new_path = rename_file_or_directory(item_path, old_name, new_name)
            if new_path != item_path:
                renamed_items.append((item_path, new_path))
                print(f"已重命名: {item_path.name} -> {new_path.name}")
    
    print("-" * 50)
    print(f"处理完成！")
    print(f"修改的文件数量: {processed_files}")
    if not dry_run:
        print(f"重命名的项目数量: {len(renamed_items)}")
    
    return processed_files, renamed_items

def main():
    parser = argparse.ArgumentParser(description='将项目中的ragflow相关名字替换成ragforge')
    parser.add_argument('--dry-run', action='store_true', 
                       help='试运行模式，只显示会修改的文件，不实际修改')
    parser.add_argument('--backup', action='store_true',
                       help='在修改前创建备份')
    parser.add_argument('--directory', default='.',
                       help='要处理的目录路径 (默认: 当前目录)')
    
    args = parser.parse_args()
    
    # 确认操作
    print("=" * 60)
    print("RAGFlow -> RAGForge 项目重命名脚本")
    print("=" * 60)
    print(f"处理目录: {args.directory}")
    print(f"试运行模式: {'是' if args.dry_run else '否'}")
    print(f"创建备份: {'是' if args.backup else '否'}")
    print()
    
    if not args.dry_run:
        confirm = input("警告：此操作将修改项目文件，是否继续？(y/N): ")
        if confirm.lower() != 'y':
            print("操作已取消")
            return
    
    # 创建备份
    if args.backup and not args.dry_run:
        backup_dir = f"backup_ragflow_{int(time.time())}"
        print(f"创建备份到: {backup_dir}")
        try:
            shutil.copytree(args.directory, backup_dir, 
                           ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', '.venv', 'venv'))
            print("备份创建成功")
        except Exception as e:
            print(f"备份创建失败: {e}")
            return
    
    # 执行重命名
    try:
        process_directory(args.directory, 'ragflow', 'ragforge', args.dry_run)
        print("\n重命名操作完成！")
        
        if not args.dry_run:
            print("\n注意事项:")
            print("1. 请检查修改后的文件是否正确")
            print("2. 可能需要更新一些配置文件中的路径")
            print("3. 如果使用了虚拟环境，可能需要重新安装依赖")
            print("4. 建议运行测试确保功能正常")
            
    except Exception as e:
        print(f"执行过程中出错: {e}")

if __name__ == "__main__":
    main() 