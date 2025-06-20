<div align="center">
<a href="https://demo.ragflow.io/">
<img src="web/src/assets/logo-with-text.png" width="520" alt="NewRAGflow logo">
</a>
</div>

<p align="center">
  <a href="./README.md">English</a> |
  <a href="./README_zh.md">简体中文</a> |
  <a href="./README_tzh.md">繁体中文</a> |
  <a href="./README_ja.md">日本語</a> |
  <a href="./README_ko.md">한국어</a> |
  <a href="./README_id.md">Bahasa Indonesia</a> |
  <a href="/README_pt_br.md">Português (Brasil)</a>
</p>

<p align="center">
    <a href="https://x.com/intent/follow?screen_name=infiniflowai" target="_blank">
        <img src="https://img.shields.io/twitter/follow/infiniflow?logo=X&color=%20%23f5f5f5" alt="follow on X(Twitter)">
    </a>
    <a href="https://demo.ragflow.io" target="_blank">
        <img alt="Static Badge" src="https://img.shields.io/badge/Online-Demo-4e6b99">
    </a>
    <a href="https://hub.docker.com/r/infiniflow/ragflow" target="_blank">
        <img src="https://img.shields.io/badge/docker_pull-ragflow:v0.18.0-brightgreen" alt="docker pull infiniflow/ragflow:v0.18.0">
    </a>
    <a href="https://github.com/infiniflow/ragflow/releases/latest">
        <img src="https://img.shields.io/github/v/release/infiniflow/ragflow?color=blue&label=Latest%20Release" alt="Latest Release">
    </a>
    <a href="https://github.com/infiniflow/ragflow/blob/main/LICENSE">
        <img height="21" src="https://img.shields.io/badge/License-Apache--2.0-ffffff?labelColor=d4eaf7&color=2e6cc4" alt="license">
    </a>
</p>

<h4 align="center">
  <a href="https://ragflow.io/docs/dev/">Document</a> |
  <a href="https://github.com/infiniflow/ragflow/issues/4214">Roadmap</a> |
  <a href="https://twitter.com/infiniflowai">Twitter</a> |
  <a href="https://discord.gg/NjYzJD3GM3">Discord</a> |
  <a href="https://demo.ragflow.io">Demo</a>
</h4>

<details open>
<summary><b>📕 Table of Contents</b></summary>

