import base64
import json
import os

import requests
from PIL import Image
from io import BytesIO


def resize_image(image_path, max_width_size=600):
    """调整图片大小至指定宽度"""
    with Image.open(image_path) as img:
        width, height = img.width, img.height
        img = img.copy()

        # 执行缩放操作
        ratio = max_width_size / img.width
        new_height = int(img.height * ratio)
        img = img.resize((max_width_size, new_height), Image.LANCZOS)

        # 返回图像副本和尺寸（文件指针不再相关）
        return img, width, height


def generate_prompt(image_path, max_width_size=600):
    # 调整图片大小（最大边不超过1024px）
    img, width, height = resize_image(image_path, max_width_size=max_width_size)

    # 将处理后的图片保存为字节流
    img_bytes = BytesIO()

    # 根据原始文件扩展名确定格式，没有扩展名则默认JPEG
    ext = os.path.splitext(image_path)[1].lower()[1:] if os.path.splitext(image_path)[1] else 'jpeg'
    supported_formats = ['jpeg', 'jpg', 'png', 'gif', 'bmp', 'webp']
    format = ext if ext in supported_formats else 'jpeg'

    img.save(img_bytes, format=format)
    path = os.path.join("%s_%d.png" % (os.path.splitext(image_path)[0], max_width_size))
    Image.open(img_bytes).save(path)
    img_bytes.seek(0)

    # 转换为Base64并获取MIME类型
    image_data = base64.b64encode(img_bytes.read()).decode("utf-8")
    mime_type = f"image/{format}" if format != 'jpg' else "image/jpeg"

    # 构建最终请求结构
    prompt = {
        "model": "qwen2.5-vl-32b-instruct",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{image_data}"
                        }
                    },
                    {
                        "type": "text",
                        "text": "提取图中的：['标题','作者','其他作者','发布时间','资料来源','摘要']，请你以最紧凑的JSON格式输出，不需要多余的空格与换行，不要有任何旁白"
                    }
                ]
            }
        ],
        "do_sample": True,
        "repetition_penalty": 1.0,
        "temperature": 0.01,
        "top_p": 0.001,
        "top_k": 1
    }

    # 添加处理信息
    image_info = {
        "original_size": (width, height),
        "processed_size": img.size,
        "format": format
    }

    return prompt, image_info


def run_model(api_url="http://118.193.126.254:3525/v1/chat/completions"):
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(api_url, json=request_data, headers=headers, timeout=30)
        response.raise_for_status()

        print("\nAPI响应状态:", response.status_code)

        # 尝试解析JSON响应
        try:
            json_response = response.json()
            print("API响应内容:")
            print(json.dumps(json_response, indent=2, ensure_ascii=False))

            # 尝试提取模型输出
            if "choices" in json_response and len(json_response["choices"]) > 0:
                message_content = json_response["choices"][0]["message"]["content"]
                print("\n提取的内容信息:")
                print(message_content)

        except ValueError:
            print("响应内容(非JSON格式):")
            print(response.text[:1000])  # 限制输出长度

    except requests.exceptions.RequestException as e:
        print(f"请求失败: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"错误响应: {e.response.text}")


# 使用示例
if __name__ == "__main__":
    # 替换为实际图片路径
    image_path = "test_models/FPGA抗辐射加固技术_01.png"

    # 生成请求数据
    request_data, info = generate_prompt(image_path, max_width_size=1500)

    # 输出处理信息
    print(f"原始图片: {image_path}")
    print(f"原始尺寸: {info['original_size']} | 处理后尺寸: {info['processed_size']} | 格式: {info['format']}")

    # 验证结果
    print(f"Base64 数据长度: {len(request_data['messages'][0]['content'][0]['image_url']['url']) // 1024} KB")
    print(f"完整请求体大小: {len(json.dumps(request_data)) // 1024} KB")

    run_model()
