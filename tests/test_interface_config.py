#!/usr/bin/env python3
"""
测试RAGForge界面配置功能
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
        password_bytes = password.encode('utf-8')
        password_b64 = base64.b64encode(password_bytes).decode('utf-8')
        
        # 使用RSA公钥加密
        key = RSA.import_key(public_key)
        cipher = Cipher_pkcs1_v1_5.new(key)
        encrypted = cipher.encrypt(password_b64.encode('utf-8'))
        encrypted_b64 = base64.b64encode(encrypted).decode('utf-8')
        
        return encrypted_b64
    except Exception as e:
        print(f"加密失败: {e}")
        return password

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
                return data['data']['access_token']
            else:
                print(f"登录失败: {data.get('message')}")
                return None
        else:
            print(f"登录请求失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"登录异常: {e}")
        return None

def register_user(email: str, password: str, nickname: str):
    """注册用户"""
    try:
        # 加密密码
        encrypted_password = encrypt_password(password)
        
        # 发送注册请求
        response = requests.post(
            "http://localhost:9380/v1/user/register",
            json={"email": email, "password": encrypted_password, "nickname": nickname},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 0:
                print("用户注册成功!")
                return True
            else:
                print(f"注册失败: {data.get('message')}")
                return False
        else:
            print(f"注册请求失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"注册异常: {e}")
        return False

def test_interface_config():
    """测试界面配置功能"""
    print("=== 测试RAGForge界面配置功能 ===")
    
    # 0. 先尝试注册用户
    print("\n0. 注册用户...")
    register_success = register_user("admin@ragforge.com", "admin123", "管理员")
    if not register_success:
        print("注册失败或用户已存在")
    
    # 1. 登录获取token
    print("\n1. 登录获取token...")
    token = login_and_get_token("admin@ragforge.com", "admin123")
    if not token:
        print("登录失败，无法继续测试")
        return
    
    print(f"登录成功，获取到token: {token[:20]}...")
    
    # 2. 获取当前界面配置
    print("\n2. 获取当前界面配置...")
    try:
        response = requests.get(
            "http://localhost:9380/v1/system/interface/config",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 0:
                config = data['data']
                print("当前配置:")
                print(f"  - Logo: {'已设置' if config.get('logo') else '未设置'}")
                print(f"  - Favicon: {'已设置' if config.get('favicon') else '未设置'}")
                print(f"  - 登录Logo: {'已设置' if config.get('login_logo') else '未设置'}")
                print(f"  - 欢迎词: {config.get('login_welcome_text', '未设置')}")
            else:
                print(f"获取配置失败: {data.get('message')}")
        else:
            print(f"获取配置请求失败: {response.status_code}")
    except Exception as e:
        print(f"获取配置异常: {e}")
    
    # 3. 保存界面配置
    print("\n3. 保存界面配置...")
    try:
        test_config = {
            "logo": "",
            "favicon": "",
            "login_logo": "",
            "login_welcome_text": "欢迎使用 RAGForge\n智能知识管理与AI助手平台\n测试配置"
        }
        
        response = requests.post(
            "http://localhost:9380/v1/system/interface/config",
            json=test_config,
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 0:
                print("配置保存成功!")
            else:
                print(f"保存配置失败: {data.get('message')}")
        else:
            print(f"保存配置请求失败: {response.status_code}")
    except Exception as e:
        print(f"保存配置异常: {e}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_interface_config() 