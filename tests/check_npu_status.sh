LOG_FILE="/var/log/npu1_service_monitor.log"

# 记录日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

LOG_FILE="/var/log/npu_service_monitor.log"

log "start.............."

# 检查NPU卡1进程(Qwen2.5-vl-32b-instruct)
if npu-smi info -t proc-mem -i 1 | grep "mindie_llm_back"; then
    echo "[$(date '+%F %T')] NPU卡1的mindie_llm_back服务运行正常" | tee -a $LOG_FILE
        log "Qwen2.5-vl-32b-instruct服务运行正常"
else
    echo "[$(date '+%F %T')] NPU卡1的mindie_llm_back服务未运行" | tee -a $LOG_FILE
    # 执行恢复命令
    docker stop 4428337658c0
    if docker start 4428337658c0 >/dev/null 2>&1; then
        docker exec -d 4428337658c0 /bin/bash -c \
            "cd /usr/local/Ascend/mindie/latest/mindie-service/bin/ && \
            nohup ./mindieservice_daemon > output.out 2>&1 &"
        log "Qwen2.5-vl-32b-instruct服务启动命令已执行"
    else
        log "Qwen2.5-vl-32b-instruct错误：容器启动失败"
    fi
fi

log "start......2........"

# 检查NPU卡4进程(bge-m3)
if npu-smi info -t proc-mem -i 2 | grep "python-text-emb"; then
    echo "[$(date '+%F %T')] NPU卡2的python-text-emb服务运行正常" | tee -a $LOG_FILE
        log "bge-m3服务运行正常"
else
    echo "[$(date '+%F %T')] NPU卡2的python-text-emb服务未运行" | tee -a $LOG_FILE
    # 执行恢复命令
    docker stop dbcf1a404385
    if docker start dbcf1a404385 >/dev/null 2>&1; then
        docker exec -d dbcf1a404385 /bin/bash -c \
            "export ASCEND_RT_VISIBLE_DEVICES=2 && \
            nohup bash start.sh BAAI/bge-m3 118.193.126.254 8080 > output.out 2>&1 &"
        log "bge-m3服务启动命令已运行"
    else
        log "bge-m3错误：容器启动失败"
    fi
fi

log "start.......3......."

# 检查NPU卡5进程(bge-reranker-v2-m3)
if npu-smi info -t proc-mem -i 2 | grep "python-text-emb"; then
    echo "[$(date '+%F %T')] NPU卡2的python-text-emb服务运行正常" | tee -a $LOG_FILE
        log "bge-reranker-v2-m3服务运行正常"
    exit 0
else
    echo "[$(date '+%F %T')] NPU卡2的python-text-emb服务未运行" | tee -a $LOG_FILE
    # 执行恢复命令
    docker stop 48d9a0c48599
    if docker start 48d9a0c48599 >/dev/null 2>&1; then
        docker exec -d 48d9a0c48599 /bin/bash -c \
            "export ASCEND_RT_VISIBLE_DEVICES=2 && \
            nohup bash start.sh BAAI/bge-reranker-v2-m3 118.193.126.254 1111 > output.out 2>&1 &"
        log "bge-reranker-v2-m3服务启动命令已执行"
    else
        log "bge-reranker-v2-m3错误：容器启动失败"
    fi
fi

# 执行命令crontab -e
# */5 * * * * /path/to/script.sh
