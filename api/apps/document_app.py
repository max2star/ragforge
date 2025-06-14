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
#  limitations under the License
#
import json
import os.path
import pathlib
import re

import flask
from flask import request
from flask_login import login_required, current_user

from deepdoc.parser.html_parser import RAGFlowHtmlParser
from rag.nlp import search

from api.db import FileType, TaskStatus, ParserType, FileSource
from api.db.db_models import File, Task
from api.db.services.file2document_service import File2DocumentService
from api.db.services.file_service import FileService
from api.db.services.task_service import queue_tasks
from api.db.services.user_service import UserTenantService
from api.db.services import duplicate_name
from api.db.services.knowledgebase_service import KnowledgebaseService
from api.db.services.task_service import TaskService
from api.db.services.document_service import DocumentService, doc_upload_and_parse
from api.utils.api_utils import (
    server_error_response,
    get_data_error_result,
    validate_request,
)
import uuid
from api.utils import get_uuid,current_timestamp
from api import settings
from api.utils.api_utils import get_json_result
from rag.utils.storage_factory import STORAGE_IMPL
from api.utils.file_utils import filename_type, thumbnail, get_project_base_directory
from api.utils.web_utils import html2pdf, is_valid_url
from api.constants import IMG_BASE64_PREFIX

import logging

@manager.route('/upload', methods=['POST'])  # noqa: F821
@login_required
@validate_request("kb_id")
def upload():
    kb_id = request.form.get("kb_id")
    limit_range = request.form.get("limit_range",[])
    if not kb_id:
        return get_json_result(
            data=False, message='Lack of "KB ID"', code=settings.RetCode.ARGUMENT_ERROR)
    if 'file' not in request.files:
        return get_json_result(
            data=False, message='No file part!', code=settings.RetCode.ARGUMENT_ERROR)

    file_objs = request.files.getlist('file')
    for file_obj in file_objs:
        if file_obj.filename == '':
            return get_json_result(
                data=False, message='No file selected!', code=settings.RetCode.ARGUMENT_ERROR)

    e, kb = KnowledgebaseService.get_by_id(kb_id)
    if not e:
        raise LookupError("Can't find this knowledgebase!")

    if not KnowledgebaseService.accessible(kb_id, current_user.id):
        return get_json_result(
            data=False,
            message='No authorization.',
            code=settings.RetCode.AUTHENTICATION_ERROR
        )

    #tenant_id = kb.tenant_id
    #if not tenant_id:
    #    return get_data_error_result(message="Tenant not found!")

    #usertenants = UserTenantService.query(user_id=current_user.id,tenant_id=tenant_id)
    #if not usertenants:
    #    return get_data_error_result(message="该用户不具备该文档所在空间的访问权限!")

    err, files = FileService.upload_document(kb, file_objs, current_user.id)
    files = [f[0] for f in files] # remove the blob
    
    if err:
        return get_json_result(
            data=files, message="\n".join(err), code=settings.RetCode.SERVER_ERROR)
    return get_json_result(data=files)


@manager.route('/mv_kb', methods=['POST'])  # noqa: F821
@login_required
@validate_request("src_kb_id","dst_kb_id","doc_ids")
def mv_kb():
    req = request.json
    src_kb_id = req.get("src_kb_id")
    dst_kb_id = req.get("dst_kb_id")
    if not src_kb_id or not dst_kb_id:
        return get_json_result(
            data=False, message='Lack of "KB ID"', code=settings.RetCode.ARGUMENT_ERROR)
    if src_kb_id==dst_kb_id:
        return get_json_result(
            data=False, message='Same src and dst "KB ID"', code=settings.RetCode.ARGUMENT_ERROR)

    e, src_kb = KnowledgebaseService.get_by_id(src_kb_id)
    if not e:
        raise LookupError("Can't find this src knowledgebase!")

    e, dst_kb = KnowledgebaseService.get_by_id(dst_kb_id)
    if not e:
        raise LookupError("Can't find this dst knowledgebase!")

    if not KnowledgebaseService.accessible(src_kb_id, current_user.id):
        return get_json_result(
            data=False,
            message=f'No authorization, user {current_user.id} kb {src_kb_id}',
            code=settings.RetCode.AUTHENTICATION_ERROR
        )

    if not KnowledgebaseService.accessible(dst_kb_id, current_user.id):
        return get_json_result(
            data=False,
            message=f'No authorization, user {current_user.id} kb {dst_kb_id}.',
            code=settings.RetCode.AUTHENTICATION_ERROR
        )

    #如果源和目的KB的embedding模型一致，则允许复制移动(其他的解析参数可以按文档粒度)；否则不允许移动到目标知识库。
    if src_kb.embd_id!=dst_kb.embd_id:
        raise LookupError("Can't move between the knowledgebases using diffrent embedding model id!")

    dst_kb_exist_location = []
    doc_ids = req["doc_ids"]
    for doc_id in doc_ids:
        e, src_d = DocumentService.get_by_id(doc_id)
        if not e:
            raise LookupError("Can't find document {} !".format(doc_id))
        exist, dst_d = DocumentService.get_by_location(dst_kb_id,src_d.location)
        if exist:
            logging.info('doc {} name {} dumplicate in dst kb_id {} with doc {}'.format(doc_id,src_d.name,dst_kb_id,dst_d.id))
            dst_kb_exist_location.append(dst_d.name)
    if dst_kb_exist_location:
        raise LookupError("Has same-location documents {} in destination kb!".format(dst_kb_exist_location))
    for doc_id in doc_ids:
        if not DocumentService.accessible(doc_id, current_user.id):
            return get_json_result(
                data=False,
                message=f'No authorization for doc_id {doc_id} for you {current_user.id}.',
                code=settings.RetCode.AUTHENTICATION_ERROR
            )
    docs = DocumentService.get_by_ids(doc_ids)
    for d in docs:
        if d.kb_id==dst_kb_id:
            logging.info('doc {} kb_id same with dst kb_id {}'.format(d.id,dst_kb_id))
            continue
        #如果是相同的tenant id，直接更新文档的kb_id Mysql数据库里更新+ES更新+Minio更新
        #否则会做添加和删除操作
        DocumentService.move_document(d,dst_kb_id,src_kb.tenant_id,dst_kb.tenant_id)
    docs = DocumentService.get_by_ids(doc_ids)
    return get_json_result(data=list(docs.dicts()))

