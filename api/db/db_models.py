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
import inspect
import logging
import operator
# 在文件开头添加
import os
os.environ.setdefault('PYTHONFAULTHANDLER', '1')
import sys
import typing
import time
from enum import Enum
from functools import wraps
import hashlib
import base64
import datetime
import importlib
import json
import re
import threading
import uuid

import pyodbc
import peewee
from flask_login import UserMixin
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from peewee import BigIntegerField, BooleanField, CharField, CompositeKey, DateTimeField, Field, FloatField, IntegerField, Metadata, Model, TextField, Database
from playhouse.migrate import MySQLMigrator, PostgresqlMigrator, migrate
from playhouse.pool import PooledMySQLDatabase, PooledPostgresqlDatabase

from api import settings, utils
from api.db import ParserType, SerializedType
from api.db import constant


def singleton(cls, *args, **kw):
    instances = {}

    def _singleton():
        key = str(cls) + str(os.getpid())
        if key not in instances:
            instances[key] = cls(*args, **kw)
        return instances[key]

    return _singleton


CONTINUOUS_FIELD_TYPE = {IntegerField, FloatField, DateTimeField}
AUTO_DATE_TIMESTAMP_FIELD_PREFIX = {"create", "start", "end", "update", "read_access", "write_access"}


class TextFieldType(Enum):
    MYSQL = "LONGTEXT"
    POSTGRES = "TEXT"
    DM = "TEXT"  # 达梦数据库文本字段类型


class LongTextField(TextField):
    field_type = TextFieldType[settings.DATABASE_TYPE.upper()].value


class JSONField(LongTextField):
    default_value = {}

    def __init__(self, object_hook=None, object_pairs_hook=None, **kwargs):
        self._object_hook = object_hook
        self._object_pairs_hook = object_pairs_hook
        super().__init__(**kwargs)

    def db_value(self, value):
        if value is None:
            value = self.default_value
        return utils.json_dumps(value)

    def python_value(self, value):
        if not value:
            return self.default_value
        return utils.json_loads(value, object_hook=self._object_hook, object_pairs_hook=self._object_pairs_hook)


class ListField(JSONField):
    default_value = []


class SerializedField(LongTextField):
    def __init__(self, serialized_type=SerializedType.PICKLE, object_hook=None, object_pairs_hook=None, **kwargs):
        self._serialized_type = serialized_type
        self._object_hook = object_hook
        self._object_pairs_hook = object_pairs_hook
        super().__init__(**kwargs)

    def db_value(self, value):
        if self._serialized_type == SerializedType.PICKLE:
            return utils.serialize_b64(value, to_str=True)
        elif self._serialized_type == SerializedType.JSON:
            if value is None:
                return None
            return utils.json_dumps(value, with_type=True)
        else:
            raise ValueError(f"the serialized type {self._serialized_type} is not supported")

    def python_value(self, value):
        if self._serialized_type == SerializedType.PICKLE:
            return utils.deserialize_b64(value)
        elif self._serialized_type == SerializedType.JSON:
            if value is None:
                return {}
            return utils.json_loads(value, object_hook=self._object_hook, object_pairs_hook=self._object_pairs_hook)
        else:
            raise ValueError(f"the serialized type {self._serialized_type} is not supported")


def is_continuous_field(cls: typing.Type) -> bool:
    if cls in CONTINUOUS_FIELD_TYPE:
        return True
    for p in cls.__bases__:
        if p in CONTINUOUS_FIELD_TYPE:
            return True
        elif p is not Field and p is not object:
            if is_continuous_field(p):
                return True
    else:
        return False


def auto_date_timestamp_field():
    return {f"{f}_time" for f in AUTO_DATE_TIMESTAMP_FIELD_PREFIX}


def auto_date_timestamp_db_field():
    return {f"f_{f}_time" for f in AUTO_DATE_TIMESTAMP_FIELD_PREFIX}


def remove_field_name_prefix(field_name):
    return field_name[2:] if field_name.startswith("f_") else field_name


class BaseModel(Model):
    create_time = BigIntegerField(null=True, index=True)
    create_date = DateTimeField(null=True, index=True)
    update_time = BigIntegerField(null=True, index=True)
    update_date = DateTimeField(null=True, index=True)

    def to_json(self):
        # This function is obsolete
        return self.to_dict()

    def to_dict(self):
        return self.__dict__["__data__"]

    def to_human_model_dict(self, only_primary_with: list = None):
        model_dict = self.__dict__["__data__"]

        if not only_primary_with:
            return {remove_field_name_prefix(k): v for k, v in model_dict.items()}

        human_model_dict = {}
        for k in self._meta.primary_key.field_names:
            human_model_dict[remove_field_name_prefix(k)] = model_dict[k]
        for k in only_primary_with:
            human_model_dict[k] = model_dict[f"f_{k}"]
        return human_model_dict

    @property
    def meta(self) -> Metadata:
        return self._meta

    @classmethod
    def get_primary_keys_name(cls):
        return cls._meta.primary_key.field_names if isinstance(cls._meta.primary_key, CompositeKey) else [cls._meta.primary_key.name]

    @classmethod
    def getter_by(cls, attr):
        return operator.attrgetter(attr)(cls)

    @classmethod
    def query(cls, reverse=None, order_by=None, **kwargs):
        filters = []
        for f_n, f_v in kwargs.items():
            attr_name = "%s" % f_n
            if not hasattr(cls, attr_name) or f_v is None:
                continue
            if type(f_v) in {list, set}:
                f_v = list(f_v)
                if is_continuous_field(type(getattr(cls, attr_name))):
                    if len(f_v) == 2:
                        for i, v in enumerate(f_v):
                            if isinstance(v, str) and f_n in auto_date_timestamp_field():
                                # time type: %Y-%m-%d %H:%M:%S
                                f_v[i] = utils.date_string_to_timestamp(v)
                        lt_value = f_v[0]
                        gt_value = f_v[1]
                        if lt_value is not None and gt_value is not None:
                            filters.append(cls.getter_by(attr_name).between(lt_value, gt_value))
                        elif lt_value is not None:
                            filters.append(operator.attrgetter(attr_name)(cls) >= lt_value)
                        elif gt_value is not None:
                            filters.append(operator.attrgetter(attr_name)(cls) <= gt_value)
                else:
                    filters.append(operator.attrgetter(attr_name)(cls) << f_v)
            else:
                filters.append(operator.attrgetter(attr_name)(cls) == f_v)
        if filters:
            query_records = cls.select().where(*filters)
            if reverse is not None:
                if not order_by or not hasattr(cls, f"{order_by}"):
                    order_by = "create_time"
                if reverse is True:
                    query_records = query_records.order_by(cls.getter_by(f"{order_by}").desc())
                elif reverse is False:
                    query_records = query_records.order_by(cls.getter_by(f"{order_by}").asc())
            return [query_record for query_record in query_records]
        else:
            return []

    @classmethod
    def insert(cls, __data=None, **insert):
        if isinstance(__data, dict) and __data:
            __data[cls._meta.combined["create_time"]] = utils.current_timestamp()
        if insert:
            insert["create_time"] = utils.current_timestamp()

        return super().insert(__data, **insert)

    # update and insert will call this method
    @classmethod
    def _normalize_data(cls, data, kwargs):
        normalized = super()._normalize_data(data, kwargs)
        if not normalized:
            return {}

        normalized[cls._meta.combined["update_time"]] = utils.current_timestamp()

        for f_n in AUTO_DATE_TIMESTAMP_FIELD_PREFIX:
            if {f"{f_n}_time", f"{f_n}_date"}.issubset(cls._meta.combined.keys()) and cls._meta.combined[f"{f_n}_time"] in normalized and normalized[cls._meta.combined[f"{f_n}_time"]] is not None:
                normalized[cls._meta.combined[f"{f_n}_date"]] = utils.timestamp_to_date(normalized[cls._meta.combined[f"{f_n}_time"]])

        return normalized


