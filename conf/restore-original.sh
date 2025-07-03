#!/bin/bash

# 恢复原配置脚本
echo "恢复原配置..."

if [ -f "service_conf.yaml.backup" ]; then
    echo "从备份文件恢复原配置..."
    cp service_conf.yaml.backup service_conf.yaml
    echo "原配置已恢复！"
else
    echo "错误：找不到备份文件 service_conf.yaml.backup"
    echo "请确保之前运行过 switch-to-dev.sh 脚本"
    exit 1
fi 