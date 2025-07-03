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

def list_docs(ip, host,folderId):
   
    url = f"http://{ip}:{host}/op-api/api/v1/km/resourceListRight"
    
    payload = {
            "pageNum":1,
            "pageSize":1000000,
            "parentId":folderId,
            "fileYearList":[],
            "embeddingConfigNameList":[],
            "timeSort":"desc",
            "nameSort":"desc"
            }

    #logging.info(f"列表文档使用的参数 {json.dumps(payload, indent=4, ensure_ascii=False)}")
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
        #logging.info(f"list doc✅ 响应成功! 响应结果: \n{json.dumps(dict(res), indent=4, ensure_ascii=False)}")
        return dict(res) if dict(res).get("code") == 200 else None
    else:
        #logging.error(
        #    f"list doc ❌ 响应失败! 状态码: {response.status_code}, 错误信息: \n{json.dumps(dict(json.loads(response.text)), indent=4, ensure_ascii=False)}")
        return None

if __name__ == '__main__':
    NEW_DIRS = {
            "/opt/ragforge/tests/":438,
            #"D:/App/baidu/报告/自动化/子文件夹2":,
            }
    IP = "101.52.216.178"
    PORT = 9090
    global not_exists
    global not_exists_directory
    not_exists = []
    not_exists_directory = []
    for UPLOAD_DIR in NEW_DIRS.keys():
        def get_diff_files(UPLOAD_DIR,folderId):
            files_to_diff = []
            directory = {}
            UPLOAD_DIR = UPLOAD_DIR
            start_folderId = folderId
            list_result = list_docs(ip=IP, host=PORT,folderId=start_folderId)
            for f in list_result['data']:
                print(f['id'],f['name'],f['parentId'],f['folderId'],f['guid'],f['children'],f['resourceType'],f['fileType'])
                if f['resourceType']==2:
                    f_to_diff = {}
                    f_to_diff['id'] = f['id']
                    f_to_diff['name'] = f['name']
                    f_to_diff['parentId'] = f['parentId']
                    f_to_diff['folderId'] = f['folderId']
                    f_to_diff['guid'] = f['guid']
                    f_to_diff['resourceType'] = f['resourceType']
                    f_to_diff['fileType'] = f['fileType']
                    files_to_diff.append(f_to_diff)
                if f['resourceType']==1:
                    directory[f['name']] = f['id']
            #print('需要比对的文件',files_to_diff)
            print(f"当前目录 {UPLOAD_DIR}下的子目录对应的folderID关系为 {directory}")
            for file in os.listdir(UPLOAD_DIR):
                file_path = os.path.join(UPLOAD_DIR, file)
                j = file_path
                #logging.info(f"==========================当前正在处理 {j}")
                if os.path.isdir(file_path):
                    print(f'当前的路径 {file_path} 是目录')
                    #获取该目录的foldrId
                    directory_folderId = directory.get(file,None)
                    if not directory_folderId:
                        print(f'当前的路径 {file_path} 是目录,目录 {file} 在系统中不存在')
                        global not_exists_directory
                        not_exists_directory.append(file_path)
                        continue
                    else:
                        print(f'当前的路径 {file_path} 是目录,目录 {file} 在系统存在，其folderID为 {directory_folderId},开始递归调用该目录下的检查')
                        get_diff_files(file_path,directory_folderId)
                else:
                    if not (j.endswith('.pdf') or j.endswith('.docx')  or j.endswith('.doc')):
                        continue
                    print(f"正在判断 {file} 是否存在")
                    if file in [f['name'] for f in files_to_diff]:
                        print(f"file {file_path} exists")
                    else:
                        print(f"file {file_path} not exists")
                        global not_exists
                        not_exists.append(file_path)
        folderId = NEW_DIRS[UPLOAD_DIR]
        get_diff_files(UPLOAD_DIR,folderId)
    print(f"============================================================================================================")
    print(f"发现 目录{not_exists_directory}在本地存在，但是系统中不存在；文件{not_exists} 本地存在，但是系统中不存在！")
