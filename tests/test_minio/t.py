from minio import Minio
import os
os.environ['SSL_CERT_FILE']='/var/lib/gpustack/ragflow/ragflow/docker/nginx/public.crt'


PRIMARY_ENDPOINT = "101.52.216.178:19000"
PRIMARY_ACCESS_KEY = "rag_flow"
PRIMARY_SECRET_KEY = "infini_rag_flow"

primary_client = Minio(
    PRIMARY_ENDPOINT,
    access_key=PRIMARY_ACCESS_KEY,
    secret_key=PRIMARY_SECRET_KEY,
    secure=True# 若用 HTTPS 改为 True
)


buckets = primary_client.list_buckets()
#for bucket in buckets:
#    print(bucket.name, bucket.creation_date)

# Get data of an object.
response = None
try:
    response = primary_client.list_objects("maxiao")
    for obj in response:
        print(obj.owner_id())
    # Read data from response.
finally:
    if response:
        response.close()
