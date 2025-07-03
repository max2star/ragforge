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


def upload(ip, host, file_path=None):
    
    if file_path is None:
        logging.error(f"file_path is None")
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
        logging.info(f"upload ✅ 响应成功! 响应结果: \n{json.dumps(dict(res),indent=4,ensure_ascii=False)}")
        return dict(res) if dict(res).get("code") == 200 else None
    else:
        logging.error(f"upload ❌ 响应失败! 状态码: {response.status_code}, 错误信息: \n{json.dumps(dict(json.loads(response.text)),indent=4,ensure_ascii=False)}")
        return None


def confirm_up(ip, host, res=None,folderId=None,level=2):
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
            "level": str(level),
            "scopeRule": "ONLY_ME"
        }]
    }

    logging.info(f"保存文件的使用的数据为 {json.dumps(payload, indent=4, ensure_ascii=False)}")
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
        logging.info(f"confirm_up ✅ 响应成功! 响应结果: \n{json.dumps(dict(res), indent=4, ensure_ascii=False)}")
        return dict(res) if dict(res).get("code") == 200 else None
    else:
        logging.error(
            f"confirm_up ❌ 响应失败! 状态码: {response.status_code}, 错误信息: \n{json.dumps(dict(json.loads(response.text)), indent=4, ensure_ascii=False)}")
        return None


def trigger_parse(ip, host,fileId,resourceId):
    
    url = f"http://{ip}:{host}/op-api/api/v1/ragforge/executeRag"
    #[{"fileId":"93f9a3de7c504e539078207001439398","resourceId":1655,"embeddingConfigCode":""}]
    file_= {
        "fileId":fileId ,
        "embeddingConfigCode":""
    }
    if resourceId:
        file_['resourceId'] =  resourceId
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
        logging.info(f"list doc✅ 响应成功! 响应结果: \n{json.dumps(dict(res), indent=4, ensure_ascii=False)}")
        return dict(res) if dict(res).get("code") == 200 else None
    else:
        logging.error(
            f"list doc ❌ 响应失败! 状态码: {response.status_code}, 错误信息: \n{json.dumps(dict(json.loads(response.text)), indent=4, ensure_ascii=False)}")
        return None

def create_folder(ip, host,folderName,parentId,embeddingConfigName="图书",embeddingConfigCode=23):

    url = f"http://{ip}:{host}/op-api/api/v1/km/saveFolder"

    payload = {"id":None,"guid":"","name":folderName,"parentId":parentId,"embeddingConfigCode":embeddingConfigCode,"embeddingConfigName":embeddingConfigName,"memberList":[]}
    logging.info(f"创建目录使用的参数 {json.dumps(payload, indent=4, ensure_ascii=False)}")
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
        logging.info(f"create folder ✅ 响应成功! 响应结果: \n{json.dumps(dict(res), indent=4, ensure_ascii=False)}")
        return dict(res) if dict(res).get("code") == 200 else None
    else:
        logging.error(
            f"create folder  ❌ 响应失败! 状态码: {response.status_code}, 错误信息: \n{json.dumps(dict(json.loads(response.text)), indent=4, ensure_ascii=False)}")
        return None

