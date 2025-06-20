import requests
from  loguru import logger as logging
# import logging
import os
from glob import glob
import json
from datetime import datetime

# 生成带时间戳的文件名（精确到秒）
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = f"logs/app_{timestamp}.log"

# 配置logging：清除默认设置，添加文件日志
# logging.remove()  # 移除默认输出
logging.add(
    log_file,
    rotation="1000 MB",   # 日志文件最大10MB
    # retention="30 days", # 保留最近30天
    # compression="zip",   # 旧日志自动压缩
    # level="DEBUG"
) # 设置日志级别


def upload(ip="101.52.216.178", host=9090, file_path=None):
    if file_path is None:
        logging.info(f"file_path is None")
        return None
    url = f"http://{ip}:{host}/kmFile-api/api/v1/file/uploadFile"

    payload = {}
    with open(file_path, 'rb') as f:
        files = {
            'file' : (os.path.basename(file_path), f, 'application/pdf')
        }

        logging.info(files)
        headers = {
            'Cookie': 'token=D2AE19437BF84256628E0AD77E6BE415',
            'Accept': '*/*',
            'Host': f'{ip}:{host}',
        }

        response = requests.post(url, headers=headers, data=payload, files=files)

    # 检查响应状态
    if response.status_code == 200:
        res = json.loads(response.text)
        logging.info(f"✅ 响应成功! 响应结果: \n{json.dumps(dict(res),indent=4,ensure_ascii=False)}")
        return dict(res) if dict(res).get("code") == 200 else None
    else:
        logging.info(f"❌ 响应失败! 状态码: {response.status_code}, 错误信息: \n{json.dumps(dict(json.loads(response.text)),indent=4,ensure_ascii=False)}")
        return None


def confirm_up(ip="101.52.216.178", host=9090, res=None):
    if res is None:
        return None
    url = f"http://{ip}:{host}/op-api/api/v1/km/saveFileSpecial"
    # url = f"http://{ip}:{host}/op-api/api/v1/km/saveFile"

    payload = {
        "folderId": 438,
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

    logging.info(f"{json.dumps(payload, indent=4, ensure_ascii=False)}")
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
        logging.info(f"✅ 响应成功! 响应结果: \n{json.dumps(dict(res), indent=4, ensure_ascii=False)}")
        return dict(res) if dict(res).get("code") == 200 else None
    else:
        logging.info(
            f"❌ 响应失败! 状态码: {response.status_code}, 错误信息: \n{json.dumps(dict(json.loads(response.text)), indent=4, ensure_ascii=False)}")
        return None



if __name__ == '__main__':
    UPLOAD_DIR = [
        # "D:/App/baidu/下载/图书",
        # "D:/App/baidu/下载/",
        # "D:/App/baidu/下载/1",
        "D:/App/baidu/报告",
    ]

    for i in UPLOAD_DIR:
        file_paths = glob(os.path.join(i, '*pdf'))
        # 过滤掉目录
        file_paths = [fp for fp in file_paths if os.path.isfile(fp)]
        if not file_paths:
            logging.info("⚠️ 没有找到可上传的文件")
            continue

        for j in file_paths:
            logging.info(j)
            success = False
            res_dict = upload(ip="101.52.216.178", host=9090,file_path=j)
            if res_dict is not None:
                res = confirm_up(ip="101.52.216.178", host=9090,res=res_dict)
                if res is not None:
                    success = True
            if success:
                logging.info(f"Success\t{j}")
                # 写入成功文件
                with open(f"logs/Success_{timestamp}.log", 'a') as f:
                    f.write(f"{j}\n")
            else:
                logging.error(f"Failed\t{j}")
                # 写入失败文件
                with open(f"logs/Failed_{timestamp}.log", 'a') as f:
                    f.write(f"{j}\n")


