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

def create_json():
    # 构建 JSON 结构
    json_data = {
        "model": "qwen2.5-vl-32b-instruct",
        "messages": [{
        "role": "user",
        "content": [
        {"type": "image_url", "image_url": "/model/hua.jpg"},
        {"type": "text", "text": "请描述下图片内容"}
        ]
        }],
        "max_tokens": 512,
        "do_sample": True,
        "repetition_penalty": 1.00,
        "temperature": 0.01,
        "top_p": 0.001,
        "top_k": 1
    }

    # 输出到 JSON 文件（UTF-8 编码）
    filename = "qwen_vlm.json"
    with open(filename, "w", encoding="utf-8") as f:
        # 注意：ensure_ascii=False 确保中文字符不被转义
        # indent=2 使输出更可读（可选）
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
if __name__ == "__main__":
    create_json()
