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
result_ids = []
base_url_for_doc = "http://101.52.216.178/v1/knowledgebases/documents/"
api_key = "IjEzNTJhMGZjMWY5MTExZjA4NmQ1NGE4NzhjZDc3OGVhIg.aAe6CA.xpRFlzt6uW6_hkNYx1kBHIKSu_8"
api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluIiwiZXhwIjoxNzQ1MzgzMzY2fQ.bz3tMLpMw3WSQ5PFrERMZ4eHciYcMD6Oe_qrwJdaznA"
knowleadge_base ="f5231bfa9a6e43869409ced931b7dbb3" #"6aed75aa4dc8482abde74f48bd097cb4"
headers = {
    #'Authorization': f'{api_key}',
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json',
}
list_kb_docs = "http://101.52.216.178:3333/api/v1/knowledgebases/"+knowleadge_base+"/documents?currentPage=1&size=10000"
# 服务器接收文件的URL
url_upload_file = 'http://101.52.216.178:3333/api/v1/files/upload'  # 替换为你的实际URL
#url_upload_file = "http://101.52.216.178/v1/document/upload"
#
#response = requests.get(list_files,headers=headers,timeout=5) 
#response.raise_for_status()  # Check if request was successful
#json_res = response.json()
#data = {'file_ids':[],"parent_id":""}
#if json_res:
#    print(len(json_res['data']['files']))
#    for doc in json_res['data']['files']:
#        print(doc['id'])
#        doc_url = base_url_for_doc +doc['id']
#        doc_url = base_url_for_doc
#        data['file_ids'].append(doc['id'])
#    print(data)
#    response = requests.post(f"{base_url_for_doc}",data = data,headers=headers,timeout=5)
#        #response = requests.delete(f"{doc_url}",headers=headers,timeout=5)
#        # 输出响应结果
#    print(response.text)
#data = {}
#response = requests.get(list_kb_docs,headers=headers,timeout=5) 
#response.raise_for_status()  # Check if request was successful
#json_res = response.json()
#if json_res:
#    print(len(json_res['data']['list']))
#    for doc in json_res['data']['list']:
#        print(doc['id'])
#        doc_url = base_url_for_doc +doc['id']
#        response = requests.delete(f"{doc_url}",headers=headers,timeout=5)
#        # 输出响应结果
#        print(response.text)
#
#
#
#
#
#files_up  = [
#]
## 服务器接收文件的URL
#url = url_upload_file
## 要上传的文件路径
#directory = './原文'
#file_number = 0 
#for root, dirs, files in os.walk(directory):
#    for file in files:
#        file_path = os.path.join(root, file)
#        logger.info("当前正在处理的文件是 {},文件名称 {}".format(file_path,file))
#        #if file!='Y1498462.pdf':
#        #    continue
#        #files_up.append(('file',(file, open(file_path, 'rb'), 'application/pdf')))
#        files_up.append(('files',(file, open(file_path, 'rb'), 'application/pdf')))
#        file_number = file_number + 1
#        if file_number>=50:
#            break
#        if len(files_up)>=5:
#            print("开始提交,当前file number  {}".format(file_number))
#            # 如果需要附加其他表单字段
#            data = {
#                #'kb_id':'19df303e1f9111f087d74a878cd778ea'
#            }
#            #file_path = os.path.join(root, file)
#            #files_up = {'files':(file,open(file_path, 'rb'))}
#            print(files_up)
#            try:
#            
#                headers = {
#                    #'Authorization': f'{api_key}',
#                    'Authorization': f'Bearer {api_key}',
#                    #一定不要带这个，否则服务端，找不到 request.files中的files
#                    #    'Content-Type': 'application/json',
#                }
#                # 发送POST请求
#                response = requests.post(url, headers=headers,files=files_up, data=data)
#                print(response.encoding)  # 查看当前解码编码（Requests自动判断的）
#                print(response.headers['Content-Type'])  # 查看服务器声明的编码
#                json_res = response.json()
#                print('json_res',json_res)
#                for rest in json_res['data']:
#                    result_ids.append(rest['id'])
#            
#            except requests.exceptions.RequestException as e:
#                print(f'Request failed: {e}')
#            except FileNotFoundError:
#                print(f'File not found: {file_path}')
#            except Exception as e:
#                print(f'Error occurred: {e}')
#            print("结束提交,当前file number  {}".format(file_number))
#            files_up = []
#
#if len(files_up)>=1:
#    print("开始提交,当前file number  {}".format(file_number))
#    # 如果需要附加其他表单字段
#    data = {
#        #'kb_id':'19df303e1f9111f087d74a878cd778ea'
#    }
#    #file_path = os.path.join(root, file)
#    #files_up = {'files':(file,open(file_path, 'rb'))}
#    print(files_up)
#    try:
#
#        headers = {
#            #'Authorization': f'{api_key}',
#            'Authorization': f'Bearer {api_key}',
#            #一定不要带这个，否则服务端，找不到 request.files中的files
#            #    'Content-Type': 'application/json',
#        }
#        # 发送POST请求
#        response = requests.post(url, headers=headers,files=files_up, data=data)
#        print(response.encoding)  # 查看当前解码编码（Requests自动判断的）
#        print(response.headers['Content-Type'])  # 查看服务器声明的编码
#        json_res = response.json()
#        for rest in json_res['data']:
#            result_ids.append(rest['id'])
#        print('json_res',json_res)
#
#    except requests.exceptions.RequestException as e:
#        print(f'Request failed: {e}')
#    except FileNotFoundError:
#        print(f'File not found: {file_path}')
#    except Exception as e:
#        print(f'Error occurred: {e}')
#    print("结束提交,当前file number  {}".format(file_number))
#    files_up = []
#
#print('文件',result_ids)

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json',
}

