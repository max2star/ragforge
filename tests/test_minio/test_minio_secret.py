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
import io
from minio import Minio
from minio.sse import SseCustomerKey,Sse


import os
os.environ['SSL_CERT_FILE']='/var/lib/gpustack/ragforge/ragforge/docker/nginx/public.crt'
PRIMARY_ENDPOINT = "101.52.216.178:19000"
PRIMARY_ACCESS_KEY = "rag_flow"
PRIMARY_SECRET_KEY = "infini_rag_flow"

client = Minio(
    PRIMARY_ENDPOINT,
    access_key=PRIMARY_ACCESS_KEY,
    secret_key=PRIMARY_SECRET_KEY,
    secure=True
)

# 设置SSE-C加密
customer_key = SseCustomerKey(b"32byteslongsecretkeymustprovided")
content = b"Hello MinIO! This is a sample text object."  # 要上传的内容
data_stream = io.BytesIO(content)
data_length = len(content)

bucket_name = "maxiao"
client.put_object(
       bucket_name=bucket_name,
       object_name='test',
       data=data_stream,
       length=data_length,
       content_type="text/plain",
       sse=customer_key
   )

encryption_config = client.get_bucket_encryption("test001")
print(encryption_config)

response = client.get_object(bucket_name=bucket_name,object_name='test',ssec=customer_key)
print(response.read())

## 上传对象时使用SSE-C
#client.put_object(
#    "my-bucket", "my-object", content, data_length, sse=customer_key
#)
