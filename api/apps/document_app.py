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
            message='No authorization.',
            code=settings.RetCode.AUTHENTICATION_ERROR
        )

    if not KnowledgebaseService.accessible(dst_kb_id, current_user.id):
        return get_json_result(
            data=False,
            message='No authorization.',
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
        raise LookupError("Has same-name documents {} in destination kb!".format(dst_kb_exist_location))
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
        #如果是相同的tenant id，直接更新文档的kb_id Mysql数据库里更新+ES更新
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
            message='No authorization.',
            code=settings.RetCode.AUTHENTICATION_ERROR
        )

    blob = html2pdf(url)
    if not blob:
        return server_error_response(ValueError("Download failure."))

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
                message='No authorization.',
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
            return get_data_error_result(message="Document not found!")
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
                return get_data_error_result(message="Document not found!")
            tenant_id = DocumentService.get_tenant_id(doc_id)
            if not tenant_id:
                return get_data_error_result(message="Tenant not found!")

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
            #res = res.decode('utf-8')
            response = flask.make_response(res)
        else:
            return get_data_error_result(message=f"Document {doc_id} MarkDown {doc.md_location} not found, maybe not parsed by MinerU!")

        response.headers.set('Content-Type', 'text/markdown; charset=utf-8')
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
            logging.info(f"get md for {doc_id},location {doc.layout_location}")
            res = STORAGE_IMPL.get(doc.kb_id, doc.layout_location)
            response = flask.make_response(res)
        else:
            return get_data_error_result(message=f"Document {doc_id} Layout {doc.layout_location} not found, maybe not parsed by MinerU!")

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
            return get_data_error_result(message="Not supported yet!")

        e = DocumentService.update_by_id(doc.id,
                                         {"parser_id": req["parser_id"], "progress": 0, "progress_msg": "",
                                          "run": TaskStatus.UNSTART.value})
        if not e:
            return get_data_error_result(message="Document not found!")
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
            return get_data_error_result(message="Image not found.")
        bkt, nm = image_id.split("-")
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

@manager.route('/set_filter_fields', methods=['POST'])  # noqa: F821
@login_required
@validate_request("doc_id", "filter_fields")
def set_filter_fields():
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
    range_ = filter_fields.get('filter_range',[])
    level_= filter_fields.get('filter_level',None)
    time_ = filter_fields.get('filter_time',None)
    if current_user.id not in range_:
        return get_json_result(
            data=False, message=f'Filter range not set or current user not in range.', code=settings.RetCode.ARGUMENT_ERROR)
    if not level_:
        return get_json_result(
            data=False, message=f'Filter level not set.', code=settings.RetCode.ARGUMENT_ERROR)
    if not time_:
        return get_json_result(
            data=False, message=f'Filter time not set.', code=settings.RetCode.ARGUMENT_ERROR)
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