upload_to_kb = 'http://101.52.216.178:3333/api/v1/knowledgebases/f5231bfa9a6e43869409ced931b7dbb3/documents'
data = {"file_ids":['0d490766201b11f0acd198039b6e4778', '0d5fe59e201b11f0acd198039b6e4778', '0d6fb5e6201b11f0acd198039b6e4778', '0d7a8ac0201b11f0acd198039b6e4778', '0d90cdd0201b11f0acd198039b6e4778', '0dc72f10201b11f0b6ab98039b6e4778', '0ddee100201b11f0b6ab98039b6e4778', '0deb6fc4201b11f0b6ab98039b6e4778', '0e0230c4201b11f0b6ab98039b6e4778', '0e18672c201b11f0b6ab98039b6e4778', '0e4d61d4201b11f0bf2f98039b6e4778', '0e589928201b11f0bf2f98039b6e4778', '0e698472201b11f0bf2f98039b6e4778', '0e94e252201b11f0bf2f98039b6e4778', '0ea66f90201b11f0bf2f98039b6e4778', '0edf3c94201b11f0a96198039b6e4778', '0ef7c836201b11f0a96198039b6e4778', '0f081f74201b11f0a96198039b6e4778', '0f1b3f96201b11f0a96198039b6e4778', '0f3319c2201b11f0a96198039b6e4778', '0f7293c2201b11f09de498039b6e4778', '0f83ff4a201b11f09de498039b6e4778', '0f97c200201b11f09de498039b6e4778', '0fad14a2201b11f09de498039b6e4778', '0fc3f352201b11f09de498039b6e4778', '1010ffee201b11f095fa98039b6e4778', '101f323a201b11f095fa98039b6e4778', '10686fc2201b11f095fa98039b6e4778', '10823e0c201b11f095fa98039b6e4778', '109a7a08201b11f095fa98039b6e4778', '10e200d0201b11f09e1198039b6e4778', '10fadec0201b11f09e1198039b6e4778', '11223ea2201b11f09e1198039b6e4778', '113e54ca201b11f09e1198039b6e4778', '1151acb4201b11f09e1198039b6e4778', '11b96642201b11f0b50f98039b6e4778', '11e6f4fe201b11f0b50f98039b6e4778', '1201cc34201b11f0b50f98039b6e4778', '121c2566201b11f0b50f98039b6e4778', '122fbd2e201b11f0b50f98039b6e4778', '1263c3bc201b11f093ff98039b6e4778', '1276a018201b11f093ff98039b6e4778', '128352b8201b11f093ff98039b6e4778', '128fdede201b11f093ff98039b6e4778', '12a6b2e4201b11f093ff98039b6e4778', '12d30f92201b11f0953598039b6e4778', '12e5693a201b11f0953598039b6e4778', '12fe4234201b11f0953598039b6e4778', '13175274201b11f0953598039b6e4778', '132faaea201b11f0953598039b6e4778']}
#data = {"file_ids":["aeced0b8201411f0818898039b6e4778"]}
import json
response = requests.post(upload_to_kb,data = json.dumps(data),headers=headers,timeout=5)
print(response.text)
