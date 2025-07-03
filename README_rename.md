# RAGForge -> RAGForge 项目重命名脚本

这个脚本用于将项目中的 `ragforge` 和 `RAGForge` 相关名字替换成 `ragforge`。

## 使用方法

### 1. 试运行（推荐先执行）
```bash
python rename_project.py --dry-run
```
这会显示所有将要修改的文件，但不会实际修改任何内容。

### 2. 创建备份并执行重命名
```bash
python rename_project.py --backup
```
这会先创建项目备份，然后执行重命名操作。

### 3. 直接执行重命名（不创建备份）
```bash
python rename_project.py
```

### 4. 处理指定目录
```bash
python rename_project.py --directory /path/to/project
```

## 脚本功能

- **文件内容替换**：将文件中的 `ragforge`、`RAGForge`、`RAGFORGE`、`Ragforge`、`RAGForge`、`NewRAGForge`、`newragforge`、`NEWRAGFORGE` 替换为对应的 `ragforge` 形式
- **文件/目录重命名**：重命名包含 `ragforge` 的文件和目录名
- **智能跳过**：自动跳过 `.git`、`__pycache__`、`.venv` 等不需要修改的目录
- **备份功能**：可选择在修改前创建项目备份
- **试运行模式**：预览将要修改的文件，确保安全

## 注意事项

⚠️ **重要提醒**：
1. 此脚本会修改项目文件，请在运行前确保已提交或备份重要更改
2. 建议先使用 `--dry-run` 模式查看将要修改的文件
3. 重命名后可能需要：
   - 更新配置文件中的路径
   - 重新安装依赖
   - 更新 Docker 配置
   - 检查数据库连接配置

## 跳过规则

脚本会自动跳过以下文件和目录：
- `.git/` 目录
- `__pycache__/` 目录
- `.venv/` 和 `venv/` 目录
- `node_modules/` 目录
- `.pyc`、`.pyo`、`.pyd` 文件
- `.lock` 文件
- `.gitignore` 文件
- 脚本本身 (`rename_project.py`)

## 示例输出

```
============================================================
RAGForge -> RAGForge 项目重命名脚本
============================================================
处理目录: .
试运行模式: 是
创建备份: 否

开始处理目录: /path/to/project
将 'ragforge' 替换为 'ragforge'
DRY RUN 模式 - 不会实际修改文件
--------------------------------------------------
将修改文件: pyproject.toml
将修改文件: api/apps/__init__.py
将修改文件: docker/nginx/ragforge.conf
...
--------------------------------------------------
处理完成！
修改的文件数量: 25
```

## 故障排除

如果遇到问题：
1. 确保有足够的磁盘空间（特别是使用备份功能时）
2. 确保对项目目录有写权限
3. 检查是否有文件被其他程序占用
4. 如果重命名后出现问题，可以使用备份恢复 