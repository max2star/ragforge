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
import os
import sys
import logging
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from flask import Blueprint, Flask, request
from werkzeug.wrappers.request import Request
from flask_cors import CORS
from flasgger import Swagger
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
import traceback

from api.db import StatusEnum
from api.db.db_models import close_connection, DB
from api.db.services import UserService
from api.utils import CustomJSONEncoder, commands

from flask_session import Session
from flask_login import LoginManager
from api import settings
from api.utils.api_utils import server_error_response, get_json_result
from api.constants import API_VERSION

__all__ = ["app"]

Request.json = property(lambda self: self.get_json(force=True, silent=True))

app = Flask(__name__)

# Add this at the beginning of your file to configure Swagger UI
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,  # Include all endpoints
            "model_filter": lambda tag: True,  # Include all models
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/",
}

swagger = Swagger(
    app,
    config=swagger_config,
    template={
        "swagger": "2.0",
        "info": {
            "title": "RAGForge API",
            "description": "",
            "version": "1.0.0",
        },
        "securityDefinitions": {
            "ApiKeyAuth": {"type": "apiKey", "name": "Authorization", "in": "header"}
        },
    },
)

CORS(app, supports_credentials=True, max_age=2592000)
app.url_map.strict_slashes = False
app.json_encoder = CustomJSONEncoder
app.errorhandler(Exception)(server_error_response)

## convince for dev and debug
# app.config["LOGIN_DISABLED"] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["MAX_CONTENT_LENGTH"] = int(
    os.environ.get("MAX_CONTENT_LENGTH", 1024 * 1024 * 1024)
)

Session(app)
login_manager = LoginManager()
login_manager.init_app(app)

commands.register_commands(app)


def search_pages_path(pages_dir):
    app_path_list = [
        path for path in pages_dir.glob("*_app.py") if not path.name.startswith(".")
    ]
    api_path_list = [
        path for path in pages_dir.glob("*sdk/*.py") if not path.name.startswith(".")
    ]
    app_path_list.extend(api_path_list)
    return app_path_list


def register_page(page_path):
    path = f"{page_path}"

    page_name = page_path.stem.rstrip("_app")
    module_name = ".".join(
        page_path.parts[page_path.parts.index("api"): -1] + (page_name,)
    )

    spec = spec_from_file_location(module_name, page_path)
    page = module_from_spec(spec)
    page.app = app
    page.manager = Blueprint(page_name, module_name)
    sys.modules[module_name] = page
    spec.loader.exec_module(page)
    page_name = getattr(page, "page_name", page_name)
    sdk_path = "\\sdk\\" if sys.platform.startswith("win") else "/sdk/"
    url_prefix = (
        f"/api/{API_VERSION}" if sdk_path in path else f"/{API_VERSION}/{page_name}"
    )

    app.register_blueprint(page.manager, url_prefix=url_prefix)
    return url_prefix


pages_dir = [
    Path(__file__).parent,
    Path(__file__).parent.parent / "api" / "apps",
    Path(__file__).parent.parent / "api" / "apps" / "sdk",
]

client_urls_prefix = [
    register_page(path) for dir in pages_dir for path in search_pages_path(dir)
]


@login_manager.request_loader
def load_user(web_request):
    # 白名单：未登录也能访问的接口
    public_paths = [
        "/v1/system/config",
        "/v1/user/login",
        "/v1/user/register",
        "/health",
        "/debug",
    ]
    
    # 特殊处理：GET 请求的 interface/config 可以公开访问
    if web_request.path == "/v1/system/interface/config" and web_request.method == "GET":
        logging.debug(f"Allowing public GET access to: {web_request.path}")
        return None
    
    # 检查是否是公开路径
    if web_request.path in public_paths:
        logging.debug(f"Allowing public access to: {web_request.path}")
        return None
    
    # 检查数据库连接是否可用
    if DB is None:
        logging.error("Database connection not available")
        return None

    jwt = Serializer(secret_key=settings.SECRET_KEY)
    authorization = web_request.headers.get("Authorization")

    # 添加请求路径日志
    logging.debug(f"Request path: {web_request.path}, Authorization: {'Present' if authorization else 'Missing'}")

    if authorization:
        try:
            access_token = str(jwt.loads(authorization))

            # 添加重试机制处理数据库连接问题
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    user = UserService.query(
                        access_token=access_token, status=StatusEnum.VALID.value
                    )
                    if user:
                        logging.debug(f"User authenticated: {user[0].id}")
                        return user[0]
                    else:
                        logging.warning(f"User not found for access_token: {access_token[:10]}...")
                        return None
                except Exception as db_error:
                    if "closed cursor" in str(db_error).lower() or "connection" in str(db_error).lower():
                        logging.warning(f"Database connection issue on attempt {attempt + 1}: {db_error}")
                        if attempt < max_retries - 1:
                            # 尝试重新建立连接
                            try:
                                close_connection()
                            except:
                                pass
                            continue
                        else:
                            logging.error(f"Database connection failed after {max_retries} attempts")
                            return None
                    else:
                        # 非连接相关错误，直接抛出
                        raise db_error

        except Exception as e:
            logging.error(f"load_user got exception {e}, authorization: {authorization[:20]}...")
            logging.error(f"Full traceback: {traceback.format_exc()}")
            return None
    else:
        logging.warning(f"No Authorization header provided for path: {web_request.path}")
        return None


