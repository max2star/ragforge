import requests
from  loguru import logger
import os
import json
headers = {
    'Accept':"application/json",
    'Content-Type': 'application/json',
}
base_ip_port = "http://101.52.216.178"
log_in_url = f"{base_ip_port}/v1/user/login"
data = {"email":"M@M.test",
        #密钥使用公钥加密
        "password":"opGETT2FDaJyhPjwvQYQlg2TWUN2CXk92bUeFbNm8e/Z5n9c9N2/zJsAQzidMJKRnokG3I46wemCiBpFBHiPjZaJz9nJ+6lCP/d7t08H6zV/xq6bETAr1qjOR8gizvUDdm+RQIrql/VPt1YfHNlYYkmu4z4JPQjWKzZBUgbuC7EF75Zc3gpp60KKG0S+OP3MdPRmobwmN3JaSlAghOu9kuIBDQ8wO+rZQVgyjKYS722EBfehSNSCC/zkCg3YSbXSHd3j9z+eiBP2KOOq/rYNal2H53zEzbMdwpRvlyc4fj0osPF+og19gHQYzFE1o1xIrDky1+wkRRiDYdOm4FLF+Q=="
        }
response = requests.post(log_in_url, headers=headers, data=json.dumps(data))
response.raise_for_status()  # Check if request was successful
json_res = response.json()
#if json_res:
#    print(json_res)
#    #print(len(json_res['data']['files']))
api_key = response.headers['Authorization']

user_id =  json_res['data']['id']

print(user_id)

#list_user_id


print(response.headers['Authorization'])

headers = {
    'Authorization': f'{api_key}',
    'Accept':"application/json",
    'Content-Type': 'application/json',
}

list_kbs = f"{base_ip_port}/v1/kb/list"
data_post = {
       #"owner_ids": [user_id]
}
response = requests.post(list_kbs, headers=headers, data=json.dumps(data_post))
response.raise_for_status()  # Check if request was successful
json_res = response.json()
if json_res:
    print(json_res)
    #print(json_res['data']['kbs'])
    #for kb in json_res['data']['kbs']:
    #    print(kb['tenant_id'])
