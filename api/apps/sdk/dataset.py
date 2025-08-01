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
import logging

from flask import request
from api.db import StatusEnum, FileSource
from api.db.db_models import File
from api.db.services.document_service import DocumentService
from api.db.services.file2document_service import File2DocumentService
from api.db.services.file_service import FileService
from api.db.services.knowledgebase_service import KnowledgebaseService
from api.db.services.llm_service import TenantLLMService, LLMService
from api.db.services.user_service import TenantService, UserService
from api import settings
from api.utils import get_uuid
from api.utils.api_utils import (
    get_result,
    token_required,
    get_error_data_result,
    valid,
    get_parser_config, valid_parser_config, dataset_readonly_fields,check_duplicate_ids
)
from api.db.services.dialog_service import DialogService, ask, chat

@manager.route("/datasets", methods=["POST"])  # noqa: F821
@token_required
def create(tenant_id):
    """
    Create a new dataset.
    ---
    tags:
      - Datasets
    security:
      - ApiKeyAuth: []
    parameters:
      - in: header
        name: Authorization
        type: string
        required: true
        description: Bearer token for authentication.
      - in: body
        name: body
        description: Dataset creation parameters.
        required: true
        schema:
          type: object
          required:
            - name
          properties:
            name:
              type: string
              description: Name of the dataset.
            permission:
              type: string
              enum: ['me', 'team']
              description: Dataset permission.
            chunk_method:
              type: string
              enum: ["naive", "manual", "qa", "table", "paper", "book", "laws",
                     "presentation", "picture", "one", "email", "tag"
                     ]
              description: Chunking method.
            parser_config:
              type: object
              description: Parser configuration.
    responses:
      200:
        description: Successful operation.
        schema:
          type: object
          properties:
            data:
              type: object
    """
    req = request.json
    logging.info(f"datasets create req: {req}")
    for k in req.keys():
        if dataset_readonly_fields(k):
            return get_result(code=settings.RetCode.ARGUMENT_ERROR, message=f"'{k}' is readonly.")
    e, t = TenantService.get_by_id(tenant_id)
    permission = req.get("permission")
    chunk_method = req.get("chunk_method")
    parser_config = req.get("parser_config")
    # 创建文件夹时的元数据类型
    metadata_type = req.get("metadata_type", "default")
    logging.info(f"parser_config metadata_type={metadata_type}, chunk_method={chunk_method}, parser_config={parser_config}")
    valid_parser_config(parser_config)
    valid_permission = ["me", "team"]
    valid_chunk_method = [
        "naive",
        "manual",
        "qa",
        "table",
        "paper",
        "book",
        "laws",
        "presentation",
        "picture",
        "one",
        "email",
        "tag"
    ]
    check_validation = valid(
        permission,
        valid_permission,
        chunk_method,
        valid_chunk_method,
    )
    if check_validation:
        return check_validation
    req["parser_config"] = get_parser_config(chunk_method, parser_config, metadata_type=metadata_type)
    if "tenant_id" in req:
        return get_error_data_result(message="`tenant_id` must not be provided")
    if "chunk_count" in req or "document_count" in req:
        return get_error_data_result(
            message="`chunk_count` or `document_count` must not be provided"
        )
    if "name" not in req:
        return get_error_data_result(message="`name` is not empty!")
    req["id"] = get_uuid()
    req["name"] = req["name"].strip()
    if req["name"] == "":
        return get_error_data_result(message="`name` is not empty string!")
    if len(req["name"]) >= 128:
        return get_error_data_result(
            message="Dataset name should not be longer than 128 characters."
        )
    if KnowledgebaseService.query(
        name=req["name"], tenant_id=tenant_id, status=StatusEnum.VALID.value
    ):
        logging.info(f"Dataset {req['name']} already exists.")
        # 允许创建重名知识库
        # return get_error_data_result(
        #     message="Duplicated dataset name in creating dataset."
        # )
    req["tenant_id"] = tenant_id
    req["created_by"] = tenant_id
    if not req.get("embedding_model"):
        req["embedding_model"] = t.embd_id
    else:
        valid_embedding_models = [
            "BAAI/bge-large-zh-v1.5",
            "maidalun1020/bce-embedding-base_v1",
        ]
        embd_model = LLMService.query(
            llm_name=req["embedding_model"], model_type="embedding"
        )
        if embd_model:
            if req["embedding_model"] not in valid_embedding_models and not TenantLLMService.query(tenant_id=tenant_id,model_type="embedding",llm_name=req.get("embedding_model"),):
                return get_error_data_result(f"`embedding_model` {req.get('embedding_model')} doesn't exist")
        if not embd_model:
            embd_model=TenantLLMService.query(tenant_id=tenant_id,model_type="embedding", llm_name=req.get("embedding_model"))
        if not embd_model:
            return get_error_data_result(
                f"`embedding_model` {req.get('embedding_model')} doesn't exist"
            )
    key_mapping = {
        "chunk_num": "chunk_count",
        "doc_num": "document_count",
        "parser_id": "chunk_method",
        "embd_id": "embedding_model",
    }
    mapped_keys = {
        new_key: req[old_key]
        for new_key, old_key in key_mapping.items()
        if old_key in req
    }
    req.update(mapped_keys)
    flds = list(req.keys())
    for f in flds:
        if req[f] == "" and f in ["permission", "parser_id", "chunk_method"]:
            del req[f]
    if not KnowledgebaseService.save(**req):
        return get_error_data_result(message="Create dataset error.(Database error)")
    renamed_data = {}
    e, k = KnowledgebaseService.get_by_id(req["id"])
    for key, value in k.to_dict().items():
        new_key = key_mapping.get(key, key)
        renamed_data[new_key] = value

    users = UserService.query(email="M@M.test")
    if users:
        userid = users[0].id
        if tenant_id == userid:
            #TODO:临时方案，将知识库添加到特定智能助手中
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

    return get_result(data=renamed_data)


