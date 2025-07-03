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
import os
os.environ['SSL_CERT_FILE']='/var/lib/gpustack/ragforge/ragforge/docker/nginx/public.crt'


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
    response = primary_client.list_objects("51b9b08c361711f0a8f03e04d146f0ba",recursive=True)
    for obj in response:
        print(obj.object_name)
    # Read data from response.
finally:
    if response:
        response.close()
