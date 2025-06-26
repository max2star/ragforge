#!/usr/bin/env python3
"""
测试RAGFlow用户创建和对话框创建功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5

def encrypt_password(password: str) -> str:
    """使用RSA公钥加密密码"""
    # RSA公钥（与前端使用相同的公钥）
    public_key = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEArq9XTUSeYr2+N1h3Afl/
z8Dse/2yD0ZGrKwx+EEEcdsBLca9Ynmx3nIB5obmLlSfmskLpBo0UACBmB5rEjBp2
Q2f3AG3Hjd4B+gNCG6BDaawuDlgANIhGnaTLrIqWrrcm4EMzJOnAOI1fgzJRsOOUE
faS318Eq9OVO3apEyCCt0lOQK6PuksduOjVxtltDav+guVAA068NrPYmRNabVKRNL
JpL8w4D44sfth5RvZ3q9t+6RTArpEtc5sh5ChzvqPOzKGMXW83C95TxmXqpbK6olN
4RevSfVjEAgCydH6HN6OhtOQEcnrU97r9H0iZOWwbw3pVrZiUkuRD1R56Wzs2wID
AQAB
-----END PUBLIC KEY-----"""
    
    try:
        # 将密码进行base64编码
        password_bytes = password.encode('utf-8')
        password_b64 = base64.b64encode(password_bytes).decode('utf-8')
        
        # 使用RSA公钥加密
        rsa_key = RSA.importKey(public_key)
        cipher = Cipher_pkcs1_v1_5.new(rsa_key)
        encrypted = cipher.encrypt(password_b64.encode('utf-8'))
        
        # 返回base64编码的加密结果
        return base64.b64encode(encrypted).decode('utf-8')
    except Exception as e:
        print(f"❌ 密码加密失败: {e}")
        return None

def create_user_and_test_dialog():
    """创建用户并测试对话框创建"""
    print("🔐 RAGFlow 用户创建和对话框测试")
    print("=" * 50)
    
    # 用户信息
    email = "test@example.com"
    password = "test123456"
    
    print(f"📧 邮箱: {email}")
    print(f"🔑 密码: {password}")
    print()
    
    # 加密密码
    encrypted_password = encrypt_password(password)
    if not encrypted_password:
        print("❌ 密码加密失败，无法继续")
        return
    
    print("✅ 密码加密成功")
    
    try:
        # 1. 创建用户
        print("\n📤 创建用户...")
        register_response = requests.post(
            "http://localhost:9380/v1/user/register",
            json={
                "email": email,
                "password": encrypted_password,
                "nickname": "Test User"
            },
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📤 注册响应状态码: {register_response.status_code}")
        print(f"📤 注册响应内容: {register_response.text}")
        
        if register_response.status_code == 200:
            register_data = register_response.json()
            if register_data.get('code') == 0:
                print("✅ 用户创建成功")
            else:
                print(f"⚠️ 用户创建警告: {register_data.get('message')}")
        else:
            print(f"❌ 用户创建失败: HTTP {register_response.status_code}")
        
        # 2. 登录获取token
        print("\n📤 登录获取token...")
        login_response = requests.post(
            "http://localhost:9380/v1/user/login",
            json={"email": email, "password": encrypted_password},
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📤 登录响应状态码: {login_response.status_code}")
        print(f"📤 登录响应内容: {login_response.text}")
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            if login_data.get('code') == 0:
                access_token = login_data['data']['access_token']
                print("✅ 登录成功")
                
                # 3. 创建JWT token - 使用固定的SECRET_KEY
                from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
                
                # 使用固定的SECRET_KEY，与服务器保持一致
                secret_key = "2024-06-26"
                serializer = Serializer(secret_key)
                jwt_token = serializer.dumps(access_token)
                print("✅ JWT token创建成功")
                
                # 4. 测试对话框创建
                print("\n📤 测试对话框创建...")
                dialog_data = {
                    "name": "Test Dialog",
                    "description": "Test dialog for vector_similarity_weight fix",
                    "kb_ids": [],
                    "llm_id": "qwen_large",
                    "llm_setting": "{}",
                    "prompt_type": "basic",
                    "prompt_config": {
                        "system": "你是一个智能助手，请总结知识库的内容来回答问题，请列举知识库中的数据详细回答。当所有知识库内容都与问题无关时，你的回答必须包括\"知识库中未找到您要的答案！\"这句话。回答需要考虑聊天历史。\n以下是知识库：\n{knowledge}\n以上是知识库。",
                        "prologue": "您好，我是您的助手小樱，长得可爱又善良，can I help you?",
                        "parameters": [
                            {"key": "knowledge", "optional": False}
                        ],
                        "empty_response": "Sorry! 知识库中未找到相关内容！"
                    }
                }
                
                dialog_response = requests.post(
                    "http://localhost:9380/v1/dialog/set",
                    json=dialog_data,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': jwt_token
                    }
                )
                
                print(f"📤 对话框创建响应状态码: {dialog_response.status_code}")
                print(f"📤 对话框创建响应内容: {dialog_response.text}")
                
                if dialog_response.status_code == 200:
                    dialog_data = dialog_response.json()
                    if dialog_data.get('code') == 0:
                        print("✅ 对话框创建成功！vector_similarity_weight问题已修复！")
                    else:
                        print(f"❌ 对话框创建失败: {dialog_data.get('message')}")
                else:
                    print(f"❌ 对话框创建失败: HTTP {dialog_response.status_code}")
            else:
                print(f"❌ 登录失败: {login_data.get('message')}")
        else:
            print(f"❌ 登录失败: HTTP {login_response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_user_and_test_dialog() 