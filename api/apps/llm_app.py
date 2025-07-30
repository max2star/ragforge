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
import json
import os
from flask import request
from flask_login import login_required, current_user
from api.db.services.llm_service import LLMFactoriesService, TenantLLMService, LLMService
from api import settings
from api.utils.api_utils import server_error_response, get_data_error_result, validate_request
from api.db import StatusEnum, LLMType
from api.db.db_models import TenantLLM
from api.utils.api_utils import get_json_result
from api.utils.file_utils import get_project_base_directory
from rag.llm import EmbeddingModel, ChatModel, RerankModel, CvModel, TTSModel


@manager.route('/factories', methods=['GET'])  # noqa: F821
@login_required
def factories():
    try:
        fac = LLMFactoriesService.get_all()
        fac = [f.to_dict() for f in fac if f.name not in ["Youdao", "FastEmbed", "BAAI"]]
        llms = LLMService.get_all()
        mdl_types = {}
        for m in llms:
            if m.status != StatusEnum.VALID.value:
                continue
            if m.fid not in mdl_types:
                mdl_types[m.fid] = set([])
            mdl_types[m.fid].add(m.model_type)
        for f in fac:
            f["model_types"] = list(mdl_types.get(f["name"], [LLMType.CHAT, LLMType.EMBEDDING, LLMType.RERANK,
                                                              LLMType.IMAGE2TEXT, LLMType.SPEECH2TEXT, LLMType.TTS]))
        return get_json_result(data=fac)
    except Exception as e:
        return server_error_response(e)


@manager.route('/set_api_key', methods=['POST'])  # noqa: F821
@login_required
@validate_request("llm_factory", "api_key")
def set_api_key():
    req = request.json
    # test if api key works
    chat_passed, embd_passed, rerank_passed = False, False, False
    factory = req["llm_factory"]
    msg = ""
    for llm in LLMService.query(fid=factory):
        if not embd_passed and llm.model_type == LLMType.EMBEDDING.value:
            assert factory in EmbeddingModel, f"Embedding model from {factory} is not supported yet."
            mdl = EmbeddingModel[factory](
                req["api_key"], llm.llm_name, base_url=req.get("base_url"))
            try:
                arr, tc = mdl.encode(["Test if the api key is available"])
                if len(arr[0]) == 0:
                    raise Exception("Fail")
                embd_passed = True
            except Exception as e:
                msg += f"\nFail to access embedding model({llm.llm_name}) using this api key." + str(e)
        elif not chat_passed and llm.model_type == LLMType.CHAT.value:
            assert factory in ChatModel, f"Chat model from {factory} is not supported yet."
            mdl = ChatModel[factory](
                req["api_key"], llm.llm_name, base_url=req.get("base_url"))
            try:
                m, tc = mdl.chat(None, [{"role": "user", "content": "Hello! How are you doing!"}],
                                 {"temperature": 0.9, 'max_tokens': 50})
                if m.find("**ERROR**") >= 0:
                    raise Exception(m)
                chat_passed = True
            except Exception as e:
                msg += f"\nFail to access model({llm.llm_name}) using this api key." + str(
                    e)
        elif not rerank_passed and llm.model_type == LLMType.RERANK:
            assert factory in RerankModel, f"Re-rank model from {factory} is not supported yet."
            mdl = RerankModel[factory](
                req["api_key"], llm.llm_name, base_url=req.get("base_url"))
            try:
                arr, tc = mdl.similarity("What's the weather?", ["Is it sunny today?"])
                if len(arr) == 0 or tc == 0:
                    raise Exception("Fail")
                rerank_passed = True
                logging.debug(f'passed model rerank {llm.llm_name}')
            except Exception as e:
                msg += f"\nFail to access model({llm.llm_name}) using this api key." + str(
                    e)
        if any([embd_passed, chat_passed, rerank_passed]):
            msg = ''
            break

    if msg:
        return get_data_error_result(message=msg)

    llm_config = {
        "api_key": req["api_key"],
        "api_base": req.get("base_url", "")
    }
    for n in ["model_type", "llm_name"]:
        if n in req:
            llm_config[n] = req[n]

    for llm in LLMService.query(fid=factory):
        llm_config["max_tokens"] = llm.max_tokens
        result = TenantLLMService.filter_update(
            [TenantLLM.tenant_id == current_user.id,
             TenantLLM.llm_factory == factory,
             TenantLLM.llm_name == llm.llm_name],
            llm_config)
        if not result or result <= 0:
            TenantLLMService.save(
                tenant_id=current_user.id,
                llm_factory=factory,
                llm_name=llm.llm_name,
                model_type=llm.model_type,
                api_key=llm_config["api_key"],
                api_base=llm_config["api_base"],
                max_tokens=llm_config["max_tokens"]
            )

    return get_json_result(data=True)


