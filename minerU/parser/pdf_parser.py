#
#  Copyright 2025 The InfiniFlow Authors. All Rights Reserved.
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

import logging
import os
import sys

#增加minerU所使用的类库
sys.path.append("/usr/local/lib/python3.10/dist-packages/")
#os.environ['SSL_CERT_FILE']='/etc/nginx/public.crt'
import time
import random
import re
import threading
from copy import deepcopy
from io import BytesIO
from timeit import default_timer as timer
import json

import numpy as np
import trio
import xgboost as xgb
from PIL import Image
from pypdf import PdfReader as pdf2_read
from api.utils.file_utils import get_project_base_directory

from minerU.parser.figure_parser import VisionFigureParser
#from rag.app.picture import vision_llm_chunk as picture_vision_llm_chunk
from rag.nlp import rag_tokenizer
#from rag.prompts import vision_llm_describe_prompt
#from rag.settings import PARALLEL_DEVICES

os.environ['CUDA_VISIBLE_DEVICES']="0,1"

import fitz
from magic_pdf.data.data_reader_writer import S3DataReader, S3DataWriter
from magic_pdf.data.dataset import PymuDocDataset
from magic_pdf.model.doc_analyze_by_custom_model import doc_analyze
from magic_pdf.data.data_reader_writer import FileBasedDataWriter, FileBasedDataReader
from magic_pdf.data.dataset import PymuDocDataset
from magic_pdf.model.doc_analyze_by_custom_model import doc_analyze
from magic_pdf.config.enums import SupportedPdfParseMethod
from magic_pdf.data.read_api import read_local_office
from magic_pdf.config.ocr_content_type import (BlockType, CategoryId,
                                               ContentType)
from magic_pdf.libs.draw_bbox import draw_bbox_without_number,draw_bbox_with_number
from api.db.services.document_service import DocumentService
from api.db import constant

from rag import settings

from api.db import LLMType
from api.db.services.llm_service import LLMBundle

def _has_color(o):
    #Non-Stroking Color Space（非描边颜色空间），即文本/图形等的填充颜色所使用的颜色空间模型
    if o.get("ncs", "") == "DeviceGray":
        #颜色空间为DeviceGray（灰度空间，其他还有DeviceRGB/DeviceCMYK等），
        #并且描边颜色的第一个分量为纯白色；
        #并且填充颜色的第一个分量为纯白色;
        if o["stroking_color"] and o["stroking_color"][0] == 1 and o["non_stroking_color"] and \
                o["non_stroking_color"][0] == 1:
            #文本是英文
            if re.match(r"[a-zT_\[\]\(\)-]+", o.get("text", "")):
                #说明是隐藏文字，没有颜色，返回False
                return False
    return True

def get_bbox_from_block(block):
    """
    从 preproc_blocks 中的一个块提取最外层的 bbox 信息。

    Args:
        block (dict): 代表一个块的字典，期望包含 'bbox' 键。

    Returns:
        list: 包含4个数字的 bbox 列表，如果找不到或格式无效则返回 [0, 0, 0, 0]。
    """
    if isinstance(block, dict) and "bbox" in block:
        bbox = block.get("bbox")
        # 验证 bbox 是否为包含4个数字的有效列表
        if isinstance(bbox, list) and len(bbox) == 4 and all(isinstance(n, (int, float)) for n in bbox):
            return bbox
        else:
            print(f"[Parser-WARNING] 块的 bbox 格式无效: {bbox}，将使用默认值。")
    # 如果 block 不是字典或没有 bbox 键，或 bbox 格式无效，返回默认值
    return [0, 0, 0, 0]

