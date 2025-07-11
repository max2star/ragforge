#!/usr/bin/env python3
"""
测试 API 连接
"""

import mysql.connector
import redis
import requests
import json

def test_mysql_connection():
    """测试 MySQL 连接"""
    try:
        connection = mysql.connector.connect(
            host='172.16.1.50',
            port=5455,
            user='root',
            password='ragforge123',
            database='ragforge',
        )
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"✅ MySQL 连接成功 - 服务器版本: {db_info}")
            
            cursor = connection.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            print(f"✅ 当前数据库: {record[0]}")
        
            cursor.close()
        connection.close()
        return True
        else:
            print("❌ MySQL 连接失败")
            return False
            
    except Exception as e:
        print(f"❌ MySQL 连接错误: {e}")
        return False

def test_redis_connection():
    """测试 Redis 连接"""
    try:
        r = redis.Redis(
            host='172.16.1.50',
            port=16379,
            password='ragforge123',
            decode_responses=True
        )
        
        # 测试连接
        response = r.ping()
        if response:
            print("✅ Redis 连接成功")
            return True
        else:
            print("❌ Redis 连接失败")
            return False
            
    except Exception as e:
        print(f"❌ Redis 连接错误: {e}")
        return False

def test_elasticsearch_connection():
    """测试 Elasticsearch 连接"""
    try:
        response = requests.get('http://172.16.1.50:1200', timeout=5)
        if response.status_code == 200:
            print("✅ Elasticsearch 连接成功")
            return True
        else:
            print(f"❌ Elasticsearch 连接失败 - 状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Elasticsearch 连接错误: {e}")
        return False

def test_minio_connection():
    """测试 MinIO 连接"""
    try:
        response = requests.get('http://172.16.1.50:19000', timeout=5)
        if response.status_code == 200:
            print("✅ MinIO 连接成功")
        return True
        else:
            print(f"❌ MinIO 连接失败 - 状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ MinIO 连接错误: {e}")
        return False

def main():
    """主函数"""
    print("=== API 连接测试 ===")
    
    results = {
        'mysql': test_mysql_connection(),
        'redis': test_redis_connection(),
        'elasticsearch': test_elasticsearch_connection(),
        'minio': test_minio_connection()
    }
    
    print("\n=== 测试结果 ===")
    for service, result in results.items():
        status = "✅ 成功" if result else "❌ 失败"
        print(f"{service}: {status}")
    
    success_count = sum(results.values())
    total_count = len(results)
    
    print(f"\n总结: {success_count}/{total_count} 个服务连接成功")
    
    if success_count == total_count:
        print("🎉 所有服务连接正常！")
    else:
        print("⚠️ 部分服务连接失败，请检查配置")

if __name__ == "__main__":
    main() 