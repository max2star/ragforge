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
import logging
import random
import re
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime
from io import BytesIO

import trio
import xxhash
from peewee import fn

from api import settings
from api.db import FileType, LLMType, ParserType, StatusEnum, TaskStatus, UserTenantRole
from api.db.db_models import DB, Document, Knowledgebase, Task, Tenant, UserTenant
from api.db.db_utils import bulk_insert_into_db
from api.db.services.common_service import CommonService
from api.db.services.knowledgebase_service import KnowledgebaseService
from api.utils import current_timestamp, get_format_time, get_uuid
from rag.nlp import rag_tokenizer, search
from rag.settings import get_svr_queue_name
from rag.utils.redis_conn import REDIS_CONN
from rag.utils.storage_factory import STORAGE_IMPL


class DocumentService(CommonService):
    model = Document

    @classmethod
    @DB.connection_context()
    def get_list(cls, kb_id, page_number, items_per_page,
                 orderby, desc, keywords, id, name):
        docs = cls.model.select().where(cls.model.kb_id == kb_id)
        if id:
            docs = docs.where(
                cls.model.id == id)
        if name:
            docs = docs.where(
                cls.model.name == name
            )
        if keywords:
            docs = docs.where(
                fn.LOWER(cls.model.name).contains(keywords.lower())
            )
        if desc:
            docs = docs.order_by(cls.model.getter_by(orderby).desc())
        else:
            docs = docs.order_by(cls.model.getter_by(orderby).asc())

        count = docs.count()
        docs = docs.paginate(page_number, items_per_page)
        return list(docs.dicts()), count

    @classmethod
    @DB.connection_context()
    def get_by_kb_id(cls, kb_id, page_number, items_per_page,
                     orderby, desc, keywords):
        if keywords:
            docs = cls.model.select().where(
                (cls.model.kb_id == kb_id),
                (fn.LOWER(cls.model.name).contains(keywords.lower()))
            )
        else:
            docs = cls.model.select().where(cls.model.kb_id == kb_id)
        count = docs.count()
        if desc:
            docs = docs.order_by(cls.model.getter_by(orderby).desc())
        else:
            docs = docs.order_by(cls.model.getter_by(orderby).asc())

        docs = docs.paginate(page_number, items_per_page)

        return list(docs.dicts()), count

    @classmethod
    @DB.connection_context()
    def insert(cls, doc):
        if not cls.save(**doc):
            raise RuntimeError("Database error (Document)!")
        if not KnowledgebaseService.atomic_increase_doc_num_by_id(doc["kb_id"]):
            raise RuntimeError("Database error (Knowledgebase)!")
        return Document(**doc)

    @classmethod
    @DB.connection_context()
    def get_by_location(cls, kb_id, location):
        # Get a record by ID
        # Args:
        #     pid: Record ID
        # Returns:
        #     Tuple of (success, record)
        try:
            obj = cls.model.get_or_none(cls.model.kb_id==kb_id,cls.model.location == location)
            if obj:
                return True, obj
        except Exception:
            pass
        return False, None


    @classmethod
    @DB.connection_context()
    def remove_document(cls, doc, tenant_id):
        cls.clear_chunk_num(doc.id)
        try:
            settings.docStoreConn.delete({"doc_id": doc.id}, search.index_name(tenant_id), doc.kb_id)
            settings.docStoreConn.update({"kb_id": doc.kb_id, "knowledge_graph_kwd": ["entity", "relation", "graph", "subgraph", "community_report"], "source_id": doc.id},
                                         {"remove": {"source_id": doc.id}},
                                         search.index_name(tenant_id), doc.kb_id)
            settings.docStoreConn.update({"kb_id": doc.kb_id, "knowledge_graph_kwd": ["graph"]},
                                         {"removed_kwd": "Y"},
                                         search.index_name(tenant_id), doc.kb_id)
            settings.docStoreConn.delete({"kb_id": doc.kb_id, "knowledge_graph_kwd": ["entity", "relation", "graph", "subgraph", "community_report"], "must_not": {"exists": "source_id"}},
                                         search.index_name(tenant_id), doc.kb_id)
        except Exception as e:
            logging.exception("remove_document {} exception {}".format(doc.id,e))
            pass
        return cls.delete_by_id(doc.id)


    @classmethod
    @DB.connection_context()
    def move_document(cls, doc, dst_kb_id,src_tenant_id,dst_tenant_id):
        if src_tenant_id==dst_tenant_id:
            try:
                settings.docStoreConn.update({"doc_id": doc.id}, {"kb_id": dst_kb_id},search.index_name(dst_tenant_id), doc.kb_id)
                settings.docStoreConn.update({"kb_id": doc.kb_id, "knowledge_graph_kwd": ["entity", "relation", "graph", "subgraph", "community_report"], "source_id": doc.id},
                                             {"kb_id": dst_kb_id},
                                             search.index_name(dst_tenant_id), doc.kb_id)
            except Exception:
                logging.exception("move document {} exception {}".format(doc.id,e))
                pass
        else:
            #doc里边不能带_id
            doc_chunks = settings.docStoreConn.get_chunks(doc.id,search.index_name(src_tenant_id))
            # 构造有效文档集合
            valid_docs = []
            for chunk_d in doc_chunks:
                valid_docs.append(chunk_d)
            settings.docStoreConn.insert(valid_docs,search.index_name(dst_tenant_id),dst_kb_id)
            #从原始的Index中删除
            settings.docStoreConn.delete({"doc_id": doc.id}, search.index_name(src_tenant_id), doc.kb_id)
            settings.docStoreConn.update({"kb_id": doc.kb_id, "knowledge_graph_kwd": ["entity", "relation", "graph", "subgraph", "community_report"], "source_id": doc.id},
                                         {"remove": {"source_id": doc.id}},
                                         search.index_name(src_tenant_id), doc.kb_id)
            settings.docStoreConn.update({"kb_id": doc.kb_id, "knowledge_graph_kwd": ["graph"]},
                                         {"removed_kwd": "Y"},
                                         search.index_name(src_tenant_id), doc.kb_id)
            settings.docStoreConn.delete({"kb_id": doc.kb_id, "knowledge_graph_kwd": ["entity", "relation", "graph", "subgraph", "community_report"], "must_not": {"exists": "source_id"}},
                                         search.index_name(src_tenant_id), doc.kb_id)

        #需要在对象存储中也移动,因为会根据kb作为bucket去查找对象
        #如果目标下有同名文件咋办,会在上层检查下同名的拒绝执行
        thumbnail_location = f'thumbnail_{doc.id}.png'
        STORAGE_IMPL.mv(doc.kb_id,doc.location,dst_kb_id)
        STORAGE_IMPL.mv(doc.kb_id,thumbnail_location,dst_kb_id)
        STORAGE_IMPL.mv(doc.kb_id,doc.md_location,dst_kb_id)
        STORAGE_IMPL.mv(doc.kb_id,doc.layout_location,dst_kb_id)

        mineru_objects = STORAGE_IMPL.list_objs(doc.kb_id, prefix=f'minerU/{doc.id}', recursive=True)
        for m_obj in mineru_objects:
            logging.debug("move object {} from bucket {} to bucket {}".format(m_obj.object_name,doc.kb_id,dst_kb_id))
            STORAGE_IMPL.mv(doc.kb_id,m_obj.object_name,dst_kb_id)

        #减少原来的kb里的chunk统计
        cls.clear_chunk_num(doc.id)

        #更新Mysql中文档记录为新的KB
        cls.update_by_id(doc.id, {"kb_id": dst_kb_id})

        #更新KB中的Chunk统计
        num = Knowledgebase.update(
            token_num=Knowledgebase.token_num +
            doc.token_num,
            chunk_num=Knowledgebase.chunk_num +
            doc.chunk_num,
            doc_num=Knowledgebase.doc_num + 1
        ).where(
            Knowledgebase.id == dst_kb_id).execute()
        return


    @classmethod
    @DB.connection_context()
    def get_newly_uploaded(cls):
        fields = [
            cls.model.id,
            cls.model.kb_id,
            cls.model.parser_id,
            cls.model.parser_config,
            cls.model.name,
            cls.model.type,
            cls.model.location,
            cls.model.size,
            Knowledgebase.tenant_id,
            Tenant.embd_id,
            Tenant.img2txt_id,
            Tenant.asr_id,
            cls.model.update_time]
        docs = cls.model.select(*fields) \
            .join(Knowledgebase, on=(cls.model.kb_id == Knowledgebase.id)) \
            .join(Tenant, on=(Knowledgebase.tenant_id == Tenant.id)) \
            .where(
            cls.model.status == StatusEnum.VALID.value,
            ~(cls.model.type == FileType.VIRTUAL.value),
            cls.model.progress == 0,
            cls.model.update_time >= current_timestamp() - 1000 * 600,
            cls.model.run == TaskStatus.RUNNING.value) \
            .order_by(cls.model.update_time.asc())
        return list(docs.dicts())

    @classmethod
    @DB.connection_context()
    def get_unfinished_docs(cls):
        fields = [cls.model.id, cls.model.process_begin_at, cls.model.parser_config, cls.model.progress_msg,
                  cls.model.run, cls.model.parser_id]
        docs = cls.model.select(*fields) \
            .where(
            cls.model.status == StatusEnum.VALID.value,
            ~(cls.model.type == FileType.VIRTUAL.value),
            cls.model.progress < 1,
            cls.model.progress > 0)
        return list(docs.dicts())

    @classmethod
    @DB.connection_context()
    def increment_chunk_num(cls, doc_id, kb_id, token_num, chunk_num, duation):
        num = cls.model.update(token_num=cls.model.token_num + token_num,
                               chunk_num=cls.model.chunk_num + chunk_num,
                               process_duation=cls.model.process_duation + duation).where(
            cls.model.id == doc_id).execute()
        if num == 0:
            raise LookupError(
                "Document not found which is supposed to be there")
        num = Knowledgebase.update(
            token_num=Knowledgebase.token_num +
            token_num,
            chunk_num=Knowledgebase.chunk_num +
            chunk_num).where(
            Knowledgebase.id == kb_id).execute()
        return num

    @classmethod
    @DB.connection_context()
    def decrement_chunk_num(cls, doc_id, kb_id, token_num, chunk_num, duation):
        num = cls.model.update(token_num=cls.model.token_num - token_num,
                               chunk_num=cls.model.chunk_num - chunk_num,
                               process_duation=cls.model.process_duation + duation).where(
            cls.model.id == doc_id).execute()
        if num == 0:
            raise LookupError(
                "Document not found which is supposed to be there")
        num = Knowledgebase.update(
            token_num=Knowledgebase.token_num -
            token_num,
            chunk_num=Knowledgebase.chunk_num -
            chunk_num
        ).where(
            Knowledgebase.id == kb_id).execute()
        return num

    @classmethod
    @DB.connection_context()
    def clear_chunk_num(cls, doc_id):
        doc = cls.model.get_by_id(doc_id)
        assert doc, "Can't fine document in database."

        num = Knowledgebase.update(
            token_num=Knowledgebase.token_num -
            doc.token_num,
            chunk_num=Knowledgebase.chunk_num -
            doc.chunk_num,
            doc_num=Knowledgebase.doc_num - 1
        ).where(
            Knowledgebase.id == doc.kb_id).execute()
        return num

    @classmethod
    @DB.connection_context()
    def get_tenant_id(cls, doc_id):
        docs = cls.model.select(
            Knowledgebase.tenant_id).join(
            Knowledgebase, on=(
                Knowledgebase.id == cls.model.kb_id)).where(
            cls.model.id == doc_id, Knowledgebase.status == StatusEnum.VALID.value)
        docs = docs.dicts()
        if not docs:
            return
        return docs[0]["tenant_id"]

    @classmethod
    @DB.connection_context()
    def get_knowledgebase_id(cls, doc_id):
        docs = cls.model.select(cls.model.kb_id).where(cls.model.id == doc_id)
        docs = docs.dicts()
        if not docs:
            return
        return docs[0]["kb_id"]

    @classmethod
    @DB.connection_context()
    def get_tenant_id_by_name(cls, name):
        docs = cls.model.select(
            Knowledgebase.tenant_id).join(
            Knowledgebase, on=(
                Knowledgebase.id == cls.model.kb_id)).where(
            cls.model.name == name, Knowledgebase.status == StatusEnum.VALID.value)
        docs = docs.dicts()
        if not docs:
            return
        return docs[0]["tenant_id"]

    @classmethod
    @DB.connection_context()
    def accessible(cls, doc_id, user_id=None):
        docs = cls.model.select(
            cls.model.id).join(
            Knowledgebase, on=(
                Knowledgebase.id == cls.model.kb_id)
        ).join(UserTenant, on=(UserTenant.tenant_id == Knowledgebase.tenant_id)
               ).where(cls.model.id == doc_id, UserTenant.user_id == user_id).paginate(0, 1)
        docs = docs.dicts()
        if not docs:
            return False

        e, d = cls.get_by_id(doc_id)
        if not e:
            return False
        #if user_id not in d.filter_fields.get('limit_range',[]):
        #    return False
        return True

    @classmethod
    @DB.connection_context()
    def accessible4deletion(cls, doc_id, user_id):
        docs = cls.model.select(cls.model.id
        ).join(
            Knowledgebase, on=(
                Knowledgebase.id == cls.model.kb_id)
        ).join(
            UserTenant, on=(
                (UserTenant.tenant_id == Knowledgebase.created_by) & (UserTenant.user_id == user_id))
        ).where(
            cls.model.id == doc_id,
            UserTenant.status == StatusEnum.VALID.value,
            ((UserTenant.role == UserTenantRole.NORMAL) | (UserTenant.role == UserTenantRole.OWNER))
        ).paginate(0, 1)
        docs = docs.dicts()
        if not docs:
            return False
        return True

    @classmethod
    @DB.connection_context()
    def get_embd_id(cls, doc_id):
        docs = cls.model.select(
            Knowledgebase.embd_id).join(
            Knowledgebase, on=(
                Knowledgebase.id == cls.model.kb_id)).where(
            cls.model.id == doc_id, Knowledgebase.status == StatusEnum.VALID.value)
        docs = docs.dicts()
        if not docs:
            return
        return docs[0]["embd_id"]

    @classmethod
    @DB.connection_context()
    def get_chunking_config(cls, doc_id):
        configs = (
            cls.model.select(
                cls.model.id,
                cls.model.kb_id,
                cls.model.parser_id,
                cls.model.parser_config,
                Knowledgebase.language,
                Knowledgebase.embd_id,
                Tenant.id.alias("tenant_id"),
                Tenant.img2txt_id,
                Tenant.asr_id,
                Tenant.llm_id,
            )
            .join(Knowledgebase, on=(cls.model.kb_id == Knowledgebase.id))
            .join(Tenant, on=(Knowledgebase.tenant_id == Tenant.id))
            .where(cls.model.id == doc_id)
        )
        configs = configs.dicts()
        if not configs:
            return None
        return configs[0]

    @classmethod
    @DB.connection_context()
    def get_doc_id_by_doc_name(cls, doc_name):
        fields = [cls.model.id]
        doc_id = cls.model.select(*fields) \
            .where(cls.model.name == doc_name)
        doc_id = doc_id.dicts()
        if not doc_id:
            return
        return doc_id[0]["id"]

    @classmethod
    @DB.connection_context()
    def get_thumbnails(cls, docids):
        fields = [cls.model.id, cls.model.kb_id, cls.model.thumbnail]
        return list(cls.model.select(
            *fields).where(cls.model.id.in_(docids)).dicts())

    @classmethod
    @DB.connection_context()
    def update_parser_config(cls, id, config):
        if not config:
            return
        e, d = cls.get_by_id(id)
        if not e:
            raise LookupError(f"Document({id}) not found.")

        #更新：如果没有字段直接添加；如果有字段，字段不是dic则替换，是dic则需要更新
        #这样实际效果是dic的每个key/value 都被替换或者增加了，
        #但是不会把之前已有的，新的里边没有的情况下给丢弃
        #注意如果不是dic，则会被直接添加或者替换了，比如[] 列表
        def dfs_update(old, new):
            for k, v in new.items():
                if k not in old:
                    old[k] = v
                    continue
                if isinstance(v, dict):
                    assert isinstance(old[k], dict)
                    dfs_update(old[k], v)
                else:
                    old[k] = v

        dfs_update(d.parser_config, config)
        if not config.get("raptor") and d.parser_config.get("raptor"):
            del d.parser_config["raptor"]
        cls.update_by_id(id, {"parser_config": d.parser_config})

    @classmethod
    @DB.connection_context()
    def update_filter_fields(cls, id, config,user_id):
        if not config:
            return

        for k,v in config.items():
            if k not in ['limit_range','limit_level','limit_time']:
                return
        e, d = cls.get_by_id(id)
        if not e:
            raise LookupError(f"Document({id}) not found.")

        def dfs_update(old, new):
            for k, v in new.items():
                if k not in old:
                    old[k] = v
                    continue
                if isinstance(v, dict):
                    assert isinstance(old[k], dict)
                    dfs_update(old[k], v)
                else:
                    old[k] = v
        dfs_update(d.filter_fields, config)
        if user_id and user_id not in d.filter_fields['limit_range']:
            logging.info(f"update_filter_fields insert the user_id {user_id}")
            d.filter_fields['limit_range'] = d.filter_fields['limit_range'] + [user_id]
        cls.update_by_id(id, {"filter_fields": d.filter_fields})

    @classmethod
    @DB.connection_context()
    def get_doc_count(cls, tenant_id):
        docs = cls.model.select(cls.model.id).join(Knowledgebase,
                                                   on=(Knowledgebase.id == cls.model.kb_id)).where(
            Knowledgebase.tenant_id == tenant_id)
        return len(docs)

    @classmethod
    @DB.connection_context()
    def begin2parse(cls, docid):
        cls.update_by_id(
            docid, {"progress": random.random() * 1 / 100.,
                    "progress_msg": "Task is queued...",
                    "process_begin_at": get_format_time()
                    })

    @classmethod
    @DB.connection_context()
    def update_meta_fields(cls, doc_id, meta_fields):
        return cls.update_by_id(doc_id, {"meta_fields": meta_fields})

    @classmethod
    @DB.connection_context()
    def update_md_location_fields(cls, doc_id, md_location):
        return cls.update_by_id(doc_id, {"md_location": md_location})

    @classmethod
    @DB.connection_context()
    def update_layout_location_fields(cls, doc_id, layout_location):
        return cls.update_by_id(doc_id, {"layout_location": layout_location})

    @classmethod
    @DB.connection_context()
    def update_progress(cls):
        docs = cls.get_unfinished_docs()
        for d in docs:
            try:
                tsks = Task.query(doc_id=d["id"], order_by=Task.create_time)
                if not tsks:
                    logging.warning(f"update_progress not find doc {d['id']}")
                    continue
                msg = []
                prg = 0
                finished = True
                bad = 0
                has_raptor = False
                has_graphrag = False
                e, doc = DocumentService.get_by_id(d["id"])
                status = doc.run  # TaskStatus.RUNNING.value
                priority = 0
                for t in tsks:
                    if 0 <= t.progress < 1:
                        finished = False
                    if t.progress == -1:
                        bad += 1
                    prg += t.progress if t.progress >= 0 else 0
                    msg.append(t.progress_msg)
                    if t.task_type == "raptor":
                        has_raptor = True
                    elif t.task_type == "graphrag":
                        has_graphrag = True
                    priority = max(priority, t.priority)
                prg /= len(tsks)
                if finished and bad:
                    prg = -1
                    status = TaskStatus.FAIL.value
                elif finished:
                    if d["parser_config"].get("raptor", {}).get("use_raptor") and not has_raptor:
                        queue_raptor_o_graphrag_tasks(d, "raptor", priority)
                        prg = 0.98 * len(tsks) / (len(tsks) + 1)
                    elif d["parser_config"].get("graphrag", {}).get("use_graphrag") and not has_graphrag:
                        queue_raptor_o_graphrag_tasks(d, "graphrag", priority)
                        prg = 0.98 * len(tsks) / (len(tsks) + 1)
                    else:
                        status = TaskStatus.DONE.value

                msg = "\n".join(sorted(msg))
                info = {
                    "process_duation": datetime.timestamp(
                        datetime.now()) -
                    d["process_begin_at"].timestamp(),
                    "run": status}
                if prg != 0:
                    info["progress"] = round(prg,2)
                if msg:
                    info["progress_msg"] = msg
                cls.update_by_id(d["id"], info)
            except Exception as e:
                if str(e).find("'0'") < 0:
                    logging.exception("fetch task exception")

    @classmethod
    @DB.connection_context()
    def get_kb_doc_count(cls, kb_id):
        return len(cls.model.select(cls.model.id).where(
            cls.model.kb_id == kb_id).dicts())

    @classmethod
    @DB.connection_context()
    def do_cancel(cls, doc_id):
        try:
            _, doc = DocumentService.get_by_id(doc_id)
            return doc.run == TaskStatus.CANCEL.value or doc.progress < 0
        except Exception:
            pass
        return False


