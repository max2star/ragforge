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

from api import settings
from api.db import UserTenantRole, StatusEnum
from api.db.db_models import UserTenant
from api.db.services.user_service import UserTenantService, UserService

from api.utils import get_uuid, delta_seconds
from api.utils.api_utils import get_json_result, validate_request, server_error_response, get_data_error_result


@manager.route("/<tenant_id>/user/list", methods=["GET"])  # noqa: F821
@login_required
def user_list(tenant_id):
    if current_user.id != tenant_id:
        return get_json_result(
            data=False,
            message='No authorization.',
            code=settings.RetCode.AUTHENTICATION_ERROR
        )

    try:
        users = UserTenantService.get_by_tenant_id(tenant_id)
        for u in users:
            u["delta_seconds"] = delta_seconds(str(u["update_date"]))
        return get_json_result(data=users)
    except Exception as e:
        return server_error_response(e)


@manager.route('/<tenant_id>/user', methods=['POST'])  # noqa: F821
@login_required
@validate_request("email")
def create(tenant_id):
    if current_user.id != tenant_id:
        return get_json_result(
            data=False,
            message='No authorization.',
            code=settings.RetCode.AUTHENTICATION_ERROR
        )

    req = request.json
    invite_user_email = req["email"]
    invite_users = UserService.query(email=invite_user_email)
    if not invite_users:
        return get_data_error_result(message=f"User for email {invite_user_email} not found.")

    user_id_to_invite = invite_users[0].id
    user_tenants = UserTenantService.query(user_id=user_id_to_invite, tenant_id=tenant_id)
    if user_tenants:
        user_tenant_role = user_tenants[0].role
        if user_tenant_role == UserTenantRole.NORMAL:
            return get_data_error_result(message=f"{invite_user_email} is already in the team.")
        if user_tenant_role == UserTenantRole.OWNER:
            return get_data_error_result(message=f"{invite_user_email} is the owner of the team.")
        return get_data_error_result(message=f"{invite_user_email} is in the team, but the role: {user_tenant_role} is invalid.")

    UserTenantService.save(
        id=get_uuid(),
        user_id=user_id_to_invite,
        tenant_id=tenant_id,
        invited_by=current_user.id,
        role=UserTenantRole.INVITE,
        status=StatusEnum.VALID.value)

    usr = invite_users[0].to_dict()
    usr = {k: v for k, v in usr.items() if k in ["id", "avatar", "email", "nickname"]}

    return get_json_result(data=usr)


@manager.route('/<tenant_id>/user/<user_id>', methods=['DELETE'])  # noqa: F821
@login_required
def rm(tenant_id, user_id):
    #如果操作的空间不是自己，则必须用户是自己
    #如果操作的空间是自己，则用户可以不是自己
    if current_user.id != tenant_id and current_user.id != user_id:
        return get_json_result(
            data=False,
            message='No authorization.',
            code=settings.RetCode.AUTHENTICATION_ERROR
        )

    #TODO 自己可以把自己从自己空间里删除吗？
    if current_user.id == tenant_id and current_user.id == user_id:
        return get_json_result(
            data=False,
            message=f'No authorization,the user {current_user.id} is delting itself from the tenant.',
            code=settings.RetCode.AUTHENTICATION_ERROR
        )

    try:
        UserTenantService.filter_delete([UserTenant.tenant_id == tenant_id, UserTenant.user_id == user_id])
        return get_json_result(data=True)
    except Exception as e:
        return server_error_response(e)


@manager.route("/list", methods=["GET"])  # noqa: F821
@login_required
def tenant_list():
    try:
        users = UserTenantService.get_tenants_by_user_id(current_user.id)
        for u in users:
            u["delta_seconds"] = delta_seconds(str(u["update_date"]))
        return get_json_result(data=users)
    except Exception as e:
        return server_error_response(e)


@manager.route("/agree/<tenant_id>", methods=["PUT"])  # noqa: F821
@login_required
def agree(tenant_id):
    try:
        #UserTenant.user_id 只能是自己，限制了只能同意对自己的邀约请求
        UserTenantService.filter_update([UserTenant.tenant_id == tenant_id, UserTenant.user_id == current_user.id], {"role": UserTenantRole.NORMAL})
        return get_json_result(data=True)
    except Exception as e:
        return server_error_response(e)
