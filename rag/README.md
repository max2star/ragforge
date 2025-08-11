# RAG 模块使用指南

RAG（Retrieval-Augmented Generation）是 RAGForge 的核心模块，提供强大的检索增强生成功能。本指南将重点介绍文档解析任务执行器的使用方法。

## 🎯 核心功能

### 🔍 **智能检索**
- 多路召回与融合重排序
- 支持多种向量数据库（Elasticsearch、Infinity）
- 语义检索和关键词检索结合

### 🧠 **文本处理**
- 基于模板的智能文本切片
- 多语言支持
- 自定义分块策略

### 🚀 **答案生成**
- 有理有据的答案生成
- 最大程度降低幻觉
- 支持多种 LLM 模型

## 📋 系统要求

- Python 3.10+
- 内存 >= 8GB
- 磁盘空间 >= 10GB（用于模型文件）

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export PYTHONPATH=/path/to/ragforge
```

### 2. 模型下载

RAG 模块需要下载相应的模型文件。使用以下命令下载：

```bash
# 进入 driver 目录
cd driver

# 运行模型下载脚本
python download_models.py
```

下载的模型文件将存储在 `driver/models` 目录下，包括：
- **Embedding 模型**: 用于文本向量化
- **Rerank 模型**: 用于重排序
- **LLM 模型**: 用于答案生成

### 3. 配置数据库

#### Elasticsearch 配置

```yaml
# conf/service_conf.yaml
es:
  hosts: 'http://localhost:9200'
  username: 'elastic'
  password: ''
```

#### Infinity 配置

```yaml
# conf/service_conf.yaml
infinity:
  uri: 'localhost:23817'
  db_name: 'default_db'
```

### 4. 启动文档解析服务

```bash
# 启动文档解析任务执行器（核心服务）
python rag/svr/task_executor.py
```

## 📚 使用指南

### 使用 RAGForge Shell 命令行工具

RAGForge 提供了便捷的命令行工具 `ragforge-shell`，可以轻松完成所有 RAG 操作：

#### 1. 安装和配置

```bash
# 进入 ragforge-shell 目录
cd ragforge-shell

# 安装依赖
uv pip install -r requirements.txt

# 配置认证信息
# 编辑 config.yaml 文件
api:
  api_token: your-api-token
  auth_token: your-auth-token
  base_url: http://localhost:9380
```

#### 2. 基本操作流程

```bash
# 检查系统状态
uv run python main.py system status

# 查看数据集列表
uv run python main.py datasets list

# 创建数据集
uv run python main.py datasets create "我的知识库" --description "用于测试的知识库"

# 上传文档
uv run python main.py documents upload <dataset_id> --file document.pdf

# 启动文档解析
uv run python main.py documents parse <dataset_id> <document_id>

# 检索文档内容
uv run python main.py retrieval search "查询内容" <dataset_id>
```

#### 3. 完整工作流示例

```bash
# 1. 系统检查
uv run python main.py system status

# 2. 创建知识库
dataset_id=$(uv run python main.py datasets create "技术文档库" --description "技术文档集合" --output-format json | jq -r '.id')

# 3. 上传文档
uv run python main.py documents upload $dataset_id --file tech_doc.pdf

# 4. 查看文档列表
uv run python main.py documents list $dataset_id

# 5. 启动解析（使用 MinerU 解析器）
uv run python main.py documents parse $dataset_id <document_id> --parser-config '{"layout_recognize": "MinerU"}'

# 6. 检索问答
uv run python main.py retrieval search "如何配置数据库连接？" $dataset_id
```

### 核心服务：task_executor.py

`rag/svr/task_executor.py` 是文档解析的核心服务，负责：

- **文档解析任务处理**: 接收并处理文档解析请求
- **多解析器支持**: 支持 MinerU、DeepDOC、Plain Text 等解析方式
- **进度回调**: 实时反馈解析进度
- **错误处理**: 完善的错误处理和日志记录

#### 启动解析服务

```bash
# 启动文档解析任务执行器
python rag/svr/task_executor.py

# 或者使用后台运行
nohup python rag/svr/task_executor.py > task_executor.log 2>&1 &
```

#### 服务配置

解析服务会自动读取以下配置：
- `conf/service_conf.yaml`: 服务配置
- `conf/magic-pdf.json`: PDF 解析配置
- 环境变量: 数据库连接、模型路径等

## ⚙️ 配置说明

### 核心配置文件

#### 1. 服务配置

```yaml
# conf/service_conf.yaml
user_default_llm:
  factory: 'OpenAI'
  api_key: 'your-api-key'
  base_url: 'https://api.openai.com/v1'
  default_models:
    chat_model: 'gpt-3.5-turbo'
    embedding_model: 'text-embedding-ada-002'
    rerank_model: 'text-embedding-ada-002'

