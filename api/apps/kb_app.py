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
import os

from flask import request
from flask_login import login_required, current_user

from api.db.services import duplicate_name
from api.db.services.document_service import DocumentService
from api.db.services.file2document_service import File2DocumentService
from api.db.services.file_service import FileService
from api.db.services.user_service import TenantService, UserTenantService, UserService
from api.utils.api_utils import server_error_response, get_data_error_result, validate_request, not_allowed_parameters
from api.utils import get_uuid
from api.db import StatusEnum, FileSource
from api.db.services.knowledgebase_service import KnowledgebaseService
from api.db.db_models import File
from api.utils.api_utils import get_json_result
from api import settings
from rag.nlp import search
from api.constants import DATASET_NAME_LIMIT
from rag.settings import PAGERANK_FLD
import datetime
import logging

from api.db.services.dialog_service import DialogService, ask, chat

@manager.route('/create', methods=['post'])  # noqa: F821
@login_required
@validate_request("name")
def create():
    req = request.json
    dataset_name = req["name"]
    if not isinstance(dataset_name, str):
        return get_data_error_result(message="Dataset name must be string.")
    if dataset_name == "":
        return get_data_error_result(message="Dataset name can't be empty.")
    if len(dataset_name) >= DATASET_NAME_LIMIT:
        return get_data_error_result(
            message=f"Dataset name length is {len(dataset_name)} which is large than {DATASET_NAME_LIMIT}")

    dataset_name = dataset_name.strip()
    dataset_name = duplicate_name(
        KnowledgebaseService.query,
        name=dataset_name,
        tenant_id=current_user.id,
        status=StatusEnum.VALID.value)
    try:
        req["id"] = get_uuid()
        req["tenant_id"] = current_user.id
        req["created_by"] = current_user.id
        e, t = TenantService.get_by_id(current_user.id)
        if not e:
            return get_data_error_result(message="Tenant not found.")
        req["embd_id"] = t.embd_id
        if not KnowledgebaseService.save(**req):
            return get_data_error_result()

        #TODO:临时方案，将知识库添加到特定智能助手中
        #dialog_id = "8a5fe1c641b211f084720aa9420e5f66"
        # 正式环境
        # dialog_id = "58ce279249c011f0a0c90242ac1400fe"
        users = UserService.query(email="M@M.test")
        if users:
            userid = users[0].id
            if current_user.id == userid:
                for dialog_id in ['8a5fe1c641b211f084720aa9420e5f66','58ce279249c011f0a0c90242ac1400fe','ed1d4f484b3411f091d9cef343bd0a30']:
                    e, dia = DialogService.get_by_id(dialog_id)
                    if e:
                        logging.info(f"Dialog {dialog_id} exists,will update it!")
                        dia = dia.to_dict()
                        dia_to_update = {}
                        dia_to_update['kb_ids'] = dia.get('kb_ids',[])+[req["id"]]
                        if not DialogService.update_by_id(dialog_id, dia_to_update):
                            logging.error(f"Dialog {dialog_id} update error dia_to_update {dia_to_update}!")
                        else:
                            logging.info(f"Dialog {dialog_id} update success dia_to_update {dia_to_update}!")
                    else:
                        logging.info(f"Dialog {dialog_id} Not Exists")

        return get_json_result(data={"kb_id": req["id"]})
    except Exception as e:
        return server_error_response(e)