class JsonSerializedField(SerializedField):
    def __init__(self, object_hook=utils.from_dict_hook, object_pairs_hook=None, **kwargs):
        super(JsonSerializedField, self).__init__(serialized_type=SerializedType.JSON, object_hook=object_hook, object_pairs_hook=object_pairs_hook, **kwargs)


# 添加达梦连接适配器，将pyodbc连接包装成与peewee兼容的接口
class DmConnection:
    def __init__(self, pyodbc_conn):
        self.conn = pyodbc_conn
        self.closed = False
        self._active_cursors = set()  # 跟踪活跃的cursor

    def cursor(self):
        cursor = DmCursor(self.conn.cursor(), self)
        self._active_cursors.add(cursor)
        return cursor

    def commit(self):
        return self.conn.commit()

    def rollback(self):
        return self.conn.rollback()

    def close(self):
        # 关闭所有活跃的cursor
        for cursor in list(self._active_cursors):
            try:
                cursor.close()
            except:
                pass
        self._active_cursors.clear()

        self.closed = True
        return self.conn.close()

    def _remove_cursor(self, cursor):
        """从活跃cursor集合中移除cursor"""
        self._active_cursors.discard(cursor)

    def has_active_cursors(self):
        """检查是否有活跃的cursor"""
        return len(self._active_cursors) > 0

    # 以下方法模拟MySQL连接对象的接口，以支持peewee
    def set_character_set(self, charset):
        # 达梦数据库不直接支持此方法，对应MySQL的设置字符集
        pass

    def character_set_name(self):
        # 返回默认字符集
        return 'UTF8'

    def set_client_encoding(self, encoding):
        # 达梦数据库不支持此方法，但peewee可能会调用
        pass

    def get_autocommit(self):
        # 获取自动提交状态，pyodbc没有直接对应的API
        # 返回默认值
        try:
            return self.conn.autocommit
        except:
            return False

    def set_autocommit(self, autocommit):
        # 达梦数据库通过pyodbc设置自动提交
        self.conn.autocommit = autocommit

    def get_server_info(self):
        # peewee会调用此方法获取服务器版本
        # 使用一个通用版本号作为默认返回
        return '8.0.0'

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.closed:
            self.close()


class DmCursor:
    """达梦数据库cursor包装器"""
    def __init__(self, pyodbc_cursor, connection):
        self.cursor = pyodbc_cursor
        self.connection = connection
        self.closed = False

    def execute(self, sql, params=None):
        if params:
            return self.cursor.execute(sql, params)
        else:
            return self.cursor.execute(sql)

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchmany(self, size=None):
        if size is None:
            return self.cursor.fetchmany()
        return self.cursor.fetchmany(size)

    def close(self):
        if not self.closed:
            self.closed = True
            try:
                self.cursor.close()
            except:
                pass
            # 从连接的活跃cursor集合中移除
            self.connection._remove_cursor(self)

    @property
    def rowcount(self):
        return getattr(self.cursor, 'rowcount', 0)

    @property
    def description(self):
        return getattr(self.cursor, 'description', None)

    def __iter__(self):
        return self

    def __next__(self):
        row = self.fetchone()
        if row is None:
            # 不要在这里关闭cursor，让调用者决定何时关闭
            raise StopIteration
        return row

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class DmQueryCursor:
    """用于SELECT查询的特殊cursor，负责管理连接生命周期"""
    def __init__(self, cursor, connection, database):
        self.cursor = cursor
        self.connection = connection
        self.database = database
        self.closed = False
        self._fetched_all = False
        self._close_scheduled = False

    def fetchone(self):
        if self.closed:
            raise Exception("Attempt to use a closed cursor.")

        try:
            result = self.cursor.fetchone()
            if result is None:
                self._fetched_all = True
                # 不立即关闭，让peewee完成处理
            return result
        except Exception as e:
            if "connection was closed" in str(e).lower():
                self._mark_closed()
                raise
            raise

    def fetchall(self):
        if self.closed:
            raise Exception("Attempt to use a closed cursor.")

        try:
            result = self.cursor.fetchall()
            self._fetched_all = True
            # fetchall后延迟关闭
            self._schedule_delayed_close()
            return result
        except Exception as e:
            self._mark_closed()
            raise

    def fetchmany(self, size=None):
        if self.closed:
            raise Exception("Attempt to use a closed cursor.")

        try:
            if size is None:
                result = self.cursor.fetchmany()
            else:
                result = self.cursor.fetchmany(size)

            # 如果返回的结果少于请求的数量，可能已经到达末尾
            if size and len(result) < size:
                self._fetched_all = True
                self._schedule_delayed_close()

            return result
        except Exception as e:
            self._mark_closed()
            raise

    def _schedule_delayed_close(self):
        """延迟关闭连接，给peewee处理结果的时间"""
        if self._close_scheduled:
            return

        self._close_scheduled = True
        import threading
        def delayed_close():
            import time
            time.sleep(1.0)  # 延迟1秒，给peewee足够时间处理
            if not self.closed:
                logging.debug("延迟关闭cursor和连接")
                self.close()

        # 在后台线程中延迟关闭
        threading.Thread(target=delayed_close, daemon=True).start()

    def _mark_closed(self):
        """标记为已关闭但不实际关闭资源"""
        self.closed = True

    def close(self):
        if not self.closed:
            self.closed = True
            try:
                if hasattr(self.cursor, 'close'):
                    self.cursor.close()
            except:
                pass
            # 归还连接到连接池
            if self.connection:
                self.database._close_conn(self.connection)
                self.connection = None

    @property
    def rowcount(self):
        return getattr(self.cursor, 'rowcount', 0)

    @property
    def description(self):
        return getattr(self.cursor, 'description', None)

    def __iter__(self):
        return self

    def __next__(self):
        if self.closed:
            raise StopIteration

        try:
            row = self.fetchone()
            if row is None:
                # 迭代完成，延迟关闭
                if not self._close_scheduled:
                    self._schedule_delayed_close()
                raise StopIteration
            return row
        except StopIteration:
            raise
        except Exception as e:
            self._mark_closed()
            raise

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        # 确保连接被归还
        if not self.closed:
            self.close()


