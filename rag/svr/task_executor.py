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

# from beartype import BeartypeConf
# from beartype.claw import beartype_all  # <-- you didn't sign up for this
# beartype_all(conf=BeartypeConf(violation_type=UserWarning))    # <-- emit warnings from all code
import random
import sys
import threading
import time
import math
sys.path.append('/usr/local/lib/python3.10/dist-packages/')
import fitz
from PIL import Image

from api.utils.log_utils import initRootLogger, get_project_base_directory
from graphrag.general.index import run_graphrag
from graphrag.utils import get_llm_cache, set_llm_cache, get_tags_from_cache, set_tags_to_cache
from minerU.mineru_extractor import get_pdf_file_bytes, extract_metadata, extract_directory, format_time
from rag.prompts import keyword_extraction, question_proposal, content_tagging

import logging
import os
import bisect
import traceback
from datetime import datetime
import json
import xxhash
import copy
import re
from functools import partial
from io import BytesIO
from multiprocessing.context import TimeoutError
from timeit import default_timer as timer
import tracemalloc
import signal
import trio
import exceptiongroup
import faulthandler

import numpy as np
from peewee import DoesNotExist

from api.db import LLMType, ParserType, TaskStatus, constant
from api.db.services.document_service import DocumentService
from api.db.services.llm_service import LLMBundle
from api.db.services.task_service import TaskService
from api.db.services.file2document_service import File2DocumentService
from api import settings
from api.versions import get_ragflow_version
from api.db.db_models import close_connection
from rag.app import laws, paper, presentation, manual, qa, table, book, resume, picture, naive, one, audio, \
    email, tag
from rag.nlp import search, rag_tokenizer
from rag.raptor import RecursiveAbstractiveProcessing4TreeOrganizedRetrieval as Raptor
from rag.paper_extractor import PaperExtractor as PaperExtractor
from rag.paper_classifier import PaperClassifier as PaperClassifier
from rag.settings import DOC_MAXIMUM_SIZE, SVR_CONSUMER_GROUP_NAME, get_svr_queue_name, get_svr_queue_names, print_rag_settings, TAG_FLD, PAGERANK_FLD
from rag.utils import num_tokens_from_string, truncate
from rag.utils.redis_conn import REDIS_CONN, RedisDistributedLock
from rag.utils.storage_factory import STORAGE_IMPL
from graphrag.utils import chat_limiter

BATCH_SIZE = 64

FACTORY = {
    "general": naive,
    ParserType.NAIVE.value: naive,
    ParserType.PAPER.value: paper,
    ParserType.BOOK.value: book,
    ParserType.PRESENTATION.value: presentation,
    ParserType.MANUAL.value: manual,
    ParserType.LAWS.value: laws,
    ParserType.QA.value: qa,
    ParserType.TABLE.value: table,
    ParserType.RESUME.value: resume,
    ParserType.PICTURE.value: picture,
    ParserType.ONE.value: one,
    ParserType.AUDIO.value: audio,
    ParserType.EMAIL.value: email,
    ParserType.KG.value: naive,
    ParserType.TAG.value: tag
}

UNACKED_ITERATOR = None

CONSUMER_NO = "0" if len(sys.argv) < 2 else sys.argv[1]
CONSUMER_NAME = "task_executor_" + CONSUMER_NO
BOOT_AT = datetime.now().astimezone().isoformat(timespec="milliseconds")
PENDING_TASKS = 0
LAG_TASKS = 0
DONE_TASKS = 0
FAILED_TASKS = 0

CURRENT_TASKS = {}

MAX_CONCURRENT_TASKS = int(os.environ.get('MAX_CONCURRENT_TASKS', "5"))
MAX_CONCURRENT_CHUNK_BUILDERS = int(os.environ.get('MAX_CONCURRENT_CHUNK_BUILDERS', "1"))
task_limiter = trio.CapacityLimiter(MAX_CONCURRENT_TASKS)
chunk_limiter = trio.CapacityLimiter(MAX_CONCURRENT_CHUNK_BUILDERS)
WORKER_HEARTBEAT_TIMEOUT = int(os.environ.get('WORKER_HEARTBEAT_TIMEOUT', '120'))
stop_event = threading.Event()


def find_interval(arr, n):
    if len(arr) == 0:
        return None, None

    # 使用 bisect_left 定位 n 的插入位置 (寻找子论文属于哪个分块)
    pos = bisect.bisect_left(arr, n)

    if pos == 0:
        return None, arr[0]  # n 小于第一个元素
    elif pos == len(arr):
        return arr[-1], None  # n 大于最后一个元素
    elif arr[pos] == n:
        return arr[pos], arr[pos]  # n 等于数组中的元素
    else:
        return arr[pos - 1], arr[pos]  # n 在 arr[pos-1] 和 arr[pos] 之间


def signal_handler(sig, frame):
    logging.info("Received interrupt signal, shutting down...")
    stop_event.set()
    time.sleep(1)
    sys.exit(0)


# SIGUSR1 handler: start tracemalloc and take snapshot
def start_tracemalloc_and_snapshot(signum, frame):
    if not tracemalloc.is_tracing():
        logging.info("start tracemalloc")
        tracemalloc.start()
    else:
        logging.info("tracemalloc is already running")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot_file = f"snapshot_{timestamp}.trace"
    snapshot_file = os.path.abspath(os.path.join(get_project_base_directory(), "logs", f"{os.getpid()}_snapshot_{timestamp}.trace"))

    snapshot = tracemalloc.take_snapshot()
    snapshot.dump(snapshot_file)
    current, peak = tracemalloc.get_traced_memory()
    if sys.platform == "win32":
        import  psutil
        process = psutil.Process()
        max_rss = process.memory_info().rss / 1024
    else:
        import resource
        max_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    logging.info(f"taken snapshot {snapshot_file}. max RSS={max_rss / 1000:.2f} MB, current memory usage: {current / 10**6:.2f} MB, Peak memory usage: {peak / 10**6:.2f} MB")

# SIGUSR2 handler: stop tracemalloc
def stop_tracemalloc(signum, frame):
    if tracemalloc.is_tracing():
        logging.info("stop tracemalloc")
        tracemalloc.stop()
    else:
        logging.info("tracemalloc not running")

