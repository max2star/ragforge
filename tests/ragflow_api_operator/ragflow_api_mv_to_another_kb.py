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
import requests
from  loguru import logger
import os
api_key = "IjIyNjlhM2FjMzRjYjExZjA4ZTUxM2FlMmQ2MzQzNjFmIg.aCtW3g.32EvX_KGr2thFbXD6qCkZ4WQpTE"#ImQ0ZjI1M2MyMzQ0MjExZjBiZjE4NjI2YTIwNTRkMThhIg.aCpyMQ.crnAlGYDxjvZvYXYgbzP-2f4F90"
headers = {
    'Authorization': f'{api_key}',
    'Accept':"application/json",
    #'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json',
}

mv_doc_kb = "http://101.52.216.178/v1/document/mv_kb"
data = {
    #"doc_id":"0686fdde32cc11f0a8d4e2c7bf1d9f90",
    #"doc_id":"0bc03d44322f11f09dab9616e0e925dd",
    "doc_ids":["8b89384c33aa11f09816c66e26712cba",'7f8697f233ae11f088383a16057ad21f','15e9a70833ae11f0a9013a16057ad21f','813ccf1633aa11f08673c66e26712cba'],
    #"src_kb_id":"55081d7a339f11f08200ce16978df45e",
    #"dst_kb_id":"ed5f2368344211f0a747626a2054d18a",
    "src_kb_id":"ed5f2368344211f0a747626a2054d18a",
    "dst_kb_id":"55081d7a339f11f08200ce16978df45e",
    "page":1,
    "size":10,
    "keywords":""
}
import json
response = requests.post(mv_doc_kb, headers=headers, data=json.dumps(data))
response.raise_for_status()  # Check if request was successful
json_res = response.json()
if json_res:
    print(json_res)
    #print(len(json_res['data']['files']))