@manager.route('/update', methods=['post'])  # noqa: F821
@login_required
@validate_request("kb_id", "name", "description", "parser_id")
@not_allowed_parameters("id", "tenant_id", "created_by", "create_time", "update_time", "create_date", "update_date")
def update():
    req = request.json
    req["name"] = req["name"].strip()
    #if not KnowledgebaseService.accessible4deletion(req["kb_id"], current_user.id):
    #    return get_json_result(
    #        data=False,
    #        message=f'No authorization, you {current_user.id} not the kb {req["kb_id"]} owner.',
    #        code=settings.RetCode.AUTHENTICATION_ERROR
    #    )
    try:
        if not KnowledgebaseService.query(
                created_by=current_user.id, id=req["kb_id"]):
            return get_json_result(
                data=False, message='Only owner of knowledgebase authorized for this operation.',
                code=settings.RetCode.OPERATING_ERROR)

        e, kb = KnowledgebaseService.get_by_id(req["kb_id"])
        if not e:
            return get_data_error_result(
                message="Can't find this knowledgebase!")

        if req.get("parser_id", "") == "tag" and os.environ.get('DOC_ENGINE', "elasticsearch") == "infinity":
            return get_json_result(
                data=False,
                message='The chunk method Tag has not been supported by Infinity yet.',
                code=settings.RetCode.OPERATING_ERROR
            )

        parser_config =  req.get("parser_config", None)
        if parser_config:
            extractor = parser_config.get('extractor',None)
            classifier= parser_config.get('classifier',None)
            layout_recognize =  parser_config.get('layout_recognize',"")
            parser_id  = req.get("parser_id", "")
            import logging
            logging.info('Current parser_config {}'.format(kb.parser_config))
            if not layout_recognize:
                if not parser_id or parser_id=='paper':
                    parser_config['layout_recognize'] = 'MinerU'
                    req['parser_id'] ='paper'
            if not extractor:
                pre_configed_0 = kb.parser_config.get('extractor',None)
                if pre_configed_0:
                    parser_config['extractor'] = pre_configed_0
            if not classifier:
                pre_configed_1 = kb.parser_config.get('classifier',None)
                if pre_configed_1:
                    parser_config['classifier'] = pre_configed_1
            from api.utils.api_utils import get_extractor
            parser_config['extractor'] = get_extractor(parser_config, metadata_type="default")

        if req["name"].lower() != kb.name.lower() \
                and len(
            KnowledgebaseService.query(name=req["name"], tenant_id=current_user.id, status=StatusEnum.VALID.value)) > 1:
            return get_data_error_result(
                message=f"Duplicated knowledgebase name {req['name']}.")

        del req["kb_id"]
        if not KnowledgebaseService.update_by_id(kb.id, req):
            return get_data_error_result()

        if kb.pagerank != req.get("pagerank", 0):
            if req.get("pagerank", 0) > 0:
                settings.docStoreConn.update({"kb_id": kb.id}, {PAGERANK_FLD: req["pagerank"]},
                                         search.index_name(kb.tenant_id), kb.id)
            else:
                # Elasticsearch requires PAGERANK_FLD be non-zero!
                settings.docStoreConn.update({"exists": PAGERANK_FLD}, {"remove": PAGERANK_FLD},
                                         search.index_name(kb.tenant_id), kb.id)

        e, kb = KnowledgebaseService.get_by_id(kb.id)
        if not e:
            return get_data_error_result(
                message="Database error (Knowledgebase update)!")
        kb = kb.to_dict()
        kb.update(req)

        return get_json_result(data=kb)
    except Exception as e:
        return server_error_response(e)


@manager.route('/detail', methods=['GET'])  # noqa: F821
@login_required
def detail():
    kb_id = request.args["kb_id"]
    try:
        tenants = UserTenantService.query(user_id=current_user.id)
        for tenant in tenants:
            if KnowledgebaseService.query(
                    tenant_id=tenant.tenant_id, id=kb_id):
                break
        else:
            return get_json_result(
                data=False, message='Only the user own or join the tenant of the knowledgebase authorized for this operation.',
                code=settings.RetCode.OPERATING_ERROR)
        kb = KnowledgebaseService.get_detail(kb_id)
        if not kb:
            return get_data_error_result(
                message="Can't find this knowledgebase!")
        return get_json_result(data=kb)
    except Exception as e:
        return server_error_response(e)


