import json
import shutil
import os

import requests
from modelscope import snapshot_download


def download_json(url):
    # 下载JSON文件
    response = requests.get(url)
    response.raise_for_status()  # 检查请求是否成功
    return response.json()


def download_and_modify_json(url, local_filename, modifications):
    if os.path.exists(local_filename):
        data = json.load(open(local_filename))
        config_version = data.get('config_version', '0.0.0')
        if config_version < '1.2.0':
            data = download_json(url)
    else:
        data = download_json(url)

    # 修改内容
    for key, value in modifications.items():
        data[key] = value

    # 保存修改后的内容
    with open(local_filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    # 获取脚本所在目录（driver目录）
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f'脚本目录: {script_dir}')
    
    # 创建models目录
    models_dir = os.path.join(script_dir, 'models')
    os.makedirs(models_dir, exist_ok=True)
    print(f'模型目录: {models_dir}')
    
    mineru_patterns = [
        # "models/Layout/LayoutLMv3/*",
        "models/Layout/YOLO/*",
        "models/MFD/YOLO/*",
        "models/MFR/unimernet_hf_small_2503/*",
        "models/OCR/paddleocr_torch/*",
        # "models/TabRec/TableMaster/*",
        # "models/TabRec/StructEqTable/*",
    ]
    
    # 下载模型到driver/models目录
    print('开始下载模型...')
    model_dir = snapshot_download('opendatalab/PDF-Extract-Kit-1.0', 
                                 allow_patterns=mineru_patterns,
                                 cache_dir=models_dir)
    layoutreader_model_dir = snapshot_download('ppaanngggg/layoutreader',
                                             cache_dir=models_dir)
    
    # 获取实际的模型目录路径
    actual_model_dir = os.path.join(model_dir, 'models')
    print(f'模型下载目录: {actual_model_dir}')
    print(f'LayoutReader模型目录: {layoutreader_model_dir}')

    # 配置文件路径 - 创建在conf目录下
    config_file_name = 'magic-pdf.json'
    conf_dir = os.path.join(os.path.dirname(script_dir), 'conf')
    config_file = os.path.join(conf_dir, config_file_name)
    print(f'配置文件路径: {config_file}')

    # 使用相对路径 - 从项目根目录的角度
    relative_model_dir = 'driver/models'
    relative_layoutreader_dir = 'driver/models'

    json_mods = {
        'models-dir': relative_model_dir,
        'layoutreader-model-dir': relative_layoutreader_dir,
    }

    # 如果配置文件不存在，创建默认配置
    if not os.path.exists(config_file):
        default_config = {
            "bucket_info": {
                "bucket-name-1": [
                    "ak",
                    "sk", 
                    "endpoint"
                ],
                "bucket-name-2": [
                    "ak",
                    "sk",
                    "endpoint"
                ]
            },
            "models-dir": relative_model_dir,
            "layoutreader-model-dir": relative_layoutreader_dir,
            "device-mode": "cpu",
            "layout-config": {
                "model": "doclayout_yolo"
            },
            "formula-config": {
                "mfd_model": "yolo_v8_mfd",
                "mfr_model": "unimernet_small",
                "enable": True
            },
            "table-config": {
                "model": "rapid_table",
                "sub_model": "slanet_plus",
                "enable": True,
                "max_time": 400
            },
            "latex-delimiter-config": {
                "display": {
                    "left": "$$",
                    "right": "$$"
                },
                "inline": {
                    "left": "$",
                    "right": "$"
                }
            },
            "llm-aided-config": {
                "formula_aided": {
                    "api_key": "your_api_key",
                    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                    "model": "qwen2.5-7b-instruct",
                    "enable": False
                },
                "text_aided": {
                    "api_key": "your_api_key",
                    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                    "model": "qwen2.5-7b-instruct",
                    "enable": False
                },
                "title_aided": {
                    "api_key": "your_api_key",
                    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                    "model": "qwen2.5-32b-instruct",
                    "enable": False
                }
            },
            "config_version": "1.2.1"
        }
        
        # 应用修改
        for key, value in json_mods.items():
            default_config[key] = value
            
        # 保存配置文件
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=4)
    else:
        # 如果配置文件存在，更新路径
        download_and_modify_json(None, config_file, json_mods)

    print(f'✅ 模型下载完成！')
    print(f'✅ 配置文件已更新: {config_file}')
    print(f'✅ 模型目录: {actual_model_dir}')
    print(f'✅ 使用相对路径配置，便于项目迁移')