class TaskCanceledException(Exception):
    def __init__(self, msg):
        self.msg = msg


def set_progress(task_id, from_page=0, to_page=-1, prog=None, msg="Processing..."):
    try:
        if prog is not None and prog < 0:
            msg = "[ERROR]" + msg
        cancel = TaskService.do_cancel(task_id)

        if cancel:
            msg += " [Canceled]"
            prog = -1

        if to_page > 0:
            if msg:
                if from_page < to_page:
                    msg = f"Page({from_page + 1}~{to_page + 1}): " + msg
        if msg:
            msg = datetime.now().strftime("%H:%M:%S") + " " + msg
        d = {"progress_msg": msg}
        if prog is not None:
            d["progress"] = round(prog, 4)

        TaskService.update_progress(task_id, d)

        close_connection()
        if cancel:
            raise TaskCanceledException(msg+",task id {}".format(task_id))
        logging.info(f"set_progress({task_id}), progress: {prog}, progress_msg: {msg}")
    except DoesNotExist:
        import traceback
        traceback.print_exc()
        logging.warning(f"set_progress({task_id}) got exception DoesNotExist,stack is {traceback.format_exc()}")
    except Exception:
        logging.exception(f"set_progress({task_id}), progress: {prog}, progress_msg: {msg}, got exception")

async def collect():
    global CONSUMER_NAME, DONE_TASKS, FAILED_TASKS
    global UNACKED_ITERATOR
    svr_queue_names = get_svr_queue_names()
    try:
        if not UNACKED_ITERATOR:
            UNACKED_ITERATOR = REDIS_CONN.get_unacked_iterator(svr_queue_names, SVR_CONSUMER_GROUP_NAME, CONSUMER_NAME)
        try:
            redis_msg = next(UNACKED_ITERATOR)
        except StopIteration:
            for svr_queue_name in svr_queue_names:
                redis_msg = REDIS_CONN.queue_consumer(svr_queue_name, SVR_CONSUMER_GROUP_NAME, CONSUMER_NAME)
                if redis_msg:
                    break
    except Exception:
        logging.exception("collect got exception")
        return None, None

    if not redis_msg:
        return None, None
    msg = redis_msg.get_message()
    if not msg:
        logging.error(f"collect got empty message of {redis_msg.get_msg_id()}")
        redis_msg.ack()
        return None, None

    canceled = False
    #Task是从数据库获取的；所以有些在doc或msg中的信息，需要添加进去
    task = TaskService.get_task(msg["id"])
    if task:
        _, doc = DocumentService.get_by_id(task["doc_id"])
        canceled = doc.run == TaskStatus.CANCEL.value or doc.progress < 0
    if not task or canceled:
        state = "is unknown" if not task else "has been cancelled"
        FAILED_TASKS += 1
        logging.warning(f"collect task {msg['id']} {state}")
        redis_msg.ack()
        return None, None
    task["task_type"] = msg.get("task_type", "")
    task["meta_fields"] = doc.meta_fields
    task["filter_fields"] = doc.filter_fields
    task["doc_name"] = doc.name
    return redis_msg, task


async def get_storage_binary(bucket, name):
    return await trio.to_thread.run_sync(lambda: STORAGE_IMPL.get(bucket, name))


