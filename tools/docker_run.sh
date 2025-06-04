git clone https://github.com/infiniflow/ragflow.git
cd ragflow/
#运行uv lock
uv lock
export HF_ENDPOINT=https://hf-mirror.com
export https_proxy=http://81.70.135.187:8118
export http_proxy=http://81.70.135.187:8118
#wget https://storage.googleapis.com/chrome-for-testing-public/121.0.6167.85/linux64/chrome-linux64.zip
#wget https://storage.googleapis.com/chrome-for-testing-public/121.0.6167.85/linux64/chromedriver-linux64.zip
uv run download_deps.py --china-mirrors
docker build -f Dockerfile.deps -t infiniflow/ragflow_deps .
docker build -f Dockerfile -t infiniflow/ragflow:nightly .
