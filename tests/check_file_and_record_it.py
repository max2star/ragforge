import requests
import os
import json
from datetime import datetime

class Logger:
    # 生成带时间戳的文件名（精确到秒）
    time_format = "%Y-%m-%d %H:%M:%S"
    timestamp_format = "%Y%m%d%H%M%S"
    timestamp = datetime.now().strftime(timestamp_format)
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = f"logs/app_{timestamp}.log"

    def __init__(self):
        pass

    def save(self, msg, level="INFO"):
        if type(msg) == dict:
            msg = json.dumps(msg, indent=4, ensure_ascii=False, default=str)
        level = level.upper()
        time_tmp = datetime.now().strftime(self.time_format)
        write_in = "[{}] [{}] {}".format(time_tmp, level, msg)
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(write_in + "\n")
            if level not in ["DEBUG"]:
                print(write_in)
        except UnicodeEncodeError as e:
            # 处理特殊字符情况
            write_in = write_in.encode('utf-8', errors='replace').decode('utf-8')
            with open(self.log_file, 'a', encoding='utf-8', errors='replace') as f:
                f.write(write_in + "\n" + str(e) + "\n")
            print(write_in + "\n" + str(e))
        except Exception as e:
            print(write_in + "\n" + str(e))
            raise

    def info(self, msg):
        self.save(msg)

    def error(self, msg):
        self.save(msg, level="ERROR")

    def debug(self, msg):
        self.save(msg, level="DEBUG")


logging = Logger()
timestamp = logging.timestamp

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

    logging.info(f"列表文档使用的参数 {json.dumps(payload, indent=4, ensure_ascii=False)}")
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
        logging.info(f"list doc✅ 响应成功!")
        return dict(res) if dict(res).get("code") == 200 else None
    else:
        logging.error(
            f"list doc ❌ 响应失败! 状态码: {response.status_code}, 错误信息: \n{json.dumps(dict(json.loads(response.text)), indent=4, ensure_ascii=False)}")
        return None


def trigger_parse(ip, host, fileId, resourceId):
    url = f"http://{ip}:{host}/op-api/api/v1/ragforge/executeRag"
    # [{"fileId":"93f9a3de7c504e539078207001439398","resourceId":1655,"embeddingConfigCode":""}]
    file_ = {
        "fileId": fileId,
        "embeddingConfigCode": ""
    }
    if resourceId:
        file_['resourceId'] = resourceId
    payload = [file_]

    logging.info(f"触发文档解析使用的参数 {json.dumps(payload, indent=4, ensure_ascii=False)}")
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
        logging.info(f"trigger_parse ✅ 响应成功! 响应结果: \n{json.dumps(dict(res), indent=4, ensure_ascii=False)}")
        return dict(res) if dict(res).get("code") == 200 else None
    else:
        logging.error(
            f"trigger_parse ❌ 响应失败! 状态码: {response.status_code}, 错误信息: \n{json.dumps(dict(json.loads(response.text)), indent=4, ensure_ascii=False)}")
        return None


if __name__ == '__main__':
    # 对特定状态任务执行抽取开始操作
    # 只需 父文件夹id
    NEW_DIRS = [6886,]
    IP = "101.52.216.178"
    PORT = 9090
    # 任务执行类型
    class Status:
        NOT_START = 1
        SUCCESS = 2
        FAIL = 3
    indexingStatus = Status.FAIL
    # indexingStatus = Status.NOT_START
    # indexingStatus = Status.SUCCESS
    total_num = 0
    for folderId in NEW_DIRS:
        num = 0
        try:
            res = list_docs(ip=IP,host=PORT,folderId=folderId,indexingStatus=indexingStatus)
        except Exception as e:
            logging.error(f"list_docs {e}")
            continue
        if res:
            logging.info("获取结果如下")
            for doc in res['data']:
                try:
                    logging.info("{} {} {} {} {} {}".format(doc['id'],doc['name'],doc['parentId'],doc['folderId'],doc['guid'],doc['fileType']))
                    trigger_parse(IP, PORT, doc['guid'], doc['id'])
                    num += 1
                except Exception as e:
                    logging.error(f"trigger_parse {e}")
        total_num += num
        logging.info(f"folderId {folderId} 调用执行任务成功数： {num}")
    logging.info(f"调用执行任务成功数 共计： {total_num}")