@manager.route('/web_crawl', methods=['POST'])  # noqa: F821
@login_required
@validate_request("kb_id", "name", "url")
def web_crawl():
    kb_id = request.form.get("kb_id")
    if not kb_id:
        return get_json_result(
            data=False, message='Lack of "KB ID"', code=settings.RetCode.ARGUMENT_ERROR)
    name = request.form.get("name")
    url = request.form.get("url")
    if not is_valid_url(url):
        return get_json_result(
            data=False, message='The URL format is invalid', code=settings.RetCode.ARGUMENT_ERROR)
    e, kb = KnowledgebaseService.get_by_id(kb_id)
    if not e:
        raise LookupError("Can't find this knowledgebase!")

    if not KnowledgebaseService.accessible(kb_id, current_user.id):
        return get_json_result(
            data=False,
            message=f'No authorization, user {current_user.id} kb {kb_id}.',
            code=settings.RetCode.AUTHENTICATION_ERROR
        )

    blob = html2pdf(url)
    if not blob:
        return server_error_response(ValueError(f"Download failure {url}."))

    root_folder = FileService.get_root_folder(current_user.id)
    pf_id = root_folder["id"]
    FileService.init_knowledgebase_docs(pf_id, current_user.id)
    kb_root_folder = FileService.get_kb_folder(current_user.id)
    kb_folder = FileService.new_a_file_from_kb(kb.tenant_id, kb.name, kb_root_folder["id"])

    try:
        filename = duplicate_name(
            DocumentService.query,
            name=name + ".pdf",
            kb_id=kb.id)
        filetype = filename_type(filename)
        if filetype == FileType.OTHER.value:
            raise RuntimeError("This type of file has not been supported yet!")

        location = filename
        while STORAGE_IMPL.obj_exist(kb_id, location):
            location += "_"
        STORAGE_IMPL.put(kb_id, location, blob)
        doc = {
            "id": get_uuid(),
            "kb_id": kb.id,
            "parser_id": kb.parser_id,
            "parser_config": kb.parser_config,
            "created_by": current_user.id,
            "type": filetype,
            "name": filename,
            "location": location,
            "size": len(blob),
            "thumbnail": thumbnail(filename, blob)
        }
        if doc["type"] == FileType.VISUAL:
            doc["parser_id"] = ParserType.PICTURE.value
        if doc["type"] == FileType.AURAL:
            doc["parser_id"] = ParserType.AUDIO.value
        if re.search(r"\.(ppt|pptx|pages)$", filename):
            doc["parser_id"] = ParserType.PRESENTATION.value
        if re.search(r"\.(eml)$", filename):
            doc["parser_id"] = ParserType.EMAIL.value

        doc_filter_field = {}
        doc_filter_field['limit_range'] = [current_user.id]
        doc_filter_field['limit_level'] = 1
        doc_filter_field['limit_time'] = current_timestamp()
        doc['filter_fields'] = doc_filter_field

        DocumentService.insert(doc)
        FileService.add_file_from_kb(doc, kb_folder["id"], kb.tenant_id)
    except Exception as e:
        return server_error_response(e)
    return get_json_result(data=True)