def queue_raptor_o_graphrag_tasks(doc, ty, priority):
    chunking_config = DocumentService.get_chunking_config(doc["id"])
    hasher = xxhash.xxh64()
    for field in sorted(chunking_config.keys()):
        hasher.update(str(chunking_config[field]).encode("utf-8"))

    def new_task():
        nonlocal doc
        return {
            "id": get_uuid(),
            "doc_id": doc["id"],
            "from_page": 100000000,
            "to_page": 100000000,
            "task_type": ty,
            "progress_msg":  datetime.now().strftime("%H:%M:%S") + " created task " + ty
        }

    task = new_task()
    for field in ["doc_id", "from_page", "to_page"]:
        hasher.update(str(task.get(field, "")).encode("utf-8"))
    hasher.update(ty.encode("utf-8"))
    task["digest"] = hasher.hexdigest()
    bulk_insert_into_db(Task, [task], True)
    assert REDIS_CONN.queue_product(get_svr_queue_name(priority), message=task), "Can't access Redis. Please check the Redis' status."


def doc_upload_and_parse(conversation_id, file_objs, user_id):
    from api.db.services.api_service import API4ConversationService
    from api.db.services.conversation_service import ConversationService
    from api.db.services.dialog_service import DialogService
    from api.db.services.file_service import FileService
    from api.db.services.llm_service import LLMBundle
    from api.db.services.user_service import TenantService
    from rag.app import audio, email, naive, picture, presentation

    e, conv = ConversationService.get_by_id(conversation_id)
    if not e:
        e, conv = API4ConversationService.get_by_id(conversation_id)
    assert e, "Conversation not found!"

    e, dia = DialogService.get_by_id(conv.dialog_id)
    if not dia.kb_ids:
        raise LookupError("No knowledge base associated with this conversation. "
                          "Please add a knowledge base before uploading documents")
    logging.info("doc_upload_and_parse for user id {}".format(user_id))
    kb_id = dia.kb_ids[0]
    e, kb = KnowledgebaseService.get_by_id(kb_id)
    if not e:
        raise LookupError("Can't find this knowledgebase!")

    if not KnowledgebaseService.accessible(kb_id, user_id):
        raise Exception(f"You don't own the dataset {kb_id}.")

    embd_mdl = LLMBundle(kb.tenant_id, LLMType.EMBEDDING, llm_name=kb.embd_id, lang=kb.language)

    err, files = FileService.upload_document(kb, file_objs, user_id)
    assert not err, "\n".join(err)

    def dummy(prog=None, msg=""):
        pass

    FACTORY = {
        ParserType.PRESENTATION.value: presentation,
        ParserType.PICTURE.value: picture,
        ParserType.AUDIO.value: audio,
        ParserType.EMAIL.value: email
    }
    parser_config = {"chunk_token_num": 4096, "delimiter": "\n!?;。；！？", "layout_recognize": "Plain Text"}
    exe = ThreadPoolExecutor(max_workers=12)
    threads = []
    doc_nm = {}
    for d, blob in files:
        doc_nm[d["id"]] = d["name"]
    for d, blob in files:
        kwargs = {
            "callback": dummy,
            "parser_config": parser_config,
            "from_page": 0,
            "to_page": 100000,
            "tenant_id": kb.tenant_id,
            "lang": kb.language
        }
        threads.append(exe.submit(FACTORY.get(d["parser_id"], naive).chunk, d["name"], blob, **kwargs))

    for (docinfo, _), th in zip(files, threads):
        docs = []
        doc = {
            "doc_id": docinfo["id"],
            "kb_id": [kb.id]
        }
        for ck in th.result():
            d = deepcopy(doc)
            d.update(ck)
            d["id"] = xxhash.xxh64((ck["content_with_weight"] + str(d["doc_id"])).encode("utf-8")).hexdigest()
            d["create_time"] = str(datetime.now()).replace("T", " ")[:19]
            d["create_timestamp_flt"] = datetime.now().timestamp()
            if not d.get("image"):
                docs.append(d)
                continue

            output_buffer = BytesIO()
            if isinstance(d["image"], bytes):
                output_buffer = BytesIO(d["image"])
            else:
                d["image"].save(output_buffer, format='JPEG')

            STORAGE_IMPL.put(kb.id, d["id"], output_buffer.getvalue())
            d["img_id"] = "{}-{}".format(kb.id, d["id"])
            d.pop("image", None)
            docs.append(d)

    parser_ids = {d["id"]: d["parser_id"] for d, _ in files}
    docids = [d["id"] for d, _ in files]
    chunk_counts = {id: 0 for id in docids}
    token_counts = {id: 0 for id in docids}
    es_bulk_size = 64

    def embedding(doc_id, cnts, batch_size=16):
        nonlocal embd_mdl, chunk_counts, token_counts
        vects = []
        for i in range(0, len(cnts), batch_size):
            vts, c = embd_mdl.encode(cnts[i: i + batch_size])
            vects.extend(vts.tolist())
            chunk_counts[doc_id] += len(cnts[i:i + batch_size])
            token_counts[doc_id] += c
        return vects

    idxnm = search.index_name(kb.tenant_id)
    try_create_idx = True

    _, tenant = TenantService.get_by_id(kb.tenant_id)
    llm_bdl = LLMBundle(kb.tenant_id, LLMType.CHAT, tenant.llm_id)
    for doc_id in docids:
        cks = [c for c in docs if c["doc_id"] == doc_id]

        if parser_ids[doc_id] != ParserType.PICTURE.value:
            from graphrag.general.mind_map_extractor import MindMapExtractor
            mindmap = MindMapExtractor(llm_bdl)
            try:
                mind_map = trio.run(mindmap, [c["content_with_weight"] for c in docs if c["doc_id"] == doc_id])
                mind_map = json.dumps(mind_map.output, ensure_ascii=False, indent=2)
                if len(mind_map) < 32:
                    raise Exception("Few content: " + mind_map)
                cks.append({
                    "id": get_uuid(),
                    "doc_id": doc_id,
                    "kb_id": [kb.id],
                    "docnm_kwd": doc_nm[doc_id],
                    "title_tks": rag_tokenizer.tokenize(re.sub(r"\.[a-zA-Z]+$", "", doc_nm[doc_id])),
                    "content_ltks": rag_tokenizer.tokenize("summary summarize 总结 概况 file 文件 概括"),
                    "content_with_weight": mind_map,
                    "knowledge_graph_kwd": "mind_map"
                })
            except Exception as e:
                logging.exception("Mind map generation error")

        vects = embedding(doc_id, [c["content_with_weight"] for c in cks])
        assert len(cks) == len(vects)
        for i, d in enumerate(cks):
            v = vects[i]
            d["q_%d_vec" % len(v)] = v
        for b in range(0, len(cks), es_bulk_size):
            if try_create_idx:
                if not settings.docStoreConn.indexExist(idxnm, kb_id):
                    settings.docStoreConn.createIdx(idxnm, kb_id, len(vects[0]))
                try_create_idx = False
            settings.docStoreConn.insert(cks[b:b + es_bulk_size], idxnm, kb_id)

        DocumentService.increment_chunk_num(
            doc_id, kb.id, token_counts[doc_id], chunk_counts[doc_id], 0)

    return [d["id"] for d, _ in files]
