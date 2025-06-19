<div align="center">
<a href="https://demo.ragflow.io/">
<img src="web/src/assets/logo-with-text.png" width="350" alt="NewRAGflow logo">
</a>
</div>

<p align="center">
  <a href="./README.md">English</a> |
  <a href="./README_zh.md">简体中文</a> |
  <a href="./README_tzh.md">繁体中文</a> |
</p>

## 💡 NewRAGflow 是什么？

NewRAGflow 是基于 RAGFlow 进行功能增强的开源 RAG（Retrieval-Augmented Generation）引擎。在保持原有 RAGFlow 核心功能的基础上，新增了多项企业级功能增强，为开发人员提供更强大的 RAG 解决方案。

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

| 功能特性 | 开源版 | 企业版 |
|---------|--------|--------|
| **核心 RAG 功能** | ✅ | ✅ |
| **深度文档理解** | ✅ | ✅ |
| **智能文本处理** | ✅ | ✅ |
| **自动化 RAG 工作流** | ✅ | ✅ |
| **MinerU 集成** | ✅ | ✅ |
| **国产数据库支持** | ❌ | ✅ |
| **ARM 架构支持** | ❌ | ✅ |
| **华为 910B NPU 支持** | ❌ | ✅ |

## 🌈 功能增强-企业版

- **MinerU 集成**：无缝集成 MinerU 功能，提供增强的数据挖掘和分析能力
- **国产数据库支持**：新增对达梦数据库的兼容性支持，为企业级中国数据库系统提供强大支持
- **ARM 架构支持**：完整支持基于 ARM 的系统，使其能够在更广泛的硬件平台上部署
- **华为 910B NPU 支持**：优化了对华为昇腾 910B NPU 的支持，提供加速的 AI 计算能力

## 🎬 快速开始

### 📋 系统要求
- CPU >= 4 核
- RAM >= 16 GB
- Disk >= 50 GB
- Docker >= 24.0.0 & Docker Compose >= v2.26.1

### 🚀 快速部署

1. **克隆项目**
   ```bash
   git clone https://github.com/infiniflow/ragflow.git
   cd ragflow/docker
   ```

2. **启动服务**
   ```bash
   # CPU 版本
   docker compose -f docker-compose.yml up -d
   
   # GPU 版本（加速 embedding 和 DeepDoc 任务）
   # docker compose -f docker-compose-gpu.yml up -d
   ```

3. **验证启动**
   ```bash
   docker logs -f ragflow-server
   ```

4. **访问系统**
   - 浏览器访问：`http://YOUR_SERVER_IP`
   - 配置 LLM API Key：编辑 `service_conf.yaml.template`

### ⚙️ 配置说明

- **.env**：基础环境变量（端口、密码等）
- **service_conf.yaml.template**：后端服务配置
- **docker-compose.yml**：容器编排配置

## 🔧 开发指南

### 源码编译
```bash
# 不含 embedding 模型的轻量版本（约 2GB）
docker build -f Dockerfile -t newragflow:slim .

# 完整版本（约 9GB）
docker build -f Dockerfile -t newragflow:full .
```

### ARM 架构支持
如需在 ARM64 平台运行，请参考[构建指南](https://ragflow.io/docs/dev/build_docker_image)自行编译镜像。

## 📚 文档资源

- [API 文档](https://ragflow.io/docs/dev/category/api)
- [配置指南](https://ragflow.io/docs/dev/category/configuration)
- [部署指南](https://ragflow.io/docs/dev/category/deployment)

## 🤝 商务合作

如有商务合作需求，请联系：business@infiniflow.com
