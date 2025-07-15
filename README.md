<div align="center">
<a href="https://demo.ragforge.io/">
<img src="conf/logo-with-text.png" width="100" alt="RAGForge logo">
</a>
</div>

<p align="center">
  <a href="./README_en.md">English</a> |
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
| **国产数据库支持** | ❌ | ✅ | ✅ |
| **ARM 架构支持** | ❌ | ✅ | ✅ |
| **华为 910B NPU 支持** | ❌ | ✅ | ✅ |
| **高级文档处理** | ❌ | ✅ | ✅ |
| **自定义模型支持** | ❌ | ✅ | ✅ |
| **企业级技术支持** | ❌ | ❌ | ✅ |
| **私有化部署** | ❌ | ❌ | ✅ |
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

### 📋 系统要求
- CPU >= 4 核
- RAM >= 16 GB
- Disk >= 50 GB
- Docker >= 24.0.0 & Docker Compose >= v2.26.1

### 🚀 快速部署

1. **克隆项目**
   ```bash
   git clone https://gitee.com/wow_ai/ragforge.git
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

## 🔧 源码编译

### 构建 RAGForge 镜像
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

---

**注意**：开发环境配置仅用于本地开发和测试，不要在生产环境中使用。
