#/etc/sysctl.conf最后一行追加
#vm.max_map_count=2097152
#sysctl -w vm.max_map_count=2097152
cd ../
export HF_ENDPOINT=https://hf-mirror.com
export https_proxy=http://81.70.135.187:8118
export http_proxy=http://81.70.135.187:8118
docker build -f Dockerfile -t infiniflow/ragforge:nightly .