@manager.route('/list', methods=['POST'])  # noqa: F821
@login_required
def list_kbs():
    keywords = request.args.get("keywords", "")
    page_number = int(request.args.get("page", 0))
    items_per_page = int(request.args.get("page_size", 0))
    parser_id = request.args.get("parser_id")
    orderby = request.args.get("orderby", "create_time")
    desc = request.args.get("desc", True)

    req = request.get_json()
    owner_ids = req.get("owner_ids", [])

    try:
        if not owner_ids:
            tenants = TenantService.get_joined_tenants_by_user_id(current_user.id)
            tenants = [m["tenant_id"] for m in tenants]
            kbs, total = KnowledgebaseService.get_by_tenant_ids(
                tenants, current_user.id, page_number,
                items_per_page, orderby, desc, keywords, parser_id)
        else:
            tenants_stored = TenantService.get_joined_tenants_by_user_id(current_user.id)
            tenants_stored = [m["tenant_id"] for m in tenants_stored]
            tenants_stored.append(current_user.id)
            not_in = []
            for o in owner_ids:
                if o not in tenants_stored:
                    not_in.append(o)
            if not_in:
                return get_json_result(
                            data=False,
                            message=f'The user {current_user.id} only joined or own {tenants_stored},but not joined or own {not_in}.',
                            code=settings.RetCode.AUTHENTICATION_ERROR
                )
            tenants = tenants_stored
            kbs, total = KnowledgebaseService.get_by_tenant_ids(
                tenants, current_user.id, 0,
                0, orderby, desc, keywords, parser_id)
            kbs = [kb for kb in kbs if kb["tenant_id"] in tenants]
            if page_number and items_per_page:
                kbs = kbs[(page_number-1)*items_per_page:page_number*items_per_page]
            total = len(kbs)
        return get_json_result(data={"kbs": kbs, "total": total})
    except Exception as e:
        return server_error_response(e)

@manager.route('/rm', methods=['post'])  # noqa: F821
@login_required
@validate_request("kb_id")
def rm():
    req = request.json
    if not KnowledgebaseService.accessible4deletion(req["kb_id"], current_user.id):
        return get_json_result(
            data=False,
            message=f'No authorization for kb {req["kb_id"]}',
            code=settings.RetCode.AUTHENTICATION_ERROR
        )
    try:
        kbs = KnowledgebaseService.query(
            created_by=current_user.id, id=req["kb_id"])
        if not kbs:
            return get_json_result(
                data=False, message='Only owner of knowledgebase authorized for this operation.',
                code=settings.RetCode.OPERATING_ERROR)

        for doc in DocumentService.query(kb_id=req["kb_id"]):
            if not DocumentService.remove_document(doc, kbs[0].tenant_id):
                return get_data_error_result(
                    message=f"Database error (Document removal) for doc {doc.id} kb {req['kb_id']}!")
            f2d = File2DocumentService.get_by_document_id(doc.id)
            if f2d:
                FileService.filter_delete([File.source_type == FileSource.KNOWLEDGEBASE, File.id == f2d[0].file_id])
            File2DocumentService.delete_by_document_id(doc.id)
        FileService.filter_delete(
            [File.source_type == FileSource.KNOWLEDGEBASE, File.type == "folder", File.name == kbs[0].name])
        if not KnowledgebaseService.delete_by_id(req["kb_id"]):
            return get_data_error_result(
                message=f"Database error (Knowledgebase removal) for kb {req['kb_id']}!")
        for kb in kbs:
            settings.docStoreConn.delete({"kb_id": kb.id}, search.index_name(kb.tenant_id), kb.id)
            settings.docStoreConn.deleteIdx(search.index_name(kb.tenant_id), kb.id)
        return get_json_result(data=True)
    except Exception as e:
        return server_error_response(e)


@manager.route('/<kb_id>/tags', methods=['GET'])  # noqa: F821
@login_required
def list_tags(kb_id):
    if not KnowledgebaseService.accessible(kb_id, current_user.id):
        return get_json_result(
            data=False,
            message=f'No authorization, user {current_user.id} kb {kb_id}',
            code=settings.RetCode.AUTHENTICATION_ERROR
        )

    tags = settings.retrievaler.all_tags(current_user.id, [kb_id])
    return get_json_result(data=tags)


@manager.route('/tags', methods=['GET'])  # noqa: F821
@login_required
def list_tags_from_kbs():
    kb_ids = request.args.get("kb_ids", "").split(",")
    for kb_id in kb_ids:
        if not KnowledgebaseService.accessible(kb_id, current_user.id):
            return get_json_result(
                data=False,
                message=f'No authorization for kb {kb_id}.',
                code=settings.RetCode.AUTHENTICATION_ERROR
            )

    tags = settings.retrievaler.all_tags(current_user.id, kb_ids)
    return get_json_result(data=tags)


