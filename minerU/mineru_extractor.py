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
from datetime import datetime
import json
import logging
import re

from magic_pdf.data.data_reader_writer import S3DataReader
from timeit import default_timer as timer
from minerU.parser.figure_parser import VisionFigureParser

from api.db import LLMType, constant
from api.db.services.llm_service import LLMBundle
from rag import settings


def format_time(time_field_value):
    time_field_value_format = None

    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y年%m月%d日",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d",
        "%Y.%m.%d",
        "%m/%d/%Y %H:%M",
    ]
    for format_string in formats:
        try:
            time_field_value_format = datetime.strptime(time_field_value, format_string)
            logging.info(f"Parsed date {time_field_value}-->{time_field_value_format}")
            time_field_value_format = "{}".format(time_field_value_format.strftime('%Y-%m-%d %H:%M:%SZ'))
            return time_field_value_format
        except Exception as e:
            logging.error("Failed to parse {} use format {} for Exception {}".format(time_field_value,format_string,time_field_value_format))
            continue
    return time_field_value_format


def get_pdf_file_bytes(bucketname, filename, doc_id, pdf_flag=True):
    """获取pdf文件字节流"""
    pdf_file_name = filename
    prefix = ''
    if not pdf_flag:
        name_without_suff = filename.split(".")[0]
        pdf_file_name = name_without_suff + ".pdf"
        prefix = f'minerU/{doc_id}'

    s3_config = settings.S3
    ak = s3_config.get('access_key', None)
    sk = s3_config.get('secret_key', None)
    endpoint_url = s3_config.get('endpoint_url', None)
    bucket_name = bucketname

    try:
        reader = S3DataReader(f'/{prefix}', bucket_name, ak, sk, endpoint_url)
        # 打开PDF流
        logging.info("正在读取prefix {} file name {}".format(prefix, pdf_file_name))
        pdf_bytes_new = reader.read(pdf_file_name)
        return pdf_bytes_new
    except Exception as e:
        logging.info("发生错误,文件 {},错误 {}".format(filename, e))

    return None


def vision_parser(tenant_id, figures, key_list_to_extract=None, prompt=None):
    """视觉模型执行方法-自定义prompt提示词"""
    logging.info("正在进行视觉模型调用...")
    try:
        vision_model = LLMBundle(tenant_id, LLMType.IMAGE2TEXT)
    except Exception:
        vision_model = None
        logging.error(f"Not Found Vision Model For tenant_id {tenant_id}")
    if vision_model:
        try:
            pdf_vision_parser = VisionFigureParser(
                vision_model=vision_model,
                figures_data=figures,
                key_list_to_extract=key_list_to_extract,
                prompt=prompt
            )
            boosted_figures = pdf_vision_parser()
            return boosted_figures
        except Exception as e:
            logging.error(f"Visual model error: {e}")
            raise e
    return None


def judge_directory_type(tenant_id=None, img=None, callback=None):
    # 判断第一页目录图片是否是论文集或书籍
    is_what = ""
    maybe = {
        "论文集目录": "核心特征是 每篇独立的文章标题后都跟随着该文作者的姓名（且作者可能不止一人）。内容是多位作者关于不同（但相关）主题的独立论文集合。",
        "书籍目录": "核心特征是 层级化的章节结构（引子、第X章、X.X节）和 页码的连续性。内容是围绕一个或几个核心主题由（通常少量）作者进行的系统性阐述，目录中不出现作者署名。",
    }
    example = {"结果":""}
    prompt = (
        f"声明：你的回答不需要有任何旁白，若不是纯粹的目录页面，请直接输出一个空花括号即可；定义：{maybe}"
        f"现在输入的图片，有可能是文档的目录索引，也有可能是正文章节，也有可能都不是;"
        f"请根据图片内容判断该图片是不是文档的纯粹的目录页面，如果不是纯粹的目录页面，请直接输出一个空花括号即可;如果是存粹的目录页面，请结合定义判断该页目录最有可能属于什么类型的目录；"
        f"请你以JSON格式输出，以结果二字为Key，值是定义内最符合结果的键名；请你以最紧凑的JSON格式输出文本，可以去掉多余的空格；格式示例：{example}")
    logging.info(f"======prompt======{prompt}")
    callback(msg="正在识别是否存在子论文...")

    vision_result = vision_parser(tenant_id, [img], prompt=prompt)
    if len(vision_result) > 0:
        logging.info("<vision_result> {}".format(vision_result[0]))
        res = json.loads(vision_result[0])
        if "结果" in res:
            is_what = res["结果"]

    callback(msg=f"识别结果：{is_what}")
    return is_what.replace("目录", "")