def draw_layout_bbox_(pdf_info, pdf_bytes,writer,file_dst):
    dropped_bbox_list = []
    tables_list, tables_body_list = [], []
    tables_caption_list, tables_footnote_list = [], []
    imgs_list, imgs_body_list, imgs_caption_list = [], [], []
    imgs_footnote_list = []
    titles_list = []
    texts_list = []
    interequations_list = []
    lists_list = []
    indexs_list = []
    for page in pdf_info:

        page_dropped_list = []
        tables, tables_body, tables_caption, tables_footnote = [], [], [], []
        imgs, imgs_body, imgs_caption, imgs_footnote = [], [], [], []
        titles = []
        texts = []
        interequations = []
        lists = []
        indices = []

        for dropped_bbox in page['discarded_blocks']:
            page_dropped_list.append(dropped_bbox['bbox'])
        dropped_bbox_list.append(page_dropped_list)
        for block in page['para_blocks']:
            bbox = block['bbox']
            if block['type'] == BlockType.Table:
                tables.append(bbox)
                for nested_block in block['blocks']:
                    bbox = nested_block['bbox']
                    if nested_block['type'] == BlockType.TableBody:
                        tables_body.append(bbox)
                    elif nested_block['type'] == BlockType.TableCaption:
                        tables_caption.append(bbox)
                    elif nested_block['type'] == BlockType.TableFootnote:
                        tables_footnote.append(bbox)
            elif block['type'] == BlockType.Image:
                imgs.append(bbox)
                for nested_block in block['blocks']:
                    bbox = nested_block['bbox']
                    if nested_block['type'] == BlockType.ImageBody:
                        imgs_body.append(bbox)
                    elif nested_block['type'] == BlockType.ImageCaption:
                        imgs_caption.append(bbox)
                    elif nested_block['type'] == BlockType.ImageFootnote:
                        imgs_footnote.append(bbox)
            elif block['type'] == BlockType.Title:
                titles.append(bbox)
            elif block['type'] == BlockType.Text:
                texts.append(bbox)
            elif block['type'] == BlockType.InterlineEquation:
                interequations.append(bbox)
            elif block['type'] == BlockType.List:
                lists.append(bbox)
            elif block['type'] == BlockType.Index:
                indices.append(bbox)

        tables_list.append(tables)
        tables_body_list.append(tables_body)
        tables_caption_list.append(tables_caption)
        tables_footnote_list.append(tables_footnote)
        imgs_list.append(imgs)
        imgs_body_list.append(imgs_body)
        imgs_caption_list.append(imgs_caption)
        imgs_footnote_list.append(imgs_footnote)
        titles_list.append(titles)
        texts_list.append(texts)
        interequations_list.append(interequations)
        lists_list.append(lists)
        indexs_list.append(indices)

    layout_bbox_list = []

    table_type_order = {
        'table_caption': 1,
        'table_body': 2,
        'table_footnote': 3
    }
    for page in pdf_info:
        page_block_list = []
        for block in page['para_blocks']:
            if block['type'] in [
                BlockType.Text,
                BlockType.Title,
                BlockType.InterlineEquation,
                BlockType.List,
                BlockType.Index,
            ]:
                bbox = block['bbox']
                page_block_list.append(bbox)
            elif block['type'] in [BlockType.Image]:
                for sub_block in block['blocks']:
                    bbox = sub_block['bbox']
                    page_block_list.append(bbox)
            elif block['type'] in [BlockType.Table]:
                sorted_blocks = sorted(block['blocks'], key=lambda x: table_type_order[x['type']])
                for sub_block in sorted_blocks:
                    bbox = sub_block['bbox']
                    page_block_list.append(bbox)

        layout_bbox_list.append(page_block_list)

    pdf_docs = fitz.open('pdf', pdf_bytes)

    for i, page in enumerate(pdf_docs):

        draw_bbox_without_number(i, dropped_bbox_list, page, [158, 158, 158], True)
        # draw_bbox_without_number(i, tables_list, page, [153, 153, 0], True)  # color !
        draw_bbox_without_number(i, tables_body_list, page, [204, 204, 0], True)
        draw_bbox_without_number(i, tables_caption_list, page, [255, 255, 102], True)
        draw_bbox_without_number(i, tables_footnote_list, page, [229, 255, 204], True)
        # draw_bbox_without_number(i, imgs_list, page, [51, 102, 0], True)
        draw_bbox_without_number(i, imgs_body_list, page, [153, 255, 51], True)
        draw_bbox_without_number(i, imgs_caption_list, page, [102, 178, 255], True)
        draw_bbox_without_number(i, imgs_footnote_list, page, [255, 178, 102], True),
        draw_bbox_without_number(i, titles_list, page, [102, 102, 255], True)
        draw_bbox_without_number(i, texts_list, page, [153, 0, 76], True)
        draw_bbox_without_number(i, interequations_list, page, [0, 255, 0], True)
        draw_bbox_without_number(i, lists_list, page, [40, 169, 92], True)
        draw_bbox_without_number(i, indexs_list, page, [40, 169, 92], True)

        draw_bbox_with_number(
            i, layout_bbox_list, page, [255, 0, 0], False, draw_bbox=False
        )

    # Save the PDF
    pdf_stream = BytesIO()
    pdf_docs.save(pdf_stream)
    pdf_stream.seek(0)

    writer.write(file_dst, pdf_stream)

