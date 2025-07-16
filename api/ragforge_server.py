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

# from beartype import BeartypeConf
# from beartype.claw import beartype_all  # <-- you didn't sign up for this
# beartype_all(conf=BeartypeConf(violation_type=UserWarning))    # <-- emit warnings from all code

from api.utils.log_utils import initRootLogger
initRootLogger("ragforge_server")

import logging
import os
import signal
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
import threading
import uuid
import functools
import gc

from werkzeug.serving import run_simple
from api import settings
from api.apps import app
from api.db.runtime_config import RuntimeConfig
from api.db.services.document_service import DocumentService
from api import utils

from api.db.db_models import init_database_tables as init_web_db, close_connection
from api.db.init_data import init_web_data
from api.versions import get_ragforge_version
from api.utils import show_configs
from rag.settings import print_rag_settings
from rag.utils.redis_conn import RedisDistributedLock

stop_event = threading.Event()

RAGFORGE_DEBUGPY_LISTEN = int(os.environ.get('RAGFORGE_DEBUGPY_LISTEN', "0"))

def database_retry(max_retries=3, retry_delay=1):
    """数据库操作重试装饰器"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    error_str = str(e).lower()

                    # 检查是否是数据库相关错误
                    is_db_error = any(keyword in error_str for keyword in [
                        'closed cursor', 'connection', 'database', 'timeout',
                        'lost connection', 'server has gone away', 'broken pipe'
                    ])

                    if is_db_error and attempt < max_retries - 1:
                        logging.warning(f"Database connection issue in {func.__name__} on attempt {attempt + 1}: {e}")
                        try:
                            # 强制关闭所有连接
                            close_connection()
                            # 强制垃圾回收
                            gc.collect()
                        except Exception as cleanup_error:
                            logging.warning(f"Connection cleanup failed: {cleanup_error}")

                        # 指数退避
                        sleep_time = retry_delay * (2 ** attempt)
                        time.sleep(sleep_time)
                        continue
                    else:
                        logging.error(f"{func.__name__} exception: {e}")
                        logging.error(f"Full traceback: {traceback.format_exc()}")
                        break

            if last_exception:
                # 记录最终失败
                logging.error(f"{func.__name__} failed after {max_retries} attempts")
                # 不抛出异常，返回None避免程序崩溃
                return None
            return None
        return wrapper
    return decorator

# 添加连接状态监控
def log_database_status():
    """记录数据库连接状态"""
    try:
        from api.db.db_models import DB
        if hasattr(DB, 'is_closed'):
            status = 'Closed' if DB.is_closed() else 'Connected'
        else:
            status = 'Unknown'
        logging.debug(f"Database connection status: {status}")
    except Exception as e:
        logging.warning(f"Failed to check database status: {e}")

# 使用装饰器修饰 update_progress 函数
@database_retry(max_retries=3, retry_delay=2)
def update_progress():
    lock_value = str(uuid.uuid4())
    redis_lock = RedisDistributedLock("update_progress", lock_value=lock_value, timeout=60)
    logging.info(f"update_progress lock_value: {lock_value}")
    result = None
    while not stop_event.is_set():
        try:
            if redis_lock.acquire():
                """更新文档处理进度"""
                log_database_status()
                DocumentService.update_progress()
                result = True
                redis_lock.release()
            stop_event.wait(6)
        except Exception as e:
            logging.exception(f"update_progress exception: {e}")
        finally:
            redis_lock.release()
    return result

def safe_update_progress():
    """安全的进度更新函数，防止崩溃"""
    while not stop_event.is_set():
        try:
            # 等待30秒后执行
            if stop_event.wait(30):
                break

            result = update_progress()
            if result is None:
                logging.warning("update_progress returned None")

        except Exception as e:
            logging.error(f"safe_update_progress caught exception: {e}")
            logging.error(f"Full traceback: {traceback.format_exc()}")

        # 无论成功失败都继续循环

def signal_handler(sig, frame):
    logging.info("Received interrupt signal, shutting down...")
    stop_event.set()
    logging.error(f"收到信号 {sig}")
    logging.error(f"当前堆栈:")
    traceback.print_stack(frame)
    time.sleep(1)
    sys.exit(0)

# 注册信号处理器
signal.signal(signal.SIGSEGV, signal_handler)  # 段错误
signal.signal(signal.SIGABRT, signal_handler)  # 异常终止

# 添加内存监控
def monitor_memory():
    """监控内存使用情况"""
    try:
        import psutil
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        logging.info(f"Memory usage: RSS={memory_info.rss / 1024 / 1024:.2f}MB, VMS={memory_info.vms / 1024 / 1024:.2f}MB")

        # 如果内存使用过高，强制垃圾回收
        if memory_info.rss > 1024 * 1024 * 1024:  # 1GB
            logging.warning("High memory usage detected, forcing garbage collection")
            gc.collect()

    except ImportError:
        logging.debug("psutil not available, skipping memory monitoring")
    except Exception as e:
        logging.warning(f"Memory monitoring failed: {e}")

def periodic_maintenance():
    """定期维护任务"""
    while not stop_event.is_set():
        try:
            # 每5分钟执行一次维护
            if stop_event.wait(300):  # 5分钟
                break

            logging.debug("Running periodic maintenance")

            # 内存监控
            monitor_memory()

            # 数据库连接清理
            try:
                close_connection()
            except Exception as e:
                logging.warning(f"Database cleanup failed: {e}")

            # 强制垃圾回收
            gc.collect()

        except Exception as e:
            logging.error(f"Periodic maintenance failed: {e}")

if __name__ == '__main__':
    logging.info("🚀 RAGForge Server Starting...")
    logging.info(f'RAGForge version: {get_ragforge_version()}')
    logging.info(f'project base: {utils.file_utils.get_project_base_directory()}')

    try:
        show_configs()
        settings.init_settings()
        print_rag_settings()
    except Exception as e:
        logging.error(f"Configuration initialization failed: {e}")
        sys.exit(1)

    if RAGFORGE_DEBUGPY_LISTEN > 0:
        logging.info(f"debugpy listen on {RAGFORGE_DEBUGPY_LISTEN}")
        import debugpy
        debugpy.listen(("0.0.0.0", RAGFORGE_DEBUGPY_LISTEN))

    # init db
    # 只需要执行一次，成功后注释
    #TODO 这个有配置文件更新等需要写入数据库，不能只执行一次;需要修改
    init_web_db()
    init_web_data()

    # init runtime config
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--version", default=False, help="RAGForge version", action="store_true"
    )
    parser.add_argument(
        "--debug", default=False, help="debug mode", action="store_true"
    )
    args = parser.parse_args()
    if args.version:
        print(get_ragforge_version())
        sys.exit(0)

    RuntimeConfig.DEBUG = args.debug
    if RuntimeConfig.DEBUG:
        logging.info("run on debug mode")

    try:
        RuntimeConfig.init_env()
        RuntimeConfig.init_config(JOB_SERVER_HOST=settings.HOST_IP, HTTP_PORT=settings.HOST_PORT)
    except Exception as e:
        logging.error(f"Runtime configuration failed: {e}")
        sys.exit(1)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # thread = ThreadPoolExecutor(max_workers=1)
    # thread.submit(update_progress)
    # 启动后台任务
    executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="ragforge-bg")

    try:
        # 启动进度更新任务 - 改为循环任务而不是递归调用
        executor.submit(safe_update_progress)

        # 启动定期维护任务
        executor.submit(periodic_maintenance)

        logging.info("Background tasks started successfully")

    except Exception as e:
        logging.error(f"Failed to start background tasks: {e}")

    # start http server
    # 启动HTTP服务器
    try:
        logging.info("RAGForge HTTP server starting...")
        run_simple(
            hostname=settings.HOST_IP,
            port=settings.HOST_PORT,
            application=app,
            threaded=True,
            use_reloader=RuntimeConfig.DEBUG,
            use_debugger=RuntimeConfig.DEBUG,
        )
    except Exception as e:
        logging.error(f"HTTP server failed: {e}")
        logging.error(f"Full traceback: {traceback.format_exc()}")

        traceback.print_exc()
        # 清理资源
        stop_event.set()
        try:
            executor.shutdown(wait=False)
            close_connection()
        except:
            pass

        time.sleep(1)
        os.kill(os.getpid(), signal.SIGKILL)

# 如果有其他类似的定时任务函数，也需要添加类似的错误处理
def safe_database_operation(operation_name, operation_func, *args, **kwargs):
    """安全执行数据库操作的通用函数"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return operation_func(*args, **kwargs)
        except Exception as e:
            error_str = str(e).lower()
            is_db_error = any(keyword in error_str for keyword in [
                'closed cursor', 'connection', 'database', 'timeout'
            ])

            if is_db_error and attempt < max_retries - 1:
                logging.warning(f"Database connection issue in {operation_name} on attempt {attempt + 1}: {e}")
                try:
                    close_connection()
                    gc.collect()
                except:
                    pass
                time.sleep(2 ** attempt)  # 指数退避
                continue
            else:
                logging.error(f"{operation_name} exception: {e}")
                logging.error(f"Full traceback: {traceback.format_exc()}")
                return None
    return None
