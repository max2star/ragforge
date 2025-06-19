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
if __name__ == "__main__":
    import sys
    import numpy as np
    from openai import OpenAI
    #client = OpenAI(api_key='gpustack_3c3306069544b759_ea80926d3a80bef2f199944249d6ce89', base_url='http://101.52.216.178:890/v1-openai')
    ##client = OpenAI( api_key="ollama",base_url='http://10.1.60.39:11434/v1')
    #res = client.embeddings.create(input='test',#[truncate('test', 8191)],
    #    model='bge-m3',encoding_format="float" )
    #print(res)
    #print("MaXiao encode OpenAIEmbed length {}".format(len(res.data[0].embedding)))
    #print("MaXiao encode OpenAIEmbed length {}".format(len(np.array(res.data[0].embedding))))

    model = "deepseek-r1-70B-Q8" #'deepseek-v3'
    base_url = "http://101.52.216.178:890/v1-openai"
    api_key = "gpustack_e17331aefa8790c4_e02d061feb7ca3d0ede4fdf926b50559"
    client = OpenAI(
        api_key = api_key,
        base_url = base_url
    )
    print("MaXiao 创建会话")
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "你是谁，用中文回答",
            }
        ],
        model=model,
    )
    print("MaXiao 结束会话")
    print('model',model,chat_completion)
    print('model',model,chat_completion.choices[0].message.content)