class MinerUPdf:
    def __init__(self, **kwargs):
        self.page_from = 0

    def remove_tag(self, txt):
        return re.sub(r"@@[\t0-9.-]+?##", "", txt)

    def crop(self, text, ZM=3, need_position=False):
        imgs = []
        poss = []
        positions = []
        print("text is {}".format(text))
        logging.info("text is {}".format(text))
        for tag in re.findall(r"@@[0-9-]+\t[0-9.\t]+##", text):
            pn, left, right, top, bottom = tag.strip(
                "#").strip("@").split("\t")
            left, right, top, bottom = float(left), float(
                right), float(top), float(bottom)
            print("crop pn is {}".format(pn))
            logging.info("crop pn is {}".format(pn))
            poss.append((int(pn),left, right, top, bottom))
        if not poss:
            if need_position:
                return None, None
            return None
        if need_position:
            return None,poss 
        return None

    def __init__(self):
        super().__init__()

    #[[page, x1, x2, y1, y2]]
    def _line_tag_(self, page_idx,content_index,bx):
        return "@@{}\t{:.1f}\t{:.1f}\t{:.1f}\t{:.1f}##" \
            .format("-".join([str(page_idx)+"--"+str(content_index)]),bx[0], bx[1], bx[2], bx[3])

    def vision_parser(self,tenant_id,figures,key_list_to_extract):
        try:
            vision_model = LLMBundle(tenant_id, LLMType.IMAGE2TEXT)
        except Exception:
            vision_model = None
            logging.error(f"Not Found Vision Model For tenant_id {tenant_id}")
        if vision_model:
            try:
                pdf_vision_parser = VisionFigureParser(vision_model=vision_model, figures_data=figures, key_list_to_extract=key_list_to_extract)
                boosted_figures = pdf_vision_parser()
                return boosted_figures
                #tables.extend(boosted_figures)
            except Exception as e:
                logging.error(f"Visual model error: {e}")
        return None

    def call_function(self, bucketname,filename,kb_id,doc_id,tenant_id,parser_config,pdf_flag,binary=None, from_page=0,
                 to_page=100000, zoomin=3, callback=None):
        pdf_file_name = filename
        prefix = ''
        if not pdf_flag:
            name_without_suff = filename.split(".")[0]
            pdf_file_name = name_without_suff+".pdf"
            prefix=f'minerU/{doc_id}'
        time_start_process= time.time()
        self.s3_config = settings.S3
        ak = self.s3_config.get('access_key', None)
        sk = self.s3_config.get('secret_key', None)
        endpoint_url = self.s3_config.get('endpoint_url', None)
        bucket_name = bucketname
        #local_image_dir, local_md_dir = "/var/lib/gpustack/output/images", "/var/lib/gpustack/output/output"

        from timeit import default_timer as timer
        callback(msg="MinerU处理开始。即将进行视觉大模型要素抽取")
        
        # 使用MinerU处理
        try:
            start = timer()
            store_bucket_name = kb_id
            name_without_suff = pdf_file_name.split(".")[0]
            reader = S3DataReader(f'/{prefix}', bucket_name, ak, sk, endpoint_url)
            writer = S3DataWriter(f'minerU/{doc_id}', store_bucket_name, ak, sk, endpoint_url)
            image_writer = S3DataWriter(f'minerU/{doc_id}/images', store_bucket_name, ak, sk, endpoint_url)
            reader_stored_files = S3DataReader(f'minerU/{doc_id}/images/', bucket_name, ak, sk, endpoint_url)

            # 打开PDF流
            logging.info("正在读取prefix {} file name {}".format(prefix,pdf_file_name))
            pdf_bytes_new = reader.read(pdf_file_name)
            pdf_doc = fitz.open('pdf', pdf_bytes_new)
            img_results = []

            for page_num in range(len(pdf_doc)):
                if page_num>4:
                    break
                page = pdf_doc.load_page(page_num)
                # 将PDF页面转换为高质量图像（调整dpi参数根据需要）
                mat = fitz.Matrix(2.0, 2.0)  # 缩放因子，提高分辨率
                pix = page.get_pixmap(matrix=mat)

                # 转换为PIL Image对象
                img_bytes = pix.tobytes()
                img = Image.open(BytesIO(img_bytes))
                img_results.append(img)
            ## Save the PDF
            #pdf_stream = BytesIO()
            #pdf_docs[0].save(pdf_stream)
            #pdf_stream.seek(0)
            key_list_to_extract = constant.keyvalues_mapping['default']
            extractor_config = parser_config.get('extractor')
            if extractor_config:
               key_list_to_extract = extractor_config.get("keyvalues",key_list_to_extract)
            keys_to_use_list = []
            for i in key_list_to_extract:
                keys_to_use_list.append(i['name'])
            vision_results = self.vision_parser(tenant_id,img_results,keys_to_use_list)
            merged_results = {}
            logging.info("视觉解析抽取{} 结果 {}".format(keys_to_use_list,vision_results))
            try:
                if vision_results:
                    for k_v_ in vision_results.values():
                        k_v_j = json.loads(k_v_)
                        for k_,v_ in k_v_j.items():
                            if (not merged_results.get(k_,None)) and v_:
                                merged_results[k_] = v_
            except Exception as e:
                logging.info("视觉解析错误,继续其他处理 {}".format(e))
            logging.info("视觉解析抽取{} 结果 {},合并结果 {}".format(keys_to_use_list,vision_results,merged_results))
            callback(prog=0.15,msg="MinerU 视觉大模型分析处理完成 ({:.2f}s),处理了{}页。即将从对象存储获取文档".format(timer()-start,(page_num+1)))

            start = timer()
            #从对象存储读取文件
            pdf_bytes = reader.read(pdf_file_name)
            callback(prog=0.25,msg="MinerU 从对象存储读取文件完成 ({:.2f}s)。即将使用MinerU进行解析".format(timer()-start))
            ## Create Dataset Instance
            start = timer()
            ds = PymuDocDataset(pdf_bytes)
            use_ocr = False
            if ds.classify() == SupportedPdfParseMethod.OCR:
                use_ocr=True
                infer_result = ds.apply(doc_analyze, ocr=use_ocr)
                ## pipeline
                pipe_result = infer_result.pipe_ocr_mode(image_writer)
            else:
                infer_result = ds.apply(doc_analyze, ocr=use_ocr)
                ## pipeline
                pipe_result = infer_result.pipe_txt_mode(image_writer)
            callback(prog=0.6,msg="MinerU 分析处理完成 ({:.2f}s),是否OCR :{}。即将进行结果绘制".format(timer()-start,use_ocr))

            start = timer()
            pdf_info = pipe_result._pipe_res['pdf_info']
            pdf_bytes= pipe_result._dataset.data_bits()
            draw_layout_bbox_(pdf_info, pdf_bytes,writer,f"{name_without_suff}_layout.pdf")
            DocumentService.update_layout_location_fields(doc_id,f"minerU/{name_without_suff}_layout.pdf")

            #TODO
            ## get model inference result
            ##model_inference_result = infer_result.get_infer_res()
            ### draw model result on each page
            #infer_result.draw_model(os.path.join(local_md_dir, f"{name_without_suff}_model.pdf"))
            ## draw layout result on each page
            #pipe_result.draw_layout(os.path.join(local_md_dir, f"{name_without_suff}_layout.pdf"))
            ## draw spans result on each page
            #pipe_result.draw_span(os.path.join(local_md_dir, f"{name_without_suff}_spans.pdf"))
            
            #获取MD文件
            md_content = pipe_result.get_markdown(image_writer)#image_dir)
            callback(prog=0.65,msg="MinerU 绘制处理结果 ({:.2f}s)完成。即将进行结果存储".format(timer()-start))
            
            start = timer()
            #将MarkDown文件进行输出
            pipe_result.dump_md(writer, f"{name_without_suff}.md",'')
            #将content list文件进行输出
            pipe_result.dump_content_list(writer, f"{name_without_suff}_content_list.json", "")
            #将middle json文件进行输出
            pipe_result.dump_middle_json(writer, f'{name_without_suff}_middle.json')

            DocumentService.update_md_location_fields(doc_id,f"minerU/{name_without_suff}.md")

            
            content_list = pipe_result.get_content_list("")
            middle_content = pipe_result.get_middle_json()
            middle_json_content = json.loads(middle_content)
            callback(prog=0.75,msg="MinerU 保存处理结果到对象存储完成 ({:.2f}s)。即将进行结果分析".format(timer()-start))
            #logging.info('[MinerU] 获取content_list长度 {},middle_content长度 {},middle_json_content长度 {}'.format(len(content_list),len(middle_content),len(middle_json_content)))
            start = timer()
            # 解析middle_json_content 并提取块信息，结果保存在block_info_list
            block_info_list = []
            sections = []
            if middle_json_content:
                try:
                    if isinstance(middle_json_content, dict):
                        middle_data = middle_json_content # 直接赋值
                    else:
                        middle_data = None
                        logging.error(f"[MinerU] middle_json_content 不是预期的字典格式，实际类型: {type(middle_json_content)}。")
                    # 提取信息 
                    for page_idx, page_data in enumerate(middle_data.get("pdf_info", [])):
                        for block in page_data.get("preproc_blocks", []):
                            block_bbox = get_bbox_from_block(block)
                            # 仅提取包含文本且有 bbox 的块
                            if block_bbox != [0, 0, 0, 0]:
                                    block_info_list.append({
                                        "page_idx": page_idx,
                                        "bbox": block_bbox
                                    })
                            else:
                                logging.warning("[MinerU] 块的 bbox 无效: {}, block 是 {}。".format(block_bbox,block))
                                #试着从blocks中获取
                                blocks_bbox = block.get('blocks',None)
                                if blocks_bbox and type(blocks_bbox) is list:
                                    block_bbox_to_get = blocks_bbox[0]
                                    if block_bbox_to_get:
                                        block_bbox = get_bbox_from_block(block_bbox_to_get)
                                block_info_list.append({
                                       "page_idx": page_idx,
                                       "bbox": block_bbox
                                   })
                        logging.info(f"[MinerU] 已从 middle_data 提取了 {len(block_info_list)} 个块的信息。")
                    logging.info(f"[MinerU] 总计提取了 {len(block_info_list)} 个块的信息。")
                except Exception as e:
                    logging.error(f"[MinerU] 处理 middle_json_content 时出错: {e}")
            logging.info("MinerU 解析 bucketname {} filename {} 得到的 content_list {},提供的块信息{}".format(bucketname,filename,len(content_list),len(block_info_list)))
            assert(len(content_list)==len(block_info_list))
            chunk_count = 0
            chunk_ids_list = []
            middle_block_idx = 0 # 用于按顺序匹配 block_info_list
            processed_text_chunks = 0 # 记录处理的文本块数量
            image_info_list = []  # 图片信息列表
            #对应content_list和解析得到的坐标信息block_info_list，进行解析
            for chunk_idx, chunk_data in enumerate(content_list):
                page_idx = 0
                bbox = [0, 0, 0, 0]
                # 尝试使用 chunk_idx 直接从 block_info_list 获取对应的块信息
                if chunk_idx < len(block_info_list):
                    block_info = block_info_list[chunk_idx]
                    page_idx = block_info.get("page_idx", 0)
                    bbox = block_info.get("bbox", [0, 0, 0, 0])
                    # 验证 bbox 是否有效，如果无效则重置为默认值 (可选，取决于是否需要严格验证)
                    if not (isinstance(bbox, list) and len(bbox) == 4 and all(isinstance(n, (int, float)) for n in bbox)):
                        logging.error(f"[MinerU] Chunk {chunk_idx} 对应的 bbox 格式无效: {bbox}，将使用默认值。")
                        bbox = [0, 0, 0, 0]
                else:
                    # 如果 block_info_list 的长度小于 content_list，打印警告
                    # 仅在第一次索引越界时打印一次警告，避免刷屏
                    #if chunk_idx == len(block_info_list):
                    logging.error("MinerU middle_data 提供的块信息{} 少于 content_list 中的文本块数量{}!".format())
 
                # 转换坐标格式
                x1, y1, x2, y2 = bbox
                bbox_reordered = [x1, x2, y1, y2]
                poss = []
                #left right top bottom
                poss.append((page_idx,x1, x2, y1, y2))
                chunk_object = {}
                chunk_object['type'] = chunk_data["type"]
                chunk_object['chunk_idx'] = chunk_idx
                chunk_object['poss'] = poss

                if chunk_data["type"] == "text" or chunk_data["type"] == "equation":
                    content = chunk_data["text"]
                    # 过滤 markdown 特殊符号
                    content = re.sub(r"[!#\\$/]", "", content)
                    chunk_object['text'] = content
                    sections.append(chunk_object)
                elif chunk_data["type"] == "table":
                    #表格数据为了后续做向量化，需要图片信息、文本信息、位置信息
                    #tbls里存储的是 （image,rows）,poss
                    caption_list = chunk_data.get("table_caption", []) # 获取列表
                    table_footnote = chunk_data.get("table_footnote", []) # 获取列表
                    table_body = chunk_data.get("table_body", "")     # 获取表格主体
                    # 检查 caption_list 是否为列表，并且包含字符串元素
                    if isinstance(caption_list, list) and all(isinstance(item, str) for item in caption_list):
                        # 使用空格将列表中的所有字符串拼接起来
                        caption_str = " ".join(caption_list)
                    elif isinstance(caption_list, str):
                        # 如果 caption 本身就是字符串，直接使用
                        caption_str = caption_list
                    else:
                        # 其他情况（如空列表、None 或非字符串列表），使用空字符串
                        caption_str = ""
                    if isinstance(table_footnote, list) and all(isinstance(item, str) for item in table_footnote):
                        # 使用空格将列表中的所有字符串拼接起来
                        table_footnote_str= " ".join(table_footnote)
                    elif isinstance(caption_list, str):
                        # 如果 caption 本身就是字符串，直接使用
                        table_footnote_str =table_footnote
                    else:
                        # 其他情况（如空列表、None 或非字符串列表），使用空字符串
                        table_footnote_str = ""

                    # 将处理后的标题字符串和表格主体拼接
                    content = caption_str + table_body + table_footnote_str
                    #读取image信息
                    img_path_relative = chunk_data.get('img_path')
                    if img_path_relative:
                        logging.info("MinerU 读取原始图片 {}".format(img_path_relative))
                        img_path_relative = img_path_relative.replace('/',"")
                        image_bytes = reader_stored_files.read(img_path_relative)
                    else:
                        image_bytes = None
                    if content:
                        content = content+"\t\n"+img_path_relative
                    else:
                        content = img_path_relative
                    chunk_object['text'] = content
                    chunk_object['image'] = image_bytes
                    chunk_object['image_url'] = img_path_relative
                    sections.append(chunk_object)
                elif chunk_data["type"] == "image":
                    #图片为了后续结构化及与text内容关联，需要图片信息、图片标题信息、位置信息
                    #tbls里存储的是 （image,rows）,poss;这里rows直接用图片标题即可
                    img_path_relative = chunk_data.get('img_path')
                    if img_path_relative:
                        img_path_relative = img_path_relative.replace('/',"")
                        image_bytes = reader_stored_files.read(img_path_relative)
                    else:
                        image_bytes = None
                    caption_list = chunk_data.get('img_caption',[])
                    # 检查 caption_list 是否为列表，并且包含字符串元素
                    if isinstance(caption_list, list) and all(isinstance(item, str) for item in caption_list):
                        # 使用空格将列表中的所有字符串拼接起来
                        caption_str = " ".join(caption_list)
                    elif isinstance(caption_list, str):
                        # 如果 caption 本身就是字符串，直接使用
                        caption_str = caption_list
                    else:
                        # 其他情况（如空列表、None 或非字符串列表），使用空字符串
                        caption_str = ""
                    image_footnote = chunk_data.get("image_footnote", []) # 获取列表
                    if isinstance(image_footnote, list) and all(isinstance(item, str) for item in image_footnote):
                        # 使用空格将列表中的所有字符串拼接起来
                        image_footnote_str= " ".join(image_footnote)
                    elif isinstance(image_footnote, str):
                        # 如果 caption 本身就是字符串，直接使用
                        image_footnote_str= image_footnote
                    else:
                        # 其他情况（如空列表、None 或非字符串列表），使用空字符串
                        image_footnote_str = ""
                    content = caption_str+image_footnote_str
                    #if not content:
                    #    content = img_path_relative
                    if content:
                        content = content+"\t\n"+img_path_relative
                    else:
                        content = img_path_relative
                    chunk_object['text'] = content
                    chunk_object['image'] = image_bytes
                    chunk_object['image_url'] = img_path_relative
                    sections.append(chunk_object)

            callback(prog=0.81,msg="MinerU 解析处理结果完成 ({:.2f}s)。".format(timer()-start))
            md_content_to = md_content[:10000]
           
            time_end_process = time.time()
            time_cost = 1000*(time_end_process-time_start_process)
            logging.info('file {} MinerU 解析花费 {} md_content 长度 {} md_content_to 长度 {}'.format(filename,time_cost,len(md_content),len(md_content_to)))
        except Exception as e:
            logging.info("发生错误,文件 {},错误 {}".format(filename,e))
            import traceback
            traceback.print_exc()
            logging.info("Exception {} ,excetion info is {}".format(e,traceback.format_exc()))
            return
         #进一步对信息进行提取
        def _match_content(txt):
            return re.match(
                "[0-9. 一、i]*(introduction|abstract|摘要|引言|keywords|key words|关键词|background|背景|目录|前言|contents)",
                txt.lower().strip())
        start = timer()
        ## get title and authors
        #title = ""
        #authors = []
        #i = 0
        #while i < min(32, len(self.boxes)-1):
        #    b = self.boxes[i]
        #    i += 1
        #    if b.get("layoutno", "").find("title") >= 0:
        #        title = b["text"]
        #        if _begin(title):
        #            title = ""
        #            break
        #        for j in range(3):
        #            if _begin(self.boxes[i + j]["text"]):
        #                break
        #            authors.append(self.boxes[i + j]["text"])
        #            break
        #        break
        ## get abstract
        #abstr = ""
        #i = 0
        #while i + 1 < min(32, len(self.boxes)):
        #    b = self.boxes[i]
        #    i += 1
        #    txt = b["text"].lower().strip()
        #    if re.match("(abstract|摘要)", txt):
        #        if len(txt.split()) > 32 or len(txt) > 64:
        #            abstr = txt + self._line_tag(b, zoomin)
        #            break
        #        txt = self.boxes[i]["text"].lower().strip()
        #        if len(txt.split()) > 32 or len(txt) > 64:
        #            abstr = txt + self._line_tag(self.boxes[i], zoomin)
        #        i += 1
        #        break
        #if not abstr:
        #    i = 0


        #TODO
        #content_list实际是内容
        title = ""
        authors = []
        tbls = []
        abstr = ""
        callback(prog=0.82,msg="MinerU 解析信息提取完成({:.2f}s)".format(timer()-start))
        callback(prog=0.85,msg="MinerU 处理完成")
        # 返回的sections需要包括 text+_line_tag、layoutno。其中_line_tag表达了text的坐标信息，它用特殊字符进行分隔，以方便后续处理匹配到这些坐标信息.
        return {
            "title": title,
            "authors": " ".join(authors),
            "abstract": abstr,
            "sections":sections,
            "tables": tbls
        }

