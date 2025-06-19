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
import json
import uuid
import sys
import os
import time
from datetime import datetime
import requests
import re
import numpy as np
from loguru import logger
from magic_pdf.data.data_reader_writer import FileBasedDataWriter, FileBasedDataReader
from magic_pdf.data.dataset import PymuDocDataset
from magic_pdf.model.doc_analyze_by_custom_model import doc_analyze
from magic_pdf.config.enums import SupportedPdfParseMethod
import pandas as pd
import pypandoc
from magic_pdf.data.data_reader_writer import *
from magic_pdf.data.data_reader_writer import MultiBucketS3DataReader
from magic_pdf.data.schemas import S3Config
from magic_pdf.data.data_reader_writer import S3DataReader, S3DataWriter
from magic_pdf.data.dataset import PymuDocDataset
from magic_pdf.model.doc_analyze_by_custom_model import doc_analyze
import os
os.environ['CUDA_VISIBLE_DEVICES']="6,7"

logger.add("../for-debug.log", level="DEBUG")

def classify(api_url,api_key,content):
    logger.debug('parameter api_url is {},api_key is {}'.format(api_url,api_key))
    # Request headers
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    # Request payload
    data = {
        "inputs": {"content": content},
        "response_mode": "blocking",
        "user": "abc-123",
    }
    error = False
    try:
        # Send POST request
        start_post = time.time()
        logger.debug('start post query for {}'.format(api_url))
        response = requests.post(api_url, headers=headers, data=json.dumps(data),timeout=600)
        end_post = time.time()
        post_cost = 1000*(end_post-start_post)
        logger.debug('end post query for {},post cost {}ms'.format(api_url,post_cost))
        response.raise_for_status()  # Check if request was successful

        json_res = None
        if (response and response.json()):
            logger.debug('post query for {},response {}'.format(api_url,response.json()))
            data_ = response.json().get('data',None)
            #print('data_',data_)
            if data_:
                outputs_ = data_.get('outputs',None)
                if outputs_:
                    raw_text =outputs_.get('outputs',None)
                    # Get the returned text and clean it
                    logger.info(f'responese is {raw_text}.')
                    if raw_text:
                        cleaned_text = re.sub(r"^```json\n|\n```$", "", raw_text)  # Remove JSON block markers
                        # Parse JSON
                        cleaned_text = cleaned_text.replace('\n','').replace('\t','').replace('```','')
                        logger.info(f'cleaned_text is {cleaned_text}.')
                        return cleaned_text,error
                else:
                    error = True
                    logger.info('query for {} has no outputs.'.format(api_url))
            else:
                error = True
                logger.info('query for {} has no data {}'.format(api_url))
        else:
            error = True
            logger.info('query for {} response {}'.format(api_url,response))
        return None,error
    except requests.exceptions.RequestException as e:
        error = True
        logger.error(f"Request error: {e}")
        return None,error
    except json.JSONDecodeError as e:
        error = True
        logger.error(f"JSON parse error: {e}")
        return None,error
    except Exception as e:
        error = True
        logger.error(f"JSON parse error: {e}")
        return None,error

def extract_entity_relationship_with_ai(api_url,api_key,content):
    logger.debug('parameter api_url is {},api_key is {}'.format(api_url,api_key))
    # Request headers
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    # Request payload
    data = {
        "inputs": {"content": content},
        "response_mode": "blocking",
        "user": "abc-123",
    }
    error = False
    try:
        # Send POST request
        start_post = time.time()
        logger.debug('start post query for {}'.format(api_url))
        response = requests.post(api_url, headers=headers, data=json.dumps(data),timeout=600)
        end_post = time.time()
        post_cost = 1000*(end_post-start_post)
        logger.debug('end post query for {},post cost {}ms'.format(api_url,post_cost))
        response.raise_for_status()  # Check if request was successful

        json_res = None
        if (response and response.json()):
            logger.debug('post query for {},response {}'.format(api_url,response.json()))
            data_ = response.json().get('data',None)
            #print('data_',data_)
            if data_:
                outputs_ = data_.get('outputs',None)
                if outputs_:
                    json_res ={}
                    json_res_one = None
                    json_res_two = None
                    raw_text =outputs_.get('outputs',None)
                    # Get the returned text and clean it
                    logger.info(f'responese is {raw_text}.')
                    if raw_text:
                        cleaned_text = re.sub(r"^```json\n|\n```$", "", raw_text)  # Remove JSON block markers
                        # Parse JSON
                        cleaned_text = cleaned_text.replace('\n','').replace('\t','').replace('```','')
                        logger.info(f'cleaned_text is {cleaned_text}.')
                        json_res_one = json.loads(cleaned_text)
                        #html_output = pypandoc.convert_text(cleaned_text, 'html', 'markdown')
                        #logger.info(f'html_output is {html_output}.')
                        #json_res_one = json.loads(html_output)
                        return json_res_one,error
                else:
                    error = True
                    logger.info('query for {} has no outputs.'.format(api_url))
            else:
                error = True
                logger.info('query for {} has no data {}'.format(api_url))
        else:
            error = True
            logger.info('query for {} response {}'.format(api_url,response))
        return json_res,error
    except requests.exceptions.RequestException as e:
        error = True
        logger.error(f"Request error: {e}")
        return None,error
    except json.JSONDecodeError as e:
        error = True
        logger.error(f"JSON parse error: {e}")
        return None,error
    except Exception as e:
        error = True
        logger.error(f"JSON parse error: {e}")
        return None,error

