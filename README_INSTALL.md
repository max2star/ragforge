# RAGForge 一键安装指南

## 🚀 快速开始

### 一键安装（推荐）

```bash
curl -fsSL https://raw.githubusercontent.com/zhaozhilong1993/ragforge/main/install.sh | bash
```

这个命令会自动完成以下操作：
1. ✅ 检查系统要求
2. 📦 下载 RAGForge 源码
3. 🐍 安装 Python 依赖
4. 🐳 启动 Docker 服务
5. 🚀 启动 RAGForge 服务器

### 系统要求

在运行安装脚本之前，请确保您的系统已安装：

- **Python 3.10+** - [下载地址](https://python.org)
- **Docker** - [下载地址](https://docker.com)
- **Docker Compose** - 通常随 Docker 一起安装
- **Git** - [下载地址](https://git-scm.com)

## 📋 安装步骤详解

### 1. 检查系统要求
脚本会自动检查：
- 操作系统兼容性
- Python 版本
- Docker 和 Docker Compose
- Git

### 2. 设置项目目录
- 默认安装到：`$HOME/ragforge`
- 如果目录已存在，会询问是否重新安装

### 3. 下载源码
- 从 GitHub 克隆最新代码
- 如果已存在则跳过下载

### 4. 安装依赖
- 自动安装 `uv` 包管理器（如果未安装）
- 创建 Python 虚拟环境
- 安装所有 Python 依赖

### 5. 启动服务
- 启动所有 Docker 容器（MySQL、Redis、Elasticsearch、MinIO）
- 等待服务完全启动
- 启动 RAGForge 服务器

## 🌐 访问服务

安装完成后，您可以访问：

- **Web 界面**: http://localhost:9380
- **API 文档**: http://localhost:9380/apidocs/

## 🛠️ 常用命令

### 重新启动服务
```bash
cd ~/ragforge
./start.sh
```

### 启动 Docker 服务
```bash
cd ~/ragforge/docker
docker-compose up -d
```

### 停止 Docker 服务
```bash
cd ~/ragforge/docker
docker-compose down
```

### 查看服务状态
```bash
cd ~/ragforge/docker
docker-compose ps
```

### 查看日志
```bash
cd ~/ragforge/docker
docker-compose logs -f
```

## 📁 项目结构

安装完成后，项目结构如下：

```
~/ragforge/
├── api/                    # API 服务
├── docker/                 # Docker 配置
├── agent/                  # 智能体模块
├── rag/                    # RAG 核心
├── web/                    # Web 前端
├── .venv/                  # Python 虚拟环境
├── start.sh               # 启动脚本
└── install.sh             # 安装脚本
```

## 🔧 故障排除

### 常见问题

1. **Python 版本过低**
   ```
   错误: Python3 未安装或版本过低
   解决: 安装 Python 3.10+
   ```

2. **Docker 未启动**
   ```
   错误: Docker 未安装或未启动
   解决: 安装并启动 Docker
   ```

3. **端口被占用**
   ```
   错误: 端口 9380 被占用
   解决: 停止占用端口的服务或修改端口
   ```

4. **Docker 容器启动失败**
   ```bash
   cd ~/ragforge/docker
   docker-compose logs
   ```

### 手动安装

如果自动安装失败，可以手动执行：

```bash
# 1. 克隆仓库
git clone https://github.com/zhaozhilong1993/ragforge.git
cd ragforge

# 2. 安装依赖
uv sync --python 3.10

# 3. 启动 Docker 服务
cd docker
docker-compose up -d

# 4. 启动服务器
cd ..
source .venv/bin/activate
python api/ragforge_server.py
```

## 📞 获取帮助

- **GitHub Issues**: [提交问题](https://github.com/zhaozhilong1993/ragforge/issues)
- **文档**: [查看完整文档](https://ragforge.ai)
- **社区**: [加入讨论](https://github.com/zhaozhilong1993/ragforge/discussions)

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。 