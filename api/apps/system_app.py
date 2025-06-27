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
import logging
import os
from datetime import datetime
import json

from flask import request
from flask_login import login_required, current_user

from api.db.db_models import APIToken
from api.db.services.api_service import APITokenService
from api.db.services.knowledgebase_service import KnowledgebaseService
from api.db.services.user_service import UserTenantService
from api import settings
from api.utils import current_timestamp, datetime_format
from api.utils.api_utils import (
    get_json_result,
    get_data_error_result,
    server_error_response,
    generate_confirmation_token,
)
from api.versions import get_ragflow_version
from rag.utils.storage_factory import STORAGE_IMPL, STORAGE_IMPL_TYPE
from timeit import default_timer as timer

from rag.utils.redis_conn import REDIS_CONN

@manager.route("/version", methods=["GET"])  # noqa: F821
@login_required
def version():
    """
    Get the current version of the application.
    ---
    tags:
      - System
    security:
      - ApiKeyAuth: []
    responses:
      200:
        description: Version retrieved successfully.
        schema:
          type: object
          properties:
            version:
              type: string
              description: Version number.
    """
    return get_json_result(data=get_ragflow_version())


@manager.route("/status", methods=["GET"])  # noqa: F821
@login_required
def status():
    """
    Get the system status.
    ---
    tags:
      - System
    security:
      - ApiKeyAuth: []
    responses:
      200:
        description: System is operational.
        schema:
          type: object
          properties:
            es:
              type: object
              description: Elasticsearch status.
            storage:
              type: object
              description: Storage status.
            database:
              type: object
              description: Database status.
      503:
        description: Service unavailable.
        schema:
          type: object
          properties:
            error:
              type: string
              description: Error message.
    """
    res = {}
    st = timer()
    try:
        res["doc_engine"] = settings.docStoreConn.health()
        res["doc_engine"]["elapsed"] = "{:.1f}".format((timer() - st) * 1000.0)
    except Exception as e:
        res["doc_engine"] = {
            "type": "unknown",
            "status": "red",
            "elapsed": "{:.1f}".format((timer() - st) * 1000.0),
            "error": str(e),
        }

    st = timer()
    try:
        STORAGE_IMPL.health()
        res["storage"] = {
            "storage": STORAGE_IMPL_TYPE.lower(),
            "status": "green",
            "elapsed": "{:.1f}".format((timer() - st) * 1000.0),
        }
    except Exception as e:
        res["storage"] = {
            "storage": STORAGE_IMPL_TYPE.lower(),
            "status": "red",
            "elapsed": "{:.1f}".format((timer() - st) * 1000.0),
            "error": str(e),
        }

    st = timer()
    try:
        KnowledgebaseService.get_by_id("x")
        res["database"] = {
            "database": settings.DATABASE_TYPE.lower(),
            "status": "green",
            "elapsed": "{:.1f}".format((timer() - st) * 1000.0),
        }
    except Exception as e:
        res["database"] = {
            "database": settings.DATABASE_TYPE.lower(),
            "status": "red",
            "elapsed": "{:.1f}".format((timer() - st) * 1000.0),
            "error": str(e),
        }

    st = timer()
    try:
        if not REDIS_CONN.health():
            raise Exception("Lost connection!")
        res["redis"] = {
            "status": "green",
            "elapsed": "{:.1f}".format((timer() - st) * 1000.0),
        }
    except Exception as e:
        res["redis"] = {
            "status": "red",
            "elapsed": "{:.1f}".format((timer() - st) * 1000.0),
            "error": str(e),
        }

    task_executor_heartbeats = {}
    try:
        task_executors = REDIS_CONN.smembers("TASKEXE")
        now = datetime.now().timestamp()
        for task_executor_id in task_executors:
            heartbeats = REDIS_CONN.zrangebyscore(task_executor_id, now - 60*30, now)
            heartbeats = [json.loads(heartbeat) for heartbeat in heartbeats]
            task_executor_heartbeats[task_executor_id] = heartbeats
    except Exception:
        logging.exception("get task executor heartbeats failed!")
    res["task_executor_heartbeats"] = task_executor_heartbeats

    return get_json_result(data=res)


@manager.route("/new_token", methods=["POST"])  # noqa: F821
@login_required
def new_token():
    """
    Generate a new API token.
    ---
    tags:
      - API Tokens
    security:
      - ApiKeyAuth: []
    parameters:
      - in: query
        name: name
        type: string
        required: false
        description: Name of the token.
    responses:
      200:
        description: Token generated successfully.
        schema:
          type: object
          properties:
            token:
              type: string
              description: The generated API token.
    """
    try:
        tenants = UserTenantService.query(user_id=current_user.id)
        if not tenants:
            return get_data_error_result(message="Tenant not found!")

        tenant_id = [tenant for tenant in tenants if tenant.role == 'owner'][0].tenant_id
        obj = {
            "tenant_id": tenant_id,
            "token": generate_confirmation_token(tenant_id),
            "beta": generate_confirmation_token(generate_confirmation_token(tenant_id)).replace("ragflow-", "")[:32],
            "create_time": current_timestamp(),
            "create_date": datetime_format(datetime.now()),
            "update_time": None,
            "update_date": None,
        }

        if not APITokenService.save(**obj):
            return get_data_error_result(message="Fail to new a dialog!")

        return get_json_result(data=obj)
    except Exception as e:
        return server_error_response(e)


