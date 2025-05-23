import requests
from  loguru import logger
import os
api_key = "ImZjZmFlZTZhMzZhZTExZjBhNDQ2YTIxNmU5YTJkMGU4Ig.aC6CpA.sy7PQoMcTuJQTHYzRrPYmJY3GZ0"
api_key = "ragflow-RjMDk1MTQ2MzZjNzExZjA5MjM0YTI1ZT"
headers = {
    #'Authorization': f'{api_key}',
    'Accept':"application/json",
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json',
}

#api/apps/api_app.py和api/apps/sdk/doc.py都提供了retrieval召回的接口。它们的参数有所差异。
#其中api/apps/api_app.py为
#retrieval = "http://101.52.216.178/v1/api/retrieval"
#api/apps/sdk/doc.py为
retrieval = "http://101.52.216.178/api/v1/retrieval"
data = {
       "question": "Previous Advanced Fuel Cycle Initiative (AFCI) studies were made to assess the effects of the existing accumulation of LWR spent fuel in the United States on the capability to partitiontransmute actinides using existing an",#将 水泵 充满 蒸馏水 打开 水泵 冲 是很重要的步骤吗",
       #api/apps/sdk/doc.py使用的
       "dataset_ids": ["a9a202dc354e11f0b64462e2928833bd"],
       #api/apps/api_app.py使用的
       "kb_id":["a9a202dc354e11f0b64462e2928833bd"],
        }
import json
response = requests.post(retrieval, headers=headers, data=json.dumps(data))
response.raise_for_status()  # Check if request was successful
json_res = response.json()
if json_res:
    print(json_res)
    #print(len(json_res['data']['files']))
#print(response.headers['Authorization'])
