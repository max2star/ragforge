<div align="center">
<a href="https://demo.ragforge.io/">
<img src="conf/logo-with-text.png" width="100" alt="RAGForge logo">
</a>
</div>

<p align="center">
  <a href="./README.md">简体中文</a>
</p>

## 💡 RAGForge 是什么？

RAGForge 是基于 RAGFlow、MinerU等项目，进行功能增强的开源 RAG（Retrieval-Augmented Generation）引擎。在保持原有 RAGFlow 核心功能的基础上，新增了多项企业级功能增强，为开发人员提供更强大的 RAG 解决方案。

## 🌟 核心功能

### 🔍 **深度文档理解**
- 基于深度文档理解，从复杂格式的非结构化数据中提取知识
- 支持 Word、PPT、Excel、PDF、图片、网页等多种格式

### 🧠 **智能文本处理**
- 基于模板的智能文本切片
- 多路召回与融合重排序
- 有理有据的答案生成，最大程度降低幻觉

### 🚀 **自动化 RAG 工作流**
- 完整的 RAG 编排流程
- 可配置的 LLM 和向量模型
- 易用的 API 接口

## 📊 版本对比

| 功能特性 | 社区版 | 专业版 | 企业版 |
|---------|--------|--------|--------|
| **核心 RAG 功能** | ✅ | ✅ | ✅ |
| **深度文档理解** | ✅ | ✅ | ✅ |
| **智能文本处理** | ✅ | ✅ | ✅ |
| **自动化 RAG 工作流** | ✅ | ✅ | ✅ |
| **MinerU 集成** | ✅ | ✅ | ✅ |
| **基础文档处理** | ✅ | ✅ | ✅ |
| **多格式文档支持** | ✅ | ✅ | ✅ |
| **向量数据库支持** | ✅ | ✅ | ✅ |
| **API 接口** | ✅ | ✅ | ✅ |
| **Web 控制台** | ✅ | ✅ | ✅ |
| **ARM 架构支持** | ❌ | ✅ | ✅ |
| **国产数据库支持** | ❌ | ❌ | ✅ |
| **华为 910B NPU 支持** | ❌ | ❌ | ✅ |
| **高级文档处理** | ❌ | ❌ | ✅ |
| **自定义模型支持** | ❌ | ❌ | ✅ |
| **企业级技术支持** | ❌ | ✅ | ✅ |
| **私有化部署** | ❌ | ✅ | ✅ |
| **定制化开发** | ❌ | ❌ | ✅ |

## 🌈 版本功能说明

### 🆓 社区版
- **核心 RAG 功能**：完整的检索增强生成能力
- **基础文档处理**：支持常见文档格式的处理
- **多格式文档支持**：Word、PPT、Excel、PDF、图片、网页等
- **向量数据库支持**：集成主流向量数据库
- **API 接口**：提供完整的 RESTful API
- **Web 控制台**：直观的 Web 管理界面

### ⭐ 专业版
- **国产数据库支持**：新增对达梦数据库的兼容性支持
- **ARM 架构支持**：完整支持基于 ARM 的系统部署
- **华为 910B NPU 支持**：优化对华为昇腾 910B NPU 的支持
- **高级文档处理**：更强大的文档解析和处理能力
- **自定义模型支持**：支持自定义模型集成

### 🏢 企业版
- **企业级技术支持**：专业的技术支持和咨询服务
- **私有化部署**：支持完全私有化部署方案
- **定制化开发**：根据企业需求进行定制开发
- **MinerU 集成**：无缝集成 MinerU 功能，提供增强的数据挖掘和分析能力

## 🎬 快速开始

### 🖼️ 系统预览

