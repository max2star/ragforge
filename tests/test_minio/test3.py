#
#  Copyright 2024 The InfiniFlow Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
from minio import Minio
from minio.versioningconfig import VersioningConfig  # ✅ 新版导入路径
from minio.commonconfig import ENABLED
from minio.error import S3Error
from minio.replicationconfig import (
    ReplicationConfig,
    Rule,
    DeleteMarkerReplication,
    Destination,
    Status,
)
import os
os.environ['SSL_CERT_FILE']='/var/lib/gpustack/ragflow/ragflow/docker/nginx/public.crt'


PRIMARY_ENDPOINT = "101.52.216.178:19000"
PRIMARY_ACCESS_KEY = "rag_flow"
PRIMARY_SECRET_KEY = "infini_rag_flow"

SECONDARY_ENDPOINT = "101.52.216.178:29000"
SECONDARY_ACCESS_KEY = "rag_flow"
SECONDARY_SECRET_KEY = "infini_rag_flow_another"

SECONDARY_BUCKET = "backup-bucket"  # 目标 Bucket 名称

import boto3
# 初始化MinIO客户端
client = boto3.client('s3', endpoint_url="https://"+PRIMARY_ENDPOINT, aws_access_key_id=PRIMARY_ACCESS_KEY, aws_secret_access_key=PRIMARY_SECRET_KEY,verify=False)
#client = boto3.client('s3', endpoint_url='https://101.52.216.178:29000', aws_access_key_id=SECONDARY_ACCESS_KEY, aws_secret_access_key=SECONDARY_SECRET_KEY,verify=False)
# 列出存储桶
response = client.list_buckets()
print('response',response)


def configure_bucket_replication(bucket_name):
    try:
        # 初始化主集群客户端
        primary_client = Minio(
            PRIMARY_ENDPOINT,
            access_key=PRIMARY_ACCESS_KEY,
            secret_key=PRIMARY_SECRET_KEY,
            secure=True# 若用 HTTPS 改为 True
        )

        # 1. 创建 Bucket（如果不存在）
        if not primary_client.bucket_exists(bucket_name):
            primary_client.make_bucket(bucket_name)
            print(f"Bucket {bucket_name} 创建成功。")

        # 2. 启用版本控制（必需）
        primary_client.set_bucket_versioning(
            bucket_name,
            VersioningConfig(ENABLED)
        )

        # 初始化主集群客户端
        second_client = Minio(
            SECONDARY_ENDPOINT,
            access_key=SECONDARY_ACCESS_KEY,
            secret_key=SECONDARY_SECRET_KEY,
            secure=True# 若用 HTTPS 改为 True
        )

        # 1. 创建 Bucket（如果不存在）
        if not second_client.bucket_exists(bucket_name):
            second_client.make_bucket(bucket_name)
            print(f"Bucket {bucket_name} 创建成功。")

        # 2. 启用版本控制（必需）
        second_client.set_bucket_versioning(
            bucket_name,
            VersioningConfig(ENABLED)
        )
        dest_arn = "https://rag_flow:infini_rag_flow_another@101.52.216.178:29000/maxiao"
        #dest_arn = f"arn:s3:replication:ded6c710-f7bb-41c8-8a0d-f4d240f5d840:{bucket_name}"
        dest_arn = "arn:minio:replication::ded6c710-f7bb-41c8-8a0d-f4d240f5d840:{bucket_name}"

        #config = primary_client.get_bucket_replication(f"{bucket_name}")
        #print(f"current config {str(config.toxml(element=None))}")
        #print(f"current config {config},config arn {config.__file__}")
        config = ReplicationConfig(
            "",#"REPLACE-WITH-ACTUAL-ROLE",
            [
                Rule(
                    Destination(
                      dest_arn #"REPLACE-WITH-ACTUAL-DESTINATION-BUCKET-ARN",#" dest_arn,#"REPLACE-WITH-ACTUAL-DESTINATION-BUCKET-ARN",
                    ),
                    ENABLED,
                    delete_marker_replication=DeleteMarkerReplication(
                        ENABLED,
                    ),
                    #rule_filter=Filter(
                    #    AndOperator(
                    #        "TaxDocs",
                    #        {"key1": "value1", "key2": "value2"},
                    #    ),
                    #),
                    rule_id="rule1",
                    priority=1,
                ),
            ],
        )
        primary_client.set_bucket_replication(f"{bucket_name}", config)
        config = primary_client.get_bucket_replication(f"{bucket_name}")
        print(config)


       # dest_arn = f"arn:aws:s3:::{bucket_name}"

       # # 3. 配置复制规则
       # # 定义目标集群信息（SDK 7.x 使用 bucket 参数）
       # destination = Destination(
       #     bucket_arn=SECONDARY_BUCKET,  # ✅ 7.x 版本用 bucket 参数
       #     access_key=SECONDARY_ACCESS_KEY,
       #     secret_key=SECONDARY_SECRET_KEY,
       #     endpoint=f"http://{SECONDARY_ENDPOINT}",  # 注意协议前缀
       # )


       # # 定义复制规则
       # rule = Rule(
       #     status=Status.ENABLED,
       #     priority=1,
       #     delete_marker_replication=DeleteMarkerReplication(status=Status.ENABLED),
       #     destination=destination,
       # )

       # # 创建复制配置
       # replication_config = ReplicationConfig(
       #     role="",  # MinIO 中可留空
       #     rules=[rule]
       # )

       # # 应用复制策略
       # primary_client.set_bucket_replication(bucket_name, replication_config)
       # print(f"Bucket {bucket_name} 的复制策略配置完成。")

    except S3Error as e:
        print(f"MinIO 操作失败: {e}")

if __name__ == "__main__":
    bucket_name = "maxiao-3"
    configure_bucket_replication(bucket_name)
