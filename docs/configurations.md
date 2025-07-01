---
sidebar_position: 1
slug: /configurations
---

# 配置

通过 Docker 部署 RAGFlow 的配置。

## 指南

在系统配置方面，您需要管理以下文件：

- [.env](https://github.com/infiniflow/ragflow/blob/main/docker/.env)：包含 Docker 的重要环境变量。
- [service_conf.yaml.template](https://github.com/infiniflow/ragflow/blob/main/docker/service_conf.yaml.template)：配置后端服务。它指定 RAGFlow 的系统级配置，由其 API 服务器和任务执行器使用。容器启动时，`service_conf.yaml` 文件将基于此模板文件生成。此过程替换模板中的任何环境变量，允许根据容器环境进行动态配置。
- [docker-compose.yml](https://github.com/infiniflow/ragflow/blob/main/docker/docker-compose.yml)：用于启动 RAGFlow 服务的 Docker Compose 文件。

要更新默认 HTTP 服务端口 (80)，请转到 [docker-compose.yml](https://github.com/infiniflow/ragflow/blob/main/docker/docker-compose.yml) 并将 `80:80` 更改为 `<YOUR_SERVING_PORT>:80`。

:::tip 注意
上述配置的更新需要重启所有容器才能生效：

```bash
docker compose -f docker/docker-compose.yml up -d
```

:::

## Docker Compose

- **docker-compose.yml**  
  Sets up environment for RAGFlow and its dependencies.
- **docker-compose-base.yml**  
  Sets up environment for RAGFlow's dependencies: Elasticsearch/[Infinity](https://github.com/infiniflow/infinity), MySQL, MinIO, and Redis.

:::danger IMPORTANT
We do not actively maintain **docker-compose-CN-oc9.yml**, **docker-compose-gpu-CN-oc9.yml**, or **docker-compose-gpu.yml**, so use them at your own risk. However, you are welcome to file a pull request to improve any of them.
:::

## Docker environment variables

The [.env](https://github.com/infiniflow/ragflow/blob/main/docker/.env) file contains important environment variables for Docker.

### Elasticsearch

- `STACK_VERSION`  
  The version of Elasticsearch. Defaults to `8.11.3`
- `ES_PORT`  
  The port used to expose the Elasticsearch service to the host machine, allowing **external** access to the service running inside the Docker container.  Defaults to `1200`.
- `ELASTIC_PASSWORD`  
  The password for Elasticsearch.

### Kibana

- `KIBANA_PORT`  
  The port used to expose the Kibana service to the host machine, allowing **external** access to the service running inside the Docker container. Defaults to `6601`.
- `KIBANA_USER`  
  The username for Kibana. Defaults to `rag_flow`.
- `KIBANA_PASSWORD`  
  The password for Kibana. Defaults to `infini_rag_flow`.

### Resource management

- `MEM_LIMIT`  
  The maximum amount of the memory, in bytes, that *a specific* Docker container can use while running. Defaults to `8073741824`.

### MySQL

- `MYSQL_PASSWORD`  
  The password for MySQL.
- `MYSQL_PORT`  
  The port used to expose the MySQL service to the host machine, allowing **external** access to the MySQL database running inside the Docker container. Defaults to `5455`.

### MinIO

RAGFlow utilizes MinIO as its object storage solution, leveraging its scalability to store and manage all uploaded files.

- `MINIO_CONSOLE_PORT`  
  The port used to expose the MinIO console interface to the host machine, allowing **external** access to the web-based console running inside the Docker container. Defaults to `9001`
- `MINIO_PORT`  
  The port used to expose the MinIO API service to the host machine, allowing **external** access to the MinIO object storage service running inside the Docker container. Defaults to `9000`.
- `MINIO_USER`  
  The username for MinIO.
- `MINIO_PASSWORD`  
  The password for MinIO.

### Redis

- `REDIS_PORT`  
  The port used to expose the Redis service to the host machine, allowing **external** access to the Redis service running inside the Docker container. Defaults to `6379`.
- `REDIS_PASSWORD`  
  The password for Redis.

### RAGFlow

- `SVR_HTTP_PORT`  
  The port used to expose RAGFlow's HTTP API service to the host machine, allowing **external** access to the service running inside the Docker container. Defaults to `9380`.
- `RAGFLOW-IMAGE`  
  The Docker image edition. Available editions:  
  
  - `infiniflow/ragflow:v0.18.0-slim` (default): The RAGFlow Docker image without embedding models.  
  - `infiniflow/ragflow:v0.18.0`: The RAGFlow Docker image with embedding models including:
    - Built-in embedding models:
      - `BAAI/bge-large-zh-v1.5` 
      - `maidalun1020/bce-embedding-base_v1`


:::tip NOTE  
If you cannot download the RAGFlow Docker image, try the following mirrors.  

- For the `nightly-slim` edition:  
  - `RAGFLOW_IMAGE=swr.cn-north-4.myhuaweicloud.com/infiniflow/ragflow:nightly-slim` or,
  - `RAGFLOW_IMAGE=registry.cn-hangzhou.aliyuncs.com/infiniflow/ragflow:nightly-slim`.
- For the `nightly` edition:  
  - `RAGFLOW_IMAGE=swr.cn-north-4.myhuaweicloud.com/infiniflow/ragflow:nightly` or,
  - `RAGFLOW_IMAGE=registry.cn-hangzhou.aliyuncs.com/infiniflow/ragflow:nightly`.
:::

### Timezone

- `TIMEZONE`  
  The local time zone. Defaults to `'Asia/Shanghai'`.

### Hugging Face mirror site

- `HF_ENDPOINT`  
  The mirror site for huggingface.co. It is disabled by default. You can uncomment this line if you have limited access to the primary Hugging Face domain.

### MacOS

- `MACOS`  
  Optimizations for macOS. It is disabled by default. You can uncomment this line if your OS is macOS.

## Service configuration

[service_conf.yaml.template](https://github.com/infiniflow/ragflow/blob/main/docker/service_conf.yaml.template) specifies the system-level configuration for RAGFlow and is used by its API server and task executor.

### `ragflow`

- `host`: The API server's IP address inside the Docker container. Defaults to `0.0.0.0`.
- `port`: The API server's serving port inside the Docker container. Defaults to `9380`.

### `mysql`
  
- `name`: The MySQL database name. Defaults to `rag_flow`.
- `user`: The username for MySQL.
- `password`: The password for MySQL.
- `port`: The MySQL serving port inside the Docker container. Defaults to `3306`.
- `max_connections`: The maximum number of concurrent connections to the MySQL database. Defaults to `100`.
- `stale_timeout`: Timeout in seconds.

### `minio`
  
- `user`: The username for MinIO.
- `password`: The password for MinIO.
- `host`: The MinIO serving IP *and* port inside the Docker container. Defaults to `minio:9000`.

### `oauth`  

The OAuth configuration for signing up or signing in to RAGFlow using a third-party account.  It is disabled by default. To enable this feature, uncomment the corresponding lines in **service_conf.yaml.template**.

- `github`: The GitHub authentication settings for your application. Visit the [GitHub Developer Settings](https://github.com/settings/developers) page to obtain your client_id and secret_key.

### `user_default_llm`  

The default LLM to use for a new RAGFlow user. It is disabled by default. To enable this feature, uncomment the corresponding lines in **service_conf.yaml.template**.  

- `factory`: The LLM supplier. Available options:
  - `"OpenAI"`
  - `"DeepSeek"`
  - `"Moonshot"`
  - `"Tongyi-Qianwen"`
  - `"VolcEngine"`
  - `"ZHIPU-AI"`
- `api_key`: The API key for the specified LLM. You will need to apply for your model API key online.

:::tip NOTE  
If you do not set the default LLM here, configure the default LLM on the **Settings** page in the RAGFlow UI.
:::