if __name__ == '__main__':
    #请映射好本地根目录和要上传的根目录ID；程序会按照本地根目录在系统对应根目录下创建子目录和文件
    NEW_DIRS = {
            # "/opt/ragforge/tests/":438,
            "D:/App/baidu/报告/自动化/子文件夹2":416,
            }
    global embeddingConfigName
    global embeddingConfigCode
    embeddingConfigName = "图书"
    embeddingConfigCode = 23
    IP = "101.52.216.178"
    PORT = 9090
    for UPLOAD_DIR in NEW_DIRS.keys():
        folderId = NEW_DIRS[UPLOAD_DIR]
        count_ = 0
        dict_directory_map = {}
        change_name_prefix = "[内部]"
        #目录下如果有不是以 [内部]/[公开] 作为前缀的文件，则重命名为 change_name_prefix开头
        for root, dirs, files in os.walk(UPLOAD_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                j = file_path
                logging.info(f"==========================当前正在处理 {j}")
                if not (j.endswith('.pdf') or j.endswith('.docx')  or j.endswith('.doc')):
                    logging.info(f"忽略当前正在处理的 {j}，因为它不是pdf或者docx或者doc")
                    continue
                if (file.startswith('[公开]') or file.startswith('[内部]')):
                    logging.info(f"当前正在处理的 {j}，它以[公开] 或者 [内部] 开头,不需要重新命名")
                    continue
                new_filename = change_name_prefix + file
                new_path = os.path.join(root, new_filename)
                try:
                    # 重命名文件
                    os.rename(file_path, new_path)
                    logging.info(f"重命名: {file_path} -> {new_path}")
                except Exception as e:
                    logging.error(f"无法重命名 {file_path}: {e}")
        def build_directory_tree(start_path):
            def _build_tree(current_path):
                tree = {
                    'name': os.path.basename(current_path),
                    'path': current_path,
                    'type': 'directory',
                    'children': []
                }
                try:
                    with os.scandir(current_path) as entries:
                        for entry in entries:
                            if entry.is_dir():
                                tree['children'].append(_build_tree(entry.path))
                except PermissionError:
                    pass  # 跳过无权限访问的目录
                return tree
            return _build_tree(start_path)
        directory_tree = build_directory_tree(UPLOAD_DIR)

        logging.info(f"将要创建的目录树为 {directory_tree}")

        def create_tree_from_structure(tree_node, start_folderId):
            """
            基于之前构建的目录树结构创建目录
            参数:
                tree_node: 之前构建的目录树节点
                target_root (str): 目标根目录路径
            """
            global embeddingConfigCode
            global embeddingConfigName
            # 递归创建子目录
            for child in tree_node.get('children', []):
                create_result = create_folder(ip=IP,host=PORT,folderName=child['name'],parentId=start_folderId,embeddingConfigName=embeddingConfigName,embeddingConfigCode=embeddingConfigCode)
                guid= create_result['data']
                list_result = list_docs(ip=IP, host=PORT,folderId=start_folderId)
                for da_ in list_result.get('data',[]):
                    if da_['guid'] == guid:
                        start_folderId_= da_['id']
                        break
                child['folderId'] = start_folderId_
                create_tree_from_structure(child,start_folderId_)
        create_tree_from_structure(directory_tree,folderId)

        logging.info(f"创建目录树完成,现在上传目录结构下的文件,目录结构为 {directory_tree}...")
        logging.info(f"将根目录下的也添加进去...")
        directory_tree['children'].append({'folderId':folderId,'path':UPLOAD_DIR})
        def upload_and_trigger(tree_node, start_folderId):
            # 递归创建子目录
            for child in tree_node.get('children', []):
                logging.info(f"正在处理 {child}...")
                # 遍历目录和子目录
                folderId = child['folderId']
                for file in os.listdir(child['path']):
                    #for file in files:
                    file_path = os.path.join(child['path'], file)
                    j = file_path
                    logging.info(f"==========================当前正在处理 {j}")
                    if not (j.endswith('.pdf') or j.endswith('.docx')  or j.endswith('.doc')):
                        logging.info(f"忽略当前正在处理的 {j}，因为它不是pdf或者docx或者doc")
                        continue
                    if not (file.startswith('[公开]') or file.startswith('[内部]')):
                        logging.info(f"忽略当前正在处理的 {j}，因为它不是以[公开] 或者 [内部] 开头")
                        continue
                    if file.startswith('[公开]'):
                        level = 1
                    if file.startswith('[内部]'):
                        level = 2
                    global count_
                    count_ = count_ +1
                    success = False
                    res_dict = upload(ip=IP, host=PORT,file_path=j)
                    if res_dict is not None:
                        logging.info(f"upload 返回的数据为{res_dict}")
                        fileId = res_dict["data"]["guid"]
                        res = confirm_up(ip=IP, host=PORT,res=res_dict,folderId=folderId,level=level)
                        if res is not None:
                            logging.info(f"confirm_up 返回的数据为{res}")
                            list_result = list_docs(ip=IP, host=PORT,folderId=folderId)
                            #logging.info(f"list 返回的数据为{list_result}")
                            resourceId = None
                            for da_ in list_result.get('data',[]):
                                if da_['fileId'] == fileId:
                                    resourceId = da_['id']
                                    break
                            if resourceId:
                                logging.info(f"搜索到了文档ID {fileId}的 资源ID 为{resourceId},触发解析...")
                                result = trigger_parse(ip=IP, host=PORT,fileId=fileId,resourceId=resourceId)
                                if result:
                                    logging.info(f"trigger_parse 返回的数据为{result}")
                                    success = True
                            else:
                                logging.info(f"没有搜索到文档ID {fileId}的 资源ID")
                    if success:
                        logging.info(f"最终成功处理 {j}")
                        # 写入成功文件记录
                        with open(f"logs/Success_{timestamp}.log", 'a', encoding='utf-8') as f:
                            f.write(f"{j}\n")
                    else:
                        logging.info(f"最终处理失败 {j}")
                        # 写入失败文件
                        with open(f"logs/Failed_{timestamp}.log", 'a', encoding='utf-8') as f:
                            f.write(f"{j}\n")
                upload_and_trigger(child,child['folderId'])
        upload_and_trigger(directory_tree,folderId)
    logging.info(f"总计处理 {count_}个")