![RAGForge 登录页面](https://ragforge-bucket.oss-cn-hangzhou.aliyuncs.com/login.png)

![RAGForge 知识库管理](https://ragforge-bucket.oss-cn-hangzhou.aliyuncs.com/knowledge.png)

### 📋 系统要求
- CPU >= 4 核
- RAM >= 16 GB
- Disk >= 50 GB
- Docker >= 24.0.0 & Docker Compose >= v2.26.1

### 🚀 快速部署

1. **克隆项目**
   ```bash
   git clone https://github.com/max2star/ragforge.git
   cd ragforge/docker
   ```

2. **一键启动服务**
   ```bash
   # 启动脚本，按提示选择生产环境或开发环境
   ./start.sh
   ```
   - 选择【1】启动所有服务（生产环境，Web 控制台端口 80）
   - 选择【2】启动所有服务（开发环境，Web 控制台端口 3000，支持热更新）

3. **停止服务**
   ```bash
   ./stop.sh
   ```
   - 按提示选择停止/清理服务的方式

4. **访问系统**
   - 生产环境 Web 控制台：http://localhost
   - 开发环境 Web 控制台：http://localhost:3000
   - API 服务：http://localhost:9380

5. **配置 LLM API Key**
   - 编辑 `service_conf.yaml.template`

### ⚙️ 配置说明

- **.env**：基础环境变量（端口、密码等）
- **service_conf.yaml.template**：后端服务配置
- **docker-compose.yml**：容器编排配置

## 🔧 开发环境设置

### 🚀 推荐开发流程

#### 方式一：Docker 开发环境（推荐）

1. **进入 docker 目录，使用脚本启动开发环境**
   ```bash
   cd docker
   ./start.sh   # 选择 2 启动开发环境
   ```
   - 开发环境 Web 控制台：http://localhost:3000
   - 支持热更新，适合前后端联调

2. **停止服务**
   ```bash
   ./stop.sh
   ```

3. **常用 Docker 命令**
   ```bash
   docker-compose ps         # 查看服务状态
   docker-compose logs -f    # 查看实时日志
   docker-compose down       # 停止并移除所有服务
   ```

#### 方式二：Python 源码启动

1. **安装依赖**
   ```bash
   # 安装 uv
   pip install uv
   
   # 安装 Python 依赖
   uv sync --python 3.10 --all-extras
   ```

2. **启动数据库服务**
   ```bash
   # 启动基础服务 (MySQL, Redis, Elasticsearch, MinIO)
   docker compose -f docker/docker-compose-base.yml up -d
   ```

3. **启动 RAGForge 服务器**
   ```bash
   # 方式一：使用启动脚本（推荐）
   ./start.sh
   
   # 方式二：手动启动
   source .venv/bin/activate
   export PYTHONPATH=$(pwd)
   python api/ragforge_server.py
   ```

4. **启动前端服务（可选）**
   ```bash
   cd web
   npm install
   npm run dev
   ```

5. **访问服务**
   - 后端 API：http://localhost:9380
   - API 文档：http://localhost:9380/apidocs/
   - 前端控制台：http://localhost:3000（如果启动了前端）

### 🛠️ 环境变量配置

```bash
# 数据库类型
export DATABASE_TYPE=mysql  # 默认使用 MySQL
# export DATABASE_TYPE=dm   # 使用达梦数据库

# 文档引擎
export DOC_ENGINE=elasticsearch  # 默认使用 Elasticsearch
# export DOC_ENGINE=infinity     # 使用 Infinity 向量数据库

# 存储实现
export STORAGE_IMPL=MINIO  # 默认使用 MinIO
# export STORAGE_IMPL=AWS_S3  # 使用 AWS S3
```

### 🔍 故障排除

**Docker 服务启动失败**：
- 端口冲突：修改 `.env` 文件中的端口配置
- 镜像拉取失败：检查网络或更换镜像源

**API 连接失败**：
- 检查 Docker 服务状态：`docker-compose ps`
- 检查端口映射和防火墙

**Python 环境问题**：
- 设置 PYTHONPATH：`export PYTHONPATH=/path/to/ragforge`
- 安装依赖：`uv sync --python 3.10 --all-extras`

## 📄 PDF 解析程序使用指南

RAGForge 集成了强大的 PDF 解析功能，支持多种解析方式，包括 MinerU、DeepDOC 等。本指南将详细介绍如何使用 PDF 解析程序。

### 🎯 支持的解析方式

#### 1. **MinerU 解析器**（推荐）
- **功能**: 基于深度学习的智能文档解析
- **支持格式**: PDF、Word、PPT、Excel
- **特点**: 
  - 自动布局识别
  - 表格结构识别
  - 公式识别
  - 图片内容提取
  - 多语言支持

#### 2. **DeepDOC 解析器**
- **功能**: 传统文档解析方式
- **支持格式**: PDF
- **特点**: 
  - 基础文本提取
  - 布局识别
  - 表格检测

#### 3. **Plain Text 解析器**
- **功能**: 纯文本提取
- **支持格式**: PDF
- **特点**: 简单快速，适合纯文本文档

### 🚀 快速开始

#### 方式一：通过 Web 控制台使用

1. **启动服务**
   ```bash
   cd docker
   ./start.sh  # 选择开发环境或生产环境
   ```

2. **访问 Web 控制台**
   - 开发环境：http://localhost:3000
   - 生产环境：http://localhost

3. **上传文档**
   - 登录系统
   - 创建或选择知识库
   - 上传 PDF 文档

4. **选择解析方式**
   - 在文档上传页面选择解析方式：
     - **MinerU**: 智能解析（推荐）
     - **DeepDOC**: 传统解析
     - **Plain Text**: 纯文本提取

5. **查看解析结果**
   - 解析完成后可在文档详情页查看结果
   - 支持查看布局分析、表格识别等结果

#### 方式二：通过 API 使用

1. **上传文档**
   ```bash
   curl -X POST "http://localhost:9380/api/v1/datasets/{dataset_id}/documents" \
     -H "Authorization: Bearer {your_token}" \
     -F "file=@your_document.pdf"
   ```

2. **启动解析**
   ```bash
   curl -X POST "http://localhost:9380/api/v1/datasets/{dataset_id}/documents/{document_id}/parse" \
     -H "Authorization: Bearer {your_token}" \
     -H "Content-Type: application/json" \
     -d '{
       "parser_config": {
         "layout_recognize": "MinerU"
       }
     }'
   ```

3. **查询解析结果**
   ```bash
   curl -X GET "http://localhost:9380/api/v1/datasets/{dataset_id}/documents/{document_id}" \
     -H "Authorization: Bearer {your_token}"
   ```

#### 方式三：通过命令行工具使用

1. **安装 RAGForge Shell**
   ```bash
   cd ragforge-shell
   uv pip install -r requirements.txt
   ```

2. **配置认证**
   ```bash
   # 编辑 config.yaml 文件
   api:
     api_token: your-api-token
     auth_token: your-auth-token
     base_url: http://localhost:9380
   ```

3. **上传并解析文档**
   ```bash
   # 上传文档
   uv run python main.py documents upload {dataset_id} --file your_document.pdf
   
   # 启动解析
   uv run python main.py documents parse {dataset_id} {document_id}
   
   # 查看解析结果
   uv run python main.py documents get {dataset_id} {document_id}
   ```

### ⚙️ 配置说明

#### 模型路径配置

PDF 解析程序需要下载相应的模型文件。模型文件默认存储在 `driver/models` 目录下：

```json
// conf/magic-pdf.json
{
  "models-dir": "driver/models/opendatalab/PDF-Extract-Kit-1___0/models",
  "layoutreader-model-dir": "driver/models/ppaanngggg/layoutreader",
  "device-mode": "cpu"
}
```

#### 解析配置选项

```json
{
  "parser_config": {
    "layout_recognize": "MinerU",  // 解析方式：MinerU, DeepDOC, Plain Text
    "extractor": {
      "keyvalues": []  // 自定义提取字段
    }
  }
}
```

### 🔧 高级配置

#### 1. 自定义模型路径

如果需要使用自定义模型，可以修改 `conf/magic-pdf.json` 文件：

```json
{
  "models-dir": "/path/to/your/models",
  "layoutreader-model-dir": "/path/to/your/layoutreader/models"
}
```

#### 2. 设备配置

```json
{
  "device-mode": "cpu",  // 或 "cuda" 用于 GPU 加速
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

#### 3. 解析参数调整

```python
# 在代码中调整解析参数
parser_config = {
    "layout_recognize": "MinerU",
    "from_page": 0,        # 起始页码
    "to_page": 100,        # 结束页码
    "zoomin": 3,           # 缩放因子
    "callback": progress_callback  # 进度回调函数
}
```

### 📊 解析结果说明

#### MinerU 解析结果包含：

1. **文本内容**: 提取的文本内容，包含位置信息
2. **布局分析**: 文档布局结构分析结果
3. **表格识别**: 表格结构识别和内容提取
4. **图片内容**: 图片中的文本和内容描述
5. **公式识别**: 数学公式识别和 LaTeX 转换
6. **Markdown 输出**: 结构化的 Markdown 格式输出

#### 结果文件：

- `{document_name}.md`: Markdown 格式的解析结果
- `{document_name}_layout.pdf`: 布局分析可视化结果
- `{document_name}_content_list.json`: 结构化内容列表
- `images/`: 提取的图片和表格图片

### 🛠️ 故障排除

#### 常见问题：

1. **模型文件下载失败**
   ```bash
   # 手动下载模型文件
   cd driver
   python download_models.py
   ```

2. **内存不足**
   ```bash
   # 调整设备配置为 CPU 模式
   # 修改 conf/magic-pdf.json 中的 "device-mode": "cpu"
   ```

3. **解析速度慢**
   ```bash
   # 使用 GPU 加速（如果可用）
   # 修改 conf/magic-pdf.json 中的 "device-mode": "cuda"
   ```

4. **特定格式解析失败**
   ```bash
   # 尝试不同的解析方式
   # MinerU -> DeepDOC -> Plain Text
   ```

#### 日志查看：

```bash
# 查看解析日志
docker-compose logs -f ragforge

# 查看详细错误信息
docker-compose logs ragforge | grep -i error
```

### 📝 示例代码

#### Python 代码示例：

```python
from minerU.parser import MinerUPdf

# 创建解析器实例
pdf_parser = MinerUPdf()

# 解析 PDF 文件
def progress_callback(**kwargs):
    print(f"进度: {kwargs.get('prog', 0)}, 消息: {kwargs.get('msg', '')}")

result = pdf_parser.call_function(
    bucketname='your_bucket',
    filename='document.pdf',
    kb_id='your_kb_id',
    doc_id='your_doc_id',
    tenant_id='your_tenant_id',
    parser_config={'layout_recognize': 'MinerU'},
    pdf_flag=True,
    callback=progress_callback
)
```

#### 测试示例：

```bash
# 运行测试
cd tests
python test_minerU.py
```

---

## 🔧 源码编译
```bash
# 在项目根目录执行
docker build -f Dockerfile -t ragforge:latest .
```

### 构建 Web 控制台镜像
```bash
# 在 web 目录执行
cd web
docker build -f Dockerfile -t ragforge-web:latest .
```

### 多架构支持
项目支持 x86_64 和 ARM64 架构。在 ARM64 平台（如 Apple Silicon Mac）上构建时，Docker 会自动使用适合的架构。

### 构建优化
- 使用 `--no-cache` 参数强制重新构建：`docker build --no-cache -f Dockerfile -t ragforge:latest .`
- 使用多阶段构建减少镜像大小（可选）
- 构建时间约 10-15 分钟，取决于网络和硬件性能


## 🤝 商务合作

如有商务合作需求，请联系：business@btdata.com.cn

如需参与社区技术交流，可加群：

<img src="https://ragforge-bucket.oss-cn-hangzhou.aliyuncs.com/wechat.png" alt="RAGForge 社区交流群" width="200" height="200" />
---

**注意**：开发环境配置仅用于本地开发和测试，不要在生产环境中使用。