@manager.route('/add_llm', methods=['POST'])  # noqa: F821
@login_required
@validate_request("llm_factory")
def add_llm():
    req = request.json
    factory = req["llm_factory"]
    api_key = req.get("api_key", "x")
    llm_name = req.get("llm_name")

    def apikey_json(keys):
        nonlocal req
        return json.dumps({k: req.get(k, "") for k in keys})

    if factory == "VolcEngine":
        # For VolcEngine, due to its special authentication method
        # Assemble ark_api_key endpoint_id into api_key
        api_key = apikey_json(["ark_api_key", "endpoint_id"])

    elif factory == "Tencent Hunyuan":
        req["api_key"] = apikey_json(["hunyuan_sid", "hunyuan_sk"])
        return set_api_key()

    elif factory == "Tencent Cloud":
        req["api_key"] = apikey_json(["tencent_cloud_sid", "tencent_cloud_sk"])
        return set_api_key()

    elif factory == "Bedrock":
        # For Bedrock, due to its special authentication method
        # Assemble bedrock_ak, bedrock_sk, bedrock_region
        api_key = apikey_json(["bedrock_ak", "bedrock_sk", "bedrock_region"])

    elif factory == "LocalAI":
        llm_name += "___LocalAI"

    elif factory == "HuggingFace":
        llm_name += "___HuggingFace"

    elif factory == "OpenAI-API-Compatible":
        llm_name += "___OpenAI-API"

    elif factory == "VLLM":
        llm_name += "___VLLM"

    elif factory == "XunFei Spark":
        if req["model_type"] == "chat":
            api_key = req.get("spark_api_password", "")
        elif req["model_type"] == "tts":
            api_key = apikey_json(["spark_app_id", "spark_api_secret", "spark_api_key"])

    elif factory == "BaiduYiyan":
        api_key = apikey_json(["yiyan_ak", "yiyan_sk"])

    elif factory == "Fish Audio":
        api_key = apikey_json(["fish_audio_ak", "fish_audio_refid"])

    elif factory == "Google Cloud":
        api_key = apikey_json(["google_project_id", "google_region", "google_service_account_key"])

    elif factory == "Azure-OpenAI":
        api_key = apikey_json(["api_key", "api_version"])

    llm = {
        "tenant_id": current_user.id,
        "llm_factory": factory,
        "model_type": req["model_type"],
        "llm_name": llm_name,
        "api_base": req.get("api_base", ""),
        "api_key": api_key,
        "max_tokens": req.get("max_tokens")
    }

    msg = ""
    mdl_nm = llm["llm_name"].split("___")[0]
    if llm["model_type"] == LLMType.EMBEDDING.value:
        assert factory in EmbeddingModel, f"Embedding model from {factory} is not supported yet."
        mdl = EmbeddingModel[factory](
            key=llm['api_key'],
            model_name=mdl_nm,
            base_url=llm["api_base"])
        try:
            arr, tc = mdl.encode(["Test if the api key is available"])
            if len(arr[0]) == 0:
                raise Exception("Fail")
        except Exception as e:
            msg += f"\nFail to access embedding model({mdl_nm})." + str(e)
    elif llm["model_type"] == LLMType.CHAT.value:
        assert factory in ChatModel, f"Chat model from {factory} is not supported yet."
        mdl = ChatModel[factory](
            key=llm['api_key'],
            model_name=mdl_nm,
            base_url=llm["api_base"]
        )
        try:
            m, tc = mdl.chat(None, [{"role": "user", "content": "Hello! How are you doing!"}], {
                "temperature": 0.9})
            if not tc and m.find("**ERROR**:") >= 0:
                raise Exception(m)
        except Exception as e:
            msg += f"\nFail to access model({mdl_nm})." + str(
                e)
    elif llm["model_type"] == LLMType.RERANK:
        assert factory in RerankModel, f"RE-rank model from {factory} is not supported yet."
        try:
            mdl = RerankModel[factory](
                key=llm["api_key"],
                model_name=mdl_nm,
                base_url=llm["api_base"]
            )
            arr, tc = mdl.similarity("Hello~ Ragforgeer!", ["Hi, there!", "Ohh, my friend!"])
            if len(arr) == 0:
                raise Exception("Not known.")
        except KeyError:
            msg += f"{factory} dose not support this model({mdl_nm})"
        except Exception as e:
            msg += f"\nFail to access model({mdl_nm})." + str(
                e)
            import traceback
            traceback.print_exc()
            logging.info("Exception {} ,excetion info is {}".format(e,traceback.format_exc()))

    elif llm["model_type"] == LLMType.IMAGE2TEXT.value:
        assert factory in CvModel, f"Image to text model from {factory} is not supported yet."
        mdl = CvModel[factory](
            key=llm["api_key"],
            model_name=mdl_nm,
            base_url=llm["api_base"]
        )
        try:
            with open(os.path.join(get_project_base_directory(), "web/src/assets/yay.jpg"), "rb") as f:
                m, tc = mdl.describe(f.read())
                if not m and not tc:
                    raise Exception(m)
        except Exception as e:
            msg += f"\nFail to access model({mdl_nm})." + str(e)
    elif llm["model_type"] == LLMType.TTS:
        assert factory in TTSModel, f"TTS model from {factory} is not supported yet."
        mdl = TTSModel[factory](
            key=llm["api_key"], model_name=mdl_nm, base_url=llm["api_base"]
        )
        try:
            for resp in mdl.tts("Hello~ Ragforgeer!"):
                pass
        except RuntimeError as e:
            msg += f"\nFail to access model({mdl_nm})." + str(e)
    else:
        # TODO: check other type of models
        pass

    if msg:
        return get_data_error_result(message=msg)

    filter_update_result = TenantLLMService.filter_update(
            [TenantLLM.tenant_id == current_user.id, TenantLLM.llm_factory == factory,
             TenantLLM.llm_name == llm["llm_name"]], llm)
    if not filter_update_result or filter_update_result <= 0:
        TenantLLMService.save(**llm)

    return get_json_result(data=True)


