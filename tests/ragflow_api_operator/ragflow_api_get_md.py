import requests
from  loguru import logger
import os
api_key = "IjcyZjc2Nzk0Mzg1MTExZjBhYTg0NjZhZDZhYTE0ZTA4Ig.aDFAtA.RhxTZlDbr0EbOrYGD5tOQJ4zeJI"
headers = {
    'Authorization': f'{api_key}',
    #'Accept':"text/markdown; charset=utf-8",
    #'Content-Type': 'application/json',
}

doc_id = "e92909a236eb11f0a1524674195f8099"
list_chunks = f"http://101.52.216.178/v1/document/get_layout/{doc_id}"
import json
response = requests.get(list_chunks, headers=headers)
print(response)
#print(response.content)
response.raise_for_status()  # Check if request was successful


from PyPDF2 import PdfReader
from io import BytesIO

pdf_file = BytesIO(response.content)
pdf_reader = PdfReader(pdf_file)
text_content = []

for page in pdf_reader.pages:
    text = page.extract_text()
    if text:  # 跳过空白页
        text_content.append(text)

# 6. 打印结果
if text_content:
    print("="*50 + "\nPDF 内容：\n" + "="*50)
    print("\n".join(text_content))
else:
    print("警告：未提取到文本内容（可能是扫描件图片PDF）")


