import logging
from PIL import Image
import fitz
from io import BytesIO

from api.db.services.file2document_service import File2DocumentService
from minerU.mineru_extractor import get_pdf_file_bytes, extract_directory, extract_metadata

task = {}

task_id = task["id"]
task_from_page = task["from_page"]
task_to_page = task["to_page"]
# task_tenant_id = task["tenant_id"]
task["tenant_id"] = "1556e06a3d6f11f0bdf8eec690b1f472"
task_tenant_id = "1556e06a3d6f11f0bdf8eec690b1f472"
task_embedding_id = task["embd_id"]
task_language = task["language"]
task_llm_id = task["llm_id"]
task_dataset_id = task["kb_id"]
# task_doc_id = task["doc_id"]
task["doc_id"] = "81ef570841c411f0b3c83a1e8c007a1b"
task_doc_id = "81ef570841c411f0b3c83a1e8c007a1b"
task_document_name = task["name"]
task_parser_config = task["parser_config"]


dict_result = {}
key_now = dict_result.keys()

file_type = task.get("type", "pdf")
# 用户设置 parser_config ['论文集', '论文', '书籍、期刊', '其他']:
pdf_article_type = task_parser_config.get('pdf_article_type', '论文')

# 进行要素提取和分类
# chat_model = LLMBundle(task_tenant_id, LLMType.CHAT, llm_name=task_llm_id, lang=task_language)
#运行
c_count = 0
content = ""

sub_paper = {}
# 是否使用视觉模型
use_vision_parser = True if file_type in ["pdf", ] else False
if use_vision_parser:
    # 获取字节流
    bucket, name = File2DocumentService.get_storage_address(doc_id=task_doc_id)
    logging.info("pdf_bytes for bucket {} doc name {},doc_id {},tenant_id {}".format(
        bucket, name, task_doc_id, task_tenant_id
    ))
    pdf_bytes = get_pdf_file_bytes(bucket, name, task_doc_id)
    if not pdf_bytes:
        logging.error(f"Can't find this document {task_doc_id}!")
        raise LookupError(f"Can't find this document {task_doc_id}!")

    pdf_doc = fitz.open('pdf', pdf_bytes)
    img_results = []
    for page_num in range(len(pdf_doc)):
        page = pdf_doc.load_page(page_num)
        # 将PDF页面转换为高质量图像（调整dpi参数根据需要）
        mat = fitz.Matrix(2.0, 2.0)  # 缩放因子，提高分辨率
        pix = page.get_pixmap(matrix=mat)

        # 转换为PIL Image对象
        img_bytes = pix.tobytes()
        img = Image.open(BytesIO(img_bytes))
        img_results.append(img)

    # fields = None  # 使用默认name字段 constant.keyvalues_mapping['default']
    fields = ['书名', '其他书名', '编者', '作者', '出版日期', '摘要', '关键词', '前言', '分类', 'ISBN', '出版社']
    if pdf_article_type in ["论文集", "书籍"]:
        """
        通过将pdf转换为图像，使用视觉模型进行目录页定位; 将目录页前内容用于元数据要素提取（摘要、标题、关键词等）
        """
        # 提取目录
        result = extract_directory(
            task_tenant_id,  # 当前租户的唯一标识符，标识数据的归属, 使用用户选择的视觉模型
            images=img_results,
            # callback=progress_callback,
        )  # 提取目录，处理合并多张图片的结果后返回相关数据的 json 对象
        page_numbers = result["page_numbers_before_directory"]

        # 提取元数据
        fields_map = extract_metadata(
            task_tenant_id,  # 当前租户的唯一标识符，标识数据的归属, 使用用户选择的视觉模型
            images=[img_results[i] for i in page_numbers],
            fields=fields,  #  可指定需要提取的元数据字段的列表(有默认值)
            # callback=progress_callback,
        )  # 提取并映射所需字段的元数据，处理合并多张图片的结果后返回一个包含元数据的 json 对象

        if pdf_article_type == "论文集":
            # 解析目录页码，定位每篇论文，用每篇论文第一页作为数据提取相应元数据
            main_content_begin = result['main_content_begin']
            sub_paper["main_content_begin"] = main_content_begin
            sub_paper["fields_map"] = {}
            for i in range(len(result['dic_result']) - 1):
                res = result['dic_result'][i]
                title_ = res['章节']
                page_ = res['页码']
                pdf_page_ = main_content_begin - 1 + page_
                picture_ = img_results[pdf_page_]
                fields_map_ = extract_metadata(
                    task_tenant_id, images=[picture_], fields=fields,
                )
                sub_paper["fields_map"][pdf_page_] = {
                    "title_": title_, "page_": page_,
                    "fields_map_": fields_map_,
                }
    else:
        """
        单篇论文、期刊
        通过将pdf转换为图像，使用视觉模型进行元数据要素提取打标签（摘要、标题、关键词等）
        """
        # 提取元数据
        fields_map = extract_metadata(
            task_tenant_id,  # 当前租户的唯一标识符，标识数据的归属, 使用用户选择的视觉模型
            images=img_results[:10],
            fields=fields,  # 可指定需要提取的元数据字段的列表(有默认值)
        )  # 提取并映射所需字段的元数据，处理合并多张图片的结果后返回一个包含元数据的 json 对象

    dict_result_add = fields_map
else:
    # for c_ in chunks:
    #     content = content + "\n" + c_['content_with_weight']
    #     c_count = c_count + len(c_['content_with_weight'])
    #     if c_count >= 5000:
    #         break
    logging.debug(f"do_handle_task current content {content}")

    # dict_result_add = await run_extract(task, chat_model, content, progress_callback)
    dict_result_add = None

logging.info(f"doc {task['doc_id']} 新抽取的 meta fields {dict_result_add}")
for key,value in dict_result_add.items():
    if key in key_now and dict_result.get(key,None):
        logging.info(f"do_handle_task doc {task['doc_id']} metadata keyvalue {key}-{value} exists.")
        dict_result[key] = value
    else:
        dict_result[key] = value
logging.info(f"doc {task['doc_id']} 合并后的 meta fields {dict_result}")