@manager.route('/delete_llm', methods=['POST'])  # noqa: F821
@login_required
@validate_request("llm_factory", "llm_name")
def delete_llm():
    req = request.json
    TenantLLMService.filter_delete(
        [TenantLLM.tenant_id == current_user.id, TenantLLM.llm_factory == req["llm_factory"],
         TenantLLM.llm_name == req["llm_name"]])
    return get_json_result(data=True)


@manager.route('/delete_factory', methods=['POST'])  # noqa: F821
@login_required
@validate_request("llm_factory")
def delete_factory():
    req = request.json
    TenantLLMService.filter_delete(
        [TenantLLM.tenant_id == current_user.id, TenantLLM.llm_factory == req["llm_factory"]])
    return get_json_result(data=True)


@manager.route('/get_llm_config', methods=['GET'])  # noqa: F821
@login_required
@validate_request("llm_factory", "llm_name")
def get_llm_config():
    req = request.args
    factory = req.get("llm_factory")
    llm_name = req.get("llm_name")
    
    try:
        # 获取当前用户的模型配置
        obj = TenantLLMService.query(
            tenant_id=current_user.id,
            llm_factory=factory,
            llm_name=llm_name
        )
        
        if obj:
            config = obj[0].to_dict()
            return get_json_result(data=config)
        else:
            return get_json_result(data=None)
    except Exception as e:
        return server_error_response(e)


@manager.route('/my_llms', methods=['GET'])  # noqa: F821
@login_required
def my_llms():
    try:
        res = {}
        for o in TenantLLMService.get_my_llms(current_user.id):
            if o["llm_factory"] not in res:
                res[o["llm_factory"]] = {
                    "tags": o["tags"],
                    "llm": []
                }
            res[o["llm_factory"]]["llm"].append({
                "type": o["model_type"],
                "name": o["llm_name"],
                "used_token": o["used_tokens"]
            })
        return get_json_result(data=res)
    except Exception as e:
        return server_error_response(e)