class PooledDmDatabase(Database):
    """简化版达梦数据库连接"""

    def __init__(self, database, **kwargs):
        self.database = database
        self.host = kwargs.get('host', 'localhost')
        self.port = kwargs.get('port', 5236)
        self.user = kwargs.get('user', 'SYSDBA')
        self.password = kwargs.get('password', 'SYSDBA')
        self.max_connections = kwargs.get('max_connections', 20)  # 减少连接数
        self.stale_timeout = kwargs.get('stale_timeout', 300)

        # 简化初始化属性
        self._initialized = False
        self._lock = threading.Lock()  # 使用简单锁
        self._connections = []  # 简化连接池

        # 先调用父类初始化
        super().__init__(database)
        logging.info("初始化达梦数据库连接")

    def _create_connection(self):
        """创建单个数据库连接"""
        try:
            conn_str = (
                f"DRIVER={{DM ODBC DRIVER}};"
                f"SERVER={self.host};"
                f"PORT={self.port};"
                f"UID={self.user};"
                f"PWD={self.password};"
                f"DATABASE={self.database};"
                f"CONNECT_TIMEOUT=10;"
                f"LOGIN_TIMEOUT=10"
            )
            pyodbc_conn = pyodbc.connect(conn_str)
            return DmConnection(pyodbc_conn)
        except Exception as e:
            logging.error(f"创建达梦数据库连接失败: {e}")
            raise

    def connect(self):
        """连接数据库"""
        if self._initialized:
            return True

        with self._lock:
            if self._initialized:
                return True

            try:
                # 创建一个测试连接
                test_conn = self._create_connection()
                test_conn.close()  # 立即关闭测试连接

                self._initialized = True
                logging.debug("达梦数据库连接池初始化成功")
                return True
            except Exception as e:
                logging.error(f"达梦数据库连接失败: {e}")
                raise

    def is_closed(self):
        """检查数据库是否关闭"""
        return not self._initialized

    def close(self):
        """关闭数据库连接"""
        with self._lock:
            # 清理所有连接
            for conn in self._connections:
                try:
                    conn.close()
                except:
                    pass
            self._connections.clear()
            self._initialized = False

    def get_conn(self):
        """获取数据库连接 - 每次创建新连接"""
        if not self._initialized:
            self.connect()

        # 简化策略：每次都创建新连接，用完即关闭
        return self._create_connection()

    def execute_sql(self, sql, params=None, commit=None):
        """执行SQL语句 - 简化版本"""
        conn = None
        cursor = None

        try:
            # 获取连接
            conn = self.get_conn()
            cursor = conn.cursor()

            # 处理SQL和参数
            processed_sql, processed_params = self._process_sql_and_params(sql, params)

            # 执行SQL
            if processed_params:
                cursor.execute(processed_sql, processed_params)
            else:
                cursor.execute(processed_sql)

            # 提交事务
            if commit or (commit is None and not self.in_transaction()):
                conn.commit()

            # 对于SELECT查询，返回结果后立即关闭连接
            if processed_sql.strip().upper().startswith('SELECT'):
                try:
                    # 立即获取所有结果
                    results = cursor.fetchall()

                    # 创建一个模拟cursor返回结果
                    class ResultCursor:
                        def __init__(self, results, description):
                            self.results = results
                            self.description = description
                            self.rowcount = len(results) if results else 0
                            self._index = 0

                        def fetchone(self):
                            if self._index < len(self.results):
                                result = self.results[self._index]
                                self._index += 1
                                return result
                            return None

                        def fetchall(self):
                            return self.results[self._index:]

                        def fetchmany(self, size=None):
                            if size is None:
                                size = len(self.results) - self._index
                            end_index = min(self._index + size, len(self.results))
                            result = self.results[self._index:end_index]
                            self._index = end_index
                            return result

                        def close(self):
                            pass

                        def __iter__(self):
                            return iter(self.results[self._index:])

                    result_cursor = ResultCursor(results, cursor.description)
                    return result_cursor

                finally:
                    # 确保连接被关闭
                    try:
                        cursor.close()
                        conn.close()
                    except:
                        pass
            else:
                # 非SELECT查询，返回cursor但确保连接会被关闭
                try:
                    result = cursor
                    return result
                finally:
                    # 延迟关闭，给调用者时间处理结果
                    def delayed_close():
                        import time
                        time.sleep(0.1)  # 短暂延迟
                        try:
                            cursor.close()
                            conn.close()
                        except:
                            pass

                    threading.Thread(target=delayed_close, daemon=True).start()

        except Exception as e:
            # 错误处理
            error_str = str(e)

            # 检查是否是唯一约束冲突（初始化数据时常见）
            if ('23000' in str(getattr(e, 'args', [''])[0]) or
                    '-6602' in error_str or
                    'Violate unique constraint' in error_str):

                init_tables = ['llm_factories', 'llm', 'tenant', 'user']
                if any(table in sql.lower() for table in init_tables):
                    logging.warning(f"初始化数据时遇到唯一约束冲突，忽略: {error_str}")

                    # 返回模拟cursor
                    class MockCursor:
                        def __init__(self):
                            self.rowcount = 0
                            self.lastrowid = None
                        def fetchone(self): return None
                        def fetchall(self): return []
                        def close(self): pass

                    return MockCursor()

            logging.error(f"SQL执行失败: {error_str}")
            logging.error(f"原始SQL: {sql}")
            logging.error(f"处理后SQL: {processed_sql}")
            # logging.error(f"原始参数: {params}")
            # logging.error(f"处理后参数: {processed_params}")
            raise

        finally:
            # 确保资源清理
            if cursor and conn:
                try:
                    cursor.close()
                    conn.close()
                except:
                    pass

    def _process_sql_and_params(self, sql, params):
        """同时处理SQL语句和参数以适配达梦数据库"""
        import re

        # 基本的SQL转换
        processed_sql = sql.replace('`', '"')  # MySQL反引号转达梦双引号

        # 处理特殊函数
        if "GET_LOCK" in processed_sql or "RELEASE_LOCK" in processed_sql:
            return "SELECT 1 FROM DUAL", []

        # 处理数据类型
        processed_sql = processed_sql.replace("AUTO_INCREMENT", "IDENTITY")
        processed_sql = processed_sql.replace("LONGTEXT", "TEXT")
        processed_sql = processed_sql.replace("BIGINT UNSIGNED", "BIGINT")

        # 处理INSERT IGNORE
        if "INSERT IGNORE" in processed_sql.upper():
            processed_sql = processed_sql.replace("INSERT IGNORE", "INSERT", 1)

        # 处理参数
        processed_params = list(params) if params else []

        # 修复IS NULL/IS NOT NULL语法问题
        # 更精确地处理IS ?模式

        # 1. 处理 NOT (column IS ?) 的情况
        not_is_pattern = r'NOT\s+\(\s*"([^"]+)"\."([^"]+)"\s+IS\s+\?\s*\)'
        not_is_matches = list(re.finditer(not_is_pattern, processed_sql, re.IGNORECASE))

        # 2. 处理 (column IS ?) 的情况
        is_pattern = r'(?<!NOT\s)\(\s*"([^"]+)"\."([^"]+)"\s+IS\s+\?\s*\)'
        is_matches = list(re.finditer(is_pattern, processed_sql, re.IGNORECASE))

        # 收集所有需要处理的匹配项
        all_matches = []

        # 添加NOT IS匹配项
        for match in not_is_matches:
            param_index = processed_sql[:match.start()].count('?')
            all_matches.append({
                'match': match,
                'param_index': param_index,
                'is_not': True,
                'table': match.group(1),
                'column': match.group(2),
                'start': match.start(),
                'end': match.end()
            })

        # 添加IS匹配项
        for match in is_matches:
            param_index = processed_sql[:match.start()].count('?')
            all_matches.append({
                'match': match,
                'param_index': param_index,
                'is_not': False,
                'table': match.group(1),
                'column': match.group(2),
                'start': match.start(),
                'end': match.end()
            })

        # 按位置从后往前排序，避免位置偏移
        all_matches.sort(key=lambda x: x['start'], reverse=True)

        # 记录需要移除的参数索引
        param_removals = []

        # 处理每个匹配项
        for match_info in all_matches:
            param_index = match_info['param_index']

            # 检查对应的参数是否为None
            if param_index < len(processed_params) and processed_params[param_index] is None:
                # 替换SQL
                if match_info['is_not']:
                    replacement = f'("{match_info["table"]}"."{match_info["column"]}" IS NOT NULL)'
                else:
                    replacement = f'("{match_info["table"]}"."{match_info["column"]}" IS NULL)'

                processed_sql = processed_sql[:match_info['start']] + replacement + processed_sql[match_info['end']:]

                # 标记要移除的参数
                param_removals.append(param_index)

        # 移除对应的参数（从后往前移除，避免索引偏移）
        for param_index in sorted(set(param_removals), reverse=True):
            if param_index < len(processed_params):
                processed_params.pop(param_index)

        # 处理LIMIT子句
        if " LIMIT " in processed_sql:
            limit_match = re.search(r"LIMIT\s+(\d+)(?:\s*,\s*(\d+))?", processed_sql, re.IGNORECASE)
            if limit_match:
                if limit_match.group(2):
                    offset = limit_match.group(1)
                    fetch = limit_match.group(2)
                    processed_sql = re.sub(r"LIMIT\s+\d+\s*,\s*\d+",
                                           f"OFFSET {offset} ROWS FETCH FIRST {fetch} ROWS ONLY",
                                           processed_sql, flags=re.IGNORECASE)
                else:
                    count = limit_match.group(1)
                    processed_sql = re.sub(r"LIMIT\s+\d+",
                                           f"FETCH FIRST {count} ROWS ONLY",
                                           processed_sql, flags=re.IGNORECASE)

        # 调试日志
        logging.debug(f"SQL处理调试:")
        logging.debug(f"  原始SQL: {sql}")
        logging.debug(f"  处理后SQL: {processed_sql}")
        logging.debug(f"  原始参数: {params}")
        logging.debug(f"  处理后参数: {processed_params}")
        logging.debug(f"  参数移除索引: {param_removals}")

        return processed_sql, processed_params

    def _process_sql(self, sql):
        """处理SQL语句以适配达梦数据库（保留向后兼容性）"""
        processed_sql, _ = self._process_sql_and_params(sql, None)
        return processed_sql

    def get_tables(self, schema=None):
        """获取表列表"""
        try:
            query = """
            SELECT TABLE_NAME FROM ALL_TABLES 
            WHERE OWNER = CURRENT_USER 
            UNION 
            SELECT VIEW_NAME FROM ALL_VIEWS 
            WHERE OWNER = CURRENT_USER
            """
            cursor = self.execute_sql(query)
            return [table_name for (table_name,) in cursor.fetchall()]
        except Exception as e:
            logging.error(f"获取表列表失败: {e}")
            return []

    def table_exists(self, table_name, schema=None):
        """检查表是否存在"""
        try:
            query = """
            SELECT COUNT(*) FROM (
                SELECT TABLE_NAME FROM ALL_TABLES 
                WHERE OWNER = CURRENT_USER AND TABLE_NAME = ?
                UNION 
                SELECT VIEW_NAME FROM ALL_VIEWS 
                WHERE OWNER = CURRENT_USER AND VIEW_NAME = ?
            )
            """
            cursor = self.execute_sql(query, (table_name, table_name))
            count = cursor.fetchone()[0]
            return count > 0
        except Exception as e:
            logging.error(f"检查表是否存在失败: {e}")
            return False

    # 事务相关方法（简化版）
    def in_transaction(self):
        return False  # 简化：不维护事务状态

    def begin(self):
        pass  # 简化：每个连接自动管理事务

    def commit(self):
        pass

    def rollback(self):
        pass

    def last_insert_id(self, cursor, query_type):
        """获取最后插入的ID"""
        try:
            cursor.execute("SELECT SCOPE_IDENTITY() AS ID FROM DUAL")
            result = cursor.fetchone()
            return result[0] if result and result[0] is not None else None
        except:
            return None

    def rows_affected(self, cursor):
        """返回影响的行数"""
        return getattr(cursor, 'rowcount', 0)

    def close_stale(self, age=300):
        """清理过期连接 - 简化版本"""
        # 由于我们不维护长连接池，这里只是占位
        pass


