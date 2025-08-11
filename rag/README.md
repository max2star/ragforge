# RAG 模块使用指南

RAG（Retrieval-Augmented Generation）是 RAGForge 的核心模块，提供强大的检索增强生成功能。本指南将详细介绍如何使用 RAG 模块。

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

### 4. 启动 RAG 服务

```bash
# 启动 RAG 服务器
python api/ragforge_server.py
```

## 📚 使用指南

### 1. 创建知识库

```python
from api.db.services.dataset_service import DatasetService

# 创建数据集
dataset_service = DatasetService()
dataset = dataset_service.create_dataset(
    name="我的知识库",
    description="用于测试的知识库"
)
```

### 2. 上传文档

```python
from api.db.services.file2document_service import File2DocumentService

# 上传文档
file_service = File2DocumentService()
doc_id = file_service.upload_file(
    dataset_id=dataset.id,
    file_path="document.pdf",
    file_name="document.pdf"
)
```

### 3. 文档解析

```python
from rag.app.paper import chunk

# 解析文档
def progress_callback(**kwargs):
    print(f"进度: {kwargs.get('prog', 0)}, 消息: {kwargs.get('msg', '')}")

chunk(
    filename="document.pdf",
    from_page=0,
    to_page=100,
    callback=progress_callback,
    parser_config={
        "layout_recognize": "MinerU"
    }
)
```

### 4. 检索和问答

```python
from rag.nlp import search
from rag.llm import ChatModel

# 检索相关文档
query = "什么是机器学习？"
search_results = search.search(
    query=query,
    dataset_id=dataset.id,
    top_k=5
)

# 生成答案
chat_model = ChatModel["OpenAI"](
    key="your-api-key",
    model_name="gpt-3.5-turbo"
)

answer = chat_model.chat(
    query=query,
    context=search_results
)
```

## ⚙️ 配置说明

### 1. LLM 配置

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
```

### 2. 向量模型配置

```python
# 支持的 Embedding 模型
EMBEDDING_MODELS = {
    "BAAI/bge-large-zh-v1.5": "中文向量模型",
    "text-embedding-ada-002": "OpenAI 向量模型",
    "sentence-transformers/all-MiniLM-L6-v2": "轻量级向量模型"
}
```

### 3. 检索配置

```python
# 检索参数配置
search_config = {
    "top_k": 5,           # 检索数量
    "threshold": 0.7,      # 相似度阈值
    "rerank": True,        # 是否启用重排序
    "fusion": True         # 是否启用多路融合
}
```

## 🔧 高级功能

### 1. 自定义分块策略

```python
from rag.nlp import rag_tokenizer

# 自定义分块参数
chunk_config = {
    "chunk_size": 1000,        # 分块大小
    "chunk_overlap": 200,      # 重叠大小
    "separators": ["\n\n", "\n", "。", "！", "？"],  # 分隔符
    "min_chunk_size": 100      # 最小分块大小
}
```

### 2. 多路检索

```python
# 启用多路检索
search_results = search.multi_search(
    query=query,
    dataset_id=dataset.id,
    methods=["semantic", "keyword", "hybrid"],
    weights=[0.6, 0.2, 0.2]
)
```

### 3. 重排序

```python
from rag.llm import RerankModel

# 使用重排序模型
rerank_model = RerankModel["BAAI"](
    key="your-key",
    model_name="BAAI/bge-reranker-v2-m3"
)

reranked_results = rerank_model.rerank(
    query=query,
    documents=search_results
)
```

## 📊 性能优化

### 1. 向量数据库优化

```yaml
# Elasticsearch 优化配置
es:
  hosts: 'http://localhost:9200'
  username: 'elastic'
  password: ''
  # 性能优化参数
  max_connections: 100
  timeout: 30
  retry_on_timeout: true
```

### 2. 缓存配置

```python
# Redis 缓存配置
redis_config = {
    "host": "localhost",
    "port": 6379,
    "db": 1,
    "password": "your-password"
}
```

### 3. 批处理优化

```python
# 批量处理配置
batch_config = {
    "batch_size": 32,      # 批处理大小
    "max_workers": 4,      # 最大工作线程
    "timeout": 300         # 超时时间
}
```

## 🛠️ 故障排除

### 常见问题

1. **模型下载失败**
   ```bash
   # 检查网络连接
   ping huggingface.co
   
   # 使用镜像源
   export HF_ENDPOINT=https://hf-mirror.com
   ```

2. **内存不足**
   ```bash
   # 调整模型配置
   # 使用更小的模型或启用模型量化
   ```

3. **检索速度慢**
   ```bash
   # 优化向量数据库配置
   # 启用缓存机制
   # 调整批处理参数
   ```

### 日志查看

```bash
# 查看 RAG 服务日志
tail -f logs/ragforge.log

# 查看错误日志
grep -i error logs/ragforge.log
```

## 📝 示例代码

### 完整的 RAG 工作流

```python
import os
from api.db.services.dataset_service import DatasetService
from api.db.services.file2document_service import File2DocumentService
from rag.app.paper import chunk
from rag.nlp import search
from rag.llm import ChatModel

# 1. 创建知识库
dataset_service = DatasetService()
dataset = dataset_service.create_dataset(
    name="技术文档库",
    description="包含各种技术文档的知识库"
)

# 2. 上传文档
file_service = File2DocumentService()
doc_id = file_service.upload_file(
    dataset_id=dataset.id,
    file_path="tech_doc.pdf",
    file_name="tech_doc.pdf"
)

# 3. 解析文档
def progress_callback(**kwargs):
    print(f"解析进度: {kwargs.get('prog', 0):.2%} - {kwargs.get('msg', '')}")

chunk(
    filename="tech_doc.pdf",
    from_page=0,
    to_page=100,
    callback=progress_callback,
    parser_config={"layout_recognize": "MinerU"}
)

# 4. 检索和问答
query = "如何配置数据库连接？"

# 检索相关文档
search_results = search.search(
    query=query,
    dataset_id=dataset.id,
    top_k=5
)

# 生成答案
chat_model = ChatModel["OpenAI"](
    key=os.getenv("OPENAI_API_KEY"),
    model_name="gpt-3.5-turbo"
)

answer = chat_model.chat(
    query=query,
    context=search_results
)

print(f"问题: {query}")
print(f"答案: {answer}")
```

### 批量处理示例

```python
from concurrent.futures import ThreadPoolExecutor
import time

def process_document(doc_path, dataset_id):
    """处理单个文档"""
    try:
        # 上传文档
        doc_id = file_service.upload_file(
            dataset_id=dataset_id,
            file_path=doc_path,
            file_name=os.path.basename(doc_path)
        )
        
        # 解析文档
        chunk(
            filename=doc_path,
            callback=lambda **kwargs: None
        )
        
        return f"成功处理: {doc_path}"
    except Exception as e:
        return f"处理失败: {doc_path} - {str(e)}"

# 批量处理文档
documents = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
dataset_id = "your_dataset_id"

with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(
        lambda doc: process_document(doc, dataset_id),
        documents
    ))

for result in results:
    print(result)
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
