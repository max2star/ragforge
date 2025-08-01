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

from flask import request
from flask_login import login_required, current_user
from api.db.services.dialog_service import DialogService
from api.db import StatusEnum
from api.db.services.llm_service import TenantLLMService
from api.db.services.knowledgebase_service import KnowledgebaseService
from api.db.services.user_service import TenantService, UserTenantService
from api import settings
from api.utils.api_utils import server_error_response, get_data_error_result, validate_request
from api.utils import get_uuid
from api.utils.api_utils import get_json_result


@manager.route('/set', methods=['POST'])  # noqa: F821
@login_required
def set_dialog():
    req = request.json
    dialog_id = req.get("dialog_id")
    name = req.get("name", "New Dialog")
    description = req.get("description", "A helpful dialog")
    icon = req.get("icon", "")
    top_n = req.get("top_n", 6)
    top_k = req.get("top_k", 1024)
    rerank_id = req.get("rerank_id", "")
    if not rerank_id:
        req["rerank_id"] = ""
    similarity_threshold = req.get("similarity_threshold", 0.1)
    vector_similarity_weight = req.get("vector_similarity_weight", 0.3)
    llm_setting = req.get("llm_setting", {})
    default_prompt = {
        "system": """你是一个智能助手，请总结知识库的内容来回答问题，请列举知识库中的数据详细回答。当所有知识库内容都与问题无关时，你的回答必须包括"知识库中未找到您要的答案！"这句话。回答需要考虑聊天历史。
以下是知识库：
{knowledge}
以上是知识库。""",
        "prologue": "您好，我是您的助手小樱，长得可爱又善良，can I help you?",
        "parameters": [
            {"key": "knowledge", "optional": False}
        ],
        "empty_response": "Sorry! 知识库中未找到相关内容！"
    }
    prompt_config = req.get("prompt_config", default_prompt)

    # 兜底，防止为 null
    if similarity_threshold is None:
        similarity_threshold = 0.2
    if vector_similarity_weight is None:
        vector_similarity_weight = 0.3
    req["similarity_threshold"] = similarity_threshold
    req["vector_similarity_weight"] = vector_similarity_weight

    # 确保 prompt_config 有必要的键
    if not isinstance(prompt_config, dict):
        prompt_config = default_prompt
    else:
        # 确保有 system 键
        if "system" not in prompt_config or not prompt_config["system"]:
            prompt_config["system"] = default_prompt["system"]
        
        # 确保有其他必要的键
        if "prologue" not in prompt_config:
            prompt_config["prologue"] = default_prompt["prologue"]
        if "parameters" not in prompt_config:
            prompt_config["parameters"] = default_prompt["parameters"]
        if "empty_response" not in prompt_config:
            prompt_config["empty_response"] = default_prompt["empty_response"]

    # 检查必需参数是否在 system 中使用
    for p in prompt_config["parameters"]:
        if p["optional"]:
            continue
        if prompt_config["system"].find("{%s}" % p["key"]) < 0:
            return get_data_error_result(
                message="Parameter '{}' is not used".format(p["key"]))

    try:
        e, tenant = TenantService.get_by_id(current_user.id)
        if not e:
            return get_data_error_result(message="Tenant not found!")

        for kb_id in req.get("kb_ids",[]):
            if not KnowledgebaseService.accessible(kb_id, current_user.id):
                return get_json_result(
                    data=False,
                    message=f'No authorization for kb_id {kb_id}.',
                    code=settings.RetCode.AUTHENTICATION_ERROR
                )
        kbs = KnowledgebaseService.get_by_ids(req.get("kb_ids", []))
        embd_ids = [TenantLLMService.split_model_name_and_factory(kb.embd_id)[0] for kb in kbs]  # remove vendor suffix for comparison
        embd_count = len(set(embd_ids))
        if embd_count > 1:
            return get_data_error_result(message=f'Datasets use different embedding models: {[kb.embd_id for kb in kbs]}"')

        llm_id = req.get("llm_id", tenant.llm_id)
        if not dialog_id:
            dia = {
                "id": get_uuid(),
                "tenant_id": current_user.id,
                "name": name,
                "kb_ids": req.get("kb_ids", []),
                "description": description,
                "llm_id": llm_id,
                "llm_setting": llm_setting,
                "prompt_config": prompt_config,
                "top_n": top_n,
                "top_k": top_k,
                "rerank_id": rerank_id,
                "similarity_threshold": similarity_threshold,
                "vector_similarity_weight": vector_similarity_weight,
                "icon": icon
            }
            if not DialogService.save(**dia):
                return get_data_error_result(message="Fail to new a dialog!")
            return get_json_result(data=dia)
        else:
            del req["dialog_id"]
            if "kb_names" in req:
                del req["kb_names"]
            if not DialogService.update_by_id(dialog_id, req):
                return get_data_error_result(message="Dialog not found!")
            e, dia = DialogService.get_by_id(dialog_id)
            if not e:
                return get_data_error_result(message="Fail to update a dialog!")
            dia = dia.to_dict()
            dia.update(req)
            dia["kb_ids"], dia["kb_names"] = get_kb_names(dia["kb_ids"])
            return get_json_result(data=dia)
    except Exception as e:
        return server_error_response(e)


@manager.route('/get', methods=['GET'])  # noqa: F821
@login_required
def get():
    dialog_id = request.args["dialog_id"]
    try:

        if not DialogService.accessible(dialog_id,current_user.id):
            return get_json_result(
                data=False,
                message='No authorization.',
                code=settings.RetCode.AUTHENTICATION_ERROR
            )

        e, dia = DialogService.get_by_id(dialog_id)
        if not e:
            return get_data_error_result(message="Dialog not found!")
        dia = dia.to_dict()
        dia["kb_ids"], dia["kb_names"] = get_kb_names(dia["kb_ids"])
        return get_json_result(data=dia)
    except Exception as e:
        return server_error_response(e)


def get_kb_names(kb_ids):
    ids, nms = [], []
    for kid in kb_ids:
        e, kb = KnowledgebaseService.get_by_id(kid)
        if not e or kb.status != StatusEnum.VALID.value:
            continue
        ids.append(kid)
        nms.append(kb.name)
    return ids, nms


@manager.route('/list', methods=['GET'])  # noqa: F821
@login_required
def list_dialogs():
    try:
        diags = DialogService.query(
            tenant_id=current_user.id,
            status=StatusEnum.VALID.value,
            reverse=True,
            order_by=DialogService.model.create_time)
        diags = [d.to_dict() for d in diags]
        for d in diags:
            d["kb_ids"], d["kb_names"] = get_kb_names(d["kb_ids"])
        return get_json_result(data=diags)
    except Exception as e:
        return server_error_response(e)


@manager.route('/rm', methods=['POST'])  # noqa: F821
@login_required
@validate_request("dialog_ids")
def rm():
    req = request.json
    dialog_list=[]
    tenants = UserTenantService.query(user_id=current_user.id)
    try:
        for id in req["dialog_ids"]:
            for tenant in tenants:
                if DialogService.query(tenant_id=tenant.tenant_id, id=id):
                    break
            else:
                return get_json_result(
                    data=False, message='Only owner of dialog authorized for this operation.',
                    code=settings.RetCode.OPERATING_ERROR)
            dialog_list.append({"id": id,"status":StatusEnum.INVALID.value})
        #以标志位的方式隐藏删除
        DialogService.update_many_by_id(dialog_list)
        return get_json_result(data=True)
    except Exception as e:
        return server_error_response(e)