@manager.route('/create', methods=['POST'])  # noqa: F821
@login_required
@validate_request("name", "kb_id")
def create():
    req = request.json
    kb_id = req["kb_id"]
    if not kb_id:
        return get_json_result(
            data=False, message='Lack of "KB ID"', code=settings.RetCode.ARGUMENT_ERROR)

    try:
        e, kb = KnowledgebaseService.get_by_id(kb_id)
        if not e:
            return get_data_error_result(
                message="Can't find this knowledgebase!")

        if DocumentService.query(name=req["name"], kb_id=kb_id):
            return get_data_error_result(
                message="Duplicated document name in the same knowledgebase.")

        #tenant_id = kb.tenant_id
        #if not tenant_id:
        #    return get_data_error_result(message="Tenant not found!")

        #usertenants = UserTenantService.query(user_id=current_user.id,tenant_id=tenant_id)
        #if not usertenants:
        #    return get_data_error_result(message="该用户不具备该文档所在空间的访问权限!")

        if not KnowledgebaseService.accessible(kb_id, current_user.id):
            return get_json_result(
                data=False,
                message=f'No authorization, kb {kb_id} user {current_user.id}',
                code=settings.RetCode.AUTHENTICATION_ERROR
            )

        doc= {
            "id": get_uuid(),
            "kb_id": kb.id,
            "parser_id": kb.parser_id,
            "parser_config": kb.parser_config,
            "created_by": current_user.id,
            "type": FileType.VIRTUAL,
            "name": req["name"],
            "location": "",
            "size": 0
        }
        doc_filter_field = {}
        doc_filter_field['limit_range'] = [current_user.id]
        doc_filter_field['limit_level'] = 1
        doc_filter_field['limit_time'] = current_timestamp()
        doc['filter_fields'] = doc

        doc = DocumentService.insert(doc)
        return get_json_result(data=doc.to_json())
    except Exception as e:
        return server_error_response(e)


@manager.route('/list', methods=['GET'])  # noqa: F821
@login_required
def list_docs():
    kb_id = request.args.get("kb_id")
    if not kb_id:
        return get_json_result(
            data=False, message='Lack of "KB ID"', code=settings.RetCode.ARGUMENT_ERROR)
    tenants = UserTenantService.query(user_id=current_user.id)
    for tenant in tenants:
        if KnowledgebaseService.query(
                tenant_id=tenant.tenant_id, id=kb_id):
            break
    else:
        return get_json_result(
            data=False, message='Only owner of knowledgebase authorized for this operation.',
            code=settings.RetCode.OPERATING_ERROR)
    keywords = request.args.get("keywords", "")

    page_number = int(request.args.get("page", 1))
    items_per_page = int(request.args.get("page_size", 15))
    orderby = request.args.get("orderby", "create_time")
    desc = request.args.get("desc", True)
    try:
        docs, tol = DocumentService.get_by_kb_id(
            kb_id, page_number, items_per_page, orderby, desc, keywords)

        for doc_item in docs:
            #thumbnail 是一个 ID
            if doc_item['thumbnail'] and not doc_item['thumbnail'].startswith(IMG_BASE64_PREFIX):
                doc_item['thumbnail'] = f"/v1/document/image/{kb_id}-{doc_item['thumbnail']}"

        return get_json_result(data={"total": tol, "docs": docs})
    except Exception as e:
        return server_error_response(e)


@manager.route('/infos', methods=['POST'])  # noqa: F821
@login_required
def docinfos():
    req = request.json
    doc_ids = req["doc_ids"]
    for doc_id in doc_ids:
        try:
            uuid.UUID(str(doc_id))
        except Exception as e:
            return get_json_result(
                data=False,
                message=f'Parameter {doc_id} not uuid.',
                code=settings.RetCode.ARGUMENT_ERROR
            )
        if not DocumentService.accessible(doc_id, current_user.id):
            return get_json_result(
                data=False,
                message=f'No authorization,maybe doc {doc_id} not accessible for you {current_user.id}.',
                code=settings.RetCode.AUTHENTICATION_ERROR
            )
    docs = DocumentService.get_by_ids(doc_ids)
    return get_json_result(data=list(docs.dicts()))


@manager.route('/thumbnails', methods=['GET'])  # noqa: F821
# @login_required
def thumbnails():
    doc_ids = request.args.get("doc_ids").split(",")
    if not doc_ids:
        return get_json_result(
            data=False, message='Lack of "Document ID"', code=settings.RetCode.ARGUMENT_ERROR)
    #TODO
    #for doc_id in doc_ids:
    #    if not DocumentService.accessible(doc_id, current_user.id):
    #        return get_json_result(
    #            data=False,
    #            message='No authorization.',
    #            code=settings.RetCode.AUTHENTICATION_ERROR
    #        )

    try:
        docs = DocumentService.get_thumbnails(doc_ids)

        for doc_item in docs:
            if doc_item['thumbnail'] and not doc_item['thumbnail'].startswith(IMG_BASE64_PREFIX):
                doc_item['thumbnail'] = f"/v1/document/image/{doc_item['kb_id']}-{doc_item['thumbnail']}"

        return get_json_result(data={d["id"]: d["thumbnail"] for d in docs})
    except Exception as e:
        return server_error_response(e)


