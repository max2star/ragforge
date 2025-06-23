import requests
import os
from glob import glob
import json
from datetime import datetime

class Logger:
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


def confirm_up(ip="101.52.216.178", host=9090, res=None, folderId=None, level=1):
    if res is None:
        return None
    if folderId is None:
        logging.error(f"folderId is None")
        return None
    url = f"http://{ip}:{host}/op-api/api/v1/km/saveFileSpecial"
    # url = f"http://{ip}:{host}/op-api/api/v1/km/saveFile"

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
            "level": str(level),
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
    folderId = 6782
    IP = "101.52.216.178"
    PORT = 9090
    for i in UPLOAD_DIR:
        file_paths = glob(os.path.join(i, '*pdf'))
        # 过滤掉目录
        file_paths = [fp for fp in file_paths if os.path.isfile(fp)]
        if not file_paths:
            logging.info("⚠️ 没有找到可上传的文件")
            continue

        num = 0
        for j in file_paths:
            logging.info(j)
            success = False
            res_dict = None
            try:
                res_dict = upload(ip=IP, host=PORT,file_path=j)
            except Exception as e:
                logging.error(f"upload {j} error {e}")
            if res_dict is not None:
                try:
                    res = confirm_up(ip=IP, host=PORT,res=res_dict, folderId=folderId)
                    if res is not None:
                        success = True
                except Exception as e:
                    logging.error(f"confirm_up {j} error {e}")
            if success:
                logging.info(f"Success\t{j}")
                # 写入成功文件
                with open(f"logs/Success_{timestamp}.log", 'a', encoding='utf-8') as f:
                    f.write(f"{j}\n")
            else:
                logging.error(f"Failed\t{j}")
                # 写入失败文件
                with open(f"logs/Failed_{timestamp}.log", 'a', encoding='utf-8') as f:
                    f.write(f"{j}\n")