async def build_chunks(task, progress_callback):
    if task["size"] > DOC_MAXIMUM_SIZE:
        set_progress(task["id"], prog=-1, msg="File size exceeds(doc size {}Mb,but should <= {}Mb )".format(
            int(task["size"]/1024/1024),int(DOC_MAXIMUM_SIZE / 1024 / 1024)))
        #return []

    chunker = FACTORY[task["parser_id"].lower()]
    try:
        st = timer()
        bucket, name = File2DocumentService.get_storage_address(doc_id=task["doc_id"])
        binary = await get_storage_binary(bucket, name)
        logging.info("From minio({}) {}/{}".format(timer() - st, task["location"], task["name"]))
    except TimeoutError:
        progress_callback(-1, "Internal server error: Fetch file from minio timeout. Could you try it again.")
        logging.exception(
            "Minio {}/{} got timeout: Fetch file from minio timeout.".format(task["location"], task["name"]))
        raise
    except Exception as e:
        if re.search("(No such file|not found)", str(e)):
            progress_callback(-1, "Can not find file <%s> from minio. Could you try it again?" % task["name"])
        else:
            progress_callback(-1, "Get file from minio: %s" % str(e).replace("'", ""))
        import traceback
        traceback.print_exc()
        logging.exception("Chunking {}/{} got exception {}".format(task["location"], task["name"],traceback.format_exc()))
        raise

    try:
        async with chunk_limiter:
            cks = await trio.to_thread.run_sync(lambda: chunker.chunk(task["name"], binary=binary, from_page=task["from_page"],
                                to_page=task["to_page"], lang=task["language"], callback=progress_callback,
                                kb_id=task["kb_id"], parser_config=task["parser_config"], tenant_id=task["tenant_id"],doc_id=task["doc_id"]))
        logging.info("Chunking({}) {}/{} done".format(timer() - st, task["location"], task["name"]))
    except TaskCanceledException:
        logging.exception("Chunking {}/{} got exception {}".format(task["location"], task["name"],"TaskCanceledException"))
        raise
    except Exception as e:
        progress_callback(-1, "Internal server error while chunking: %s" % str(e).replace("'", ""))
        logging.exception("Chunking {}/{} got exception".format(task["location"], task["name"]))
        raise

    docs = []
    doc = {
        "doc_id": task["doc_id"],
        "kb_id": str(task["kb_id"])
    }
    if task["pagerank"]:
        doc[PAGERANK_FLD] = int(task["pagerank"])
    el = 0
    for ck in cks:
        d = copy.deepcopy(doc)
        d.update(ck)
        d["id"] = xxhash.xxh64((ck["content_with_weight"] + str(d["doc_id"])).encode("utf-8")).hexdigest()
        d["create_time"] = str(datetime.now()).replace("T", " ")[:19]
        d["create_timestamp_flt"] = datetime.now().timestamp()
        if not d.get("image"):
            _ = d.pop("image", None)
            d["img_id"] = ""
            docs.append(d)
            continue

        try:
            output_buffer = BytesIO()
            if isinstance(d["image"], bytes):
                output_buffer = BytesIO(d["image"])
            else:
                d["image"].save(output_buffer, format='JPEG')

            st = timer()
            await trio.to_thread.run_sync(lambda: STORAGE_IMPL.put(task["kb_id"], d["id"], output_buffer.getvalue()))
            el += timer() - st
        except Exception:
            logging.exception(
                "Saving image of chunk {}/{}/{} got exception".format(task["location"], task["name"], d["id"]))
            raise

        d["img_id"] = "{}-{}".format(task["kb_id"], d["id"])
        del d["image"]
        docs.append(d)
    logging.info("MINIO PUT({}):{}".format(task["name"], el))

    if task["parser_config"].get("auto_keywords", 0):
        st = timer()
        progress_callback(msg="Start to generate keywords for every chunk ...")
        chat_mdl = LLMBundle(task["tenant_id"], LLMType.CHAT, llm_name=task["llm_id"], lang=task["language"])

        async def doc_keyword_extraction(chat_mdl, d, topn):
            cached = get_llm_cache(chat_mdl.llm_name, d["content_with_weight"], "keywords", {"topn": topn})
            if not cached:
                async with chat_limiter:
                    cached = await trio.to_thread.run_sync(lambda: keyword_extraction(chat_mdl, d["content_with_weight"], topn))
                set_llm_cache(chat_mdl.llm_name, d["content_with_weight"], cached, "keywords", {"topn": topn})
            if cached:
                d["important_kwd"] = cached.split(",")
                d["important_tks"] = rag_tokenizer.tokenize(" ".join(d["important_kwd"]))
            return
        async with trio.open_nursery() as nursery:
            for d in docs:
                nursery.start_soon(doc_keyword_extraction, chat_mdl, d, task["parser_config"]["auto_keywords"])
        progress_callback(msg="Keywords generation {} chunks completed in {:.2f}s".format(len(docs), timer() - st))

    if task["parser_config"].get("auto_questions", 0):
        st = timer()
        progress_callback(msg="Start to generate questions for every chunk ...")
        chat_mdl = LLMBundle(task["tenant_id"], LLMType.CHAT, llm_name=task["llm_id"], lang=task["language"])

        async def doc_question_proposal(chat_mdl, d, topn):
            cached = get_llm_cache(chat_mdl.llm_name, d["content_with_weight"], "question", {"topn": topn})
            if not cached:
                async with chat_limiter:
                    cached = await trio.to_thread.run_sync(lambda: question_proposal(chat_mdl, d["content_with_weight"], topn))
                set_llm_cache(chat_mdl.llm_name, d["content_with_weight"], cached, "question", {"topn": topn})
            if cached:
                d["question_kwd"] = cached.split("\n")
                d["question_tks"] = rag_tokenizer.tokenize("\n".join(d["question_kwd"]))
        async with trio.open_nursery() as nursery:
            for d in docs:
                nursery.start_soon(doc_question_proposal, chat_mdl, d, task["parser_config"]["auto_questions"])
        progress_callback(msg="Question generation {} chunks completed in {:.2f}s".format(len(docs), timer() - st))

    if task["kb_parser_config"].get("tag_kb_ids", []):
        progress_callback(msg="Start to tag for every chunk ...")
        kb_ids = task["kb_parser_config"]["tag_kb_ids"]
        tenant_id = task["tenant_id"]
        topn_tags = task["kb_parser_config"].get("topn_tags", 3)
        S = 1000
        st = timer()
        examples = []
        all_tags = get_tags_from_cache(kb_ids)
        if not all_tags:
            all_tags = settings.retrievaler.all_tags_in_portion(tenant_id, kb_ids, S)
            set_tags_to_cache(kb_ids, all_tags)
        else:
            all_tags = json.loads(all_tags)

        chat_mdl = LLMBundle(task["tenant_id"], LLMType.CHAT, llm_name=task["llm_id"], lang=task["language"])

        docs_to_tag = []
        for d in docs:
            if settings.retrievaler.tag_content(tenant_id, kb_ids, d, all_tags, topn_tags=topn_tags, S=S):
                examples.append({"content": d["content_with_weight"], TAG_FLD: d[TAG_FLD]})
            else:
                docs_to_tag.append(d)

        async def doc_content_tagging(chat_mdl, d, topn_tags):
            cached = get_llm_cache(chat_mdl.llm_name, d["content_with_weight"], all_tags, {"topn": topn_tags})
            if not cached:
                picked_examples = random.choices(examples, k=2) if len(examples)>2 else examples
                if not picked_examples:
                    picked_examples.append({"content": "This is an example", TAG_FLD: {'example': 1}})
                async with chat_limiter:
                    cached = await trio.to_thread.run_sync(lambda: content_tagging(chat_mdl, d["content_with_weight"], all_tags, picked_examples, topn=topn_tags))
                if cached:
                    cached = json.dumps(cached)
            if cached:
                set_llm_cache(chat_mdl.llm_name, d["content_with_weight"], cached, all_tags, {"topn": topn_tags})
                d[TAG_FLD] = json.loads(cached)
        async with trio.open_nursery() as nursery:
            for d in docs_to_tag:
                nursery.start_soon(doc_content_tagging, chat_mdl, d, topn_tags)
        progress_callback(msg="Tagging {} chunks completed in {:.2f}s".format(len(docs), timer() - st))

    return docs


def init_kb(row, vector_size: int):
    idxnm = search.index_name(row["tenant_id"])
    return settings.docStoreConn.createIdx(idxnm, row.get("kb_id", ""), vector_size)