@manager.route("/datasets", methods=["DELETE"])  # noqa: F821
@token_required
def delete(tenant_id):
    """
    Delete datasets.
    ---
    tags:
      - Datasets
    security:
      - ApiKeyAuth: []
    parameters:
      - in: header
        name: Authorization
        type: string
        required: true
        description: Bearer token for authentication.
      - in: body
        name: body
        description: Dataset deletion parameters.
        required: true
        schema:
          type: object
          properties:
            ids:
              type: array
              items:
                type: string
              description: List of dataset IDs to delete.
    responses:
      200:
        description: Successful operation.
        schema:
          type: object
    """
    errors = []
    success_count = 0
    req = request.json
    logging.info(f"Delete datasets tenant_id {tenant_id} delete {req}")
    if not req:
        ids = None
    else:
        ids = req.get("ids")
    if not ids:
        id_list = []
        kbs = KnowledgebaseService.query(tenant_id=tenant_id)
        for kb in kbs:
            id_list.append(kb.id)
    else:
        id_list = ids
    unique_id_list, duplicate_messages = check_duplicate_ids(id_list, "dataset")
    id_list = unique_id_list

    for id in id_list:
        kbs = KnowledgebaseService.query(id=id, tenant_id=tenant_id)
        if not kbs:
            errors.append(f"You don't own the dataset {id}")
            continue
        for doc in DocumentService.query(kb_id=id):
            if not DocumentService.remove_document(doc, tenant_id):
                errors.append(f"Remove document error for dataset {id}")
                continue
            f2d = File2DocumentService.get_by_document_id(doc.id)
            FileService.filter_delete(
                [
                    File.source_type == FileSource.KNOWLEDGEBASE,
                    File.id == f2d[0].file_id,
                ]
            )
            File2DocumentService.delete_by_document_id(doc.id)
        FileService.filter_delete(
            [File.source_type == FileSource.KNOWLEDGEBASE, File.type == "folder", File.name == kbs[0].name])
        if not KnowledgebaseService.delete_by_id(id):
            errors.append(f"Delete dataset error for {id}")
            continue
        success_count += 1
    if errors:
        if success_count > 0:
            return get_result(
                data={"success_count": success_count, "errors": errors},
                message=f"Partially deleted {success_count} datasets with {len(errors)} errors"
            )
        else:
            return get_error_data_result(message="; ".join(errors))
    if duplicate_messages:
        if success_count > 0:
            return get_result(message=f"Partially deleted {success_count} datasets with {len(duplicate_messages)} errors", data={"success_count": success_count, "errors": duplicate_messages},)
        else:
            return get_error_data_result(message=";".join(duplicate_messages))
    return get_result(code=settings.RetCode.SUCCESS)