# 读取 Excel 文件
file_path = '论文.xlsx'
df = pd.read_excel(file_path)
time_tag = time.time()
#api_url = 'http://10.1.60.39/v1/workflows/run'
api_url = 'http://101.52.216.178/v1/workflows/run'
api_key = 'app-84dBhZLoOK03Z5q11YtLxLSy' #app-O81CNkbZbHlYB1MUfvL99hs5'
api_url_classify = 'http://101.52.216.178/v1/workflows/run'
api_key_classify = 'app-faORrYjhHZ2BZs2aTDT04Dwm' #app-O81CNkbZbHlYB1MUfvL99hs5'
error_files = []
error_files_classify = []
directory = '.'
file_number = 0
for root, dirs, files in os.walk(directory):
    for file in files:
        file_number = file_number + 1
        time_start = time.time()
        file_path = os.path.join(root, file)
        #logger.info("当前正在处理的文件是 {},文件名称 {},是第{}个。".format(file_path,file,file_number))
        try:
            # args
            pdf_file_name = file #"D03151668.pdf"  # replace with the real pdf path
            if file=='test.py' or file=='论文.xlsx' or file=='output.xlsx': #or file!='D453040.pdf':
                #logger.info('当前文件 file {},忽略'.format(file))
                continue
            if pdf_file_name!='Y1089380.pdf':
                continue
            
            name_without_suff = pdf_file_name.split(".")[0]

            local_image_dir, local_md_dir = "/var/lib/gpustack/output/images", "/var/lib/gpustack/output/output"
            #image_dir = str(os.path.basename(local_image_dir))

            bucket_name = "maxiao"
            ak = "D6Mdnsb3HvpyEVLQmmOX"
            sk = "kUkrVtKBCwdRycKbobHygRI7QBdw0no38gW8Gqef"
            endpoint_url = "http://101.52.216.178:19000/"
            reader = S3DataReader('原文/', bucket_name, ak, sk, endpoint_url)
            writer = S3DataWriter('tmp/', bucket_name, ak, sk, endpoint_url)
            image_writer = S3DataWriter('tmp/images', bucket_name, ak, sk, endpoint_url)
            #读取文件
            pdf_bytes = reader.read(pdf_file_name)
            # proc
            ## Create Dataset Instance
            ds = PymuDocDataset(pdf_bytes)
            #print("MaXiao 1")
            ## inference
            if ds.classify() == SupportedPdfParseMethod.OCR:
                infer_result = ds.apply(doc_analyze, ocr=True)
            
                ## pipeline
                pipe_result = infer_result.pipe_ocr_mode(image_writer)
            
            else:
                infer_result = ds.apply(doc_analyze, ocr=False)
            
                ## pipeline
                pipe_result = infer_result.pipe_txt_mode(image_writer)
            #print("MaXiao 2")
            
            ## draw model result on each page
            infer_result.draw_model(os.path.join(local_md_dir, f"{name_without_suff}_model.pdf"))

            # get model inference result
            model_inference_result = infer_result.get_infer_res()
            print("model_inference_result {}".format(model_inference_result))
            # draw layout result on each page
            pipe_result.draw_layout(os.path.join(local_md_dir, f"{name_without_suff}_layout.pdf"))
            
            # draw spans result on each page
            pipe_result.draw_span(os.path.join(local_md_dir, f"{name_without_suff}_spans.pdf"))
            
            ####获取MD文件
            md_content = pipe_result.get_markdown(image_writer)#image_dir)
            
            #将MarkDown文件进行输出
            pipe_result.dump_md(writer, f"{name_without_suff}.md",'tmp/md')
            #将content list文件进行输出
            pipe_result.dump_content_list(writer, f"{name_without_suff}_content_list.json", "images")
            #将middle json文件进行输出
            pipe_result.dump_middle_json(writer, f'{name_without_suff}_middle.json')

            time_end_ocr = time.time()
            time_cost = 1000*(time_end_ocr-time_start)
            md_content_to = md_content[:10000]
            logger.info('file {} OCR等解析花费 {} md_content 长度 {} md_content_to 长度 {}'.format(file,time_cost,len(md_content),len(md_content_to)))
            break
            #### get content list content
            ###content_list_content = pipe_result.get_content_list(image_dir)
            #
            ## dump content list
            #pipe_result.dump_content_list(writer, f"{name_without_suff}_content_list.json", image_dir)
            #
            ## get middle json
            #middle_json_content = pipe_result.get_middle_json()
            #
            ## dump middle json
            #pipe_result.dump_middle_json(writer, f'{name_without_suff}_middle.json')
        except Exception as e:
            logger.info("发生错误,文件 {},错误 {}".format(file,e))
            continue
        time_end = time.time()
        one_cost = 1000*(time_end-time_start)