async def embedding(docs, mdl, parser_config=None, callback=None):
    if parser_config is None:
        parser_config = {}
    batch_size = 16
    tts, cnts = [], []
    for d in docs:
        tts.append(d.get("docnm_kwd", "Title"))
        c = "\n".join(d.get("question_kwd", []))
        if not c:
            c = d["content_with_weight"]
        c = re.sub(r"</?(table|td|caption|tr|th)( [^<>]{0,12})?>", " ", c)
        if not c:
            c = "None"
        cnts.append(c)

    tk_count = 0
    if len(tts) == len(cnts):
        vts, c = await trio.to_thread.run_sync(lambda: mdl.encode(tts[0: 1]))
        tts = np.concatenate([vts for _ in range(len(tts))], axis=0)
        tk_count += c

    cnts_ = np.array([])
    for i in range(0, len(cnts), batch_size):
        vts, c = await trio.to_thread.run_sync(lambda: mdl.encode([truncate(c, mdl.max_length-10) for c in cnts[i: i + batch_size]]))
        if len(cnts_) == 0:
            cnts_ = vts
        else:
            cnts_ = np.concatenate((cnts_, vts), axis=0)
        tk_count += c
        callback(prog=0.5 + 0.1 * (i + 1) / len(cnts), msg="")
    cnts = cnts_

    title_w = float(parser_config.get("filename_embd_weight", 0.1))
    vects = (title_w * tts + (1 - title_w) *
             cnts) if len(tts) == len(cnts) else cnts

    assert len(vects) == len(docs)
    vector_size = 0
    for i, d in enumerate(docs):
        v = vects[i].tolist()
        vector_size = len(v)
        d["q_%d_vec" % len(v)] = v
    return tk_count, vector_size


async def run_raptor(row, chat_mdl, embd_mdl, vector_size, callback=None):
    chunks = []
    vctr_nm = "q_%d_vec"%vector_size
    for d in settings.retrievaler.chunk_list(row["doc_id"], row["tenant_id"], [str(row["kb_id"])],
                                             fields=["content_with_weight", vctr_nm]):
        chunks.append((d["content_with_weight"], np.array(d[vctr_nm])))

    raptor = Raptor(
        row["parser_config"]["raptor"].get("max_cluster", 64),
        chat_mdl,
        embd_mdl,
        row["parser_config"]["raptor"]["prompt"],
        row["parser_config"]["raptor"]["max_token"],
        row["parser_config"]["raptor"]["threshold"]
    )
    original_length = len(chunks)
    chunks = await raptor(chunks, row["parser_config"]["raptor"]["random_seed"], callback)
    doc = {
        "doc_id": row["doc_id"],
        "kb_id": [str(row["kb_id"])],
        "docnm_kwd": row["name"],
        "title_tks": rag_tokenizer.tokenize(row["name"])
    }
    if row["pagerank"]:
        doc[PAGERANK_FLD] = int(row["pagerank"])
    res = []
    tk_count = 0
    for content, vctr in chunks[original_length:]:
        d = copy.deepcopy(doc)
        d["id"] = xxhash.xxh64((content + str(d["doc_id"])).encode("utf-8")).hexdigest()
        d["create_time"] = str(datetime.now()).replace("T", " ")[:19]
        d["create_timestamp_flt"] = datetime.now().timestamp()
        d[vctr_nm] = vctr.tolist()
        d["content_with_weight"] = content
        d["content_ltks"] = rag_tokenizer.tokenize(content)
        d["content_sm_ltks"] = rag_tokenizer.fine_grained_tokenize(d["content_ltks"])
        res.append(d)
        tk_count += num_tokens_from_string(content)
    return res, tk_count


async def run_extract_(fields, metadata_type, chat_mdl, content, callback=None):
    key = fields
    extractor = PaperExtractor(
        chat_mdl,
        None,
        key
    )
    result = await extractor(content,key,metadata_type,callback)
    return result


async def run_extract(row, chat_mdl, content,callback=None):
    extractor_config = row["parser_config"].get('extractor')
    metadata_type = extractor_config.get("metadata_type", "default")
    prompt = None
    key = None
    if extractor_config:
        prompt = extractor_config.get("prompt",None)
        key = extractor_config.get("keyvalues",None)
    extractor = PaperExtractor(
        chat_mdl,
        prompt,
        key
    )
    result = await extractor(content,key,metadata_type,callback)
    return result


async def run_classify(row, chat_mdl, content, callback=None):
    classify_config = row["parser_config"].get('classifier')
    prompt = None
    key = None
    if classify_config:
        prompt = classify_config.get("prompt",None)
    classifier = PaperClassifier(
        chat_mdl,
        prompt
    )
    try:
        result = await classifier(content,callback)
    except Exception as e:
        result = {}
        logging.error(f"PaperClassifier Failed for {e}")
    logging.info(f"run_classify result {result}")
    return result


