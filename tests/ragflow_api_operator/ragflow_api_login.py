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
#api_key = "ragflow-RiZDg3ZjBjMzQ2MTExZjBiNTE0YmU3ZG"
headers = {
#    'Authorization': f'{api_key}',
    'Accept':"application/json",
    #'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json',
}

log_in_url = "http://101.52.216.178/v1/user/login"
#http://101.52.216.178/v1/document/mv_kb"
data = {"email":"M@M.test",
        #密钥使用公钥加密
        "password":"opGETT2FDaJyhPjwvQYQlg2TWUN2CXk92bUeFbNm8e/Z5n9c9N2/zJsAQzidMJKRnokG3I46wemCiBpFBHiPjZaJz9nJ+6lCP/d7t08H6zV/xq6bETAr1qjOR8gizvUDdm+RQIrql/VPt1YfHNlYYkmu4z4JPQjWKzZBUgbuC7EF75Zc3gpp60KKG0S+OP3MdPRmobwmN3JaSlAghOu9kuIBDQ8wO+rZQVgyjKYS722EBfehSNSCC/zkCg3YSbXSHd3j9z+eiBP2KOOq/rYNal2H53zEzbMdwpRvlyc4fj0osPF+og19gHQYzFE1o1xIrDky1+wkRRiDYdOm4FLF+Q=="
        }
import json
response = requests.post(log_in_url, headers=headers, data=json.dumps(data))
response.raise_for_status()  # Check if request was successful
json_res = response.json()
if json_res:
    print(json_res)
    #print(len(json_res['data']['files']))
print(response.headers['Authorization'])