@manager.route('/<kb_id>/rm_tags', methods=['POST'])  # noqa: F821
@login_required
def rm_tags(kb_id):
    req = request.json
    if not KnowledgebaseService.accessible(kb_id, current_user.id):
        return get_json_result(
            data=False,
            message='No authorization.',
            code=settings.RetCode.AUTHENTICATION_ERROR
        )
    e, kb = KnowledgebaseService.get_by_id(kb_id)

    for t in req["tags"]:
        settings.docStoreConn.update({"tag_kwd": t, "kb_id": [kb_id]},
                                     {"remove": {"tag_kwd": t}},
                                     search.index_name(kb.tenant_id),
                                     kb_id)
    return get_json_result(data=True)


@manager.route('/<kb_id>/rename_tag', methods=['POST'])  # noqa: F821
@login_required
def rename_tags(kb_id):
    req = request.json
    if not KnowledgebaseService.accessible(kb_id, current_user.id):
        return get_json_result(
            data=False,
            message='No authorization.',
            code=settings.RetCode.AUTHENTICATION_ERROR
        )
    e, kb = KnowledgebaseService.get_by_id(kb_id)

    settings.docStoreConn.update({"tag_kwd": req["from_tag"], "kb_id": [kb_id]},
                                     {"remove": {"tag_kwd": req["from_tag"].strip()}, "add": {"tag_kwd": req["to_tag"]}},
                                     search.index_name(kb.tenant_id),
                                     kb_id)
    return get_json_result(data=True)


@manager.route('/<kb_id>/knowledge_graph', methods=['GET'])  # noqa: F821
@login_required
def knowledge_graph(kb_id):
    if not KnowledgebaseService.accessible(kb_id, current_user.id):
        return get_json_result(
            data=False,
            message='No authorization.',
            code=settings.RetCode.AUTHENTICATION_ERROR
        )
    _, kb = KnowledgebaseService.get_by_id(kb_id)
    req = {
        "limit_range":current_user.id,
        "limit_time":str(datetime.datetime.now()).replace("T", " ")[:19],
        "limit_level":1,
        "kb_id": [kb_id],
        "knowledge_graph_kwd": ["graph"]
    }

    obj = {"graph": {}, "mind_map": {}}
    if not settings.docStoreConn.indexExist(search.index_name(kb.tenant_id), kb_id):
        return get_json_result(data=obj)
    sres = settings.retrievaler.search(req, search.index_name(kb.tenant_id), [kb_id])
    if not len(sres.ids):
        return get_json_result(data=obj)

    for id in sres.ids[:1]:
        ty = sres.field[id]["knowledge_graph_kwd"]
        try:
            content_json = json.loads(sres.field[id]["content_with_weight"])
        except Exception:
            continue

        obj[ty] = content_json

    if "nodes" in obj["graph"]:
        obj["graph"]["nodes"] = sorted(obj["graph"]["nodes"], key=lambda x: x.get("pagerank", 0), reverse=True)[:256]
        if "edges" in obj["graph"]:
            node_id_set = { o["id"] for o in obj["graph"]["nodes"] }
            filtered_edges = [o for o in obj["graph"]["edges"] if o["source"] != o["target"] and o["source"] in node_id_set and o["target"] in node_id_set]
            obj["graph"]["edges"] = sorted(filtered_edges, key=lambda x: x.get("weight", 0), reverse=True)[:128]
    return get_json_result(data=obj)

@manager.route('/<kb_id>/knowledge_graph', methods=['DELETE'])  # noqa: F821
@login_required
def delete_knowledge_graph(kb_id):
    if not KnowledgebaseService.accessible(kb_id, current_user.id):
        return get_json_result(
            data=False,
            message='No authorization.',
            code=settings.RetCode.AUTHENTICATION_ERROR
        )
    _, kb = KnowledgebaseService.get_by_id(kb_id)
    settings.docStoreConn.delete({"knowledge_graph_kwd": ["graph", "subgraph", "entity", "relation"]}, search.index_name(kb.tenant_id), kb_id)

    return get_json_result(data=True)