async def do_handle_task(task):
    task_id = task["id"]
    task_from_page = task["from_page"]
    task_to_page = task["to_page"]
    task_tenant_id = task["tenant_id"]
    task_embedding_id = task["embd_id"]
    task_language = task["language"]
    task_llm_id = task["llm_id"]
    task_dataset_id = task["kb_id"]
    task_doc_id = task["doc_id"]
    task_document_name = task["name"]
    task_parser_config = task["parser_config"]
    task_start_ts = timer()

    # prepare the progress callback function
    progress_callback = partial(set_progress, task_id, task_from_page, task_to_page)

    # FIXME: workaround, Infinity doesn't support table parsing method, this check is to notify user
    lower_case_doc_engine = settings.DOC_ENGINE.lower()
    if lower_case_doc_engine == 'infinity' and task['parser_id'].lower() == 'table':
        error_message = "Table parsing method is not supported by Infinity, please use other parsing methods or use Elasticsearch as the document engine."
        progress_callback(-1, msg=error_message)
        raise Exception(error_message)

    task_canceled = TaskService.do_cancel(task_id)
    if task_canceled:
        progress_callback(-1, msg="Task has been canceled.")
        return

    try:
        # bind embedding model
        embedding_model = LLMBundle(task_tenant_id, LLMType.EMBEDDING, llm_name=task_embedding_id, lang=task_language)
        vts, _ = embedding_model.encode(["ok"])
        vector_size = len(vts[0])
    except Exception as e:
        error_message = f'Fail to bind embedding model: {str(e)}'
        progress_callback(-1, msg=error_message)
        logging.exception(error_message)
        raise

    init_kb(task, vector_size)

    # Either using RAPTOR or Standard chunking methods
    if task.get("task_type", "") == "raptor":
        # bind LLM for raptor
        chat_model = LLMBundle(task_tenant_id, LLMType.CHAT, llm_name=task_llm_id, lang=task_language)
        # run RAPTOR
        chunks, token_count = await run_raptor(task, chat_model, embedding_model, vector_size, progress_callback)
    # Either using graphrag or Standard chunking methods
    elif task.get("task_type", "") == "graphrag":
        global task_limiter
        task_limiter = trio.CapacityLimiter(2)
        graphrag_conf = task_parser_config.get("graphrag", {})
        if not graphrag_conf.get("use_graphrag", False):
            return
        start_ts = timer()
        chat_model = LLMBundle(task_tenant_id, LLMType.CHAT, llm_name=task_llm_id, lang=task_language)
        with_resolution = graphrag_conf.get("resolution", False)
        with_community = graphrag_conf.get("community", False)
        await run_graphrag(task, task_language, with_resolution, with_community, chat_model, embedding_model, progress_callback)
        progress_callback(prog=1.0, msg="Knowledge Graph done ({:.2f}s)".format(timer() - start_ts))
        return
    else:
        # Standard chunking methods
        start_ts = timer()
        chunks = await build_chunks(task, progress_callback)
        logging.info("Build document {}: {:.2f}s".format(task_document_name, timer() - start_ts))
        if chunks is None:
            logging.error("Build document {} failed".format(task_document_name))
            return
        if not chunks:
            logging.error("Build document chunks {} failed".format(task_document_name))
            progress_callback(-1., msg=f"No chunk built from {task_document_name}")
            return
        # TODO: exception handler
        ## set_progress(task["did"], -1, "ERROR: ")
        progress_callback(0.5,msg="Generate {} chunks".format(len(chunks)))
        start_ts = timer()
        try:
            token_count, vector_size = await embedding(chunks, embedding_model, task_parser_config, progress_callback)
        except Exception as e:
            error_message = "Generate embedding error:{}".format(str(e))
            progress_callback(-1, error_message)
            logging.exception(error_message)
            token_count = 0
            raise
        progress_message = "Embedding chunks ({:.2f}s),即将进行要素抽取和分类".format(timer() - start_ts)
        logging.info(progress_message)
        progress_callback(0.7,msg=progress_message)


    chunk_count = len(set([chunk["id"] for chunk in chunks]))

    e, doc = DocumentService.get_by_id(task_doc_id)
    if not e:
        logging.error(f"Can't find this document {task_doc_id}!")
        raise LookupError(f"Can't find this document {task_doc_id}!")

    #获取过滤字段
    #知悉范围、级别、期限
    filter_fields_= task.get('filter_fields',{})
    if not filter_fields_:
        logging.error(f"Doc filter field not exists for {task_doc_id}!")
    #filter_fields_ = {'limit_range':[doc.created_by]}
    limit_range = filter_fields_.get('limit_range',[])
    if not limit_range:
        filter_fields_['limit_range']=[doc.created_by]
    limit_level = filter_fields_.get('limit_level',[])
    if not limit_level:
        filter_fields_['limit_level']= 1
    limit_time = filter_fields_.get('limit_time',[])
    if not limit_time:
        filter_fields_['limit_time']= 0
    if doc.created_by not in filter_fields_.get('limit_range',[]):
        #filter_fields_['limit_range']=filter_fields_['limit_range']+[doc.created_by]
        logging.error(f"Doc filter field error, doc owner {doc.created_by} not exists in filter {filter_fields_}!")
        raise LookupError(f"Doc filter field error, doc owner {doc.created_by} not exists in filter {filter_fields_}!")
    filter_fields_.pop('create_time',None)
    limit_time = filter_fields_.get('limit_time')
    # TODO ES首次存储时会自动将时间字符串转换为时间类型，后续若格式不符则会出现问题
    limit_time = str(datetime.fromtimestamp(limit_time/1000)).replace("T", " ")[:19]
    filter_fields_['limit_time'] = limit_time

    start_ts = timer()

    #先获取现有的元数据
    dict_result = task.get('meta_fields',{})
    DocumentService.update_meta_fields(task["doc_id"],  {})
    # dict_result.pop('meta_fields',None)
    logging.info(f"doc {task['doc_id']} 当前的 meta fields {dict_result}")
    key_now = dict_result.keys()

    file_type = task.get("type", "pdf")
    pdf_article_type = None

    # 从任务内获取元数据配置（默认知识库配置）
    extractor_config = task["parser_config"].get('extractor')
    # prompt = extractor_config.get("prompt", None)
    # metadata_type = extractor_config.get("metadata_type", "default")

    # 从文档内获取元数据配置
    doc_parser_config = doc.parser_config
    doc_extractor = doc_parser_config.get("extractor", {})
    metadata_type = doc_extractor.get("metadata_type", "default")
    logging.info(f"doc {doc.name} metadata type {metadata_type}")
    if metadata_type == "default" and extractor_config:
        metadata_type = extractor_config.get("metadata_type", "default")
        logging.info(f"task metadata type {metadata_type}")

    if extractor_config:
        logging.info(f"task extractor config {extractor_config}")
        task_keys = extractor_config.get("keyvalues", None)
    else:
        task_keys = constant.keyvalues_mapping.get(metadata_type)

    keys = doc_extractor.get("keyvalues")
    if not keys:
        logging.info(f"task keys")
        keys = task_keys
    logging.info(f"========= keys {metadata_type} ========= \n{keys}")
    fields = keys

    # 进行要素提取和分类
    chat_model = LLMBundle(task_tenant_id, LLMType.CHAT, llm_name=task_llm_id, lang=task_language)
    #运行
    c_count = 0
    content = ""
    CONTENT_MAX_LEN = 6000

    sub_paper = {}
    # 获取字节流
    bucket, name = File2DocumentService.get_storage_address(doc_id=task_doc_id)
    logging.info("pdf_bytes for bucket {} doc name {},doc_id {},tenant_id {}".format(
        bucket, name, task_doc_id, task_tenant_id
    ))
    pdf_bytes = get_pdf_file_bytes(bucket, name, task_doc_id, pdf_flag=True if file_type in ["pdf", ] else False)
    if not pdf_bytes:
        logging.error(f"Can't find this document {task_doc_id}!")
        raise LookupError(f"Can't find this document {task_doc_id}!")

    pdf_doc = fitz.open('pdf', pdf_bytes)
    # 最大识别图片页数
    MAX_NUM = 40

    # 是否使用视觉模型
    # use_vision_parser = True if len(pdf_doc) > MAX_NUM else False
    use_vision_parser = True
    if use_vision_parser:
        # 生成图片列表
        img_results = []
        flag = False
        for page_num in range(len(pdf_doc)):
            try:
                page = pdf_doc.load_page(page_num)
                factor = 1.0
                mat = fitz.Matrix(factor, factor)  # 缩放因子，调整分辨率
                pix = page.get_pixmap(matrix=mat)

                # 转换为PIL Image对象
                img_bytes = pix.tobytes()
                img = Image.open(BytesIO(img_bytes))
                width, height = img.size
                size = 600
                target_size = (size,  int(size*height/width))  # 调整大小
                img = img.resize(target_size, Image.LANCZOS)
                img_results.append(img)
                if not flag:
                    flag = True
                    w_bar, h_bar = img.size
                    token_size = int((h_bar * w_bar) / (28 * 28))
                    logging.info(f"原图片宽度: {width}px, 高度: {height}px, 缩放后图片宽度: {w_bar}px, 高度: {h_bar}px，计算token为：{token_size}")
            except Exception as e:
                logging.error(f"document: {task_doc_id} page_num: {page_num} Generate image byte stream error: {e}!")
        logging.info(f"========== pdf文件共{len(pdf_doc)}页；生成图片字节流列表：{len(img_results)} 张 ==========")

        # 提取目录
        result = None
        directory_begin = 0
        is_what = None
        try:
            result, is_what = extract_directory(
                task_tenant_id,  # 当前租户的唯一标识符，标识数据的归属, 使用用户选择的视觉模型
                images=img_results[:MAX_NUM],
                callback=progress_callback,
            )  # 提取目录，处理合并多张图片的结果后返回相关数据的 json 对象
            logging.info(f"========== 视觉模型提取目录完成： {result} ==========")
            directory_begin = result["directory_begin"]

            # 根据目录结果提取元数据：存在目录使用目录前内容；反之取前10页；
            num = max(10,directory_begin - 1)
            flag = directory_begin > 0 and len(result["dic_result"]) >= 1 # 是否存在目录

            if not flag:
                num = 10
            # 提取元数据
            fields_map = extract_metadata(
                task_tenant_id,  # 当前租户的唯一标识符，标识数据的归属, 使用用户选择的视觉模型
                images=img_results[:num],
                fields=fields,
                metadata_type=metadata_type,
                callback=progress_callback,
            )  # 提取并映射所需字段的元数据，处理合并多张图片的结果后返回一个包含元数据的 json 对象
            logging.info(f"========== 视觉模型提取元数据完成： {fields_map} ==========")
            content += json.dumps(fields_map)
            type_ = f"{metadata_type}" if metadata_type != "default" else ""
            progress_callback(msg=f"视觉模型提取{type_}元数据完成")
        except Exception as e:
            # import traceback
            traceback.print_exc()
            logging.error("Exception {}, Exception info is {}".format(e, traceback.format_exc()))
            logging.error(f"视觉模型提取失败，替换文本模型 error {e}!")
            for c_ in chunks:
                content = content + "\n" + c_['content_with_weight']
                c_count = c_count + len(c_['content_with_weight'])
                if c_count >= 10000:
                    break
            logging.debug(f"do_handle_task current content {content}")

            # fields_map = await run_extract(task, chat_model, content, progress_callback)
            fields_map = await run_extract_(fields, metadata_type, chat_model, content[:CONTENT_MAX_LEN], progress_callback)
            progress_callback(msg="文本模型提取元数据完成")

        if flag and is_what in ["论文集"]:
            logging.info(msg="识别到存在子论文")
            progress_callback(msg="识别到存在子论文，准备解析目录页码进行子论文要素抽取")
            pdf_article_type = "论文集"
            # 前往分析子目录对应的文章
            # 解析目录页码，定位每篇论文，用每篇论文第一页作为数据提取相应元数据
            main_content_begin = result['main_content_begin']
            sub_paper["dic_result"] = result
            sub_paper["main_content_begin"] = main_content_begin
            sub_paper["fields_map"] = {}
            for i in range(len(result['dic_result'])):
                res = result['dic_result'][i]
                title_ = res['章节']
                page_ = res['页码']
                pdf_page_ = main_content_begin - 1 + page_
                logging.info(f"子论文： {i} === pdf_page_: {pdf_page_} === {res}")
                try:
                    picture_ = img_results[pdf_page_]
                    fields_map_ = extract_metadata(
                        task_tenant_id, images=[picture_], fields=fields, metadata_type=metadata_type,
                        callback=progress_callback,
                    )
                except Exception as e:
                    fields_map_ = {}
                    traceback.print_exc()
                    logging.error("Exception {}, Exception info is {}".format(e, traceback.format_exc()))

                sub_paper["fields_map"][pdf_page_] = {
                    "title_": title_, "page_": page_,
                    "fields_map_": fields_map_,
                }

            progress_callback(msg="子论文提取元数据完成")
            logging.info(f"========== 视觉模型子论文提取元数据完成： {sub_paper} ")

        dict_result_add = fields_map
    else:
        for c_ in chunks:
            content = content + "\n" + c_['content_with_weight']
            c_count = c_count + len(c_['content_with_weight'])
            if c_count >= 10000:
                break
        logging.debug(f"do_handle_task current content {content}")
        # dict_result_add = await run_extract(task, chat_model, content, progress_callback)
        dict_result_add = await run_extract_(fields, metadata_type, chat_model, content[:CONTENT_MAX_LEN], progress_callback)
        progress_callback(msg="文本模型提取元数据完成")

    logging.info(f"doc {task['doc_id']} 新抽取的 meta fields {dict_result_add}")
    for key,value in dict_result_add.items():
        if key in key_now and dict_result.get(key,None):
            logging.info(f"do_handle_task doc {task['doc_id']} metadata keyvalue {key}-{value} exists.")
            dict_result[key] = value
        else:
            dict_result[key] = value
    logging.info(f"doc {task['doc_id']} 合并后的 meta fields {dict_result}")

    # 分类标签
    classification_result = await run_classify(task, chat_model, content[:CONTENT_MAX_LEN], progress_callback)

    #抽取失败用空覆盖之前
    classify_result = []
    if classification_result:
        for key, value in classification_result.items():
            if (type(key)==str) and  not key.isdigit():
                logging.info(f"分类信息有误 key{key} value {value}")
                continue
            if (type(key)!=int and type(key)!=str) or type(value)!=str:
                logging.info(f"分类信息有误 key{key} value {value}")
                continue
            classify_obj = {"类别编号":key,"分类类别":value}
            classify_result.append(classify_obj)
    dict_result['分类标签'] =  classify_result
    logging.info(f"do_handle_task doc {task['doc_id']} 合并分类标签后的 meta fields {dict_result}, filter fields {filter_fields_}")

    for c_ in chunks:
        logging.info(f"c_['page_num_int'] == {c_['page_num_int']}")
        page_c_ = list(set(c_['page_num_int']))
        # dict_result["dic_result"] = sub_paper["dic_result"]
        dict_result['sub_paper'] = sub_paper
        if pdf_article_type != "论文集" or (page_c_[0] < sub_paper["main_content_begin"] and pdf_article_type == "论文集"):
            # 将元数据更新到Chunk
            c_['meta_fields'] = dict_result
            for key, value in dict_result.items():
                c_[key] = value
        else:
            # 保存子论文要素至对应分块
            try:
                pages = [int(i) for i in list(sub_paper["fields_map"].keys())]
                # 确保子论文与相应的chunk范围能一一对应
                pages.sort()
                pdf_p_begin, pdf_p_end = find_interval(pages, page_c_[0])
                if pdf_p_begin:
                    sub_paper_dict_result = sub_paper["fields_map"][pdf_p_begin]
                    logging.info(f"pdf_p_begin {pdf_p_begin}; pdf_p_end {pdf_p_end }; pages {pages}; sub_paper_dict_result {sub_paper_dict_result}")
                    c_['meta_fields'] = sub_paper_dict_result["fields_map_"]
                    for key, value in sub_paper_dict_result["fields_map_"].items():
                        c_[key] = value

            except Exception as e:
                logging.info(f"替换为论文集元数据, 子论文对应分块失败： {e}")
                c_['meta_fields'] = dict_result
                for key, value in dict_result.items():
                    c_[key] = value

        c_['filter_fields'] = filter_fields_
        for key,value in filter_fields_.items():
            try:
                if re.search(r'时间|日期', key, re.IGNORECASE):
                    value = format_time(value)
                    if value:
                        value = value[:19]
            except Exception as e:
                logging.info(f"fromtimestamp error {e}")
            c_[key] = value
        c_['limit_range'] = limit_range
        c_['limit_level'] = limit_level
        c_['limit_time'] = limit_time

    #更新元数据到文档
    DocumentService.update_meta_fields(task["doc_id"],  dict_result)
    #DocumentService.update_by_id(task["doc_id"], {"meta_fields": dict_result})

    progress_callback(prog=0.8,msg="完成大模型要素提取和分类打标 ({:.2f}s)".format(timer()-start_ts))
    start_ts = timer()
    doc_store_result = ""
    es_bulk_size = 4
    for b in range(0, len(chunks), es_bulk_size):
        doc_store_result = await trio.to_thread.run_sync(lambda: settings.docStoreConn.insert(chunks[b:b + es_bulk_size], search.index_name(task_tenant_id), task_dataset_id))
        if b % 128 == 0:
            progress_callback(prog=0.8 + 0.1 * (b + 1) / len(chunks), msg="")
        if doc_store_result:
            error_message = f"Insert chunk error: {doc_store_result} chunk example {chunks[b:b+1]}, please check log file and Elasticsearch/Infinity status!"
            progress_callback(-1, msg=error_message)
            raise Exception(error_message)
        chunk_ids = [chunk["id"] for chunk in chunks[:b + es_bulk_size]]
        chunk_ids_str = " ".join(chunk_ids)
        try:
            TaskService.update_chunk_ids(task["id"], chunk_ids_str)
        except DoesNotExist:
            logging.warning(f"do_handle_task update_chunk_ids failed since task {task['id']} is unknown.")
            doc_store_result = await trio.to_thread.run_sync(lambda: settings.docStoreConn.delete({"id": chunk_ids}, search.index_name(task_tenant_id), task_dataset_id))
            return
    progress_callback(prog=0.9,msg="将结果写入到存储数据库({:.2f}s)".format(timer()-start_ts))
    logging.info("Indexing doc({}), page({}-{}), chunks({}), elapsed: {:.2f}".format(task_document_name, task_from_page,
                                                                                     task_to_page, len(chunks),
                                                                                     timer() - start_ts))

    DocumentService.increment_chunk_num(task_doc_id, task_dataset_id, token_count, chunk_count, 0)

    time_cost = timer() - start_ts
    task_time_cost = timer() - task_start_ts
    progress_callback(prog=1.0, msg="Indexing done ({:.2f}s). Task done ({:.2f}s)".format(time_cost, task_time_cost))
    logging.info(
        "Chunk doc({}), page({}-{}), chunks({}), token({}), elapsed:{:.2f}".format(task_document_name, task_from_page,
                                                                                   task_to_page, len(chunks),
                                                                                   token_count, task_time_cost))


