import requests
from  loguru import logger
import os
api_key = "ImYyOWE3ZTY4MzJjYjExZjA5NjcxZTJjN2JmMWQ5ZjkwIg.aCf9PQ.dMfQoy2WXLR3MM5rYUc88pPHl2s"
api_key = "ImJkYTUxMjYwMzJlYzExZjA4NzJjOWFjN2ViNzE2YTEzIg.aCg0Qg.flAbWjDK5hgrwElQkRtraHbSlqE"
headers = {
    'Authorization': f'{api_key}',
    'Accept':"application/json",
    #'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json',
}

#获取Chunks的API
list_chunks = "http://101.52.216.178/v1/chunk/list"
data = {
    #"doc_id":"0686fdde32cc11f0a8d4e2c7bf1d9f90",
    "doc_id":"0bc03d44322f11f09dab9616e0e925dd",
    #"doc_id":"fb7f9a8632cb11f0b107e2c7bf1d9f90",
    "page":1,
    "size":10,
    "keywords":""
}
import json
response = requests.post(list_chunks, headers=headers, data=json.dumps(data))
response.raise_for_status()  # Check if request was successful
json_res = response.json()
if json_res:
    print(json_res)
    #print(len(json_res['data']['files']))