@manager.route("/token_list", methods=["GET"])  # noqa: F821
@login_required
def token_list():
    """
    List all API tokens for the current user.
    ---
    tags:
      - API Tokens
    security:
      - ApiKeyAuth: []
    responses:
      200:
        description: List of API tokens.
        schema:
          type: object
          properties:
            tokens:
              type: array
              items:
                type: object
                properties:
                  token:
                    type: string
                    description: The API token.
                  name:
                    type: string
                    description: Name of the token.
                  create_time:
                    type: string
                    description: Token creation time.
    """
    try:
        tenants = UserTenantService.query(user_id=current_user.id)
        if not tenants:
            return get_data_error_result(message="Tenant not found!")

        tenant_id = [tenant for tenant in tenants if tenant.role == 'owner'][0].tenant_id
        objs = APITokenService.query(tenant_id=tenant_id)
        objs = [o.to_dict() for o in objs]
        for o in objs:
            if not o["beta"]:
                o["beta"] = generate_confirmation_token(generate_confirmation_token(tenants[0].tenant_id)).replace("ragflow-", "")[:32]
                APITokenService.filter_update([APIToken.tenant_id == tenant_id, APIToken.token == o["token"]], o)
        return get_json_result(data=objs)
    except Exception as e:
        return server_error_response(e)


@manager.route("/token/<token>", methods=["DELETE"])  # noqa: F821
@login_required
def rm(token):
    """
    Remove an API token.
    ---
    tags:
      - API Tokens
    security:
      - ApiKeyAuth: []
    parameters:
      - in: path
        name: token
        type: string
        required: true
        description: The API token to remove.
    responses:
      200:
        description: Token removed successfully.
        schema:
          type: object
          properties:
            success:
              type: boolean
              description: Deletion status.
    """
    APITokenService.filter_delete(
        [APIToken.tenant_id == current_user.id, APIToken.token == token]
    )
    return get_json_result(data=True)


@manager.route('/config', methods=['GET'])  # noqa: F821
#@login_required
def get_config():
    """
    Get system configuration.
    ---
    tags:
        - System
    responses:
        200:
            description: Return system configuration
            schema:
                type: object
                properties:
                    registerEnable:
                        type: integer 0 means disabled, 1 means enabled
                        description: Whether user registration is enabled
    """
    return get_json_result(data={
        "registerEnabled": settings.REGISTER_ENABLED
    })


@manager.route('/interface/config', methods=['GET'])  # noqa: F821
#@login_required
def get_interface_config():
    """
    Get interface configuration including logos and login page settings.
    ---
    tags:
        - System
    responses:
        200:
            description: Return interface configuration
            schema:
                type: object
                properties:
                    logo:
                        type: string
                        description: Base64 encoded logo image
                    favicon:
                        type: string
                        description: Base64 encoded favicon image
                    login_logo:
                        type: string
                        description: Base64 encoded login page logo
                    login_welcome_text:
                        type: string
                        description: Welcome text for login page
                    app_name:
                        type: string
                        description: Application name displayed in header
                    login_title:
                        type: string
                        description: Main title for login page
    """
    try:
        # 从存储中获取界面配置
        config = {}
        
        # 尝试从存储中读取配置
        try:
            if STORAGE_IMPL.obj_exist("system", "interface_config.json"):
                config_data = STORAGE_IMPL.get("system", "interface_config.json")
                config = json.loads(config_data.decode('utf-8'))
        except Exception as e:
            logging.warning(f"Failed to load interface config from storage: {e}")
        
        # 返回默认配置或已保存的配置
        return get_json_result(data={
            "logo": config.get("logo", ""),
            "favicon": config.get("favicon", ""),
            "login_logo": config.get("login_logo", ""),
            "login_welcome_text": config.get("login_welcome_text", "欢迎使用 RAGFlow\n智能知识管理与AI助手平台"),
            "app_name": config.get("app_name", "RAGFlow"),
            "login_title": config.get("login_title", "欢迎使用 RAGFlow")
        })
    except Exception as e:
        return server_error_response(e)


