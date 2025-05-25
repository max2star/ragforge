from minio import Minio
from minio.commonconfig import ENABLED
from minio.replicationconfig import (
    ReplicationConfig,
    Rule,
    DeleteMarkerReplication,
    Destination,
    Status
)
from minio.versioningconfig import VersioningConfig  # ✅ 新版导入路径

PRIMARY_ENDPOINT = "101.52.216.178:19000"
PRIMARY_ACCESS_KEY = "rag_flow"
PRIMARY_SECRET_KEY = "infini_rag_flow"

SECONDARY_ENDPOINT = "101.52.216.178:29000"
SECONDARY_ACCESS_KEY = "rag_flow"
SECONDARY_SECRET_KEY = "infini_rag_flow_another"
import os
from minio.replicationconfig import Destination
os.environ['SSL_CERT_FILE']='/var/lib/gpustack/ragflow/ragflow/docker/nginx/public.crt'

def configure_bucket_replication(bucket_name):
    primary_client = Minio(
        PRIMARY_ENDPOINT,
        access_key=PRIMARY_ACCESS_KEY,
        secret_key=PRIMARY_SECRET_KEY,
        secure=True
    )

    if not primary_client.bucket_exists(bucket_name):
        primary_client.make_bucket(bucket_name)
        print(f"Bucket {bucket_name} 创建成功。")

    primary_client.set_bucket_versioning(bucket_name, VersioningConfig(ENABLED))
    dest_arn = f"arn:aws:s3:::{bucket_name}"

    # 新版 SDK (>=8.0.0) 的正确写法
    destination = Destination(
        dest_arn,  # ✅ 直接指定目标 ARN
        access_key=SECONDARY_ACCESS_KEY,
        secret_key=SECONDARY_SECRET_KEY,
        endpoint=f"https://101.52.216.178:29000",
    )


    rule = Rule(
        status=ENABLED,
        priority=1,
        delete_marker_replication=DeleteMarkerReplication(
            status=ENABLED
        ),
        destination = destination,
    )

    replication_config = ReplicationConfig(
        role="",
        rules=[rule]
    )

    primary_client.set_bucket_replication(bucket_name, replication_config)
    print(f"Bucket {bucket_name} 复制策略配置完成。")

if __name__ == "__main__":
    configure_bucket_replication("my-bucket")