async def handle_task():
    async with task_limiter:
        global DONE_TASKS, FAILED_TASKS
        redis_msg, task = await collect()
        if not task:
            await trio.sleep(5)
            logging.info(f"handle_task not collect any task...")
            return
        try:
            logging.info(f"handle_task begin for task {json.dumps(task,ensure_ascii=False)}")
            CURRENT_TASKS[task["id"]] = copy.deepcopy(task)
            await do_handle_task(task)
            DONE_TASKS += 1
            CURRENT_TASKS.pop(task["id"], None)
            logging.info(f"handle_task done for task {json.dumps(task,ensure_ascii=False)}")
        except Exception as e:
            FAILED_TASKS += 1
            CURRENT_TASKS.pop(task["id"], None)
            try:
                err_msg = str(e)
                while isinstance(e, exceptiongroup.ExceptionGroup):
                    e = e.exceptions[0]
                    err_msg += ' -- ' + str(e)
                set_progress(task["id"], prog=-1, msg=f"[Exception]: {err_msg}")
            except Exception:
                logging.exception(f"handle_task got exception for task {json.dumps(task,ensure_ascii=False)},but set error msg {err_msg} failed")
                pass
            logging.exception(f"handle_task got exception for task {json.dumps(task,ensure_ascii=False)}")
        redis_msg.ack()