#        count_ = 0
#        dict_directory_map = {}
#        change_name_prefix = "[内部]"
#        for root, dirs, files in os.walk(UPLOAD_DIR):
#            for file in files:
#                file_path = os.path.join(root, file)
#                j = file_path
#                logging.info(f"==========================当前正在处理 {j}")
#                if not (j.endswith('.pdf') or j.endswith('.docx')  or j.endswith('.doc')):
#                    logging.info(f"忽略当前正在处理的 {j}，因为它不是pdf或者docx或者doc")
#                    continue
#                if (file.startswith('[公开]') or file.startswith('[内部]')):
#                    logging.info(f"当前正在处理的 {j}，它以[公开] 或者 [内部] 开头,不需要重新命名")
#                    continue
#                new_filename = change_name_prefix + file
#                new_path = os.path.join(root, new_filename)
#                try:
#                    # 重命名文件
#                    os.rename(file_path, new_path)
#                    logging.info(f"重命名: {file_path} -> {new_path}")
#                except Exception as e:
#                    logging.error(f"无法重命名 {file_path}: {e}")
#        logging.info(f"将要创建的目录树为 {directory_tree}")
#
#        def create_tree_from_structure(tree_node, start_folderId):
#            """
#            基于之前构建的目录树结构创建目录
#            参数:
#                tree_node: 之前构建的目录树节点
#                target_root (str): 目标根目录路径
#            """
#            global embeddingConfigCode
#            global embeddingConfigName
#            # 递归创建子目录
#            for child in tree_node.get('children', []):
#                create_result = create_folder(ip=IP,host=PORT,folderName=child['name'],parentId=start_folderId,embeddingConfigName=embeddingConfigName,embeddingConfigCode=embeddingConfigCode)
#                guid= create_result['data']
#                list_result = list_docs(ip=IP, host=PORT,folderId=start_folderId)
#                for da_ in list_result.get('data',[]):
#                    if da_['guid'] == guid:
#                        start_folderId_= da_['id']
#                        break
#                child['folderId'] = start_folderId_
#                create_tree_from_structure(child,start_folderId_)
#        create_tree_from_structure(directory_tree,folderId)
#
#        logging.info(f"创建目录树完成,现在上传目录结构下的文件,目录结构为 {directory_tree}...")
#        logging.info(f"将根目录下的也添加进去...")
#        directory_tree['children'].append({'folderId':folderId,'path':UPLOAD_DIR})
#        def upload_and_trigger(tree_node, start_folderId):
#            # 递归创建子目录
#            for child in tree_node.get('children', []):
#                logging.info(f"正在处理 {child}...")
#                # 遍历目录和子目录
#                folderId = child['folderId']
#                for file in os.listdir(child['path']):
#                    #for file in files:
#                    file_path = os.path.join(child['path'], file)
#                    j = file_path
#                    logging.info(f"==========================当前正在处理 {j}")
#                    if not (j.endswith('.pdf') or j.endswith('.docx')  or j.endswith('.doc')):
#                        logging.info(f"忽略当前正在处理的 {j}，因为它不是pdf或者docx或者doc")
#                        continue
#                    if not (file.startswith('[公开]') or file.startswith('[内部]')):
#                        logging.info(f"忽略当前正在处理的 {j}，因为它不是以[公开] 或者 [内部] 开头")
#                        continue
#                    if file.startswith('[公开]'):
#                        level = 1
#                    if file.startswith('[内部]'):
#                        level = 2
#                    global count_
#                    count_ = count_ +1
#                    success = False
#                    res_dict = upload(ip=IP, host=PORT,file_path=j)
#                    if res_dict is not None:
#                        logging.info(f"upload 返回的数据为{res_dict}")
#                        fileId = res_dict["data"]["guid"]
#                        res = confirm_up(ip=IP, host=PORT,res=res_dict,folderId=folderId,level=level)
#                        if res is not None:
#                            logging.info(f"confirm_up 返回的数据为{res}")
#                            list_result = list_docs(ip=IP, host=PORT,folderId=folderId)
#                            #logging.info(f"list 返回的数据为{list_result}")
#                            resourceId = None
#                            for da_ in list_result.get('data',[]):
#                                if da_['fileId'] == fileId:
#                                    resourceId = da_['id']
#                                    break
#                            if resourceId:
#                                logging.info(f"搜索到了文档ID {fileId}的 资源ID 为{resourceId},触发解析...")
#                                result = trigger_parse(ip=IP, host=PORT,fileId=fileId,resourceId=resourceId)
#                                if result:
#                                    logging.info(f"trigger_parse 返回的数据为{result}")
#                                    success = True
#                            else:
#                                logging.info(f"没有搜索到文档ID {fileId}的 资源ID")
#                    if success:
#                        logging.info(f"最终成功处理 {j}")
#                        # 写入成功文件记录
#                        with open(f"logs/Success_{timestamp}.log", 'a', encoding='utf-8') as f:
#                            f.write(f"{j}\n")
#                    else:
#                        logging.info(f"最终处理失败 {j}")
#                        # 写入失败文件
#                        with open(f"logs/Failed_{timestamp}.log", 'a', encoding='utf-8') as f:
#                            f.write(f"{j}\n")
#                upload_and_trigger(child,child['folderId'])
#        upload_and_trigger(directory_tree,folderId)