@manager.route('/change_status', methods=['POST'])  # noqa: F821
@login_required
@validate_request("doc_id", "status")
def change_status():
    req = request.json
    if str(req["status"]) not in ["0", "1"]:
        return get_json_result(
            data=False,
            message='"Status" must be either 0 or 1!',
            code=settings.RetCode.ARGUMENT_ERROR)

    if not DocumentService.accessible(req["doc_id"], current_user.id):
        return get_json_result(
            data=False,
            message=f'No authorization doc_id {req["doc_id"]} for you {current_user.id}.',
            code=settings.RetCode.AUTHENTICATION_ERROR
        )

    try:
        e, doc = DocumentService.get_by_id(req["doc_id"])
        if not e:
            return get_data_error_result(message=f'Document {req["doc_id"]} not found!')
        e, kb = KnowledgebaseService.get_by_id(doc.kb_id)
        if not e:
            return get_data_error_result(
                message="Can't find this knowledgebase!")

        if not DocumentService.update_by_id(
                req["doc_id"], {"status": str(req["status"])}):
            return get_data_error_result(
                message="Database error (Document update)!")

        status = int(req["status"])
        settings.docStoreConn.update({"doc_id": req["doc_id"]}, {"available_int": status},
                                     search.index_name(kb.tenant_id), doc.kb_id)
        return get_json_result(data=True)
    except Exception as e:
        return server_error_response(e)


@manager.route('/rm', methods=['POST'])  # noqa: F821
@login_required
@validate_request("doc_id")
def rm():
    req = request.json
    doc_ids = req["doc_id"]
    if isinstance(doc_ids, str):
        doc_ids = [doc_ids]

    for doc_id in doc_ids:
        if not DocumentService.accessible4deletion(doc_id, current_user.id):
            return get_json_result(
                data=False,
                message=f'No authorization doc_id {doc_id} for you {current_user.id}.',
                code=settings.RetCode.AUTHENTICATION_ERROR
            )

    root_folder = FileService.get_root_folder(current_user.id)
    pf_id = root_folder["id"]
    FileService.init_knowledgebase_docs(pf_id, current_user.id)
    errors = ""
    for doc_id in doc_ids:
        try:
            e, doc = DocumentService.get_by_id(doc_id)
            if not e:
                return get_data_error_result(message=f"Document {doc_id} not found!")
            tenant_id = DocumentService.get_tenant_id(doc_id)
            if not tenant_id:
                return get_data_error_result(message=f"Tenant for doc {doc_id} not found!")

            b, n = File2DocumentService.get_storage_address(doc_id=doc_id)

            TaskService.filter_delete([Task.doc_id == doc_id])
            if not DocumentService.remove_document(doc, tenant_id):
                return get_data_error_result(
                    message="Database error (Document removal)!")

            f2d = File2DocumentService.get_by_document_id(doc_id)
            deleted_file_count = FileService.filter_delete([File.source_type == FileSource.KNOWLEDGEBASE, File.id == f2d[0].file_id])
            File2DocumentService.delete_by_document_id(doc_id)
            if deleted_file_count > 0:
                STORAGE_IMPL.rm(b, n)
        except Exception as e:
            errors += str(e)

    if errors:
        return get_json_result(data=False, message=errors, code=settings.RetCode.SERVER_ERROR)

    return get_json_result(data=True)


@manager.route('/run', methods=['POST'])  # noqa: F821
@login_required
@validate_request("doc_ids", "run")
def run(): 
    req = request.json
    for doc_id in req["doc_ids"]:
        if not DocumentService.accessible(doc_id, current_user.id):
            return get_json_result(
                data=False,
                message=f'No authorization doc_id {doc_id} for you {current_user.id}.',
                code=settings.RetCode.AUTHENTICATION_ERROR
            )
    try:
        for id in req["doc_ids"]:
            info = {"run": str(req["run"]), "progress": 0}
            if str(req["run"]) == TaskStatus.RUNNING.value and req.get("delete", False):
                info["progress_msg"] = ""
                info["chunk_num"] = 0
                info["token_num"] = 0
            DocumentService.update_by_id(id, info)
            tenant_id = DocumentService.get_tenant_id(id)
            if not tenant_id:
                return get_data_error_result(message="Tenant not found!")
            e, doc = DocumentService.get_by_id(id)
            if not e:
                return get_data_error_result(message="Document not found!")
            if req.get("delete", False):
                TaskService.filter_delete([Task.doc_id == id])
                if settings.docStoreConn.indexExist(search.index_name(tenant_id), doc.kb_id):
                    settings.docStoreConn.delete({"doc_id": id}, search.index_name(tenant_id), doc.kb_id)

            if str(req["run"]) == TaskStatus.RUNNING.value:
                e, doc = DocumentService.get_by_id(id)
                doc = doc.to_dict()
                doc["tenant_id"] = tenant_id
                bucket, name = File2DocumentService.get_storage_address(doc_id=doc["id"])
                #添加任务的时候使用的是从DocumentService中获取的doc，里边具备任务的parser_id/parser_config等信息
                queue_tasks(doc, bucket, name, 0)

        return get_json_result(data=True)
    except Exception as e:
        return server_error_response(e)


