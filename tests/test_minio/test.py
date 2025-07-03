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

# 配置主集群和目标集群信息
PRIMARY_ENDPOINT = "https://101.52.216.178:19000"
PRIMARY_ACCESS_KEY = ""
PRIMARY_SECRET_KEY = ""

SECONDARY_ENDPOINT = "https://101.52.216.178:29000"
SECONDARY_ACCESS_KEY = ""
SECONDARY_SECRET_KEY = ""

from minio import Minio
from minio.commonconfig import ENABLED  # ENABLED 仍位于 commonconfig
from minio.replicationconfig import (  # 从 replicationconfig 导入复制相关类
    ReplicationConfig,
    Rule,
    DeleteMarkerReplication,
    Destination,
    Status,
)
from datetime import datetime

# 其他代码保持不变...

def configure_bucket_replication(bucket_name):
    # 初始化客户端、创建 Bucket 等代码不变...

    # 修改复制规则的构造方式
    rule = Rule(
        status=ENABLED,  # 使用 Status.ENABLED 替代直接 ENABLED
        priority=1,
        delete_marker_replication=DeleteMarkerReplication(
            status=ENABLED
        ),
        destination=Destination(
            bucket=dest_arn,
            access_key=SECONDARY_ACCESS_KEY,
            secret_key=SECONDARY_SECRET_KEY,
            endpoint=f"http://{SECONDARY_ENDPOINT}",
        ),
    )

    replication_config = ReplicationConfig(
        role="",  # MinIO 中 role 可留空
        rules=[rule]
    )

    primary_client.set_bucket_replication(bucket_name, replication_config)


if __name__ == "__main__":
    bucket_name = "my-replicated-bucket"
    configure_bucket_replication(bucket_name)
