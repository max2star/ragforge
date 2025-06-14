import json
import uuid
import sys
import os
#os.environ['CUDA_VISIBLE_DEVICES']="6,7"
#os.environ['SSL_CERT_FILE']='/etc/nginx/public.crt'
#sys.path.append("/usr/local/lib/python3.10/dist-packages/")
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
from magic_pdf.data.data_reader_writer import *
from magic_pdf.data.data_reader_writer import MultiBucketS3DataReader
from magic_pdf.data.schemas import S3Config
from magic_pdf.data.data_reader_writer import S3DataReader, S3DataWriter
from magic_pdf.data.dataset import PymuDocDataset
from magic_pdf.model.doc_analyze_by_custom_model import doc_analyze
import os
from openai import OpenAI
import base64
from timeit import default_timer as timer

logger.add("../for-debug.log", level="DEBUG")

import boto3
print('boto3',boto3.__file__)
import fitz
from PIL import Image
from pypdf import PdfReader as pdf2_read
from io import BytesIO

start_ts = timer()
bucket_name = "maxiao"
ak = "D6Mdnsb3HvpyEVLQmmOX"
sk = "kUkrVtKBCwdRycKbobHygRI7QBdw0no38gW8Gqef"
endpoint_url = "https://101.52.216.178:19000/"
reader = S3DataReader('/tmp/images/', bucket_name, ak, sk, endpoint_url)
writer = S3DataWriter('tmp/', bucket_name, ak, sk, endpoint_url)
image_writer = S3DataWriter('tmp/images', bucket_name, ak, sk, endpoint_url)
#读取文件
for name in ['FPGA抗辐射加固技术.pdf']:
    pdf_file_name=name #'FPGA抗辐射加固技术.pdf'
    try:
        pdf_bytes = reader.read(pdf_file_name)
    except Exception as e:
        print(f'name {name} exception {e}')
        continue
    #print(pdf_bytes)
    pdf_bytes_new = pdf_bytes
    pdf_doc = fitz.open('pdf', pdf_bytes_new)
    img_results = []
    import uuid
    import io
    def get_uuid():
        return uuid.uuid1().hex
    
    #  base 64 编码格式
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    
    tmp_dir = ("./tmp")
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)
    path = None
    for page_num in range(len(pdf_doc)):
        if page_num > 10:
            break
        page = pdf_doc.load_page(page_num)
        # 将PDF页面转换为高质量图像（调整dpi参数根据需要）
        mat = fitz.Matrix(2.0, 2.0)  # 缩放因子，提高分辨率
        pix = page.get_pixmap(matrix=mat)
        # 转换为PIL Image对象
        img_bytes = pix.tobytes()
        img = Image.open(BytesIO(img_bytes))
        path = os.path.join(tmp_dir, "%s.jpg" % get_uuid())
        img.save(path)
        base64_image = encode_image(path)
        img_results.append(base64_image)
    result = []
    for base64_image in img_results:
        client = OpenAI(
            #api_key=os.getenv("DASHSCOPE_API_KEY"),
            api_key = "sk-d065862c06754b26813e9d220b9a4f18",#sk-886e90542f6e4f90b13d295ebbcfe739",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        fields = ['标题','作者','发布时间','资料来源','摘要']
        fields = ['目录']
        completion = client.chat.completions.create(
            model="qwen-vl-max-latest", # 此处以qwen-vl-max-latest为例，可按需更换模型名称。模型列表：https://help.aliyun.com/model-studio/getting-started/models
            messages=[
                {
                    "role": "system",
                    "content": [], #{"type": "text", "text": f"提取图中的：{fields}，请你以JSON格式输出，不要输出```json```代码段。"}],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url":{
                                "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                        },
                        {"type": "text", "text": f"现在输入的图片，有可能是文档的目录索引，也有可能是正文章节，也有可能都不是，请先判断是不是文档的纯粹的目录索引，如果是，请提取图中的：{fields}，以输出目录中的各个章节所对应的页码;如果不是纯粹的目录索引，不要提取。请你以JSON格式输出纯文本，以目录为Key，值是一个章节索引的列表，列表中是章节作为key，页码作为Key，两个Key组成，不要输出```json```等markdown格式代码段。"},
                    ],
                },
            ],
        )
        result_t = completion.choices[0].message.content
        print('当前',completion.choices[0].message.content)
        if result_t:
            result.append(result_t)
    print(f"针对前10页的解析结果 {result}")
    current_page_index = 0
    page_end = 0
    page_start = 0
    dic_result  = []
    index_id = 0
    first_flag = False
    page_numbers = []
    for r in result:
        r_d = json.loads(r)
        index_id = index_id +1
        if '目录' in r_d:
            print(r_d['目录'])
            for i in r_d['目录']:
                obj = {}
                if not i.get('章节',None) or not i.get('页码',None):
                    continue
                obj['章节'] = i['章节']
                obj['页码'] = i['页码']
                try:
                    int_obj = int(obj['页码'])
                except Exception:
                    continue
                print(f'比较页面 {int_obj}')
                if obj['页码'] and int_obj>= current_page_index:
                    if not first_flag:
                        first_flag = True
                        page_start = index_id
                    dic_result.append(obj)
                    current_page_index = int_obj
                    page_end = index_id
                else:
                    continue
    #for i in dic_result:
    #    page_numbers.append(i['页码']+(page_end-1))
    #    print('结果页面 {}'.format(page_numbers))
    if page_start==0:
        page_start = 1
    elif page_start==1:
        page_start = 1
    elif page_start>1:
        page_start = page_start-1
    page_numbers = list(range(0,page_start))
    print('\n章节页码结果{}, 从index_id {}开始是正文,{}~{}是目录.将会对{}进行分析'.format(dic_result,page_end,page_start,page_end,page_numbers))
    img_results = []
    pdf_doc = fitz.open('pdf', pdf_bytes_new)
    for page_num in page_numbers:
        page = pdf_doc.load_page(page_num)
        # 将PDF页面转换为高质量图像（调整dpi参数根据需要）
        mat = fitz.Matrix(2.0, 2.0)  # 缩放因子，提高分辨率
        pix = page.get_pixmap(matrix=mat)
    
        # 转换为PIL Image对象
        img_bytes = pix.tobytes()
        img = Image.open(BytesIO(img_bytes))
        path = os.path.join(tmp_dir, "%s.jpg" % get_uuid())
        img.save(path)
        base64_image = encode_image(path)
        img_results.append(base64_image)
    fields = ['标题','作者','作者机构','摘要','关键词']
    fields = ['书名','其他书名','编者','作者','出版日期','前言','分类','ISBN','出版社']
    fields_map = {}
    for base64_image in img_results:
        client = OpenAI(
            #api_key=os.getenv("DASHSCOPE_API_KEY"),
            api_key = "sk-d065862c06754b26813e9d220b9a4f18",#sk-886e90542f6e4f90b13d295ebbcfe739",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        completion = client.chat.completions.create(
            model="qwen-vl-max-latest", # 此处以qwen-vl-max-latest为例，可按需更换模型名称。模型列表：https://help.aliyun.com/model-studio/getting-started/models
            messages=[
                {
                    "role": "system",
                    "content": [{"type": "text", "text": f"提取图中的：{fields}，对于摘要，不要进行修改，对于请你以JSON格式输出，不要输出```json```代码段。"}],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url":{
                                "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                        },
                        {"type": "text", "text": f"提取图中的：{fields}，请你以JSON格式输出纯文本，不要输出```json```等markdown格式代码段。"},
                    ],
                },
            ],
        )
        result_t = completion.choices[0].message.content
        if result_t:
            r_d = json.loads(result_t)
            for key in fields:
                value_now =  fields_map.get(key,None)
                if value_now:
                    if key not in ['摘要','正文','前言']:
                        continue
                    else:
                        current_value = r_d.get(key,None)
                        if current_value:
                            fields_map[key]= value_now + '\n'+current_value
                else:
                    current_value = r_d.get(key,None)
                    if current_value:
                        fields_map[key]=current_value
        print(result_t)
    task_time_cost = timer() - start_ts
    print("文档 {} 解析花费时间 {}, 解析结果 {}".format(name,task_time_cost,fields_map))
