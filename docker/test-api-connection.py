#!/usr/bin/env python3
"""
测试后端API的数据库连接配置
"""

import sys
import pymysql
import redis

def test_mysql_connection():
    """测试MySQL连接"""
    print("=== 测试MySQL连接 ===")
    try:
        # 使用配置文件中的参数
        connection = pymysql.connect(
            host='localhost',
            port=5455,
            user='root',
            password='infini_rag_flow',
            database='rag_flow',
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f"✓ MySQL连接成功: {result}")
        
        connection.close()
        return True
    except Exception as e:
        print(f"✗ MySQL连接失败: {e}")
        return False

def test_redis_connection():
    """测试Redis连接"""
    print("\n=== 测试Redis连接 ===")
    try:
        r = redis.Redis(
            host='localhost',
            port=16379,
            password='infini_rag_flow',
            db=1,
            decode_responses=True
        )
        result = r.ping()
        print(f"✓ Redis连接成功: {result}")
        return True
    except Exception as e:
        print(f"✗ Redis连接失败: {e}")
        return False

def main():
    """主函数"""
    print("RAGForge 后端API MySQL/Redis连接测试")
    print("=" * 50)
    
    # 测试MySQL连接
    mysql_ok = test_mysql_connection()
    redis_ok = test_redis_connection()
    
    # 总结
    print("\n" + "=" * 50)
    print("测试结果总结:")
    print(f"MySQL: {'✓' if mysql_ok else '✗'}")
    print(f"Redis: {'✓' if redis_ok else '✗'}")
    
    if mysql_ok and redis_ok:
        print("\n🎉 MySQL/Redis连接正常！后端API应该可以正常启动。")
        return 0
    else:
        print("\n❌ MySQL或Redis连接失败，请检查配置。")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 