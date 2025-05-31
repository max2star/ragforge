import requests
from  loguru import logger
import os
api_key = "IjdjZmU1MzdlMzlmNTExZjBiMGRiZDZkNjQ4N2ZkY2QyIg.aDQBaQ.vTuWgkZLGxeKHtAzHpdeofCM0o0"
api_key = "IjU2MDUyZGFlMzlmNzExZjBiNjAwZDZkNjQ4N2ZkY2QyIg.aDQEgw.lipz37V11BwOWDeoQSlpGpBxb6k"
headers = {
    'Authorization': f'{api_key}',
    'Accept':"application/json",
    #'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json',
}

#api/apps/api_app.py和api/apps/sdk/doc.py都提供了retrieval召回的接口。它们的参数有所差异。
#其中api/apps/api_app.py为
#retrieval = "http://101.52.216.178/v1/api/retrieval"
#api/apps/sdk/doc.py为
retrieval = "http://101.52.216.178/v1/kb/list"
data = {
       "owner_ids": ["61989cb4339e11f0abc3ce16978df45e","566715d8370311f09e1f9a03ebf94012","a9a202dc354e11f0b64462e2928833bd"],
        }
import json
response = requests.post(retrieval, headers=headers, data=json.dumps(data))
response.raise_for_status()  # Check if request was successful
json_res = response.json()
if json_res:
    print(json_res)
    #print(len(json_res['data']['files']))
#print(response.headers['Authorization'])
