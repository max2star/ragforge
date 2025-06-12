import json
import logging
import re

from magic_pdf.data.data_reader_writer import S3DataReader
from timeit import default_timer as timer
from minerU.parser.figure_parser import VisionFigureParser
import fitz
from api.db import LLMType, constant
from api.db.services.llm_service import LLMBundle
from rag import settings
import trio
from graphrag.utils import (
    chat_limiter,
)


class ChatWithModel:
    def __init__(self, llm_model, prompt):
        self._llm_model = llm_model
        self._prompt = prompt

    async def _chat(self, system, history, gen_conf):
        response = await trio.to_thread.run_sync(
            lambda: self._llm_model.chat(system, history, gen_conf)
        )
        logging.info(f"response begin ==>\n{response}")
        if "</think>" in response:
            response = re.sub(r"^.*?</think>", "", response, flags=re.DOTALL)
        if "```json" in response:
            response = re.sub(r"```json|```", "", response, flags=re.DOTALL).strip()
        logging.info(f"response clean ==>\n{response}")
        if response.find("**ERROR**") >= 0:
            raise Exception(response)
        return response


    async def __call__(self, callback=None):
        results = {}
        async def classifier():
            nonlocal results
            result = None

            async with chat_limiter:
                result = await self._chat(
                    "You're a helpful assistant.",
                    [
                        {
                            "role": "system",
                            "content": "",
                        },
                        {
                            "role": "user",
                            "content": self._prompt,
                        }
                    ],
                    {"temperature": 0.3,'response_format':{'type': 'json_object'}},
                )
            try:
                results = json.loads(result)
                logging.info(f"dict {results}")
            except Exception as e:
                results = {}
                logging.error(f"chat Failed for {e}")

        async with trio.open_nursery() as nursery:
               async with chat_limiter:
                    nursery.start_soon(classifier)

        return results



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
    return None


# 识别提取元数据
def extract_metadata(tenant_id, images, fields=None, metadata_type="default", callback=None):
    start_ts = timer()
    # 获取相应元数据字段
    keys_to_use_list = []
    # 过滤字段
    for i in fields:
        if i["name"] in [j["name"] for j in constant.keyvalues_mapping[metadata_type]]:
            keys_to_use_list.append({
                "name": i["name"],
                "description": i["description"],
                "must_exist": i["must_exist"],
            })

    # 通过视觉模型 从目录页前的内容中 提取元数据
    fields_map = {}

    prompt = (
        f"提取图中的：{keys_to_use_list} 文本内容；按照 description 进行提取相应的 name 字段，must_exist 为True的字段必须提取；对于从图片中提取的内容，不要修改原文；"
        f"不要输出```json```等Markdown格式代码段，请你以JSON格式输出。"
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

            for key in keys_to_use_list:
                value_now = fields_map.get(key, None)
                if value_now:
                    if key not in ['摘要', '正文', '前言']:
                        continue
                    else:
                        current_value = r_d.get(key, None)
                        if current_value:
                            fields_map[key] = value_now + '\n' + current_value
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
    prompt = f"声明：你的回答不需要有任何旁白，若不是纯粹的目录页面，请直接输出一个空花括号即可；现在输入的图片，有可能是文档的目录索引，也有可能是正文章节，也有可能都不是，请根据图片内容判断该图片是不是文档的纯粹的目录页面，如果不是纯粹的目录页面，请不要提取。如果是，请提取图中的目录，请输出目录中的各个章节所对应的页码。请你以JSON格式输出，以目录二字为Key，值是一个章节索引的列表，列表中是章节作为key，页码作为Key，两个Key组成；格式示例：{example}"
    logging.info(f"======prompt======{prompt}")
    callback(msg="正在进行视觉模型调用提取目录...")
    vision_results = vision_parser(tenant_id, images[:MAX_IMAGES], prompt=prompt)
    result = [v for k,v in vision_results.items()]
    logging.info(f"输入 images 共{len(images)}页 解析{len(images[:MAX_IMAGES])}页结果：{result}")

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
        "main_content_begin": page_end + 1,
        "directory_begin": page_start,
        "directory_end": page_end,
        "page_numbers_before_directory": page_numbers,
    }
