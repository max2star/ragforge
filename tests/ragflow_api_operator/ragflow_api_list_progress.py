import requests
from  loguru import logger
import os
api_key = "ImUxZTZjZWQwMzc4MjExZjA4OWFiNDIzYTFjMTZkMjk2Ig.aC_mJA.94HxMz_rQpU-tJep9x1h7eFCK_Y"
headers = {
    'Authorization': f'{api_key}',
    'Accept':"application/json",
    #'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json',
}

#获取Chunks的API
list_chunks = "http://101.52.216.178/v1/document/infos"
data = {
    #"doc_id":"0686fdde32cc11f0a8d4e2c7bf1d9f90",
    "doc_ids":["e92909a236eb11f0a1524674195f8099"],
    #"doc_id":"fb7f9a8632cb11f0b107e2c7bf1d9f90",
    "page":1,
    "size":10,
}
import json
response = requests.post(list_chunks, headers=headers, data=json.dumps(data))
response.raise_for_status()  # Check if request was successful
json_res = response.json()
if json_res:
    print(json_res)
    #print(len(json_res['data']['files']))
