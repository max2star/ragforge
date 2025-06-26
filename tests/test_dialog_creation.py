#!/usr/bin/env python3
"""
测试RAGFlow对话框创建功能
"""

import requests
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from api import settings

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
        password_base64 = base64.b64encode(password.encode('utf-8')).decode("utf-8")
        
        # 使用RSA公钥加密
        rsa_key = RSA.importKey(public_key)
        cipher = Cipher_pkcs1_v1_5.new(rsa_key)
        encrypted_password = cipher.encrypt(password_base64.encode())
        
        # 返回base64编码的加密结果
        return base64.b64encode(encrypted_password).decode('utf-8')
    except Exception as e:
        raise Exception(f"密码加密失败: {e}")

def login_and_get_token(email: str, password: str):
    """登录并获取token"""
    try:
        # 加密密码
        encrypted_password = encrypt_password(password)
        
        # 发送登录请求
        response = requests.post(
            "http://localhost:9380/v1/user/login",
            json={"email": email, "password": encrypted_password},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 0:
                # 获取access_token并创建JWT token
                access_token = data['data']['access_token']
                
                # 创建JWT token（模拟前端的做法）
                jwt = Serializer(secret_key=settings.SECRET_KEY)
                jwt_token = jwt.dumps(access_token)
                
                return jwt_token
            else:
                print(f"❌ 登录失败: {data.get('message', '未知错误')}")
                return None
        else:
            print(f"❌ 请求失败: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 登录错误: {e}")
        return None

def create_dialog(token: str):
    """创建对话框"""
    try:
        dialog_data = {
            "name": "Test Dialog",
            "description": "Test dialog for vector_similarity_weight fix",
            "kb_ids": [],
            "llm_id": "gpt-3.5-turbo",
            "vector_similarity_weight": 0.3,
            "similarity_threshold": 0.2,
            "top_n": 6,
            "top_k": 1024,
            "rerank_id": "",
            "llm_setting": {
                "temperature": 0.1,
                "top_p": 0.3,
                "frequency_penalty": 0.7,
                "presence_penalty": 0.4,
                "max_tokens": 512
            },
            "prompt_config": {
                "system": "你是一个智能助手，请总结知识库的内容来回答问题，请列举知识库中的数据详细回答。当所有知识库内容都与问题无关时，你的回答必须包括\"知识库中未找到您要的答案！\"这句话。回答需要考虑聊天历史。\n以下是知识库：\n{knowledge}\n以上是知识库。",
                "prologue": "您好，我是您的助手小樱，长得可爱又善良，can I help you?",
                "parameters": [
                    {"key": "knowledge", "optional": False}
                ],
                "empty_response": "Sorry! 知识库中未找到相关内容！"
            }
        }
        
        response = requests.post(
            "http://localhost:9380/v1/dialog/set",
            json=dialog_data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': token
            }
        )
        
        print(f"📤 创建对话框响应状态码: {response.status_code}")
        print(f"📤 创建对话框响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 0:
                print("✅ 对话框创建成功！")
                return True
            else:
                print(f"❌ 对话框创建失败: {data.get('message', '未知错误')}")
                return False
        else:
            print(f"❌ 请求失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 创建对话框错误: {e}")
        return False

if __name__ == "__main__":
    print("🔐 RAGFlow 对话框创建测试")
    print("=" * 50)
    
    # 测试用户凭据
    email = "test@example.com"
    password = "infini_rag_flow"
    
    print(f"📧 邮箱: {email}")
    print(f"🔑 密码: {password}")
    print()
    
    # 登录获取token
    token = login_and_get_token(email, password)
    if not token:
        print("❌ 登录失败，无法继续测试")
        exit(1)
    
    print(f"✅ 登录成功，获取到token: {token[:20]}...")
    print()
    
    # 创建对话框
    success = create_dialog(token)
    
    if success:
        print("\n🎉 对话框创建测试成功！vector_similarity_weight问题已修复。")
    else:
        print("\n❌ 对话框创建测试失败，vector_similarity_weight问题仍然存在。") 