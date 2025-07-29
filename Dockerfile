# 使用Python 3.10作为基础镜像
FROM python:3.10-slim

# 兼容新版 debian，换源前先判断文件是否存在
RUN if [ -f /etc/apt/sources.list ]; then \
      sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list && \
      sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list; \
    fi && \
    if [ -f /etc/apt/sources.list.d/debian.sources ]; then \
      sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources && \
      sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources; \
    fi

# 设置工作目录
WORKDIR /ragforge

# 设置环境变量
ENV PYTHONPATH=/ragforge
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# 安装系统依赖，带重试机制
RUN set -eux; \
    for i in 1 2 3; do \
      apt-get update --fix-missing && \
      apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    wget \
    git \
    build-essential \
    pkg-config \
    libicu-dev \
    libglib2.0-0 \
    libglx-mesa0 \
    libgl1 \
    libgdiplus \
    default-jdk \
    libatk-bridge2.0-0 \
    libpython3-dev \
    libgtk-4-1 \
    libnss3 \
    xdg-utils \
    libgbm-dev \
    libjemalloc-dev \
    libreoffice \
    libreoffice-l10n-zh-cn \
    fonts-wqy-zenhei \
    fonts-wqy-microhei \
    unixodbc \
    unixodbc-dev \
      && rm -rf /var/lib/apt/lists/* && break || sleep 5; \
    done

# 安装uv包管理器，使用国内镜像源和重试机制
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ --trusted-host pypi.tuna.tsinghua.edu.cn uv || \
    pip install -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com uv || \
    pip install uv

# 复制项目文件
COPY pyproject.toml uv.lock ./
COPY api/ ./api/
COPY rag/ ./rag/
COPY conf/ ./conf/
COPY deepdoc/ ./deepdoc/
COPY agent/ ./agent/
COPY minerU/ ./minerU/
COPY tests/ ./tests/
COPY graphrag/ ./graphrag/
COPY agentic_reasoning/ ./agentic_reasoning/
COPY mcp/ ./mcp/
# COPY sdk/ ./sdk/  # 已删除
# COPY helm/ ./helm/  # 已删除
# COPY intergrations/ ./intergrations/  # 已删除
# COPY flask_session/ ./flask_session/  # 目录不存在，已删除

# 安装Python依赖，使用国内镜像源
RUN uv sync --python 3.10 --frozen --index-url https://pypi.tuna.tsinghua.edu.cn/simple/ || \
    uv sync --python 3.10 --frozen --index-url https://mirrors.aliyun.com/pypi/simple/ || \
    uv sync --python 3.10 --frozen

# 下载NLTK数据
RUN .venv/bin/python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('averaged_perceptron_tagger'); nltk.download('wordnet'); nltk.download('stopwords')"

# 创建必要的目录
RUN mkdir -p /ragforge/logs /root/.ragforge

# 设置入口点，使用虚拟环境中的Python
ENTRYPOINT [".venv/bin/python", "api/ragforge_server.py"]

# 环境变量说明：
# 数据库配置：
# - RAGFORGE_MYSQL_HOST: MySQL主机地址 (默认: localhost)
# - RAGFORGE_MYSQL_PORT: MySQL端口 (默认: 3306)
# - RAGFORGE_MYSQL_USER: MySQL用户名 (默认: root)
# - RAGFORGE_MYSQL_PASSWORD: MySQL密码 (默认: ragforge123)
# - RAGFORGE_MYSQL_DBNAME: MySQL数据库名 (默认: rag_flow)
#
# Elasticsearch配置：
# - RAGFORGE_ES_HOSTS: Elasticsearch地址 (默认: http://localhost:9200)
# - RAGFORGE_ES_USERNAME: Elasticsearch用户名 (默认: elastic)
# - RAGFORGE_ES_PASSWORD: Elasticsearch密码 (默认: 空密码)
#
# MinIO配置：
# - RAGFORGE_MINIO_HOST: MinIO地址 (默认: localhost:9000)
# - RAGFORGE_MINIO_USER: MinIO用户名 (默认: minioadmin)
# - RAGFORGE_MINIO_PASSWORD: MinIO密码 (默认: minioadmin)
#
# Redis配置：
# - RAGFORGE_REDIS_HOST: Redis地址 (默认: localhost)
# - RAGFORGE_REDIS_PORT: Redis端口 (默认: 6379)
# - RAGFORGE_REDIS_PASSWORD: Redis密码 (默认: ragforge123)
#
# 使用示例：
# docker run -e RAGFORGE_MYSQL_HOST=mysql-server -e RAGFORGE_ES_HOSTS=http://es-server:9200 ragforge-simple:latest 