@manager.route('/interface/config', methods=['POST'])  # noqa: F821
@login_required
def save_interface_config():
    """
    Save interface configuration including logos and login page settings.
    ---
    tags:
        - System
    security:
        - ApiKeyAuth: []
    parameters:
        - in: body
          name: body
          description: Interface configuration to save
          required: true
          schema:
            type: object
            properties:
              logo:
                type: string
                description: Base64 encoded logo image
              favicon:
                type: string
                description: Base64 encoded favicon image
              login_logo:
                type: string
                description: Base64 encoded login page logo
              login_welcome_text:
                type: string
                description: Welcome text for login page
              app_name:
                type: string
                description: Application name displayed in header
              login_title:
                type: string
                description: Main title for login page
    responses:
        200:
            description: Configuration saved successfully
    """
    try:
        request_data = request.json
        
        # 验证输入数据
        config = {
            "logo": request_data.get("logo", ""),
            "favicon": request_data.get("favicon", ""),
            "login_logo": request_data.get("login_logo", ""),
            "login_welcome_text": request_data.get("login_welcome_text", "欢迎使用 RAGFlow\n智能知识管理与AI助手平台"),
            "app_name": request_data.get("app_name", "RAGFlow"),
            "login_title": request_data.get("login_title", "欢迎使用 RAGFlow")
        }
        
        # 保存配置到存储
        config_json = json.dumps(config, ensure_ascii=False)
        STORAGE_IMPL.put("system", "interface_config.json", config_json.encode('utf-8'))
        
        # 如果上传了新的logo，保存到静态文件目录
        if config["logo"]:
            try:
                import base64
                logo_data = base64.b64decode(config["logo"].split(',')[1] if ',' in config["logo"] else config["logo"])
                logo_path = os.path.join(settings.STATIC_FOLDER, "logo.png")
                with open(logo_path, 'wb') as f:
                    f.write(logo_data)
            except Exception as e:
                logging.warning(f"Failed to save logo file: {e}")
        
        # 如果上传了新的favicon，保存到静态文件目录
        if config["favicon"]:
            try:
                import base64
                favicon_data = base64.b64decode(config["favicon"].split(',')[1] if ',' in config["favicon"] else config["favicon"])
                favicon_path = os.path.join(settings.STATIC_FOLDER, "favicon.ico")
                with open(favicon_path, 'wb') as f:
                    f.write(favicon_data)
            except Exception as e:
                logging.warning(f"Failed to save favicon file: {e}")
        
        # 如果上传了新的登录logo，保存到静态文件目录
        if config["login_logo"]:
            try:
                import base64
                login_logo_data = base64.b64decode(config["login_logo"].split(',')[1] if ',' in config["login_logo"] else config["login_logo"])
                login_logo_path = os.path.join(settings.STATIC_FOLDER, "login-logo.png")
                with open(login_logo_path, 'wb') as f:
                    f.write(login_logo_data)
            except Exception as e:
                logging.warning(f"Failed to save login logo file: {e}")
        
        return get_json_result(data=True, message="界面配置保存成功")
    except Exception as e:
        return server_error_response(e)


@manager.route('/interface/upload', methods=['POST'])  # noqa: F821
@login_required
def upload_interface_file():
    """
    Upload interface files (logos, favicons, etc.)
    ---
    tags:
        - System
    security:
        - ApiKeyAuth: []
    parameters:
        - in: formData
          name: file
          type: file
          description: File to upload
          required: true
        - in: formData
          name: type
          type: string
          description: File type (logo, favicon, login_logo)
          required: true
    responses:
        200:
            description: File uploaded successfully
    """
    try:
        if 'file' not in request.files:
            return get_json_result(
                data=False, message='No file part!', code=settings.RetCode.ARGUMENT_ERROR)
        
        file_obj = request.files['file']
        file_type = request.form.get('type', 'logo')
        
        if file_obj.filename == '':
            return get_json_result(
                data=False, message='No file selected!', code=settings.RetCode.ARGUMENT_ERROR)
        
        # 读取文件内容
        file_content = file_obj.read()
        
        # 根据文件类型保存到不同位置
        if file_type == 'logo':
            file_path = os.path.join(settings.STATIC_FOLDER, "logo.png")
        elif file_type == 'favicon':
            file_path = os.path.join(settings.STATIC_FOLDER, "favicon.ico")
        elif file_type == 'login_logo':
            file_path = os.path.join(settings.STATIC_FOLDER, "login-logo.png")
        else:
            return get_json_result(
                data=False, message='Invalid file type!', code=settings.RetCode.ARGUMENT_ERROR)
        
        # 保存文件
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # 转换为base64返回
        import base64
        base64_data = base64.b64encode(file_content).decode('utf-8')
        mime_type = "image/png" if file_type in ['logo', 'login_logo'] else "image/x-icon"
        data_url = f"data:{mime_type};base64,{base64_data}"
        
        return get_json_result(data={
            "url": data_url,
            "filename": file_obj.filename
        })
    except Exception as e:
        return server_error_response(e)
