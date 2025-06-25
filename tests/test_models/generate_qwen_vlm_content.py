import json
import random
import sys

import random
import textwrap
import sys

import json
import random
import textwrap
import sys

import base64

#  base 64 编码格式
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
base64_image = encode_image("./FPGA抗辐射加固技术_02.png")
def create_json():
    # 构建 JSON 结构
    json_data = {
        "model": "qwen2.5-vl-32b-instruct",
        "messages": [{
        "role": "user",
        "content": [
        {"type": "image_url", "image_url": {"url":f"data:image/jpeg;base64,{base64_image}"}},
        {"type": "text", "text": "提取图中的：['标题','作者','发布时间','资料来源','摘要']，请你以JSON格式输出，不要输出```json```代码段。"}
        ]
        }],
        #"max_tokens": 512,
        "do_sample": True,
        "repetition_penalty": 1.00,
        "temperature": 0.01,
        "top_p": 0.001,
        "top_k": 1
    }
    print(json_data)
    # 输出到 JSON 文件（UTF-8 编码）
    filename = "qwen_vlm.json"
    with open(filename, "w", encoding="utf-8") as f:
        # 注意：ensure_ascii=False 确保中文字符不被转义
        # indent=2 使输出更可读（可选）
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
if __name__ == "__main__":
    create_json()