@manager.route("/datasets/<dataset_id>", methods=["PUT"])  # noqa: F821  
@token_required
def update(tenant_id, dataset_id):
    """
    Update a dataset.
    ---
    tags:
      - Datasets
    security:
      - ApiKeyAuth: []
    parameters:
      - in: path
        name: dataset_id
        type: string
        required: true
        description: ID of the dataset to update.
      - in: header
        name: Authorization
        type: string
        required: true
        description: Bearer token for authentication.
      - in: body
        name: body
        description: Dataset update parameters.
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              description: New name of the dataset.
            permission:
              type: string
              enum: ['me', 'team']
              description: Updated permission.
            chunk_method:
              type: string
              enum: ["naive", "manual", "qa", "table", "paper", "book", "laws",
                     "presentation", "picture", "one", "email", "tag"
                     ]
              description: Updated chunking method.
            parser_config:
              type: object
              description: Updated parser configuration.
    responses:
      200:
        description: Successful operation.
        schema:
          type: object
    """
    if not KnowledgebaseService.query(id=dataset_id, tenant_id=tenant_id):
        return get_error_data_result(message="You don't own the dataset")
    req = request.json
    logging.info(f"update dataset {dataset_id} req {req}")
    for k in req.keys():
        if dataset_readonly_fields(k):
            return get_result(code=settings.RetCode.ARGUMENT_ERROR, message=f"'{k}' is readonly.")
    e, t = TenantService.get_by_id(tenant_id)
    invalid_keys = {"id", "embd_id", "chunk_num", "doc_num", "parser_id", "create_date", "create_time", "created_by", "status","token_num","update_date","update_time"}
    if any(key in req for key in invalid_keys):
        return get_error_data_result(message="The input parameters are invalid.")
    permission = req.get("permission")
    chunk_method = req.get("chunk_method")
    parser_config = req.get("parser_config")
    valid_parser_config(parser_config)
    valid_permission = ["me", "team"]
    valid_chunk_method = [
        "naive",
        "manual",
        "qa",
        "table",
        "paper",
        "book",
        "laws",
        "presentation",
        "picture",
        "one",
        "email",
        "tag"
    ]
    check_validation = valid(
        permission,
        valid_permission,
        chunk_method,
        valid_chunk_method,
    )
    if check_validation:
        return check_validation
    if "tenant_id" in req:
        if req["tenant_id"] != tenant_id:
            return get_error_data_result(message="Can't change `tenant_id`.")
    e, kb = KnowledgebaseService.get_by_id(dataset_id)
    if "parser_config" in req:
        temp_dict = kb.parser_config
        temp_dict.update(req["parser_config"])
        req["parser_config"] = temp_dict
    if "chunk_count" in req:
        if req["chunk_count"] != kb.chunk_num:
            return get_error_data_result(message="Can't change `chunk_count`.")
        req.pop("chunk_count")
    if "document_count" in req:
        if req["document_count"] != kb.doc_num:
            return get_error_data_result(message="Can't change `document_count`.")
        req.pop("document_count")
    if req.get("chunk_method"):
        if kb.chunk_num != 0 and req["chunk_method"] != kb.parser_id:
            return get_error_data_result(
                message="If `chunk_count` is not 0, `chunk_method` is not changeable."
            )
        req["parser_id"] = req.pop("chunk_method")
        if req["parser_id"] != kb.parser_id:
            if not req.get("parser_config"):
                req["parser_config"] = get_parser_config(chunk_method, parser_config)
    if "embedding_model" in req:
        if kb.chunk_num != 0 and req["embedding_model"] != kb.embd_id:
            return get_error_data_result(
                message="If `chunk_count` is not 0, `embedding_model` is not changeable."
            )
        if not req.get("embedding_model"):
            return get_error_data_result("`embedding_model` can't be empty")
        valid_embedding_models = [
            "BAAI/bge-large-zh-v1.5",
            "BAAI/bge-base-en-v1.5",
            "BAAI/bge-large-en-v1.5",
            "BAAI/bge-small-en-v1.5",
            "BAAI/bge-small-zh-v1.5",
            "jinaai/jina-embeddings-v2-base-en",
            "jinaai/jina-embeddings-v2-small-en",
            "nomic-ai/nomic-embed-text-v1.5",
            "sentence-transformers/all-MiniLM-L6-v2",
            "text-embedding-v2",
            "text-embedding-v3",
            "maidalun1020/bce-embedding-base_v1",
        ]
        embd_model = LLMService.query(
            llm_name=req["embedding_model"], model_type="embedding"
        )
        if embd_model:
            if req["embedding_model"] not in valid_embedding_models and not TenantLLMService.query(tenant_id=tenant_id,model_type="embedding",llm_name=req.get("embedding_model"),):
                return get_error_data_result(f"`embedding_model` {req.get('embedding_model')} doesn't exist")
        if not embd_model:
            embd_model=TenantLLMService.query(tenant_id=tenant_id,model_type="embedding", llm_name=req.get("embedding_model"))

        if not embd_model:
            return get_error_data_result(
                f"`embedding_model` {req.get('embedding_model')} doesn't exist"
            )
        req["embd_id"] = req.pop("embedding_model")
    if "name" in req:
        req["name"] = req["name"].strip()
        if len(req["name"]) >= 128:
            return get_error_data_result(
                message="Dataset name should not be longer than 128 characters."
            )
        if (
            req["name"].lower() != kb.name.lower()
            and len(
                KnowledgebaseService.query(
                    name=req["name"], tenant_id=tenant_id, status=StatusEnum.VALID.value
                )
            )
            > 0
        ):
            # 允许创建或更新重名知识库
            logging.info(f"Dataset name `{req['name']}` already exists. But it is be allowed.")
            # return get_error_data_result(
            #     message="Duplicated dataset name in updating dataset."
            # )
    flds = list(req.keys())
    for f in flds:
        if req[f] == "" and f in ["permission", "parser_id", "chunk_method"]:
            del req[f]
    if not KnowledgebaseService.update_by_id(kb.id, req):
        return get_error_data_result(message="Update dataset error.(Database error)")
    return get_result(code=settings.RetCode.SUCCESS)


