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
from flask import request, jsonify

from api.db import LLMType
from api.db.services.knowledgebase_service import KnowledgebaseService
from api.db.services.llm_service import LLMBundle
from api import settings
from api.utils.api_utils import validate_request, build_error_result, apikey_required
from rag.app.tag import label_question


@manager.route('/dify/retrieval', methods=['POST'])  # noqa: F821
@apikey_required
@validate_request("knowledge_id", "query")
def retrieval(tenant_id):
    req = request.json
    question = req["query"]
    kb_id = req["knowledge_id"]
    use_kg = req.get("use_kg", False)
    retrieval_setting = req.get("retrieval_setting", {})
    similarity_threshold = float(retrieval_setting.get("score_threshold", 0.0))
    top = int(retrieval_setting.get("top_k", 1024))

    limit_range = tenant_id
    limit_time = str(datetime.datetime.now()).replace("T", " ")[:19]
    limit_level= req.get('limit_level',1)

    try:

        e, kb = KnowledgebaseService.get_by_id(kb_id)
        if not e:
            return build_error_result(message="Knowledgebase not found!", code=settings.RetCode.NOT_FOUND)

        if kb.tenant_id != tenant_id:
            return build_error_result(message=f"Knowledgebase owner {kb.tenant_id} not same with {tenant_id} !", code=settings.RetCode.NOT_FOUND)

        embd_mdl = LLMBundle(kb.tenant_id, LLMType.EMBEDDING.value, llm_name=kb.embd_id)

        ranks = settings.retrievaler.retrieval(
            question,
            embd_mdl,
            kb.tenant_id,
            [kb_id],
            page=1,
            page_size=top,
            similarity_threshold=similarity_threshold,
            vector_similarity_weight=0.3,
            top=top,
            rank_feature=label_question(question, [kb]),
            limit_range = limit_range,
            limit_time = limit_time,
            limit_level =limit_level
        )

        if use_kg:
            ck = settings.kg_retrievaler.retrieval(question,
                                                   [tenant_id],
                                                   [kb_id],
                                                   embd_mdl,
                                                   LLMBundle(kb.tenant_id, LLMType.CHAT))
            if ck["content_with_weight"]:
                ranks["chunks"].insert(0, ck)

        records = []
        for c in ranks["chunks"]:
            c.pop("vector", None)
            records.append({
                "content": c["content_with_weight"],
                "score": c["similarity"],
                "title": c["docnm_kwd"],
                "metadata": {}
            })

        return jsonify({"records": records})
    except Exception as e:
        if str(e).find("not_found") > 0:
            return build_error_result(
                message='No chunk found! Check the chunk status please!',
                code=settings.RetCode.NOT_FOUND
            )
        return build_error_result(message=str(e), code=settings.RetCode.SERVER_ERROR)