async def report_status():
    global CONSUMER_NAME, BOOT_AT, PENDING_TASKS, LAG_TASKS, DONE_TASKS, FAILED_TASKS
    REDIS_CONN.sadd("TASKEXE", CONSUMER_NAME)
    redis_lock = RedisDistributedLock("clean_task_executor", lock_value=CONSUMER_NAME, timeout=60)
    while True:
        try:
            now = datetime.now()
            group_info = REDIS_CONN.queue_info(get_svr_queue_name(0), SVR_CONSUMER_GROUP_NAME)
            if group_info is not None:
                PENDING_TASKS = int(group_info.get("pending", 0))
                LAG_TASKS = int(group_info.get("lag", 0))

            current = copy.deepcopy(CURRENT_TASKS)
            heartbeat = json.dumps({
                "name": CONSUMER_NAME,
                "now": now.astimezone().isoformat(timespec="milliseconds"),
                "boot_at": BOOT_AT,
                "pending": PENDING_TASKS,
                "lag": LAG_TASKS,
                "done": DONE_TASKS,
                "failed": FAILED_TASKS,
                "current": current,
            })
            heartbeat_ = json.dumps({
                "name": CONSUMER_NAME,
                "now": now.astimezone().isoformat(timespec="milliseconds"),
                "boot_at": BOOT_AT,
                "pending": PENDING_TASKS,
                "lag": LAG_TASKS,
                "done": DONE_TASKS,
                "failed": FAILED_TASKS,
            })

            REDIS_CONN.zadd(CONSUMER_NAME, heartbeat, now.timestamp())
            logging.debug(f"{CONSUMER_NAME} reported heartbeat: {heartbeat}")
            logging.info(f"{CONSUMER_NAME} reported heartbeat: {heartbeat_}")

            expired = REDIS_CONN.zcount(CONSUMER_NAME, 0, now.timestamp() - 60 * 30)
            if expired > 0:
                REDIS_CONN.zpopmin(CONSUMER_NAME, expired)

            # clean task executor
            if redis_lock.acquire():
                task_executors = REDIS_CONN.smembers("TASKEXE")
                for consumer_name in task_executors:
                    if consumer_name == CONSUMER_NAME:
                        continue
                    expired = REDIS_CONN.zcount(
                        consumer_name, now.timestamp() - WORKER_HEARTBEAT_TIMEOUT, now.timestamp() + 10
                    )
                    if expired == 0:
                        logging.info(f"{consumer_name} expired, removed")
                        REDIS_CONN.srem("TASKEXE", consumer_name)
                        REDIS_CONN.delete(consumer_name)
        except Exception:
            logging.exception("report_status got exception")
        await trio.sleep(30)


