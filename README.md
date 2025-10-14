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

### 📖 **详细文档**
- [产品官网](http://www.ragforge.cn) - RAGForge 官方网站
- [在线文档](http://www.ragforge.cn/docs/) - 完整的产品文档
- [RAG 模块使用指南](rag/README.md) - 检索增强生成功能详解
- [命令行工具](https://github.com/max2star/ragforge-shell/blob/main/README.md) - CLI 工具使用指南

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

## 🚀 快速开始

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

### 🔧 开发环境

#### Docker 开发环境（推荐）
```bash
cd docker
./start.sh   # 选择 2 启动开发环境
```

#### Python 源码启动
```bash
# 安装依赖
pip install uv
uv sync --python 3.10 --all-extras

# 启动基础服务
docker compose -f docker/docker-compose-base.yml up -d

# 启动 RAGForge 服务器
./start.sh
```

### 🔍 故障排除

**Docker 服务启动失败**：
- 端口冲突：修改 `.env` 文件中的端口配置
- 镜像拉取失败：检查网络或更换镜像源

**API 连接失败**：
- 检查 Docker 服务状态：`docker-compose ps`
- 检查端口映射和防火墙

## 📁 项目结构

```
ragforge/
├── 📄 核心模块
│   ├── api/                    # RESTful API 服务
│   │   ├── apps/              # API 应用模块
│   │   ├── db/                # 数据库模型和服务
│   │   ├── utils/             # 工具函数
│   │   └── ragforge_server.py # 主服务器入口
│   ├── rag/                   # 检索增强生成核心模块
│   │   ├── app/               # 应用层（文档处理、问答等）
│   │   ├── llm/               # 大语言模型集成
│   │   ├── nlp/               # 自然语言处理
│   │   ├── svr/               # 服务层
│   │   │   └── task_executor.py # 文档解析任务执行器（核心）
│   │   └── utils/             # RAG 工具函数
│   └── web/                   # 前端控制台
│       ├── src/               # 源代码
│       ├── public/            # 静态资源
│       └── package.json       # 前端依赖配置
│
├── 📄 文档处理模块
│   ├── minerU/                # 智能文档解析器
│   │   └── parser/            # PDF、Word、PPT、Excel 解析
│   ├── deepdoc/               # 传统文档解析
│   │   ├── parser/            # 基础文本提取
│   │   └── vision/            # 视觉识别（OCR、布局）
│   └── graphrag/              # 图数据库增强 RAG
│
├── 🤖 智能模块
│   ├── agent/                 # 智能代理模块
│   │   ├── component/         # 代理组件
│   │   └── templates/         # 代理模板
│   └── agentic_reasoning/     # 智能推理模块
│
├── 🛠️ 工具模块
│   ├── ragforge-shell/        # 命令行工具
│   ├── driver/                # 模型驱动
│   │   ├── models/            # AI 模型文件
│   │   └── download_models.py # 模型下载脚本
│   └── tools/                 # 辅助工具
│
├── ⚙️ 配置和部署
│   ├── conf/                  # 配置文件
│   │   ├── service_conf.yaml  # 服务配置
│   │   ├── magic-pdf.json     # PDF 解析配置
│   │   └── llm_factories.json # LLM 工厂配置
│   ├── docker/                # Docker 部署
│   ├── Dockerfile             # 主镜像构建
│   └── start.sh               # 启动脚本
│
├── 📚 文档和测试
│   ├── docs/                  # 项目文档
│   ├── tests/                 # 测试用例
│   └── README.md              # 项目说明
│
└── 🔧 开发工具
    ├── pyproject.toml         # Python 项目配置
    ├── uv.lock               # 依赖锁定文件
    └── .github/              # GitHub 配置
```

## 📚 模块说明

### 🔧 **核心模块**
- **RAG**: 检索增强生成核心模块，提供智能检索和答案生成功能
- **API**: RESTful API 服务，提供完整的接口支持
- **Web**: 前端控制台，提供直观的 Web 管理界面

### 📄 **文档处理模块**
- **MinerU**: 基于深度学习的智能文档解析器，支持 PDF、Word、PPT、Excel
- **DeepDOC**: 传统文档解析模块，提供基础文本提取和布局识别
- **GraphRAG**: 图数据库增强的 RAG 功能

### 🤖 **智能模块**
- **Agent**: 智能代理模块，支持复杂任务编排
- **Agentic Reasoning**: 智能推理模块，提供深度研究能力

### 🛠️ **工具模块**
- **RAGForge Shell**: 命令行工具，提供完整的 CLI 操作界面
- **Driver**: 模型驱动模块，管理各种 AI 模型

---

## 🔧 源码编译

```bash
# 构建 RAGForge 镜像
docker build -f Dockerfile -t ragforge:latest .

# 构建 Web 控制台镜像
cd web
docker build -f Dockerfile -t ragforge-web:latest .
```

**多架构支持**: 项目支持 x86_64 和 ARM64 架构，Docker 会自动选择适合的架构。


## 🤝 商务合作

如有商务合作需求，请联系：business@btdata.com.cn

如需参与社区技术交流，可加群：

<img src="https://ragforge-bucket.oss-cn-hangzhou.aliyuncs.com/wechat.png" alt="RAGForge 社区交流群" width="200" height="200" />
---

**注意**：开发环境配置仅用于本地开发和测试，不要在生产环境中使用。
