import requests
import os
from glob import glob
import json
from datetime import datetime

# 生成带时间戳的文件名（精确到秒）
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = f"logs/app_{timestamp}.log"

def upload(ip, host, file_path=None):
    
    if file_path is None:
        print(f"file_path is None")
        return None
    url = f"http://{ip}:{host}/kmFile-api/api/v1/file/uploadFile"

    payload = {}
    with open(file_path, 'rb') as f:
        files = {
            'file' : (os.path.basename(file_path), f, 'application/pdf')
        }
        print(files)
        headers = {
            'Cookie': 'token=D2AE19437BF84256628E0AD77E6BE415',
            'Accept': '*/*',
            'Host': f'{ip}:{host}',
        }

        response = requests.post(url, headers=headers, data=payload, files=files)

    # 检查响应状态
    if response.status_code == 200:
        res = json.loads(response.text)
        print(f"upload ✅ 响应成功! 响应结果: \n{json.dumps(dict(res),indent=4,ensure_ascii=False)}")
        return dict(res) if dict(res).get("code") == 200 else None
    else:
        print(f"upload ❌ 响应失败! 状态码: {response.status_code}, 错误信息: \n{json.dumps(dict(json.loads(response.text)),indent=4,ensure_ascii=False)}")
        return None


def confirm_up(ip, host, res=None,folderId=None):
    if res is None:
        return None
    if folderId is None:
        return None

    url = f"http://{ip}:{host}/op-api/api/v1/km/saveFileSpecial"

    payload = {
        "folderId": folderId,
        "fileList": [{
            "id": None,
            "guid": res["data"]["guid"],
            "name": res["data"]["originName"],
            "fileId": res["data"]["guid"],
            "size": res["data"]["size"],
            "fileType": res["data"]["suffix"],
            "embeddingConfigName": "",
            "embeddingConfigCode": "",
            "level": "1",
            "scopeRule": "ONLY_ME"
        }]
    }

    print(f"保存文件的使用的数据为 {json.dumps(payload, indent=4, ensure_ascii=False)}")
    headers = {
        'Cookie': 'token=D2AE19437BF84256628E0AD77E6BE415',
        'Accept': '*/*',
        'Content-Type': 'application/json',
        'Host': f'{ip}:{host}',
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    # 检查响应状态
    if response.status_code == 200:
        res = json.loads(response.text)
        print(f"confirm_up ✅ 响应成功! 响应结果: \n{json.dumps(dict(res), indent=4, ensure_ascii=False)}")
        return dict(res) if dict(res).get("code") == 200 else None
    else:
        print(
            f"confirm_up ❌ 响应失败! 状态码: {response.status_code}, 错误信息: \n{json.dumps(dict(json.loads(response.text)), indent=4, ensure_ascii=False)}")
        return None


def trigger_parse(ip, host,fileId,resourceId):
    
    url = f"http://{ip}:{host}/op-api/api/v1/ragflow/executeRag"
    #[{"fileId":"93f9a3de7c504e539078207001439398","resourceId":1655,"embeddingConfigCode":""}]
    file_= {
        "fileId":fileId ,
        "embeddingConfigCode":""
    }
    if resourceId:
        file_['resourceId'] =  resourceId
    payload = [file_]
    
    print(f"触发文档解析使用的参数 {json.dumps(payload, indent=4, ensure_ascii=False)}")
    headers = {
        'Cookie': 'token=D2AE19437BF84256628E0AD77E6BE415',
        'Accept': '*/*',
        'Content-Type': 'application/json',
        'Host': f'{ip}:{host}',
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    # 检查响应状态
    if response.status_code == 200:
        res = json.loads(response.text)
        print(f"trigger_parse ✅ 响应成功! 响应结果: \n{json.dumps(dict(res), indent=4, ensure_ascii=False)}")
        return dict(res) if dict(res).get("code") == 200 else None
    else:
        print(
            f"trigger_parse ❌ 响应失败! 状态码: {response.status_code}, 错误信息: \n{json.dumps(dict(json.loads(response.text)), indent=4, ensure_ascii=False)}")
        return None


def list_docs(ip, host,folderId):
   
    url = f"http://{ip}:{host}/op-api/api/v1/km/resourceListRight"
    
    #由于是按照timeSort降序排序，因此一般传后，前10个里肯定能搜索到刚上传的文档。如果批量可就不一定了！这个接口最好改成直接过滤filerId返回resourceId
    payload = {
            "pageNum":1,
            "pageSize":10,
            "parentId":folderId,
            "fileYearList":[],
            "embeddingConfigNameList":[],
            "timeSort":"desc",
            "nameSort":"desc"
            }

    print(f"列表文档使用的参数 {json.dumps(payload, indent=4, ensure_ascii=False)}")
    headers = {
        'Cookie': 'token=D2AE19437BF84256628E0AD77E6BE415',
        'Accept': '*/*',
        'Content-Type': 'application/json',
        'Host': f'{ip}:{host}',
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    # 检查响应状态
    if response.status_code == 200:
        res = json.loads(response.text)
        print(f"list doc✅ 响应成功! 响应结果: \n{json.dumps(dict(res), indent=4, ensure_ascii=False)}")
        return dict(res) if dict(res).get("code") == 200 else None
    else:
        print(
            f"list doc ❌ 响应失败! 状态码: {response.status_code}, 错误信息: \n{json.dumps(dict(json.loads(response.text)), indent=4, ensure_ascii=False)}")
        return None

if __name__ == '__main__':
    UPLOAD_DIR = [
        # "D:/App/baidu/下载/1",
        "/opt/ragflow/tests/",
    ]
    IP = "101.52.216.178"
    PORT = 9090
    folderId = 438
    for i in UPLOAD_DIR:
        file_paths = glob(os.path.join(i, '*pdf'))
        # 过滤掉目录
        file_paths = [fp for fp in file_paths if os.path.isfile(fp)]
        if not file_paths:
            print("⚠️ 没有找到可上传的文件")
            continue

        for j in file_paths:
            print(f"==========================当前正在处理 {j}")
            success = False
            res_dict = upload(ip=IP, host=PORT,file_path=j)
            if res_dict is not None:
                print(f"upload 返回的数据为{res_dict}")
                fileId = res_dict["data"]["guid"]
                res = confirm_up(ip=IP, host=PORT,res=res_dict,folderId=folderId)
                if res is not None:
                    print(f"confirm_up 返回的数据为{res}")
                    list_result = list_docs(ip=IP, host=PORT,folderId=folderId)
                    #print(f"list 返回的数据为{list_result}")
                    resourceId = None
                    for da_ in list_result.get('data',[]):
                        if da_['fileId'] == fileId:
                            resourceId = da_['id']
                            break
                    if resourceId:
                        print(f"搜索到了文档ID {fileId}的 资源ID 为{resourceId},触发解析...")
                        result = trigger_parse(ip=IP, host=PORT,fileId=fileId,resourceId=resourceId)
                        if result:
                            print(f"trigger_parse 返回的数据为{result}")
                            success = True
                    else:
                        print(f"没有搜索到文档ID {fileId}的 资源ID")
            if success:
                print(f"最终成功处理 {j}")
                # 写入成功文件记录
                with open(f"logs/Success_{timestamp}.log", 'a') as f:
                    f.write(f"{j}\n")
            else:
                print(f"最终处理失败 {j}")
                # 写入失败文件
                with open(f"logs/Failed_{timestamp}.log", 'a') as f:
                    f.write(f"{j}\n")
