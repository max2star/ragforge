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
import os
from openai import OpenAI

import base64

#  base 64 编码格式
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
base64_image = encode_image("/var/lib/gpustack/ragforge/ragforge/tests/tmp/c5c310783e9011f0a89298039b6e4778.jpg")

client = OpenAI(
    #api_key=os.getenv("DASHSCOPE_API_KEY"),
    api_key = "sk-d065862c06754b26813e9d220b9a4f18",#sk-886e90542f6e4f90b13d295ebbcfe739",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

completion = client.chat.completions.create(
    model="qwen-vl-max-latest", # 此处以qwen-vl-max-latest为例，可按需更换模型名称。模型列表：https://help.aliyun.com/model-studio/getting-started/models
    messages=[
        {
            "role": "system",
            "content": [{"type": "text", "text": "提取图中的：['标题','作者','发布时间']，请你以JSON格式输出，不要输出```json```代码段。"}],
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                        #"url": "http://101.52.216.178:19000/8484f36c2cbe11f09962f6470b0b23dc/minerU/WechatIMG3140.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=U22S01P37H16EQFJCNF5%2F20250515%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20250515T130730Z&X-Amz-Expires=43200&X-Amz-Security-Token=eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3NLZXkiOiJVMjJTMDFQMzdIMTZFUUZKQ05GNSIsImV4cCI6MTc0NzM1NjczMiwicGFyZW50IjoicmFnX2Zsb3cifQ.XHPb1m4Wf19aArVYzRW2fcJ9JNT7XzZuLlZeGkBL0fbbQy8mKS7BeCOiLJyabA0r-6oG6vExMUil5HxNJ3hnKw&X-Amz-SignedHeaders=host&versionId=null&X-Amz-Signature=0014d76785d9671d84d1f24ff6aa3e5698f58dee1947853e7df9bf2b939c58b4"
                    },
                },
                {"type": "text", "text": "提取图中的：['标题','作者','发布时间','资料来源','摘要']，请你以JSON格式输出，不要输出```json```代码段。"},
            ],
        },
    ],
)

print(completion.choices[0].message.content)
