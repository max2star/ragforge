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
import operator
from functools import reduce
import logging

from playhouse.pool import PooledMySQLDatabase

from api.utils import current_timestamp, timestamp_to_date

from api.db.db_models import DB, DataBaseModel


@DB.connection_context()
def bulk_insert_into_db(model, data, ignore_conflicts=False):
    """批量插入数据到数据库，支持达梦数据库"""
    if not data:
        return 0

    # 检查是否是达梦数据库
    is_dm_database = _is_dm_database()

    if ignore_conflicts and is_dm_database:
        # 达梦数据库的特殊处理
        return _bulk_insert_dm_with_ignore(model, data)
    elif ignore_conflicts:
        # 其他数据库使用原有逻辑
        try:
            query = model.insert_many(data).on_conflict_ignore()
            return query.execute()
        except Exception as e:
            logging.error(f"批量插入失败，回退到逐条插入: {e}")
            return _bulk_insert_dm_with_ignore(model, data)
    else:
        # 普通插入
        try:
            query = model.insert_many(data)
            return query.execute()
        except Exception as e:
            if is_dm_database:
                logging.warning(f"批量插入失败，使用逐条插入: {e}")
                return _bulk_insert_dm_with_ignore(model, data)
            else:
                raise e

def _is_dm_database():
    """检查是否是达梦数据库"""
    try:
        # 方法1: 检查数据库类型属性
        if hasattr(DB, '_database_type') and DB._database_type == 'dm':
            return True

        # 方法2: 检查数据库类名
        db_class_name = DB.__class__.__name__
        if 'Dm' in db_class_name or 'DM' in db_class_name:
            return True

        # 方法3: 检查连接字符串或驱动
        if hasattr(DB, 'connect_params'):
            connect_params = str(DB.connect_params)
            if 'DM ODBC' in connect_params or 'dm' in connect_params.lower():
                return True

        return False
    except Exception as e:
        logging.debug(f"检查数据库类型时出错: {e}")
        return False

def _bulk_insert_dm_with_ignore(model, data):
    """达梦数据库的批量插入，忽略冲突"""
    success_count = 0
    error_count = 0

    # 逐条插入，忽略重复键错误
    for item in data:
        try:
            model.create(**item)
            success_count += 1
        except Exception as e:
            error_str = str(e).lower()
            # 检查是否是重复键错误
            if any(keyword in error_str for keyword in [
                'duplicate', 'unique', 'primary key', 'constraint',
                '唯一约束', '主键约束', '重复键'
            ]):
                error_count += 1
                logging.debug(f"忽略重复记录: {e}")
            else:
                # 其他错误需要抛出
                logging.error(f"批量插入失败: {e}")
                raise e

    if error_count > 0:
        logging.info(f"批量插入完成: 成功 {success_count} 条, 忽略重复 {error_count} 条")
    else:
        logging.debug(f"批量插入完成: 成功 {success_count} 条")

    return success_count


def get_dynamic_db_model(base, job_id):
    return type(base.model(
        table_index=get_dynamic_tracking_table_index(job_id=job_id)))


def get_dynamic_tracking_table_index(job_id):
    return job_id[:8]


def fill_db_model_object(model_object, human_model_dict):
    for k, v in human_model_dict.items():
        attr_name = 'f_%s' % k
        if hasattr(model_object.__class__, attr_name):
            setattr(model_object, attr_name, v)
    return model_object


# https://docs.peewee-orm.com/en/latest/peewee/query_operators.html
supported_operators = {
    '==': operator.eq,
    '<': operator.lt,
    '<=': operator.le,
    '>': operator.gt,
    '>=': operator.ge,
    '!=': operator.ne,
    '<<': operator.lshift,
    '>>': operator.rshift,
    '%': operator.mod,
    '**': operator.pow,
    '^': operator.xor,
    '~': operator.inv,
}


def query_dict2expression(
        model: type[DataBaseModel], query: dict[str, bool | int | str | list | tuple]):
    expression = []

    for field, value in query.items():
        if not isinstance(value, (list, tuple)):
            value = ('==', value)
        op, *val = value

        field = getattr(model, f'f_{field}')
        value = supported_operators[op](
            field, val[0]) if op in supported_operators else getattr(
            field, op)(
            *val)
        expression.append(value)

    return reduce(operator.iand, expression)


def query_db(model: type[DataBaseModel], limit: int = 0, offset: int = 0,
             query: dict = None, order_by: str | list | tuple | None = None):
    data = model.select()
    if query:
        data = data.where(query_dict2expression(model, query))
    count = data.count()

    if not order_by:
        order_by = 'create_time'
    if not isinstance(order_by, (list, tuple)):
        order_by = (order_by, 'asc')
    order_by, order = order_by
    order_by = getattr(model, f'f_{order_by}')
    order_by = getattr(order_by, order)()
    data = data.order_by(order_by)

    if limit > 0:
        data = data.limit(limit)
    if offset > 0:
        data = data.offset(offset)

    return list(data), count
