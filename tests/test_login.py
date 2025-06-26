#!/usr/bin/env python3
"""
测试RAGFlow登录功能
"""

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
        password_base64 = base64.b64encode(password.encode('utf-8')).decode("utf-8")
        
        # 使用RSA公钥加密
        rsa_key = RSA.importKey(public_key)
        cipher = Cipher_pkcs1_v1_5.new(rsa_key)
        encrypted_password = cipher.encrypt(password_base64.encode())
        
        # 返回base64编码的加密结果
        return base64.b64encode(encrypted_password).decode('utf-8')
    except Exception as e:
        raise Exception(f"密码加密失败: {e}")

def test_login(email: str, password: str):
    """测试登录功能"""
    try:
        # 加密密码
        encrypted_password = encrypt_password(password)
        print(f"✅ 密码加密成功")
        
        # 发送登录请求
        response = requests.post(
            "http://localhost:9380/v1/user/login",
            json={"email": email, "password": encrypted_password},
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📤 登录响应状态码: {response.status_code}")
        print(f"📤 登录响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 0:
                print("✅ 登录成功！")
                return True
            else:
                print(f"❌ 登录失败: {data.get('message', '未知错误')}")
                return False
        else:
            print(f"❌ 请求失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 登录测试错误: {e}")
        return False

if __name__ == "__main__":
    print("🔐 RAGFlow 登录测试")
    print("=" * 50)
    
    # 测试用户凭据
    email = "test@example.com"
    password = "infini_rag_flow"
    
    print(f"📧 邮箱: {email}")
    print(f"🔑 密码: {password}")
    print()
    
    success = test_login(email, password)
    
    if success:
        print("\n🎉 登录测试成功！CLI工具应该可以正常工作了。")
    else:
        print("\n❌ 登录测试失败，请检查用户凭据或系统状态。") 