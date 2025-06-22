import requests
import os
from glob import glob
import json
from datetime import datetime
from collections import defaultdict

# 生成带时间戳的文件名（精确到秒）
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = f"logs/check_file_{timestamp}.log"

def list_docs(ip, host,folderId,indexingStatus=None):
   
    url = f"http://{ip}:{host}/op-api/api/v1/km/resourceListRight"
    
    #由于是按照timeSort降序排序，因此一般传后，前10个里肯定能搜索到刚上传的文档。如果批量可就不一定了！这个接口最好改成直接过滤filerId返回resourceId
    payload = {
            "pageNum":1,
            "pageSize":10000000,
            "parentId":folderId,
            "fileYearList":[],
            "embeddingConfigNameList":[],
            "timeSort":"desc",
            "nameSort":"desc"
            }
    if indexingStatus:
        payload['indexingStatus'] = indexingStatus

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
    #请映射好本地根目录和要上传的根目录ID；程序会按照本地根目录在系统对应根目录下创建子目录和文件
    NEW_DIRS = {
            "/opt/ragflow/tests/":438
            }
    IP = "101.52.216.178"
    PORT = 9090
    #查看提取失败的
    indexingStatus = 3
    res = list_docs(ip=IP,host=PORT,folderId=438,indexingStatus=indexingStatus)
    print("获取结果如下")
    for doc in res['data']:
        print(doc['id'],doc['name'],doc['parentId'],doc['folderId'],doc['guid'],doc['fileType'])
