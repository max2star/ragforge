import requests
from  loguru import logger
import os
doc_id = "b1d2fb6c379e11f08c294e79a2571c31"

api_key = "ImQ1OTQzYzgwMzg2ODExZjA4OTY5OTZmMzI5NzRmYjBlIg.aDFn7w.VnBOVJTjYbz8isxb8OO8bbAjAks"
headers = {
    'Authorization': f'{api_key}',
    #'Accept':"application/json",
    #'Content-Type': 'application/json',
}

list_chunks = "http://101.52.216.178/v1/document/infos"
data = {
    "doc_ids":['e92909a236eb11f0a1524674195f8099','140e1c4a36c211f0ad414230d86429e9'],
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
