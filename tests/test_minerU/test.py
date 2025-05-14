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
        logger.info("当前正在处理的文件是 {},文件名称 {},是第{}个。".format(file_path,file,file_number))
        try:
            # args
            pdf_file_name = file #"D03151668.pdf"  # replace with the real pdf path
            if file=='test.py' or file=='论文.xlsx' or file=='output.xlsx': #or file!='D453040.pdf':
                logger.info('当前文件 file {},忽略'.format(file))
                continue
            #if file!=pdf_file_name:
            #    print('当前文件 file {},忽略'.format(file))
            #    continue
            name_without_suff = pdf_file_name.split(".")[0]
            #print(name_without_suff)
            # prepare env
            local_image_dir, local_md_dir = "/var/lib/gpustack/output/images", "/var/lib/gpustack/output/output"
            #image_dir = str(os.path.basename(local_image_dir))
            
            os.makedirs(local_image_dir, exist_ok=True)
            
            image_writer, md_writer = FileBasedDataWriter(local_image_dir), FileBasedDataWriter(
                local_md_dir
            )
            
            # read bytes
            reader1 = FileBasedDataReader("")
            pdf_bytes = reader1.read(pdf_file_name)  # read the pdf content
            
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
            
            # draw model result on each page
            infer_result.draw_model(os.path.join(local_md_dir, f"{name_without_suff}_model.pdf"))
            
            # get model inference result
            model_inference_result = infer_result.get_infer_res()
            
            # draw layout result on each page
            pipe_result.draw_layout(os.path.join(local_md_dir, f"{name_without_suff}_layout.pdf"))
            
            # draw spans result on each page
            pipe_result.draw_span(os.path.join(local_md_dir, f"{name_without_suff}_spans.pdf"))
            
            ###获取MD文件
            md_content = pipe_result.get_markdown(local_image_dir)#image_dir)
            
            #将MarkDown文件进行输出
            pipe_result.dump_md(md_writer, f"{name_without_suff}.md", local_image_dir)

            time_end_ocr = time.time()
            time_cost = 1000*(time_end_ocr-time_start)
            md_content_to = md_content[:10000]
            logger.info('file {} OCR等解析花费 {} md_content 长度 {} md_content_to 长度 {}'.format(file,time_cost,len(md_content),len(md_content_to)))
            ### get content list content
            ##content_list_content = pipe_result.get_content_list(image_dir)
            
            ### dump content list
            ##pipe_result.dump_content_list(md_writer, f"{name_without_suff}_content_list.json", image_dir)
            
            ### get middle json
            ##middle_json_content = pipe_result.get_middle_json()
            
            ### dump middle json
            ##pipe_result.dump_middle_json(md_writer, f'{name_without_suff}_middle.json')
            #文章标题、文章作者、作者机构、摘要、关键词、作者学位、文章分类、作者学校、指导教师、年份、语言
            logger.info("当前正在处理entity extract文件是 {},文件名称 {},是第{}个".format(file_path,file,file_number))
            result_json,error = extract_entity_relationship_with_ai(api_url=api_url,api_key=api_key,content=md_content_to)
            logger.info("当前完成处理entity extract文件是 {},文件名称 {},是第{}个".format(file_path,file,file_number))
            if error:
                logger.info('file {} 解析错误,result {}'.format(file,result_json))
                error_files.append(file)
                continue
            logger.info('file {} result {}'.format(file,result_json)) 
            target_column = 'filename' # 修改为你的列名
            target_value = file
            #没有摘要
            #论文标题、论文作者姓名、作者机构、关键词、作者学位、作者学校、指导教师、年份、语言、发表时间
            for key in ["论文标题",'论文作者姓名','作者机构','关键词','作者学位','作者学校','指导教师','年份','语言','发表时间']:
                filtered_rows = df[df[target_column] == target_value]
    
               # 对符合条件的行设置新列的值（例如：固定值或动态计算）
                df.loc[df[target_column] == target_value, key] = result_json.get(key,None)
            logger.info("当前正在处理classify的文件是 {},文件名称 {},是第{}个".format(file_path,file,file_number))
            class_result,error = classify(api_url=api_url_classify,api_key=api_key_classify,content=md_content_to)
            logger.info("当前完成处理classify的文件是 {},文件名称 {},是第{}个".format(file_path,file,file_number))
            if error:
                logger.info('file {} 分类错误,result {}'.format(file,class_result))
                error_files_classify.append(file)
                continue
            df.loc[df[target_column] == target_value, '分类标签'] = class_result 
        except Exception as e:
            error_files.append(file)
            error_files_classify.append(file)
            logger.info("发生错误,文件 {},错误 {}".format(file,e))
            continue
        time_end = time.time()
        one_cost = 1000*(time_end-time_start)
        logger.info("当前正在处理的文件是 {},文件名称 {},是第{}个,处理花费时间 {}ms。".format(file_path,file,file_number,one_cost))
        # 保存结果到新文件
        output_path = "output_"+str(int(time_tag))+".xlsx"
        df.to_excel(output_path, index=False)
        logger.info(f"\n已处理并保存文件至: {output_path}")
logger.info(f"\n解析错误的文件包括: {error_files}")
logger.info(f"\n解析错误的文件包括: {error_files_classify}")