# 配置登录管理器的未授权处理
@login_manager.unauthorized_handler
def unauthorized():
    """处理未授权访问"""
    logging.warning(f"Unauthorized access attempt: {request.method} {request.url}")
    logging.warning(f"Request headers: {dict(request.headers)}")

    return get_json_result(
        data=False,
        message="未授权访问，请提供有效的认证信息",
        code=401
    ), 401


@app.teardown_request
def _db_close(exc):
    try:
        close_connection()
    except Exception as e:
        # 记录数据库关闭错误但不影响响应
        logging.warning(f"Database close warning: {e}")


# 添加数据库连接错误处理
@app.errorhandler(Exception)
def handle_database_errors(error):
    """处理数据库相关错误"""
    error_str = str(error).lower()
    if any(keyword in error_str for keyword in ['closed cursor', 'connection', 'database']):
        logging.error(f"Database error: {error}")
        logging.error(f"Full traceback: {traceback.format_exc()}")

        # 尝试清理连接
        try:
            close_connection()
        except:
            pass

        return get_json_result(
            data=False,
            message="数据库连接错误，请稍后重试",
            code=500
        ), 500

    # 对于非数据库错误，使用原有的错误处理
    return server_error_response(error)


# 添加401错误处理器
@app.errorhandler(401)
def unauthorized_error(error):
    """处理401未授权错误"""
    logging.error(f"401 Unauthorized: {request.method} {request.url}")
    logging.error(f"Request headers: {dict(request.headers)}")

    return get_json_result(
        data=False,
        message="认证失败，请检查您的登录凭据",
        code=401
    ), 401


# 在现有的错误处理器之后添加
@app.errorhandler(405)
def method_not_allowed(error):
    """处理405方法不允许错误"""
    logging.error(f"405 Method Not Allowed: {request.method} {request.url}")
    logging.error(f"Available methods for this endpoint: {list(error.valid_methods) if hasattr(error, 'valid_methods') else 'Unknown'}")
    logging.error(f"Request headers: {dict(request.headers)}")

    # 提供更友好的错误信息
    available_methods = list(error.valid_methods) if hasattr(error, 'valid_methods') else []

    return get_json_result(
        data=False,
        message=f"HTTP方法 {request.method} 不被支持。该端点支持的方法: {available_methods}",
        code=405
    ), 405

@app.errorhandler(404)
def not_found(error):
    """处理404未找到错误"""
    logging.error(f"404 Not Found: {request.method} {request.url}")
    return get_json_result(
        data=False,
        message=f"Endpoint not found: {request.method} {request.path}",
        code=404
    ), 404

# 添加请求日志中间件
@app.before_request
def log_request_info():
    """记录每个请求的详细信息"""
    logging.debug(f"Request: {request.method} {request.url}")
    if request.is_json and request.get_json():
        logging.debug(f"Request JSON: {request.get_json()}")

# 添加认证调试端点
@app.route('/debug/auth', methods=['GET'])
def debug_auth():
    """调试认证状态"""
    try:
        from flask_login import current_user
        auth_header = request.headers.get('Authorization')

        debug_info = {
            "has_auth_header": bool(auth_header),
            "auth_header_preview": auth_header[:20] + "..." if auth_header else None,
            "is_authenticated": current_user.is_authenticated if hasattr(current_user, 'is_authenticated') else False,
            "user_id": getattr(current_user, 'id', None) if hasattr(current_user, 'id') else None,
            "request_path": request.path,
            "request_method": request.method
        }

        return get_json_result(data=debug_info)
    except Exception as e:
        return get_json_result(
            data={"error": str(e)},
            message="认证调试失败",
            code=500
        ), 500

# 仅在开发环境中启用
if app.debug:
    @app.route('/debug/routes', methods=['GET'])
    def list_routes():
        """列出所有可用的路由（仅调试用）"""
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'rule': rule.rule
            })

        # 按路径排序
        routes.sort(key=lambda x: x['rule'])

        return get_json_result(data=routes)
    @app.route('/debug/route_check', methods=['GET'])
    def check_route():
        """检查特定路由的配置"""
        path = request.args.get('path', '')
        method = request.args.get('method', 'GET')

        matching_routes = []
        for rule in app.url_map.iter_rules():
            if path in rule.rule:
                matching_routes.append({
                    'endpoint': rule.endpoint,
                    'methods': list(rule.methods),
                    'rule': rule.rule,
                    'supports_method': method in rule.methods
                })

        return get_json_result(data={
            'path': path,
            'method': method,
            'matching_routes': matching_routes
        })


# 添加健康检查端点
@app.route('/health/db', methods=['GET'])
def db_health_check():
    """数据库健康检查"""
    try:
        # 简单的数据库查询测试
        UserService.query(limit=1)
        return get_json_result(data={"status": "healthy", "message": "数据库连接正常"})
    except Exception as e:
        logging.error(f"Database health check failed: {e}")
        return get_json_result(
            data={"status": "unhealthy", "message": f"数据库连接异常: {str(e)}"},
            code=500
        ), 500

# 添加认证健康检查
@app.route('/health/auth', methods=['GET'])
def auth_health_check():
    """认证系统健康检查"""
    try:
        # 测试JWT序列化器
        jwt = Serializer(secret_key=settings.SECRET_KEY)
        test_token = jwt.dumps("test")
        decoded = jwt.loads(test_token)

        return get_json_result(data={
            "status": "healthy",
            "message": "认证系统正常",
            "jwt_test": "passed"
        })
    except Exception as e:
        logging.error(f"Auth health check failed: {e}")
        return get_json_result(
            data={"status": "unhealthy", "message": f"认证系统异常: {str(e)}"},
            code=500
        ), 500
