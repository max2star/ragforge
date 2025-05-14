git clone https://github.com/infiniflow/ragflow.git
cd ragflow/
#运行uv lock
uv lock
export HF_ENDPOINT=https://hf-mirror.com
export https_proxy=http://81.70.135.187:8118
export http_proxy=http://81.70.135.187:8118
uv run download_deps.py
docker build -f Dockerfile.deps -t infiniflow/ragflow_deps .
docker build -f Dockerfile -t infiniflow/ragflow:nightly .