class PooledDatabase(Enum):
    MYSQL = PooledMySQLDatabase
    POSTGRES = PooledPostgresqlDatabase
    DM = PooledDmDatabase  # 添加达梦数据库


class DatabaseMigrator(Enum):
    MYSQL = MySQLMigrator
    POSTGRES = PostgresqlMigrator
    # 由于达梦数据库没有对应的Migrator，我们借用PostgreSQL的迁移器
    DM = PostgresqlMigrator


#@singleton
class BaseDataBase:
    _instance = None
    _lock = threading.RLock()
    _initialized = False

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(BaseDataBase, cls).__new__(cls)
            return cls._instance

    def __init__(self):
        # 防止重复初始化
        if self._initialized:
            return

        with self._lock:
            if self._initialized:
                return

            database_config = settings.DATABASE.copy()
            db_name = database_config.pop("name")

            try:
                self.database_connection = PooledDatabase[settings.DATABASE_TYPE.upper()].value(db_name,**database_config)
                logging.info(f"init {settings.DATABASE_TYPE} database on cluster mode successfully")
                self._initialized = True
            except Exception as e:
                logging.error(f"Failed to initialize {settings.DATABASE_TYPE} database: {e}")
                raise


def with_retry(max_retries=3, retry_delay=1.0):
    """Decorator: Add retry mechanism to database operations
    
    Args:
        max_retries (int): maximum number of retries
        retry_delay (float): initial retry delay (seconds), will increase exponentially
        
    Returns:
        decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for retry in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    # get self and method name for logging
                    self_obj = args[0] if args else None
                    func_name = func.__name__
                    lock_name = getattr(self_obj, 'lock_name', 'unknown') if self_obj else 'unknown'
                    
                    if retry < max_retries - 1:
                        current_delay = retry_delay * (2 ** retry)
                        logging.warning(f"{func_name} {lock_name} failed: {str(e)}, retrying ({retry+1}/{max_retries})")
                        time.sleep(current_delay)
                    else:
                        logging.error(f"{func_name} {lock_name} failed after all attempts: {str(e)}")
            
            if last_exception:
                raise last_exception
            return False
        return wrapper
    return decorator


class PostgresDatabaseLock:
    def __init__(self, lock_name, timeout=10, db=None):
        self.lock_name = lock_name
        self.lock_id = int(hashlib.md5(lock_name.encode()).hexdigest(), 16) % (2**31-1)
        self.timeout = int(timeout)
        self.db = db if db else DB

    @with_retry(max_retries=3, retry_delay=1.0)
    def lock(self):
        cursor = self.db.execute_sql("SELECT pg_try_advisory_lock(%s)", (self.lock_id,))
        ret = cursor.fetchone()
        if ret[0] == 0:
            raise Exception(f"acquire postgres lock {self.lock_name} timeout")
        elif ret[0] == 1:
            return True
        else:
            raise Exception(f"failed to acquire lock {self.lock_name}")

    @with_retry(max_retries=3, retry_delay=1.0)
    def unlock(self):
        cursor = self.db.execute_sql("SELECT pg_advisory_unlock(%s)", (self.lock_id,))
        ret = cursor.fetchone()
        if ret[0] == 0:
            raise Exception(f"postgres lock {self.lock_name} was not established by this thread")
        elif ret[0] == 1:
            return True
        else:
            raise Exception(f"postgres lock {self.lock_name} does not exist")

    def __enter__(self):
        if isinstance(self.db, PooledPostgresqlDatabase):
            self.lock()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if isinstance(self.db, PooledPostgresqlDatabase):
            self.unlock()

    def __call__(self, func):
        @wraps(func)
        def magic(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return magic


class MysqlDatabaseLock:
    def __init__(self, lock_name, timeout=10, db=None):
        self.lock_name = lock_name
        self.timeout = int(timeout)
        self.db = db if db else DB

    @with_retry(max_retries=3, retry_delay=1.0)
    def lock(self):
        # SQL parameters only support %s format placeholders
        cursor = self.db.execute_sql("SELECT GET_LOCK(%s, %s)", (self.lock_name, self.timeout))
        ret = cursor.fetchone()
        if ret[0] == 0:
            raise Exception(f"acquire mysql lock {self.lock_name} timeout")
        elif ret[0] == 1:
            return True
        else:
            raise Exception(f"failed to acquire lock {self.lock_name}")

    @with_retry(max_retries=3, retry_delay=1.0)
    def unlock(self):
        cursor = self.db.execute_sql("SELECT RELEASE_LOCK(%s)", (self.lock_name,))
        ret = cursor.fetchone()
        if ret[0] == 0:
            raise Exception(f"mysql lock {self.lock_name} was not established by this thread")
        elif ret[0] == 1:
            return True
        else:
            raise Exception(f"mysql lock {self.lock_name} does not exist")

    def __enter__(self):
        if isinstance(self.db, PooledMySQLDatabase):
            self.lock()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if isinstance(self.db, PooledMySQLDatabase):
            self.unlock()

    def __call__(self, func):
        @wraps(func)
        def magic(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return magic


class DmDatabaseLock:
    def __init__(self, lock_name, timeout=10, db=None):
        self.lock_name = lock_name
        self.timeout = int(timeout)
        self.db = db if db else DB
        # 创建锁表名
        self.lock_table = "DM_DATABASE_LOCKS"
        self._ensure_lock_table()

    def _ensure_lock_table(self):
        """确保锁表存在"""
        try:
            # 检查表是否存在 - 使用达梦兼容的SQL语法
            cursor = self.db.execute_sql(
                f'''
                SELECT COUNT(*) FROM ALL_TABLES 
                WHERE TABLE_NAME = ? AND OWNER = CURRENT_USER
                ''',
                (self.lock_table,)
            )
            table_exists = cursor.fetchone()[0] > 0

            if not table_exists:
                # 创建锁表（如果不存在）- 使用达梦兼容的SQL语法
                self.db.execute_sql(
                    f'''
                    CREATE TABLE "{self.lock_table}" (
                        "LOCK_NAME" VARCHAR(255) NOT NULL PRIMARY KEY,
                        "LOCK_TIME" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        "PROCESS_ID" VARCHAR(255) NOT NULL,
                        "TIMEOUT" INTEGER NOT NULL
                    )
                    '''
                )
                logging.info(f"成功创建达梦数据库锁表: {self.lock_table}")
        except Exception as e:
            logging.warning(f"确保锁表存在时出错: {e}")

    @with_retry(max_retries=3, retry_delay=1.0)
    def lock(self):
        # 达梦数据库锁实现
        # 获取当前进程ID作为锁标识
        process_id = str(os.getpid()) + "_" + str(threading.get_ident())

        try:
            # 尝试获取锁 - 使用达梦兼容的插入语法
            cursor = self.db.execute_sql(
                f'''
                        INSERT INTO "{self.lock_table}" 
                        ("LOCK_NAME", "PROCESS_ID", "TIMEOUT")
                        VALUES (?, ?, ?)
                        ''',
                (self.lock_name, process_id, self.timeout)
            )
            self.db.commit()
            return True
        except Exception as e:
            # 如果插入失败，检查锁是否已超时
            try:
                cursor = self.db.execute_sql(
                    f'''
                    SELECT "LOCK_TIME", "PROCESS_ID", "TIMEOUT"
                    FROM "{self.lock_table}"
                    WHERE "LOCK_NAME" = ?
                    ''',
                    (self.lock_name,)
                )
                lock_record = cursor.fetchone()

                if lock_record:
                    lock_time, lock_process_id, lock_timeout = lock_record
                    # 检查是否是自己的锁
                    if lock_process_id == process_id:
                        return True

                    # 计算锁是否已超时
                    cursor = self.db.execute_sql("SELECT CURRENT_TIMESTAMP FROM DUAL")
                    current_time = cursor.fetchone()[0]
                    # 计算时间差（秒）
                    if hasattr(current_time, 'timestamp') and hasattr(lock_time, 'timestamp'):
                        time_diff = current_time.timestamp() - lock_time.timestamp()
                    else:
                        # 简单估计，两个日期的差异
                        time_diff = (current_time - lock_time).total_seconds()

                    # 如果锁超时，则强制获取锁
                    if time_diff > lock_timeout:
                        self.db.execute_sql(
                            f'''
                            UPDATE "{self.lock_table}"
                            SET "PROCESS_ID" = ?, "LOCK_TIME" = CURRENT_TIMESTAMP, "TIMEOUT" = ?
                            WHERE "LOCK_NAME" = ?
                            ''',
                            (process_id, self.timeout, self.lock_name)
                        )
                        self.db.commit()
                        return True
            except Exception as check_ex:
                logging.error(f"检查锁超时时出错: {check_ex}")

            raise Exception(f"无法获取达梦数据库锁 {self.lock_name}")

    @with_retry(max_retries=3, retry_delay=1.0)
    def unlock(self):
        # 达梦数据库解锁实现
        process_id = str(os.getpid()) + "_" + str(threading.get_ident())

        try:
            # 仅删除自己持有的锁 - 使用达梦兼容的SQL语法
            cursor = self.db.execute_sql(
                f'''
                DELETE FROM "{self.lock_table}"
                WHERE "LOCK_NAME" = ? AND "PROCESS_ID" = ?
                ''',
                (self.lock_name, process_id)
            )
            self.db.commit()
            rows_affected = cursor.rowcount
            if rows_affected == 0:
                logging.warning(f"没有找到进程 {process_id} 持有的锁 {self.lock_name}")
            return True
        except Exception as e:
            logging.error(f"释放达梦数据库锁 {self.lock_name} 时出错: {e}")
            raise Exception(f"无法释放达梦数据库锁 {self.lock_name}")

    def __enter__(self):
        if isinstance(self.db, PooledDmDatabase):
            self.lock()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if isinstance(self.db, PooledDmDatabase):
            self.unlock()

    def __call__(self, func):
        @wraps(func)
        def magic(*args, **kwargs):
            with self:
                return func(*args, **kwargs)
            return magic


class DatabaseLock(Enum):
    MYSQL = MysqlDatabaseLock
    POSTGRES = PostgresDatabaseLock
    DM = DmDatabaseLock  # 添加达梦数据库锁


DB = BaseDataBase().database_connection
DB.lock = DatabaseLock[settings.DATABASE_TYPE.upper()].value


def close_connection():
    try:
        if DB and hasattr(DB, 'close_stale'):
            DB.close_stale(age=30)
    except Exception as e:
        logging.exception(e)


class DataBaseModel(BaseModel):
    class Meta:
        database = DB

    @classmethod
    def table_exists(cls):
        """重写表存在检查方法，以适配达梦数据库"""
        if settings.DATABASE_TYPE.upper() == 'DM':
            # 使用我们的自定义实现
            M = cls._meta
            if hasattr(cls._meta.database, 'table_exists'):
                return cls._meta.database.table_exists(M.table.__name__, M.schema)
            # 如果数据库没有实现，使用通用方法
            return M.table.__name__ in cls._meta.database.get_tables(schema=M.schema)
        else:
            # 非达梦数据库使用默认的实现
            return super().table_exists()


@DB.connection_context()
def init_database_tables(alter_fields=[]):
    members = inspect.getmembers(sys.modules[__name__], inspect.isclass)
    table_objs = []
    create_failed_list = []
    for name, obj in members:
        if obj != DataBaseModel and issubclass(obj, DataBaseModel):
            table_objs.append(obj)

            if not obj.table_exists():
                logging.debug(f"start create table {obj.__name__}")
                try:
                    obj.create_table()
                    logging.debug(f"create table success: {obj.__name__}")
                except Exception as e:
                    logging.exception(e)
                    create_failed_list.append(obj.__name__)
            else:
                logging.debug(f"table {obj.__name__} already exists, skip creation.")

    if create_failed_list:
        logging.error(f"create tables failed: {create_failed_list}")
        raise Exception(f"create tables failed: {create_failed_list}")
    migrate_db()


def fill_db_model_object(model_object, human_model_dict):
    for k, v in human_model_dict.items():
        attr_name = "%s" % k
        if hasattr(model_object.__class__, attr_name):
            setattr(model_object, attr_name, v)
    return model_object


class User(DataBaseModel, UserMixin):
    id = CharField(max_length=32, primary_key=True)
    access_token = CharField(max_length=255, null=True, index=True)
    nickname = CharField(max_length=100, null=False, help_text="nicky name", index=True)
    password = CharField(max_length=255, null=True, help_text="password", index=True)
    email = CharField(max_length=255, null=False, help_text="email", index=True)
    avatar = TextField(null=True, help_text="avatar base64 string")
    language = CharField(max_length=32, null=True, help_text="English|Chinese", default="Chinese" if "zh_CN" in os.getenv("LANG", "") else "English", index=True)
    color_schema = CharField(max_length=32, null=True, help_text="Bright|Dark", default="Bright", index=True)
    timezone = CharField(max_length=64, null=True, help_text="Timezone", default="UTC+8\tAsia/Shanghai", index=True)
    last_login_time = DateTimeField(null=True, index=True)
    is_authenticated = CharField(max_length=1, null=False, default="1", index=True)
    is_active = CharField(max_length=1, null=False, default="1", index=True)
    is_anonymous = CharField(max_length=1, null=False, default="0", index=True)
    login_channel = CharField(null=True, help_text="from which user login", index=True)
    status = CharField(max_length=1, null=True, help_text="is it validate(0: wasted, 1: validate)", default="1", index=True)
    is_superuser = BooleanField(null=True, help_text="is root", default=False, index=True)

    def __str__(self):
        return self.email

    def get_id(self):
        jwt = Serializer(secret_key=settings.SECRET_KEY)
        return jwt.dumps(str(self.access_token))

    class Meta:
        db_table = "user"


class Tenant(DataBaseModel):
    id = CharField(max_length=32, primary_key=True)
    name = CharField(max_length=100, null=True, help_text="Tenant name", index=True)
    public_key = CharField(max_length=255, null=True, index=True)
    llm_id = CharField(max_length=128, null=False, help_text="default llm ID", index=True)
    embd_id = CharField(max_length=128, null=False, help_text="default embedding model ID", index=True)
    asr_id = CharField(max_length=128, null=False, help_text="default ASR model ID", index=True)
    img2txt_id = CharField(max_length=128, null=False, help_text="default image to text model ID", index=True)
    rerank_id = CharField(max_length=128, null=False, help_text="default rerank model ID", index=True)
    tts_id = CharField(max_length=256, null=True, help_text="default tts model ID", index=True)
    parser_ids = CharField(max_length=256, null=False, help_text="document processors", index=True)
    credit = IntegerField(default=512, index=True)
    status = CharField(max_length=1, null=True, help_text="is it validate(0: wasted, 1: validate)", default="1", index=True)

    class Meta:
        db_table = "tenant"


class UserTenant(DataBaseModel):
    id = CharField(max_length=32, primary_key=True)
    user_id = CharField(max_length=32, null=False, index=True)
    tenant_id = CharField(max_length=32, null=False, index=True)
    role = CharField(max_length=32, null=False, help_text="UserTenantRole", index=True)
    invited_by = CharField(max_length=32, null=False, index=True)
    status = CharField(max_length=1, null=True, help_text="is it validate(0: wasted, 1: validate)", default="1", index=True)

    class Meta:
        db_table = "user_tenant"


class InvitationCode(DataBaseModel):
    id = CharField(max_length=32, primary_key=True)
    code = CharField(max_length=32, null=False, index=True)
    visit_time = DateTimeField(null=True, index=True)
    user_id = CharField(max_length=32, null=True, index=True)
    tenant_id = CharField(max_length=32, null=True, index=True)
    status = CharField(max_length=1, null=True, help_text="is it validate(0: wasted, 1: validate)", default="1", index=True)

    class Meta:
        db_table = "invitation_code"


class LLMFactories(DataBaseModel):
    name = CharField(max_length=128, null=False, help_text="LLM factory name", primary_key=True)
    logo = TextField(null=True, help_text="llm logo base64")
    tags = CharField(max_length=255, null=False, help_text="LLM, Text Embedding, Image2Text, ASR", index=True)
    status = CharField(max_length=1, null=True, help_text="is it validate(0: wasted, 1: validate)", default="1", index=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "llm_factories"


class LLM(DataBaseModel):
    # LLMs dictionary
    llm_name = CharField(max_length=128, null=False, help_text="LLM name", index=True)
    model_type = CharField(max_length=128, null=False, help_text="LLM, Text Embedding, Image2Text, ASR", index=True)
    fid = CharField(max_length=128, null=False, help_text="LLM factory id", index=True)
    max_tokens = IntegerField(default=0)

    tags = CharField(max_length=255, null=False, help_text="LLM, Text Embedding, Image2Text, Chat, 32k...", index=True)
    is_tools =  BooleanField(null=False, help_text="support tools", default=False)
    status = CharField(max_length=1, null=True, help_text="is it validate(0: wasted, 1: validate)", default="1", index=True)

    def __str__(self):
        return self.llm_name

    class Meta:
        primary_key = CompositeKey("fid", "llm_name")
        db_table = "llm"


class TenantLLM(DataBaseModel):
    tenant_id = CharField(max_length=32, null=False, index=True)
    llm_factory = CharField(max_length=128, null=False, help_text="LLM factory name", index=True)
    model_type = CharField(max_length=128, null=True, help_text="LLM, Text Embedding, Image2Text, ASR", index=True)
    llm_name = CharField(max_length=128, null=True, help_text="LLM name", default="", index=True)
    api_key = CharField(max_length=2048, null=True, help_text="API KEY", index=True)
    api_base = CharField(max_length=255, null=True, help_text="API Base")
    max_tokens = IntegerField(default=8192, index=True)
    used_tokens = IntegerField(default=0, index=True)

    def __str__(self):
        return self.llm_name

    class Meta:
        db_table = "tenant_llm"
        primary_key = CompositeKey("tenant_id", "llm_factory", "llm_name")


class TenantLangfuse(DataBaseModel):
    tenant_id = CharField(max_length=32, null=False, primary_key=True)
    secret_key = CharField(max_length=2048, null=False, help_text="SECRET KEY", index=True)
    public_key = CharField(max_length=2048, null=False, help_text="PUBLIC KEY", index=True)
    host = CharField(max_length=128, null=False, help_text="HOST", index=True)

    def __str__(self):
        return "Langfuse host" + self.host

    class Meta:
        db_table = "tenant_langfuse"


class Knowledgebase(DataBaseModel):
    id = CharField(max_length=32, primary_key=True)
    avatar = TextField(null=True, help_text="avatar base64 string")
    tenant_id = CharField(max_length=32, null=False, index=True)
    name = CharField(max_length=128, null=False, help_text="KB name", index=True)
    language = CharField(max_length=32, null=True, default="Chinese" if "zh_CN" in os.getenv("LANG", "") else "English", help_text="English|Chinese", index=True)
    description = TextField(null=True, help_text="KB description")
    embd_id = CharField(max_length=128, null=False, help_text="default embedding model ID", index=True)
    permission = CharField(max_length=16, null=False, help_text="me|team", default="me", index=True)
    created_by = CharField(max_length=32, null=False, index=True)
    doc_num = IntegerField(default=0, index=True)
    token_num = IntegerField(default=0, index=True)
    chunk_num = IntegerField(default=0, index=True)
    similarity_threshold = FloatField(default=0.2, index=True)
    vector_similarity_weight = FloatField(default=0.3, index=True)

    parser_id = CharField(max_length=32, null=False, help_text="default parser ID", default=ParserType.PAPER.value, index=True)
    parser_config = JSONField(null=False, default={
        "pages": [[1, 1000000]],
        "layout_recognize":"MinerU",
        "extractor":{"keyvalues":constant.keyvalues_mapping['default']},
        "classifier":{}})
    pagerank = IntegerField(default=0, index=False)
    status = CharField(max_length=1, null=True, help_text="is it validate(0: wasted, 1: validate)", default="1", index=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "knowledgebase"


class Document(DataBaseModel):
    id = CharField(max_length=32, primary_key=True)
    thumbnail = TextField(null=True, help_text="thumbnail base64 string")
    kb_id = CharField(max_length=256, null=False, index=True)
    parser_id = CharField(max_length=32, null=False, help_text="default parser ID", index=True)
    parser_config = JSONField(null=False, default={"pages": [[1, 1000000]],
        "extractor":{"keyvalues":constant.keyvalues_mapping['default']},
        "classifier":{}})
    source_type = CharField(max_length=128, null=False, default="local", help_text="where does this document come from", index=True)
    type = CharField(max_length=32, null=False, help_text="file extension", index=True)
    created_by = CharField(max_length=32, null=False, help_text="who created it", index=True)
    name = CharField(max_length=255, null=True, help_text="file name", index=True)
    location = CharField(max_length=255, null=True, help_text="where does it store", index=True)
    md_location = CharField(max_length=255, null=True, help_text="where does mineru markdown store", index=True)
    layout_location = CharField(max_length=255, null=True, help_text="where does mineru markdown store", index=True)
    size = IntegerField(default=0, index=True)
    token_num = IntegerField(default=0, index=True)
    chunk_num = IntegerField(default=0, index=True)
    progress = FloatField(default=0, index=True)
    progress_msg = TextField(null=True, help_text="process message", default="")
    process_begin_at = DateTimeField(null=True, index=True)
    process_duation = FloatField(default=0)
    meta_fields = JSONField(null=True, default={})
    filter_fields = JSONField(null=True, default={'limit_range':[],'limit_level':1,'limit_time':0})
    run = CharField(max_length=1, null=True, help_text="start to run processing or cancel.(1: run it; 2: cancel)", default="0", index=True)
    status = CharField(max_length=1, null=True, help_text="is it validate(0: wasted, 1: validate)", default="1", index=True)

    class Meta:
        db_table = "document"


class File(DataBaseModel):
    id = CharField(max_length=32, primary_key=True)
    parent_id = CharField(max_length=32, null=False, help_text="parent folder id", index=True)
    tenant_id = CharField(max_length=32, null=False, help_text="tenant id", index=True)
    created_by = CharField(max_length=32, null=False, help_text="who created it", index=True)
    name = CharField(max_length=255, null=False, help_text="file name or folder name", index=True)
    location = CharField(max_length=255, null=True, help_text="where does it store", index=True)
    size = IntegerField(default=0, index=True)
    type = CharField(max_length=32, null=False, help_text="file extension", index=True)
    source_type = CharField(max_length=128, null=False, default="", help_text="where does this document come from", index=True)

    class Meta:
        db_table = "file"


class File2Document(DataBaseModel):
    id = CharField(max_length=32, primary_key=True)
    file_id = CharField(max_length=32, null=True, help_text="file id", index=True)
    document_id = CharField(max_length=32, null=True, help_text="document id", index=True)

    class Meta:
        db_table = "file2document"


class Task(DataBaseModel):
    id = CharField(max_length=32, primary_key=True)
    doc_id = CharField(max_length=32, null=False, index=True)
    from_page = IntegerField(default=0)
    to_page = IntegerField(default=100000000)
    task_type = CharField(max_length=32, null=False, default="")
    priority = IntegerField(default=0)

    begin_at = DateTimeField(null=True, index=True)
    process_duation = FloatField(default=0)

    progress = FloatField(default=0, index=True)
    progress_msg = TextField(null=True, help_text="process message", default="")
    retry_count = IntegerField(default=0)
    digest = TextField(null=True, help_text="task digest", default="")
    chunk_ids = LongTextField(null=True, help_text="chunk ids", default="")


class Dialog(DataBaseModel):
    id = CharField(max_length=32, primary_key=True)
    tenant_id = CharField(max_length=32, null=False, index=True)
    name = CharField(max_length=255, null=True, help_text="dialog application name", index=True)
    description = TextField(null=True, help_text="Dialog description")
    icon = TextField(null=True, help_text="icon base64 string")
    language = CharField(max_length=32, null=True, default="Chinese" if "zh_CN" in os.getenv("LANG", "") else "English", help_text="English|Chinese", index=True)
    llm_id = CharField(max_length=128, null=False, help_text="default llm ID")

    llm_setting = JSONField(null=False, default={"temperature": 0.1, "top_p": 0.3, "frequency_penalty": 0.7, "presence_penalty": 0.4, "max_tokens": 512})
    prompt_type = CharField(max_length=16, null=False, default="simple", help_text="simple|advanced", index=True)
    prompt_config = JSONField(
        null=False,
        default={"system": "", "prologue": "Hi! I'm your assistant, what can I do for you?", "parameters": [], "empty_response": "Sorry! No relevant content was found in the knowledge base!"},
    )

    similarity_threshold = FloatField(default=0.2)
    vector_similarity_weight = FloatField(default=0.3)

    top_n = IntegerField(default=6)

    top_k = IntegerField(default=1024)

    do_refer = CharField(max_length=1, null=False, default="1", help_text="it needs to insert reference index into answer or not")

    rerank_id = CharField(max_length=128, null=False, help_text="default rerank model ID")

    kb_ids = JSONField(null=False, default=[])
    status = CharField(max_length=1, null=True, help_text="is it validate(0: wasted, 1: validate)", default="1", index=True)

    class Meta:
        db_table = "dialog"


class Conversation(DataBaseModel):
    id = CharField(max_length=32, primary_key=True)
    dialog_id = CharField(max_length=32, null=False, index=True)
    name = CharField(max_length=255, null=True, help_text="converastion name", index=True)
    message = JSONField(null=True)
    reference = JSONField(null=True, default=[])
    user_id = CharField(max_length=255, null=True, help_text="user_id", index=True)

    class Meta:
        db_table = "conversation"


class APIToken(DataBaseModel):
    tenant_id = CharField(max_length=32, null=False, index=True)
    token = CharField(max_length=255, null=False, index=True)
    dialog_id = CharField(max_length=32, null=True, index=True)
    source = CharField(max_length=16, null=True, help_text="none|agent|dialog", index=True)
    beta = CharField(max_length=255, null=True, index=True)

    class Meta:
        db_table = "api_token"
        primary_key = CompositeKey("tenant_id", "token")


class API4Conversation(DataBaseModel):
    id = CharField(max_length=32, primary_key=True)
    dialog_id = CharField(max_length=32, null=False, index=True)
    user_id = CharField(max_length=255, null=False, help_text="user_id", index=True)
    message = JSONField(null=True)
    reference = JSONField(null=True, default=[])
    tokens = IntegerField(default=0)
    source = CharField(max_length=16, null=True, help_text="none|agent|dialog", index=True)
    dsl = JSONField(null=True, default={})
    duration = FloatField(default=0, index=True)
    round = IntegerField(default=0, index=True)
    thumb_up = IntegerField(default=0, index=True)

    class Meta:
        db_table = "api_4_conversation"


class UserCanvas(DataBaseModel):
    id = CharField(max_length=32, primary_key=True)
    avatar = TextField(null=True, help_text="avatar base64 string")
    user_id = CharField(max_length=255, null=False, help_text="user_id", index=True)
    title = CharField(max_length=255, null=True, help_text="Canvas title")

    permission = CharField(max_length=16, null=False, help_text="me|team", default="me", index=True)
    description = TextField(null=True, help_text="Canvas description")
    canvas_type = CharField(max_length=32, null=True, help_text="Canvas type", index=True)
    dsl = JSONField(null=True, default={})

    class Meta:
        db_table = "user_canvas"


class CanvasTemplate(DataBaseModel):
    id = CharField(max_length=32, primary_key=True)
    avatar = TextField(null=True, help_text="avatar base64 string")
    title = CharField(max_length=255, null=True, help_text="Canvas title")

    description = TextField(null=True, help_text="Canvas description")
    canvas_type = CharField(max_length=32, null=True, help_text="Canvas type", index=True)
    dsl = JSONField(null=True, default={})

    class Meta:
        db_table = "canvas_template"


class UserCanvasVersion(DataBaseModel):
    id = CharField(max_length=32, primary_key=True)
    user_canvas_id = CharField(max_length=255, null=False, help_text="user_canvas_id", index=True)

    title = CharField(max_length=255, null=True, help_text="Canvas title")
    description = TextField(null=True, help_text="Canvas description")
    dsl = JSONField(null=True, default={})

    class Meta:
        db_table = "user_canvas_version"


def migrate_db():
    migrator = DatabaseMigrator[settings.DATABASE_TYPE.upper()].value(DB)
    try:
        migrate(migrator.add_column("file", "source_type", CharField(max_length=128, null=False, default="", help_text="where does this document come from", index=True)))
    except Exception:
        pass
    try:
        migrate(migrator.add_column("tenant", "rerank_id", CharField(max_length=128, null=False, default="BAAI/bge-reranker-v2-m3", help_text="default rerank model ID")))
    except Exception:
        pass
    try:
        migrate(migrator.add_column("dialog", "rerank_id", CharField(max_length=128, null=False, default="", help_text="default rerank model ID")))
    except Exception:
        pass
    try:
        migrate(migrator.add_column("dialog", "top_k", IntegerField(default=1024)))
    except Exception:
        pass
    try:
        migrate(migrator.alter_column_type("tenant_llm", "api_key", CharField(max_length=2048, null=True, help_text="API KEY", index=True)))
    except Exception:
        pass
    try:
        migrate(migrator.add_column("api_token", "source", CharField(max_length=16, null=True, help_text="none|agent|dialog", index=True)))
    except Exception:
        pass
    try:
        migrate(migrator.add_column("tenant", "tts_id", CharField(max_length=256, null=True, help_text="default tts model ID", index=True)))
    except Exception:
        pass
    try:
        migrate(migrator.add_column("api_4_conversation", "source", CharField(max_length=16, null=True, help_text="none|agent|dialog", index=True)))
    except Exception:
        pass
    try:
        migrate(migrator.add_column("task", "retry_count", IntegerField(default=0)))
    except Exception:
        pass
    try:
        migrate(migrator.alter_column_type("api_token", "dialog_id", CharField(max_length=32, null=True, index=True)))
    except Exception:
        pass
    try:
        migrate(migrator.add_column("tenant_llm", "max_tokens", IntegerField(default=8192, index=True)))
    except Exception:
        pass
    try:
        migrate(migrator.add_column("api_4_conversation", "dsl", JSONField(null=True, default={})))
    except Exception:
        pass
    try:
        migrate(migrator.add_column("knowledgebase", "pagerank", IntegerField(default=0, index=False)))
    except Exception:
        pass
    try:
        migrate(migrator.add_column("api_token", "beta", CharField(max_length=255, null=True, index=True)))
    except Exception:
        pass
    try:
        migrate(migrator.add_column("task", "digest", TextField(null=True, help_text="task digest", default="")))
    except Exception:
        pass

    try:
        migrate(migrator.add_column("task", "chunk_ids", LongTextField(null=True, help_text="chunk ids", default="")))
    except Exception:
        pass
    try:
        migrate(migrator.add_column("conversation", "user_id", CharField(max_length=255, null=True, help_text="user_id", index=True)))
    except Exception:
        pass
    try:
        migrate(migrator.add_column("document", "meta_fields", JSONField(null=True, default={})))
    except Exception:
        pass
    try:
        migrate(migrator.add_column("task", "task_type", CharField(max_length=32, null=False, default="")))
    except Exception:
        pass
    try:
        migrate(migrator.add_column("task", "priority", IntegerField(default=0)))
    except Exception:
        pass
    try:
        migrate(migrator.add_column("user_canvas", "permission", CharField(max_length=16, null=False, help_text="me|team", default="me", index=True)))
    except Exception:
        pass
    try:
        migrate(migrator.add_column("llm", "is_tools", BooleanField(null=False, help_text="support tools", default=False)))
    except Exception:
        pass
    try:
        migrate(migrator.add_column("document", "md_location", CharField(max_length=255, null=True, help_text="where does mineru markdown store", index=True)))
    except Exception:
        pass
    try:
        migrate(migrator.add_column("document", "layout_location", CharField(max_length=255, null=True, help_text="where does mineru layout pdf store", index=True)))
    except Exception:
        pass
    try:
        migrate(migrator.add_column("document", "filter_fields",  JSONField(null=True, default={'limit_range':[],'limit_level':1,'limit_time':0})))
    except Exception:
        pass


# 在数据库连接配置中添加连接池和重连参数
# 例如（具体参数取决于你使用的数据库类型）:

# 对于达梦数据库，可能需要添加：
connection_params = {
    'autocommit': True,
    'timeout': 30,
    # 其他连接参数...
}

# 添加连接健康检查
def check_connection_health(database):
    """检查数据库连接健康状态"""
    try:
        # 执行简单查询测试连接
        cursor = database.execute_sql("SELECT 1")
        cursor.fetchone()
        return True
    except Exception as e:
        logging.warning(f"Database connection health check failed: {e}")
        return False

# 在需要的地方调用健康检查
def ensure_connection(database):
    """确保数据库连接可用"""
    if not check_connection_health(database):
        try:
            close_connection()
            # 重新建立连接
            database.connect()
        except Exception as e:
            logging.error(f"Failed to re-establish database connection: {e}")

# 在文件末尾，确保正确初始化
try:
    DB = BaseDataBase().database_connection
    DB.lock = DatabaseLock[settings.DATABASE_TYPE.upper()].value
    logging.info("Database connection initialized successfully")
except Exception as e:
    logging.error(f"Failed to initialize database connection: {e}")
    # 不要在这里抛出异常，让应用继续启动
    DB = None
