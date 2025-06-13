import requests
from  loguru import logger
import os
from glob import glob
import json

def upload_files(api_url, kb_id, file_paths,api_key):
    """
    批量上传文件到API接口
    
    参数:
    api_url (str): API接口URL
    kb_id (str): 知识库ID
    file_paths (list): 要上传的文件路径列表
    """
    # 准备文件列表
    files = [('file', (os.path.basename(fp), open(fp, 'rb'))) for fp in file_paths]

    headers = {
        'Authorization': f'{api_key}',
        #'Accept':"application/json",
        #'Content-Type': 'application/json',
    }

    # 准备表单数据
    data = {'kb_id': kb_id}
    try:
        response = requests.post(
            url=api_url,
            data=data,
            headers = headers,
            files=files
        )
        
        # 检查响应状态
        if response.status_code == 200:
            res = json.loads(response.text)
            print(f"✅ 上传成功! 响应: {response.text},结果: {res}")
            #run_doc_ids = []
            #for d in res['data']:
            #    print(d['id'])
            #    run_doc_ids.append(d['id'])
            #data_run = {
            #    'doc_ids':run_doc_ids,
            #    'run':1,
            #    'delete':False,
            #}
            #headers_run = {
            #    'Authorization': f'{api_key}',
            #    'Accept':"application/json",
            #    'Content-Type': 'application/json',
            #}
            ##运行
            #run_response = requests.post(
            #    url="http://101.52.216.166/v1/document/run",
            #    data=json.dumps(data_run),
            #    headers = headers_run
            #)
            #print(f"运行 响应: {run_response} {run_response.text}")

        else:
            print(f"❌ 上传失败! 状态码: {response.status_code}, 错误信息: {response.text}")
    
    except Exception as e:
        print(f"🚨 请求异常: {str(e)}")
    finally:
        # 确保关闭所有文件
        for _, file_tuple in files:
            file_tuple[1].close()

def find_pdf_files(directory):
    """
    查找目录中的所有PDF文件（包括子目录）
    
    参数:
    directory (str): 要搜索的目录路径
    
    返回:
    list: 找到的PDF文件路径列表
    """
    pdf_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))
    return pdf_files

if __name__ == "__main__":
    # 配置参数
    API_URL= "http://101.52.216.166/v1/document/upload"
    KB_ID = "f3e7326a41a411f09b6a760a0c707fd3" #"38bc7fd0416411f0b271760a0c707fd3" #"15be108a415911f0b73c760a0c707fd3" #c4ed4384415211f0a0a4760a0c707fd3" #7bc7c428415111f0850c760a0c707fd3" #"e35d9074412711f09167760a0c707fd3" #"c264db30412111f0b23b760a0c707fd3"
    API_KEY = "ImU2OTVkYmIwNDFhNTExZjA5YWE3NWUwNTYyZTExYzg1Ig.aEDn3A.1fZ9EXIIASjp4iVmsQXRD0c-USw" #ImJlYWE3ZTVlNDBhMDExZjBhNGY0OWViMTY1ZWZmZDk3Ig.aD8xtg.jBCVUnnhFx9pbIZ1JDU6M58OIqE"
    #UPLOAD_DIR = "/path/to/your/files"
    UPLOAD_DIR = "/Volumes/系统/图书（2515册）"
    #UPLOAD_DIR = "/Volumes/系统/图书（294册）"
    #UPLOAD_DIR = "/Volumes/系统/图书（294册）/12"
    #UPLOAD_DIR = "/Volumes/系统/图书（294册）/10"
    #UPLOAD_DIR = "/Volumes/系统/图书（294册）/11"
    #UPLOAD_DIR = "/Volumes/系统/图书（294册）/12"
    #UPLOAD_DIR = "/Volumes/系统/进展报告/2011,2015进展报告（119篇）/单篇PDF/中国核学会2015"
    #UPLOAD_DIR = "/Volumes/系统/进展报告/2011,2015进展报告（119篇）/单篇PDF/中国核学会2011"
    #UPLOAD_DIR = "/Volumes/系统/进展报告/中国核科学技术进展报告（3581篇）/pdf"
    #UPLOAD_DIR = "/Volumes/系统/进展报告/2017年进展报告（724篇）/单篇PDF"
    file_paths = glob(os.path.join(UPLOAD_DIR, '*pdf'))
    # 过滤掉目录
    file_paths = [fp for fp in file_paths if os.path.isfile(fp)]
    if not file_paths:
        print("⚠️ 没有找到可上传的文件")
        exit(1)
    print(file_paths)
    batch_size = 1
    for i in range(0, len(file_paths), batch_size):
        batch = file_paths[i:i+batch_size]
        upload_files(API_URL, KB_ID, batch,API_KEY)
