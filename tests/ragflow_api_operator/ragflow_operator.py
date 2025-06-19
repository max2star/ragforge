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
base_url_for_doc = "http://101.52.216.178/v1/knowledgebases/documents/"
base_url_for_doc = "http://101.52.216.178/v1/file/rm"
api_key = "IjEzNTJhMGZjMWY5MTExZjA4NmQ1NGE4NzhjZDc3OGVhIg.aAe6CA.xpRFlzt6uW6_hkNYx1kBHIKSu_8"
knowleadge_base ="19df303e1f9111f087d74a878cd778ea" #"6aed75aa4dc8482abde74f48bd097cb4"
headers = {
    'Authorization': f'{api_key}',
    #'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json',
}
list_kb_docs = "http://101.52.216.178:3333/api/v1/knowledgebases/"+knowleadge_base+"/documents?currentPage=1&size=10000"
list_files = "http://101.52.216.178/v1/file/list?parent_id=&keywords=&page_size=10000&page=1"
# 服务器接收文件的URL
url_upload_file = 'http://101.52.216.178:3333/api/v1/files/upload'  # 替换为你的实际URL
url_upload_file = "http://101.52.216.178/v1/file/upload"
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
files_up  = [
]
# 服务器接收文件的URL
url_upload_file = "http://101.52.216.178/v1/document/upload"
url = url_upload_file
# 要上传的文件路径
directory = './原文'
file_number = 0 
for root, dirs, files in os.walk(directory):
    for file in files:
        file_path = os.path.join(root, file)
        logger.info("当前正在处理的文件是 {},文件名称 {}".format(file_path,file))
        
        files_up.append(('file',(file, open(file_path, 'rb'), 'application/pdf')))
        #files_up.append(('files',(file, open(file_path, 'rb'), 'application/pdf')))
        file_number = file_number + 1
        if len(files_up)>=5:
            print("开始提交,当前file number  {}".format(file_number))
            # 如果需要附加其他表单字段
            data = {
                'kb_id':'19df303e1f9111f087d74a878cd778ea'
            }
            #file_path = os.path.join(root, file)
            #files_up = {'files':(file,open(file_path, 'rb'))}
            print(files_up)
            try:
            
                headers = {
                    'Authorization': f'{api_key}',
                    #'Authorization': f'Bearer {api_key}',
                    #一定不要带这个，否则服务端，找不到 request.files中的files
                    #    'Content-Type': 'application/json',
                }
                # 发送POST请求
                response = requests.post(url, headers=headers,files=files_up, data=data)
                print(response.encoding)  # 查看当前解码编码（Requests自动判断的）
                print(response.headers['Content-Type'])  # 查看服务器声明的编码
                json_res = response.json()
                print('json_res',json_res)
            
            except requests.exceptions.RequestException as e:
                print(f'Request failed: {e}')
            except FileNotFoundError:
                print(f'File not found: {file_path}')
            except Exception as e:
                print(f'Error occurred: {e}')
            print("结束提交,当前file number  {}".format(file_number))
            files_up = []

if len(files_up)>=1:
    print("开始提交,当前file number  {}".format(file_number))
    # 如果需要附加其他表单字段
    data = {
        'kb_id':'19df303e1f9111f087d74a878cd778ea'
    }
    #file_path = os.path.join(root, file)
    #files_up = {'files':(file,open(file_path, 'rb'))}
    print(files_up)
    try:

        headers = {
            'Authorization': f'{api_key}',
            #'Authorization': f'Bearer {api_key}',
            #一定不要带这个，否则服务端，找不到 request.files中的files
            #    'Content-Type': 'application/json',
        }
        # 发送POST请求
        response = requests.post(url, headers=headers,files=files_up, data=data)
        print(response.encoding)  # 查看当前解码编码（Requests自动判断的）
        print(response.headers['Content-Type'])  # 查看服务器声明的编码
        json_res = response.json()
        print('json_res',json_res)

    except requests.exceptions.RequestException as e:
        print(f'Request failed: {e}')
    except FileNotFoundError:
        print(f'File not found: {file_path}')
    except Exception as e:
        print(f'Error occurred: {e}')
    print("结束提交,当前file number  {}".format(file_number))
    files_up = []