- 💡 [What is NewRAGflow?](#-what-is-newragflow)
- 🎮 [Demo](#-demo)
- 📌 [Latest Updates](#-latest-updates)
- 🌟 [Core Features](#-core-features)
- 🔎 [System Architecture](#-system-architecture)
- 🎬 [Get Started](#-get-started)
- 🔧 [Configurations](#-configurations)
- 🔧 [Build a docker image without embedding models](#-build-a-docker-image-without-embedding-models)
- 🔧 [Build a docker image including embedding models](#-build-a-docker-image-including-embedding-models)
- 🔨 [Launch service from source for development](#-launch-service-from-source-for-development)
- 📚 [Documentation](#-documentation)
- 📜 [Roadmap](#-roadmap)
- 🏄 [Community](#-community)
- 🙌 [Contributing](#-contributing)

</details>

## 💡 What is NewRAGflow?

NewRAGflow is an open-source RAG (Retrieval-Augmented Generation) engine based on RAGFlow with enhanced enterprise features. While maintaining the core functionality of RAGFlow, it adds multiple enterprise-level enhancements to provide developers with a more powerful RAG solution.

## 🎮 Demo

Try our demo at [https://demo.ragflow.io](https://demo.ragflow.io).

<div align="center" style="margin-top:20px;margin-bottom:20px;">
<img src="https://github.com/infiniflow/ragflow/assets/7248/2f6baa3e-1092-4f11-866d-36f6a9d075e5" width="1200"/>
<img src="https://github.com/user-attachments/assets/504bbbf1-c9f7-4d83-8cc5-e9cb63c26db6" width="1200"/>
</div>

## 🔥 Latest Updates

- 2025-03-19 Supports using a multi-modal model to make sense of images within PDF or DOCX files.
- 2025-02-28 Combined with Internet search (Tavily), supports reasoning like Deep Research for any LLMs.
- 2025-01-26 Optimizes knowledge graph extraction and application, offering various configuration options.
- 2024-12-18 Upgrades Document Layout Analysis model in DeepDoc.
- 2024-11-01 Adds keyword extraction and related question generation to the parsed chunks to improve the accuracy of retrieval.
- 2024-08-22 Support text to SQL statements through RAG.

## 🎉 Stay Tuned

⭐️ Star our repository to stay up-to-date with exciting new features and improvements! Get instant notifications for new
releases! 🌟

<div align="center" style="margin-top:20px;margin-bottom:20px;">
<img src="https://github.com/user-attachments/assets/18c9707e-b8aa-4caf-a154-037089c105ba" width="1200"/>
</div>

## 🌟 Core Features

### 🔍 **Deep Document Understanding**
- Based on deep document understanding to extract knowledge from complex unstructured data
- Supports Word, PPT, Excel, PDF, images, web pages and more formats

### 🧠 **Intelligent Text Processing**
- Template-based intelligent text chunking
- Multi-path retrieval with fused re-ranking
- Grounded answer generation with reduced hallucinations

### 🚀 **Automated RAG Workflow**
- Complete RAG orchestration process
- Configurable LLM and vector models
- Easy-to-use API interfaces

## 📊 Version Comparison

| Features | Open Source | Enterprise |
|----------|-------------|------------|
| **Core RAG Features** | ✅ | ✅ |
| **Deep Document Understanding** | ✅ | ✅ |
| **Intelligent Text Processing** | ✅ | ✅ |
| **Automated RAG Workflow** | ✅ | ✅ |
| **MinerU Integration** | ✅ | ✅ |
| **Domestic Database Support** | ❌ | ✅ |
| **ARM Architecture Support** | ❌ | ✅ |
| **Huawei 910B NPU Support** | ❌ | ✅ |
| **VLM Keyvalue Extractor** | ❌ | ✅ |
| **ES/Minio/Executor Cluster** | ❌ | ✅ |

## 🌈 Enhanced Features - Enterprise Edition

- **MinerU Integration**: Seamlessly integrated MinerU functionality for enhanced data mining and analysis capabilities
- **Domestic Database Support**: Added compatibility with DM (达梦) database, providing robust support for enterprise-grade Chinese database systems
- **ARM Architecture Support**: Full compatibility with ARM-based systems, enabling deployment on a wider range of hardware platforms
- **Huawei 910B NPU Support**: Optimized performance with Huawei Ascend 910B NPU support, offering accelerated AI computing capabilities

## 🔎 System Architecture

<div align="center" style="margin-top:20px;margin-bottom:20px;">
<img src="https://github.com/infiniflow/ragflow/assets/12318111/d6ac5664-c237-4200-a7c2-a4a00691b485" width="1000"/>
</div>

## 🎬 Get Started

### 📋 System Requirements
- CPU >= 4 cores
- RAM >= 16 GB
- Disk >= 50 GB
- Docker >= 24.0.0 & Docker Compose >= v2.26.1

### 🚀 Quick Deployment

1. **Clone the repository**
   ```bash
   git clone https://github.com/infiniflow/ragflow.git
   cd ragflow/docker
   ```

2. **Start the service**
   ```bash
   # CPU version
   docker compose -f docker-compose.yml up -d
   
   # GPU version (accelerate embedding and DeepDoc tasks)
   # docker compose -f docker-compose-gpu.yml up -d
   ```

3. **Verify startup**
   ```bash
   docker logs -f ragflow-server
   ```

4. **Access the system**
   - Browser access: `http://YOUR_SERVER_IP`
   - Configure LLM API Key: Edit `service_conf.yaml.template`

### ⚙️ Configuration

- **.env**: Basic environment variables (ports, passwords, etc.)
- **service_conf.yaml.template**: Backend service configuration
- **docker-compose.yml**: Container orchestration configuration

## 🔧 Configurations

When it comes to system configurations, you will need to manage the following files:

- [.env](./docker/.env): Keeps the fundamental setups for the system, such as `SVR_HTTP_PORT`, `MYSQL_PASSWORD`, and
  `MINIO_PASSWORD`.
- [service_conf.yaml.template](./docker/service_conf.yaml.template): Configures the back-end services. The environment variables in this file will be automatically populated when the Docker container starts. Any environment variables set within the Docker container will be available for use, allowing you to customize service behavior based on the deployment environment.
- [docker-compose.yml](./docker/docker-compose.yml): The system relies on [docker-compose.yml](./docker/docker-compose.yml) to start up.

> The [./docker/README](./docker/README.md) file provides a detailed description of the environment settings and service
> configurations which can be used as `${ENV_VARS}` in the [service_conf.yaml.template](./docker/service_conf.yaml.template) file.

To update the default HTTP serving port (80), go to [docker-compose.yml](./docker/docker-compose.yml) and change `80:80`
to `<YOUR_SERVING_PORT>:80`.

Updates to the above configurations require a reboot of all containers to take effect:

> ```bash
> $ docker compose -f docker-compose.yml up -d
> ```

### Switch doc engine from Elasticsearch to Infinity

RAGFlow uses Elasticsearch by default for storing full text and vectors. To switch to [Infinity](https://github.com/infiniflow/infinity/), follow these steps:

1. Stop all running containers:

   ```bash
   $ docker compose -f docker/docker-compose.yml down -v
   ```

> [!WARNING]
> `-v` will delete the docker container volumes, and the existing data will be cleared.

2. Set `DOC_ENGINE` in **docker/.env** to `infinity`.

3. Start the containers:

   ```bash
   $ docker compose -f docker-compose.yml up -d
   ```

> [!WARNING]
> Switching to Infinity on a Linux/arm64 machine is not yet officially supported.

## 🔧 Build a Docker image without embedding models

This image is approximately 2 GB in size and relies on external LLM and embedding services.

```bash
git clone https://github.com/infiniflow/ragflow.git
cd ragflow/
docker build --platform linux/amd64 --build-arg LIGHTEN=1 -f Dockerfile -t infiniflow/ragflow:nightly-slim .
```

## 🔧 Build a Docker image including embedding models

This image is approximately 9 GB in size. As it includes embedding models, it relies on external LLM services only.

```bash
git clone https://github.com/infiniflow/ragflow.git
cd ragflow/
docker build --platform linux/amd64 -f Dockerfile -t infiniflow/ragflow:nightly .
```

## 🔨 Launch service from source for development

1. Install uv, or skip this step if it is already installed:

   ```bash
   pipx install uv
   ```

2. Clone the source code and install Python dependencies:

   ```bash
   git clone https://github.com/infiniflow/ragflow.git
   cd ragflow/
   uv sync --python 3.10 --all-extras # install RAGFlow dependent python modules
   ```

3. Launch the dependent services (MinIO, Elasticsearch, Redis, and MySQL) using Docker Compose:

   ```bash
   docker compose -f docker/docker-compose-base.yml up -d
   ```

   Add the following line to `/etc/hosts` to resolve all hosts specified in **docker/.env** to `127.0.0.1`:

   ```
   127.0.0.1       es01 infinity mysql minio redis
   ```

4. If you cannot access HuggingFace, set the `HF_ENDPOINT` environment variable to use a mirror site:

   ```bash
   export HF_ENDPOINT=https://hf-mirror.com
   ```

5. Launch backend service:

   ```bash
   source .venv/bin/activate
   export PYTHONPATH=$(pwd)
   bash docker/launch_backend_service.sh
   ```

6. Install frontend dependencies:
   ```bash
   cd web
   npm install
   ```
7. Launch frontend service:

   ```bash
   npm run dev
   ```

   _The following output confirms a successful launch of the system:_

   ![](https://github.com/user-attachments/assets/0daf462c-a24d-4496-a66f-92533534e187)

## 📚 Documentation

- [API Documentation](https://ragflow.io/docs/dev/category/api)
- [Configuration Guide](https://ragflow.io/docs/dev/category/configuration)
- [Deployment Guide](https://ragflow.io/docs/dev/category/deployment)

## 📜 Roadmap

See the [RAGFlow Roadmap 2025](https://github.com/infiniflow/ragflow/issues/4214)

## 🏄 Community

- [Discord](https://discord.gg/NjYzJD3GM3)
- [Twitter](https://twitter.com/infiniflowai)
- [GitHub Discussions](https://github.com/orgs/infiniflow/discussions)

## 🙌 Contributing

RAGFlow flourishes via open-source collaboration. In this spirit, we embrace diverse contributions from the community.
If you would like to be a part, review our [Contribution Guidelines](./CONTRIBUTING.md) first.