@manager.route('/rename', methods=['POST'])  # noqa: F821
@login_required
@validate_request("doc_id", "name")
def rename():
    req = request.json
    if not DocumentService.accessible(req["doc_id"], current_user.id):
        return get_json_result(
            data=False,
            message=f'No authorization doc_id {req["doc_id"]} for you {current_user.id}.',
            code=settings.RetCode.AUTHENTICATION_ERROR
        )
    try:
        e, doc = DocumentService.get_by_id(req["doc_id"])
        if not e:
            return get_data_error_result(message="Document not found!")
        if pathlib.Path(req["name"].lower()).suffix != pathlib.Path(
                doc.name.lower()).suffix:
            return get_json_result(
                data=False,
                message="The extension of file can't be changed",
                code=settings.RetCode.ARGUMENT_ERROR)
        for d in DocumentService.query(name=req["name"], kb_id=doc.kb_id):
            if d.name == req["name"]:
                return get_data_error_result(
                    message="Duplicated document name in the same knowledgebase.")

        if not DocumentService.update_by_id(
                req["doc_id"], {"name": req["name"]}):
            return get_data_error_result(
                message="Database error (Document rename)!")

        informs = File2DocumentService.get_by_document_id(req["doc_id"])
        if informs:
            e, file = FileService.get_by_id(informs[0].file_id)
            FileService.update_by_id(file.id, {"name": req["name"]})

        return get_json_result(data=True)
    except Exception as e:
        return server_error_response(e)


@manager.route('/get/<doc_id>', methods=['GET'])  # noqa: F821
#@login_required
def get(doc_id):
    try:
        e, doc = DocumentService.get_by_id(doc_id)
        if not e:
            logging.info(f"get for {doc_id},not found")
            return get_data_error_result(message="Document not found!")

        #if not DocumentService.accessible(doc_id, current_user.id):
        #    return get_json_result(
        #        data=False,
        #        message=f'No authorization doc_id {doc_id} for you {current_user.id}.',
        #        code=settings.RetCode.AUTHENTICATION_ERROR
        #    )

        b, n = File2DocumentService.get_storage_address(doc_id=doc_id)
        response = flask.make_response(STORAGE_IMPL.get(b, n))

        ext = re.search(r"\.([^.]+)$", doc.name)
        if ext:
            logging.info(f"get for {doc_id},type {ext.group(1)}")
            if doc.type == FileType.VISUAL.value:
                response.headers.set('Content-Type', 'image/%s' % ext.group(1))
            else:
                response.headers.set(
                    'Content-Type',
                    'application/%s' %
                    ext.group(1))
        return response
    except Exception as e:
        return server_error_response(e)

import markdown
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

def markdown_to_html(md_text):
    # 创建 Markdown 转换器（启用常用扩展）
    html = markdown.markdown(
        md_text,
        extensions=[
            'extra',        # 包含表格、缩写等扩展
            'codehilite',   # 代码高亮（需 pygments）
            'toc',          # 目录生成
            'nl2br',        # 换行转 <br>
            'sane_lists'    # 智能列表
        ],
        extension_configs={
            'codehilite': {
                'css_class': 'highlight',  # 高亮代码的 CSS 类
                'linenums': True           # 显示行号
            },
            'toc': {
                'toc_depth': '2-4',        # 目录层级
                'anchorlink': True         # 添加锚点链接
            }
        },
        output_format='html5'
    )
    return html

@manager.route('/get_md/<doc_id>', methods=['GET'])  # noqa: F821
@login_required
def get_md(doc_id):
    try:
        e, doc = DocumentService.get_by_id(doc_id)
        if not e:
            return get_data_error_result(message=f"Document {doc_id} not found!")

        if not DocumentService.accessible(doc_id, current_user.id):
            return get_json_result(
                data=False,
                message=f'No authorization doc_id {doc_id} for you {current_user.id}.',
                code=settings.RetCode.AUTHENTICATION_ERROR
            )
        if doc.md_location:
            logging.info(f"get md for {doc_id},location {doc.md_location}")
            res = STORAGE_IMPL.get(doc.kb_id, doc.md_location)
            response = flask.make_response(res)
        else:
            logging.error(f"get md for {doc_id},location {doc.md_location} not found")
            #return get_data_error_result(message=f"Document {doc_id} MarkDown {doc.md_location} not found, maybe not parsed by MinerU!")
            return get_json_result(
                        data=False,
                        message=f"Document {doc_id} MarkDown {doc.md_location} not found, maybe not parsed by MinerU!",
                        code=settings.RetCode.NOT_FOUND
                    )

        response.headers.set('Content-Type', 'text/markdown; charset=utf-8')
        return response
    except Exception as e:
        return server_error_response(e)