if __name__ == "__main__":
    
    def print_msg(**kargs):
        print(kargs.get('msg',"No Message!"))
    #pdf_parser = MinerUPdfParser()
    directory = "./原文"
    #page_from = 0
    #page_to = 1
    m = MinerUPdf()
    m.call_function('maxiao','Y1089380.pdf',binary=None,from_page=0,to_page=1,zoomin=3,callback=print_msg) 
    #for root, dirs, files in os.walk(directory):
    #    #只打印第一页
    #    print_number =1
    #    for file in files:
    #        file_path = os.path.join(root, file)
    #        #logger.info("当前正在处理的文件是 {}".format(file_path))       
    #        if file !='从三次国际会议看放射卫生工作的前景_陈兴安.pdf' and file!='Y1089380.pdf':
    #            continue
    #        print("当前文件 {}".format(file))
    #        with pdfplumber.open(file_path) as pdf:
    #            count_number = 0
    #            zoomin = 3
    #            #page_images = [p.to_image(resolution=72 * zoomin).annotated for i, p in
    #            #                            enumerate(pdf.pages[0:10])]
    #            page_images = []
    #            for page in pdf.pages:
    #                count_number = count_number +1
    #                p = page.to_image(resolution=72 * zoomin).annotated
    #                print("当前页面 {},Image 大小 {}".format(count_number,p.size))
    #                page_images.append(p)
    #                page_chars = [[c for c in page.dedupe_chars().chars if _has_color(c)] for page in pdf.pages[page_from:page_to]]
    #                print("非隐藏(可见)字符page_chars length 也就是页面数量是 {}".format(len(page_chars)))
    #                text = page.extract_text()
    #                if count_number ==print_number:
    #                    print('打印当前页面的内容{}'.format(text))
    #                break
    #        for i, img in enumerate(page_images):
    #            chars = []
    #            pdf_parser.ocr_function(i+1, img, chars, ZM=3, device_id=0)
    #pass
