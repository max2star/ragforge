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
from api.db.db_models import UserCanvasVersion, DB
from api.db.services.common_service import CommonService
from peewee import DoesNotExist

class UserCanvasVersionService(CommonService):
    model = UserCanvasVersion
    
    @classmethod
    @DB.connection_context()
    def accessible(cls, version_id, user_id):
        canvas = cls.model.select(
            cls.model.id).join(
            UserCanvas, on=(
                cls.model.user_canvas_id == UserCanvas.id)
        ).where(cls.model.user_canvas_id == version_id, UserCanvas.user_id == user_id).paginate(0, 1)

        canvas = canvas.dicts()
        if not canvas:
            return False
        return True

    @classmethod
    @DB.connection_context()
    def list_by_canvas_id(cls, user_canvas_id):
        try:
            user_canvas_version = cls.model.select(
                *[cls.model.id, 
                cls.model.create_time,
                cls.model.title,
                cls.model.create_date, 
                cls.model.update_date,
                cls.model.user_canvas_id, 
                cls.model.update_time]
            ).where(cls.model.user_canvas_id == user_canvas_id)
            return user_canvas_version
        except DoesNotExist:
            return None
        except Exception:
            return None
    
    @classmethod
    @DB.connection_context()
    def delete_all_versions(cls, user_canvas_id):
        try:
            user_canvas_version = cls.model.select().where(cls.model.user_canvas_id == user_canvas_id).order_by(cls.model.create_time.desc())
            if user_canvas_version.count() > 20:
                for i in range(20, user_canvas_version.count()):
                    cls.delete(user_canvas_version[i].id)
            return True
        except DoesNotExist:
            return None
        except Exception:
            return None