@manager.route('/get_md_html/<doc_id>', methods=['GET'])  # noqa: F821
@login_required
def get_md_html(doc_id):
    try:
        e, doc = DocumentService.get_by_id(doc_id)
        if not e:
            return get_data_error_result(message=f"Document {doc_id} not found!")

        if not DocumentService.accessible(doc_id, current_user.id):
            return get_json_result(
                data=False,
                message=f'No authorization doc_id {doc_id} for you {current_user.id}.',
                code=settings.RetCode.AUTHENTICATION_ERROR
            )
        if doc.md_location:
            logging.info(f"get md for {doc_id},location {doc.md_location}")
            res = STORAGE_IMPL.get(doc.kb_id, doc.md_location)
            html = markdown_to_html(res)
            # 生成代码高亮的 CSS 样式（可选）
            css_style = HtmlFormatter(style='monokai').get_style_defs('.highlight')
            # 返回包含样式的完整 HTML
            html_out = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>{css_style}</style>
                <style>
                    body {{ font-family: sans-serif; line-height: 1.6; }}
                    table {{ border-collapse: collapse; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; }}
                    pre {{ background: #f5f5f5; padding: 15px; }}
                </style>
            </head>
            <body>{html}</body>
            </html>
            """
            response = flask.make_response(html_out)
        else:
            logging.error(f"get md for {doc_id},location {doc.md_location} not found")
            return get_json_result(
                        data=False,
                        message=f"Document {doc_id} MarkDown {doc.md_location} not found, maybe not parsed by MinerU!",
                        code=settings.RetCode.NOT_FOUND
                    )
            #return get_data_error_result(message=f"Document {doc_id} MarkDown {doc.md_location} not found, maybe not parsed by MinerU!")

        response.headers.set('Content-Type', 'text/html; charset=utf-8')
        return response
    except Exception as e:
        return server_error_response(e)

@manager.route('/get_layout/<doc_id>', methods=['GET'])  # noqa: F821
@login_required
def get_layout(doc_id):
    try:
        e, doc = DocumentService.get_by_id(doc_id)
        if not e:
            return get_data_error_result(message="Document not found!")

        if not DocumentService.accessible(doc_id, current_user.id):
            return get_json_result(
                data=False,
                message=f'No authorization doc_id {doc_id} for you {current_user.id}.',
                code=settings.RetCode.AUTHENTICATION_ERROR
            )

        if doc.layout_location:
            logging.info(f"get layout for {doc_id},location {doc.layout_location}")
            res = STORAGE_IMPL.get(doc.kb_id, doc.layout_location)
            response = flask.make_response(res)
        else:
            logging.error(f"get layout for {doc_id},layout {doc.layout_location} not found")
            return get_json_result(
                        data=False,
                        message=f"Document {doc_id} Layout {doc.layout_location} not found, maybe not parsed by MinerU!",
                        code=settings.RetCode.NOT_FOUND
                    )
            #return get_data_error_result(message=f"Document {doc_id} Layout {doc.layout_location} not found, maybe not parsed by MinerU!")

        #TODO 都是pdf？
        ext = re.search(r"\.([^.]+)$", doc.name)
        if ext:
            if doc.type == FileType.VISUAL.value:
                response.headers.set('Content-Type', 'image/%s' % ext.group(1))
            else:
                response.headers.set(
                    'Content-Type',
                    'application/%s' %
                    ext.group(1))
        return response
    except Exception as e:
        return server_error_response(e)

@manager.route('/change_parser', methods=['POST'])  # noqa: F821
@login_required
@validate_request("doc_id", "parser_id")
def change_parser():
    req = request.json
    logging.info(f"\n\nchange_parser =========> {req}\n\n")
    if not DocumentService.accessible(req["doc_id"], current_user.id):
        return get_json_result(
            data=False,
            message=f'No authorization doc_id {req["doc_id"]} for you {current_user.id}.',
            code=settings.RetCode.AUTHENTICATION_ERROR
        )
    try:
        e, doc = DocumentService.get_by_id(req["doc_id"])
        if not e:
            return get_data_error_result(message="Document not found!")
        if doc.parser_id.lower() == req["parser_id"].lower():
            if "parser_config" in req:
                if req["parser_config"] == doc.parser_config:
                    return get_json_result(data=True)
            else:
                return get_json_result(data=True)

        if ((doc.type == FileType.VISUAL and req["parser_id"] != "picture")
                or (re.search(
                    r"\.(ppt|pptx|pages)$", doc.name) and req["parser_id"] != "presentation")):
            return get_data_error_result(message="Not supported yet,ppt/pptx/pages can only use presentation, and visual can only use picture.")

        e = DocumentService.update_by_id(doc.id,
                                         {"parser_id": req["parser_id"], "progress": 0, "progress_msg": "",
                                          "run": TaskStatus.UNSTART.value})
        if not e:
            return get_data_error_result(message=f"Document {doc.id} not found!")
        if "parser_config" in req:
            DocumentService.update_parser_config(doc.id, req["parser_config"])
        if doc.token_num > 0:
            e = DocumentService.increment_chunk_num(doc.id, doc.kb_id, doc.token_num * -1, doc.chunk_num * -1,
                                                    doc.process_duation * -1)
            if not e:
                return get_data_error_result(message="Document not found!")
            tenant_id = DocumentService.get_tenant_id(req["doc_id"])
            if not tenant_id:
                return get_data_error_result(message="Tenant not found!")
            if settings.docStoreConn.indexExist(search.index_name(tenant_id), doc.kb_id):
                settings.docStoreConn.delete({"doc_id": doc.id}, search.index_name(tenant_id), doc.kb_id)

        return get_json_result(data=True)
    except Exception as e:
        return server_error_response(e)

#TODO 干啥的
@manager.route('/image/<image_id>', methods=['GET'])  # noqa: F821
# @login_required
def get_image(image_id):
    try:
        arr = image_id.split("-")
        if len(arr) != 2:
            return get_data_error_result(message=f"Image {image_id} not found.")
        bkt, nm = image_id.split("-")

        #TODO
        #if not KnowledgebaseService.accessible(bkt, current_user.id):
        #    return get_json_result(
        #        data=False,
        #        message=f'No authorization for kb {kb_id} when get image id {image_id}.',
        #        code=settings.RetCode.AUTHENTICATION_ERROR
        #    )

        response = flask.make_response(STORAGE_IMPL.get(bkt, nm))
        response.headers.set('Content-Type', 'image/JPEG')
        return response
    except Exception as e:
        return server_error_response(e)


#TODO 干啥的
@manager.route('/upload_and_parse', methods=['POST'])  # noqa: F821
@login_required
@validate_request("conversation_id")
def upload_and_parse():
    if 'file' not in request.files:
        return get_json_result(
            data=False, message='No file part!', code=settings.RetCode.ARGUMENT_ERROR)

    file_objs = request.files.getlist('file')
    for file_obj in file_objs:
        if file_obj.filename == '':
            return get_json_result(
                data=False, message='No file selected!', code=settings.RetCode.ARGUMENT_ERROR)

    doc_ids = doc_upload_and_parse(request.form.get("conversation_id"), file_objs, current_user.id)

    return get_json_result(data=doc_ids)


#TODO 干啥的
@manager.route('/parse', methods=['POST'])  # noqa: F821
@login_required
def parse():
    url = request.json.get("url") if request.json else ""
    if url:
        if not is_valid_url(url):
            return get_json_result(
                data=False, message='The URL format is invalid', code=settings.RetCode.ARGUMENT_ERROR)
        download_path = os.path.join(get_project_base_directory(), "logs/downloads")
        os.makedirs(download_path, exist_ok=True)
        from seleniumwire.webdriver import Chrome, ChromeOptions
        options = ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_experimental_option('prefs', {
            'download.default_directory': download_path,
            'download.prompt_for_download': False,
            'download.directory_upgrade': True,
            'safebrowsing.enabled': True
        })
        driver = Chrome(options=options)
        driver.get(url)
        res_headers = [r.response.headers for r in driver.requests if r and r.response]
        if len(res_headers) > 1:
            sections = RAGFlowHtmlParser().parser_txt(driver.page_source)
            driver.quit()
            return get_json_result(data="\n".join(sections))

        class File:
            filename: str
            filepath: str

            def __init__(self, filename, filepath):
                self.filename = filename
                self.filepath = filepath

            def read(self):
                with open(self.filepath, "rb") as f:
                    return f.read()

        r = re.search(r"filename=\"([^\"]+)\"", str(res_headers))
        if not r or not r.group(1):
            return get_json_result(
                data=False, message="Can't not identify downloaded file", code=settings.RetCode.ARGUMENT_ERROR)
        f = File(r.group(1), os.path.join(download_path, r.group(1)))
        txt = FileService.parse_docs([f], current_user.id)
        return get_json_result(data=txt)

    if 'file' not in request.files:
        return get_json_result(
            data=False, message='No file part!', code=settings.RetCode.ARGUMENT_ERROR)

    file_objs = request.files.getlist('file')
    txt = FileService.parse_docs(file_objs, current_user.id)

    return get_json_result(data=txt)


@manager.route('/set_meta', methods=['POST'])  # noqa: F821
@login_required
@validate_request("doc_id", "meta")
def set_meta():
    req = request.json
    if not DocumentService.accessible(req["doc_id"], current_user.id):
        return get_json_result(
            data=False,
            message=f'No authorization doc_id {req["doc_id"]} for you {current_user.id}.',
            code=settings.RetCode.AUTHENTICATION_ERROR
        )
    try:
        meta = json.loads(req["meta"])
    except Exception as e:
        return get_json_result(
            data=False, message=f'Json syntax error: {e}', code=settings.RetCode.ARGUMENT_ERROR)
    if not isinstance(meta, dict):
        return get_json_result(
            data=False, message='Meta data should be in Json map format, like {"key": "value"}', code=settings.RetCode.ARGUMENT_ERROR)

    try:
        e, doc = DocumentService.get_by_id(req["doc_id"])
        if not e:
            return get_data_error_result(message="Document not found!")

        if not DocumentService.update_by_id(
                req["doc_id"], {"meta_fields": meta}):
            return get_data_error_result(
                message="Database error (meta updates)!")

        return get_json_result(data=True)
    except Exception as e:
        return server_error_response(e)


@manager.route('/task_status/<doc_id>', methods=['GET'])  # noqa: F821
@login_required
def get_task_status(doc_id):
    """获取文档解析任务状态"""
    try:
        # 检查文档状态
        e, doc = DocumentService.get_by_id(doc_id)
        if not e:
            return get_data_error_result(message="文档不存在")

        # 检查任务记录
        from api.db.services.task_service import TaskService
        tasks = TaskService.query(doc_id=doc_id, order_by="create_time DESC", limit=10)

        # 检查 Redis 队列状态 - 修复方法
        queue_info = {"queue_name": "unknown", "queue_length": -1}
        try:
            from rag.utils.redis_conn import REDIS_CONN
            from rag.settings import get_svr_queue_name

            queue_name = get_svr_queue_name(0)  # 默认优先级
            queue_info["queue_name"] = queue_name

            # 尝试获取队列长度
            try:
                if hasattr(REDIS_CONN, 'queue_length'):
                    queue_length = REDIS_CONN.queue_length(queue_name)
                    queue_info["queue_length"] = queue_length
                elif hasattr(REDIS_CONN, 'llen'):
                    queue_length = REDIS_CONN.llen(queue_name)
                    queue_info["queue_length"] = queue_length
                elif hasattr(REDIS_CONN, 'redis') and hasattr(REDIS_CONN.redis, 'llen'):
                    queue_length = REDIS_CONN.redis.llen(queue_name)
                    queue_info["queue_length"] = queue_length
                else:
                    logging.warning("无法获取队列长度，Redis 方法不可用")
            except Exception as queue_error:
                logging.warning(f"获取队列长度失败: {queue_error}")

        except Exception as redis_error:
            logging.warning(f"Redis 队列检查失败: {redis_error}")

        status_info = {
            "document": {
                "id": doc.id,
                "name": doc.name,
                "progress": doc.progress,
                "progress_msg": doc.progress_msg,
                "run_status": doc.run,
                "process_begin_at": doc.process_begin_at,
                "chunk_num": doc.chunk_num,
                "token_num": doc.token_num
            },
            "tasks": [task.to_dict() for task in tasks],
            "queue_info": queue_info
        }

        return get_json_result(data=status_info)
    except Exception as e:
        logging.error(f"获取任务状态失败: {e}")
        return server_error_response(e)



@manager.route('/set_filter_fields', methods=['POST'])  # noqa: F821
@login_required
@validate_request("doc_id", "filter_fields")
def set_filter_fields():
    """
    知悉范围、级别、期限等字段的过滤
    """
    req = request.json
    #只有创建者可以设置过滤权限
    if not DocumentService.accessible4deletion(req["doc_id"], current_user.id):
        return get_json_result(
            data=False,
            message=f'No authorization doc_id {req["doc_id"]} for you {current_user.id}.',
            code=settings.RetCode.AUTHENTICATION_ERROR
        )
    try:
        filter_fields = json.loads(req["filter_fields"])
    except Exception as e:
        return get_json_result(
            data=False, message=f'Json syntax error: {e}', code=settings.RetCode.ARGUMENT_ERROR)
    if not isinstance(filter_fields, dict):
        return get_json_result(
            data=False, message='Filter fields data should be in Json map format, like {"key": "value"}', code=settings.RetCode.ARGUMENT_ERROR)

    for i in filter_fields.values():
        if i not in ['limit_range','limit_level','limit_time']:
            return get_json_result(
             data=False,
             message=f'Parameter {i} not valid, only support ["limit_range","limit_level","limit_time"].',
             code=settings.RetCode.ARGUMENT_ERROR
            )

    range_ = filter_fields.get('limit_range',[])
    level_= filter_fields.get('limit_level',1)
    time_ = filter_fields.get('limit_time',0)

    for user_id_ in range_:
     try:
         uuid.UUID(str(user_id_))
     except Exception as e:
         return get_json_result(
             data=False,
             message=f'Parameter limit_range has value {user_id_} not uuid.',
             code=settings.RetCode.ARGUMENT_ERROR
         )
    if not isinstance(level_,int):
        return get_json_result(
                     data=False,
                     message=f'Parameter limit_level value {level_} not int.',
                     code=settings.RetCode.ARGUMENT_ERROR
                 )
    if not isinstance(time_,int):
        return get_json_result(
                     data=False,
                     message=f'Parameter limit_time value {time_} not int.',
                     code=settings.RetCode.ARGUMENT_ERROR
                 )
    if current_user.id not in range_:
        return get_json_result(
            data=False, message=f'Filter range not set or current user not in range.', code=settings.RetCode.ARGUMENT_ERROR)
    try:
        e, doc = DocumentService.get_by_id(req["doc_id"])
        if not e:
            return get_data_error_result(message="Document not found!")

        if not DocumentService.update_by_id(
                req["doc_id"], {"filter_fields": filter_fields}):
            return get_data_error_result(
                message="Database error (filter_fields updates)!")

        return get_json_result(data=True)
    except Exception as e:
        return server_error_response(e)