# 识别提取元数据
def extract_metadata(tenant_id, images, fields=None, metadata_type="default", callback=None):
    start_ts = timer()
    # 获取相应元数据字段
    keys_to_use_list = []
    # 过滤字段
    for i in fields:
        logging.info(
            f"metadata_type [{metadata_type}] ==== i ===> {i}")
        keys_to_use_list.append({
            "name": i["name"],
            #"description": i["description"] if i.get("description") else "",
            "must_exist": i["must_exist"],
        })

    # 通过视觉模型 从目录页前的内容中 提取元数据
    fields_map = {}
    example = """{"name1": 提取内容a,"name2": 提取内容b,"name3": 提取内容c}"""
    prompt = (
        f"请提取图中的：{keys_to_use_list} 文本内容；不要编造，直接从图片中获取文本，注意完整性，不要仅返回部分内容。must_exist 为True的字段必须提取；以图片中原始文本的语言输出，不要进行总结摘要等操作。不要获取除name字段之外的信息，如果某些name字段没有没有提取到相应的内容，设置为空字符即可；"
        f"请你以最紧凑的JSON格式输出文本，可以去掉多余的空格。key使用name字段，格式示例：{example}"
    )
    logging.info(msg="正在进行视觉模型调用提取要素...")
    logging.info(f"======prompt======{prompt}")
    vision_results = vision_parser(tenant_id, images, prompt=prompt)
    for vr_key, vr_value in vision_results.items():
        logging.info(f"vr_key ===> {vr_key} vr_value ===>\n{vr_value}")
        if vr_value:
            try:
                r_d = json.loads(vr_value)
            except Exception as e:
                r_d = {}
                logging.error(f"json loads error: {e} \n{vr_value}")

            for key in [v["name"] for v in keys_to_use_list]:
                value_now = fields_map.get(key, None)
                if value_now:
                    if key not in ['摘要', '正文', '前言']:
                        continue
                    else:
                        current_value = r_d.get(key, None)
                        if current_value:
                            try:
                                fields_map[key] = value_now+ '\n' + current_value
                            except Exception as e:
                                logging.error(f"key {key} value_now {value_now},current_value {current_value},exception {e}")
                                fields_map[key] = str(value_now)+ '\n' + str(current_value)
                else:
                    current_value = r_d.get(key, None)
                    if current_value is not None:
                        fields_map[key] = current_value

    return fields_map

# 视觉模型识别提取目录数据
def extract_directory(tenant_id, images, callback=None):
    start_ts = timer()

    # 最大识别图片页数
    MAX_IMAGES = 40
    example = """{"目录": [{"章节": "章节1","页码": 1},{"章节": "章节2","页码": 14}]}"""
    prompt = (f"声明：你的回答不需要有任何旁白，若不是纯粹的目录页面，请直接输出一个空花括号即可；现在输入的图片，有可能是文档的目录索引，也有可能是正文章节，也有可能都不是，请根据图片内容判断该图片是不是文档的纯粹的目录页面，如果不是纯粹的目录页面，请不要提取。如果是，请提取图中的目录，请输出目录中的各个章节所对应的页码，"
              f"若章节没有章节序号，则提取图片内的所有章节及页码；若存在章节序号，只需要提取一级目录（一级目录的章节序号只有一个整数数字带有小数的章节序号都不是一级目录，可能存在整页都不是一级目录的情况），若没有一级目录请直接输出一个空花括号即可；"
              f"请你以JSON格式输出，以目录二字为Key，值是一个章节索引的列表，列表中是章节作为key，页码作为Key，两个Key组成；请你以最紧凑的JSON格式输出文本，可以去掉多余的空格，key值中不需要有章节序号；格式示例：{example}")
    logging.info(f"======prompt======{prompt}")
    callback(msg="正在进行视觉模型调用提取目录...")

    is_what = None
    # 找到目录后又出现空结果则判断目录页结束
    empty_num = 0
    directory_num = 0
    is_begin = False
    result = []
    the_directory_end = 0
    the_directory_begins = 0
    for idx, img in enumerate(images[:MAX_IMAGES]):
        vision_result = vision_parser(tenant_id, [img], prompt=prompt)
        res = [v for k, v in vision_result.items()]
        if len(res) > 0:
            response = res[0]
            try:
                if "目录" in json.loads(response):
                    is_begin = True
                    empty_num = 0
                    directory_num += 1
                    the_directory_end = idx
                    if not is_what:
                        the_directory_begins = idx
                        try:
                            # 判断第一页目录图片是否是论文集或书籍
                            is_what = judge_directory_type(tenant_id=tenant_id, img=img, callback=callback)
                        except Exception as e:
                            logging.error("judge_directory_type error {}".format(e))
                elif is_begin:
                    empty_num += 1
            except Exception as e:
                logging.error("error {}".format(e))
            result.append(response)
        if empty_num >= 3:
            logging.info(f"找到目录后又出现空结果{empty_num}次，判断目录页结束")
            break
        logging.info(f"idx {idx}, 已找到{directory_num}页完整目录json")

    logging.info(f"输入 images 共{len(images)}页 解析{len(images[:MAX_IMAGES])}页结果：{result}")
    logging.info(f"the_directory_begins idx: {the_directory_begins}; the_directory_end idx: {the_directory_end} ")
    current_page_index = 0
    page_end = 0
    page_start = 0
    dic_result = []
    index_id = 0
    first_flag = False
    for r in result:
        try:
            r_d = json.loads(r)
        except Exception as e:
            r_d = {}
            logging.error(f"json loads error: {e} \n{r}")
        index_id = index_id + 1
        if '目录' in r_d:
            logging.info(r_d['目录'])
            for i in r_d['目录']:
                obj = {}
                if not i.get('章节', None) or not i.get('页码', None):
                    continue
                obj['章节'] = i['章节']
                obj['页码'] = i['页码']
                try:
                    int_obj = int(obj['页码'])
                except Exception:
                    continue
                # print(f'比较页面 {int_obj}')
                if obj['页码'] and int_obj >= current_page_index:
                    if not first_flag:
                        first_flag = True
                        page_start = index_id
                    dic_result.append(obj)
                    current_page_index = int_obj
                    page_end = index_id
                else:
                    continue

    page_numbers = list(range(page_start - 1))

    logging.info('\n章节页码结果{}, 从index_id {}开始是正文,{}~{}是目录.将会对{}进行分析'.format(
        dic_result, page_end + 1, page_start, page_end, page_numbers
    ))

    callback(msg="提取目录完成，用时({:.2f}s)".format(timer() - start_ts))
    return {
        "dic_result": dic_result,
        "main_content_begin": the_directory_end + 1,
        "directory_begin": page_start,
        "directory_end": page_end,
        "page_numbers_before_directory": page_numbers,
    }, is_what