@manager.route("/datasets", methods=["GET"])  # noqa: F821
@token_required
def list_datasets(tenant_id):
    """
    List datasets.
    ---
    tags:
      - Datasets
    security:
      - ApiKeyAuth: []
    parameters:
      - in: query
        name: id
        type: string
        required: false
        description: Dataset ID to filter.
      - in: query
        name: name
        type: string
        required: false
        description: Dataset name to filter.
      - in: query
        name: page
        type: integer
        required: false
        default: 1
        description: Page number.
      - in: query
        name: page_size
        type: integer
        required: false
        default: 1024
        description: Number of items per page.
      - in: query
        name: orderby
        type: string
        required: false
        default: "create_time"
        description: Field to order by.
      - in: query
        name: desc
        type: boolean
        required: false
        default: true
        description: Order in descending.
      - in: header
        name: Authorization
        type: string
        required: true
        description: Bearer token for authentication.
    responses:
      200:
        description: Successful operation.
        schema:
          type: array
          items:
            type: object
    """
    id = request.args.get("id")
    name = request.args.get("name")
    if id:
        kbs = KnowledgebaseService.get_kb_by_id(id,tenant_id)
        if not kbs:
            return get_error_data_result(f"You don't own the dataset {id}")
    if name:
        kbs = KnowledgebaseService.get_kb_by_name(name,tenant_id)
        if not kbs:
            return get_error_data_result(f"You don't own the dataset {name}")
    page_number = int(request.args.get("page", 1))
    items_per_page = int(request.args.get("page_size", 30))
    orderby = request.args.get("orderby", "create_time")
    if request.args.get("desc", "false").lower() not in ["true", "false"]:
        return get_error_data_result("desc should be true or false")
    if request.args.get("desc", "true").lower() == "false":
        desc = False
    else:
        desc = True
    tenants = TenantService.get_joined_tenants_by_user_id(tenant_id)
    kbs = KnowledgebaseService.get_list(
        [m["tenant_id"] for m in tenants],
        tenant_id,
        page_number,
        items_per_page,
        orderby,
        desc,
        id,
        name,
    )
    renamed_list = []
    for kb in kbs:
        key_mapping = {
            "chunk_num": "chunk_count",
            "doc_num": "document_count",
            "parser_id": "chunk_method",
            "embd_id": "embedding_model",
        }
        renamed_data = {}
        for key, value in kb.items():
            new_key = key_mapping.get(key, key)
            renamed_data[new_key] = value
        renamed_list.append(renamed_data)
    return get_result(data=renamed_list)
