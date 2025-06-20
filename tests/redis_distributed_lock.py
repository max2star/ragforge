import uuid
import multiprocessing
import time
import redis

# Redis连接配置
PASSWORD = "123456@y"
PORT = 6379
IP = "127.0.0.1"
REDIS_URL = F"redis://:{PASSWORD}@{IP}:{PORT}/0"

class RedisDistributedLock:
    def __init__(self, redis_client, lock_key, expire_time=30, retry_interval=0.1):
        """
        :param redis_client: Redis客户端实例
        :param lock_key: 锁的键名
        :param expire_time: 锁的自动过期时间（秒）
        :param retry_interval: 获取锁失败时的重试间隔（秒）
        """
        self.redis = redis_client
        self.lock_key = lock_key
        self.expire_time = expire_time
        self.retry_interval = retry_interval
        self.identifier = str(uuid.uuid4())  # 唯一标识当前锁的持有者

    def acquire(self, timeout=10):
        """尝试获取锁
        :param timeout: 获取锁的超时时间（秒）
        :return: bool 是否成功获取锁
        """
        end_time = time.monotonic() + timeout
        while time.monotonic() < end_time:
            # 使用SET命令原子操作：NX(不存在才设置), EX(设置过期时间)
            if self.redis.set(self.lock_key, self.identifier, nx=True, ex=self.expire_time):
                return True
            time.sleep(self.retry_interval)
        return False

    def release(self):
        """释放锁（使用Lua脚本保证原子性）"""
        unlock_script = """
        if redis.call("GET", KEYS[1]) == ARGV[1] then
            return redis.call("DEL", KEYS[1])
        else
            return 0
        end
        """
        return bool(self.redis.eval(unlock_script, 1, self.lock_key, self.identifier))

    def __enter__(self):
        if self.acquire():
            return self
        raise TimeoutError("获取分布式锁超时")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()




def worker_process(process_id, redis_url, lock_name, work_duration):
    """工作进程函数"""
    print(f"进程-{process_id} 正在启动...")
    r = redis.Redis.from_url(redis_url)
    lock = RedisDistributedLock(r, lock_name, expire_time=5)

    try:
        # 尝试获取锁
        print(f"进程-{process_id} 正在尝试获取锁...")
        start_time = time.monotonic()
        acquired = lock.acquire(timeout=3)

        if acquired:
            lock_time = time.monotonic() - start_time
            print(f"进程-{process_id} 成功获取锁! 等待时间: {lock_time:.2f}秒")

            # 模拟工作（临界区操作）
            print(f"进程-{process_id} 开始执行工作 (持续{work_duration}秒)...")
            time.sleep(work_duration)
            print(f"进程-{process_id} 工作完成!")
        else:
            print(f"进程-{process_id} 获取锁失败!")
    finally:
        # 确保释放锁
        if acquired:
            lock.release()
            print(f"进程-{process_id} 已释放锁")
        print(f"进程-{process_id} 退出")


def test_distributed_lock():
    """分布式锁测试场景"""
    LOCK_NAME = "test_distributed_lock"

    # 创建两个工作进程
    processes = []
    durations = [2, 3]  # 两个进程的工作时长

    # 启动两个并发进程
    for i in range(2):
        p = multiprocessing.Process(
            target=worker_process,
            args=(i + 1, REDIS_URL, LOCK_NAME, durations[i])
        )
        processes.append(p)
        p.start()

    # 等待所有进程完成
    for p in processes:
        p.join()

    print("\n测试完成!")


# r = redis.Redis(host='localhost', port=6379)
#
# # 方式1：使用with语句（推荐）
# with RedisDistributedLock(r, "payment_lock", expire_time=10):
#     # 在此执行需要加锁的业务代码
#     print("锁已获取，执行业务操作...")
#     time.sleep(5)  # 模拟业务处理
#
# # 方式2：手动获取/释放
# lock = RedisDistributedLock(r, "inventory_lock")
# try:
#     if lock.acquire(timeout=5):
#         print("锁已获取，执行业务操作...")
#     else:
#         print("获取锁失败")
# finally:
#     if lock.release():
#         print("锁已释放")

# 运行测试
if __name__ == "__main__":
    # 注意：确保Redis服务器正在运行
    test_distributed_lock()