def recover_pending_tasks():
    redis_lock = RedisDistributedLock("recover_pending_tasks", lock_value=CONSUMER_NAME, timeout=60)
    svr_queue_names = get_svr_queue_names()
    while not stop_event.is_set():
        try:
            if redis_lock.acquire():
                for queue_name in svr_queue_names:
                    msgs = REDIS_CONN.get_pending_msg(queue=queue_name, group_name=SVR_CONSUMER_GROUP_NAME)
                    msgs = [msg for msg in msgs if msg['consumer'] != CONSUMER_NAME]
                    if len(msgs) == 0:
                        continue

                    task_executors = REDIS_CONN.smembers("TASKEXE")
                    task_executor_set = {t for t in task_executors}
                    msgs = [msg for msg in msgs if msg['consumer'] not in task_executor_set]
                    for msg in msgs:
                        logging.info(
                            f"Recover pending task: {msg['message_id']}, consumer: {msg['consumer']}, "
                            f"time since delivered: {msg['time_since_delivered'] / 1000} s"
                        )
                        REDIS_CONN.requeue_msg(queue_name, SVR_CONSUMER_GROUP_NAME, msg['message_id'])

            stop_event.wait(60)
        except Exception:
            logging.warning("recover_pending_tasks got exception")


async def main():
    logging.info(r"""
  ______           __      ______                     __
 /_  __/___ ______/ /__   / ____/  _____  _______  __/ /_____  _____
  / / / __ `/ ___/ //_/  / __/ | |/_/ _ \/ ___/ / / / __/ __ \/ ___/
 / / / /_/ (__  ) ,<    / /____>  </  __/ /__/ /_/ / /_/ /_/ / /
/_/  \__,_/____/_/|_|  /_____/_/|_|\___/\___/\__,_/\__/\____/_/
    """)
    global FIRST_ARG
    global task_limiter
    global chunk_limiter
    FIRST_ARG = None
    if len(sys.argv) >= 1:
        # 获取第一个参数
        FIRST_ARG = sys.argv[1]
        logging.info(f"参数数量{len(sys.argv)},第一个参数 {FIRST_ARG}")
    logging.info(f'TaskExecutor: RAGFlow version: {get_ragflow_version()},executor {FIRST_ARG},task_limiter {task_limiter},chunk_limiter {chunk_limiter}')
    settings.init_settings()
    print_rag_settings()
    if sys.platform != "win32":
        signal.signal(signal.SIGUSR1, start_tracemalloc_and_snapshot)
        signal.signal(signal.SIGUSR2, stop_tracemalloc)
    TRACE_MALLOC_ENABLED = int(os.environ.get('TRACE_MALLOC_ENABLED', "0"))
    if TRACE_MALLOC_ENABLED:
        start_tracemalloc_and_snapshot(None, None)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    threading.Thread(name="RecoverPendingTask", target=recover_pending_tasks).start()

    async with trio.open_nursery() as nursery:
        nursery.start_soon(report_status)
        while not stop_event.is_set():
            async with task_limiter:
                logging.info(f"task_limiter {task_limiter}")
                #await handle_task()
                nursery.start_soon(handle_task)
    logging.error("BUG!!! You should not reach here!!!")

if __name__ == "__main__":
    faulthandler.enable()
    initRootLogger(CONSUMER_NAME)
    trio.run(main)