es:
  hosts: 'http://localhost:9200'
  username: 'elastic'
  password: ''

redis:
  host: 'localhost'
  port: 6379
  password: 'your-password'
```

#### 2. PDF 解析配置

```json
// conf/magic-pdf.json
{
  "models-dir": "driver/models/opendatalab/PDF-Extract-Kit-1___0/models",
  "layoutreader-model-dir": "driver/models/ppaanngggg/layoutreader",
  "device-mode": "cpu",
  "layout-config": {
    "model": "doclayout_yolo"
  },
  "formula-config": {
    "enable": true
  },
  "table-config": {
    "enable": true,
    "max_time": 400
  }
}
```

## 🔧 高级功能

### 解析器选择

RAGForge 支持多种文档解析器，可通过命令行参数选择：

```bash
# 使用 MinerU 解析器（推荐）
uv run python main.py documents parse <dataset_id> <document_id> --parser-config '{"layout_recognize": "MinerU"}'

# 使用 DeepDOC 解析器
uv run python main.py documents parse <dataset_id> <document_id> --parser-config '{"layout_recognize": "DeepDOC"}'

# 使用 Plain Text 解析器
uv run python main.py documents parse <dataset_id> <document_id> --parser-config '{"layout_recognize": "Plain Text"}'
```

### 批量处理

```bash
# 批量上传文档
for file in *.pdf; do
    uv run python main.py documents upload $dataset_id --file "$file"
done

# 批量解析文档
uv run python main.py documents list $dataset_id | grep "pending" | awk '{print $1}' | xargs -I {} uv run python main.py documents parse $dataset_id {}
```

## 🛠️ 故障排除

### 常见问题

1. **task_executor.py 启动失败**
   ```bash
   # 检查依赖是否安装
   pip install -r requirements.txt
   
   # 检查配置文件
   ls -la conf/service_conf.yaml
   ls -la conf/magic-pdf.json
   
   # 检查模型文件
   ls -la driver/models/
   ```

2. **文档解析失败**
   ```bash
   # 查看解析日志
   tail -f logs/task_executor.log
   
   # 检查模型路径配置
   cat conf/magic-pdf.json | grep models-dir
   ```

3. **ragforge-shell 连接失败**
   ```bash
   # 检查 API 服务状态
   curl http://localhost:9380/api/v1/system/status
   
   # 检查认证配置
   cat ragforge-shell/config.yaml
   ```

### 日志查看

```bash
# 查看任务执行器日志
tail -f logs/task_executor.log

# 查看 API 服务日志
tail -f logs/ragforge.log

# 查看错误日志
grep -i error logs/*.log
```

## 📝 使用示例

### 完整工作流脚本

创建一个 `workflow.sh` 脚本：

```bash
#!/bin/bash

# 配置变量
API_BASE="http://localhost:9380"
DATASET_NAME="技术文档库"

echo "=== RAGForge 完整工作流 ==="

# 1. 检查系统状态
echo "1. 检查系统状态..."
uv run python main.py system status

# 2. 创建数据集
echo "2. 创建数据集..."
dataset_id=$(uv run python main.py datasets create "$DATASET_NAME" --output-format json | jq -r '.id')
echo "数据集ID: $dataset_id"

# 3. 上传文档
echo "3. 上传文档..."
for file in *.pdf; do
    echo "上传: $file"
    uv run python main.py documents upload $dataset_id --file "$file"
done

# 4. 启动解析
echo "4. 启动文档解析..."
uv run python main.py documents list $dataset_id | grep "pending" | awk '{print $1}' | while read doc_id; do
    echo "解析文档: $doc_id"
    uv run python main.py documents parse $dataset_id $doc_id --parser-config '{"layout_recognize": "MinerU"}'
done

# 5. 检索测试
echo "5. 检索测试..."
uv run python main.py retrieval search "什么是机器学习？" $dataset_id

echo "=== 工作流完成 ==="
```

使用方法：
```bash
chmod +x workflow.sh
./workflow.sh
```

## 🔗 相关链接

- [主项目 README](../README.md)
- [API 文档](../api/README.md)
- [MinerU 解析器](../minerU/README.md)
- [DeepDOC 解析器](../deepdoc/README.md)

## 📞 技术支持

如有问题，请参考：
1. 查看日志文件
2. 检查配置文件
3. 参考故障排除章节
4. 提交 Issue 到项目仓库

---

**注意**: 本模块需要正确配置模型文件和数据库连接才能正常工作。