@manager.route('/list', methods=['GET'])  # noqa: F821
@login_required
def list_app():
    self_deployed = ["Youdao", "FastEmbed", "BAAI", "Ollama", "Xinference", "LocalAI", "LM-Studio", "GPUStack"]
    weighted = ["Youdao", "FastEmbed", "BAAI"] if settings.LIGHTEN != 0 else []
    model_type = request.args.get("model_type")
    try:
        objs = TenantLLMService.query(tenant_id=current_user.id)
        facts = set([o.to_dict()["llm_factory"] for o in objs if o.api_key])
        llms = []
        #llms = LLMService.get_all()
        #llms = [m.to_dict()
        #        for m in llms if m.status == StatusEnum.VALID.value and m.fid not in weighted]
        #for m in llms:
        #    m["available"] = m["fid"] in facts#or m["llm_name"].lower() == "flag-embedding" or m["fid"] in self_deployed
        #llm_set = set([m["llm_name"] + "@" + m["fid"] for m in llms])
        llm_set = set([])
        for o in objs:
            if o.llm_name + "@" + o.llm_factory in llm_set:
                continue
            llms.append({"llm_name": o.llm_name, "model_type": o.model_type, "fid": o.llm_factory, "available": True})

        res = {}
        for m in llms:
            if model_type and m["model_type"].find(model_type) < 0:
                continue
            if m["fid"] not in res:
                res[m["fid"]] = []
            res[m["fid"]].append(m)

        return get_json_result(data=res)
    except Exception as e:
        return server_error_response(e)


@manager.route('/default_models', methods=['GET'])  # noqa: F821
@login_required
def get_default_models():
    """Get default model configuration"""
    try:
        from api import settings
        from api.db.services.user_service import TenantService
        
        # 优先从数据库获取用户的tenant信息
        tenants = TenantService.get_info_by(current_user.id)
        
        if tenants and len(tenants) > 0:
            tenant = tenants[0]
            # 从数据库获取默认模型配置
            default_models = {
                'models': {
                    'chat_model': tenant.get('llm_id', ''),
                    'embedding_model': tenant.get('embd_id', ''),
                    'rerank_model': tenant.get('rerank_id', ''),
                    'asr_model': tenant.get('asr_id', ''),
                    'image2text_model': tenant.get('img2txt_id', ''),
                    'tts_model': tenant.get('tts_id', '')
                },
                'source': 'database'
            }
        else:
            # 如果数据库中没有tenant信息，则从配置文件获取
            default_models = {
                'models': {
                    'chat_model': settings.CHAT_MDL,
                    'embedding_model': settings.EMBEDDING_MDL,
                    'rerank_model': settings.RERANK_MDL,
                    'asr_model': settings.ASR_MDL,
                    'image2text_model': settings.IMAGE2TEXT_MDL
                },
                'source': 'config'
            }
        
        return get_json_result(data=default_models)
    except Exception as e:
        return server_error_response(e)


@manager.route('/set_default_model', methods=['POST'])  # noqa: F821
@login_required
@validate_request("model_type", "llm_factory", "llm_name")
def set_default_model():
    """Set default model for a specific type"""
    try:
        req = request.json
        model_type = req.get("model_type")  # chat, embedding, rerank, asr, image2text, tts
        llm_factory = req.get("llm_factory")
        llm_name = req.get("llm_name")
        
        # 验证模型是否存在
        obj = TenantLLMService.query(
            tenant_id=current_user.id,
            llm_factory=llm_factory,
            llm_name=llm_name
        )
        
        if not obj:
            return get_json_result(code=settings.RetCode.ARGUMENT_ERROR, 
                                 message=f"Model {llm_name} not found in factory {llm_factory}")
        
        # 获取用户的tenant信息
        from api.db.services.user_service import TenantService
        tenants = TenantService.get_info_by(current_user.id)
        
        if not tenants or len(tenants) == 0:
            return get_json_result(code=settings.RetCode.ARGUMENT_ERROR, 
                                 message="Tenant not found for current user")
        
        tenant = tenants[0]
        tenant_id = tenant.get('tenant_id')
        
        # 构建模型ID（格式：model_name@factory）
        model_id = f"{llm_name}@{llm_factory}"
        
        # 根据模型类型更新对应的字段
        update_data = {}
        if model_type == 'chat':
            update_data['llm_id'] = model_id
        elif model_type == 'embedding':
            update_data['embd_id'] = model_id
        elif model_type == 'rerank':
            update_data['rerank_id'] = model_id
        elif model_type == 'asr':
            update_data['asr_id'] = model_id
        elif model_type == 'image2text':
            update_data['img2txt_id'] = model_id
        elif model_type == 'tts':
            update_data['tts_id'] = model_id
        else:
            return get_json_result(code=settings.RetCode.ARGUMENT_ERROR, 
                                 message=f"Unsupported model type: {model_type}")
        
        # 更新数据库中的tenant信息
        TenantService.update_by_id(tenant_id, update_data)
        
        return get_json_result(data=True, message=f"Default {model_type} model set to {model_id}")
        
    except Exception as e:
        return server_error_response(e)
