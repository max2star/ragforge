import requests
from  loguru import logger
import os
api_key = "ImM5NDM2YjM0M2MzOTExZjA5ZDEzNzI5YTQxODY0YjZkIg.aDfO_Q.fsIpj3z11cXWg1Pow7FzjFRQrr8"#IjFhZWI3ZDgwMzg1OTExZjBiNTk0NzYzMzg0Nzg0ZjFlIg.aDFNjA.FgR8i6OqNipBWpxjrD-shl76RVg"
api_key = "IjRhMDYwNjFhM2MzZTExZjBhZGE2NWFiYmUyOTc3NTY0Ig.aDfWiw.NqfagBXhPK-cNTWdDwNnuHK7b7o"
headers = {
    'Authorization': f'{api_key}',
    #'Accept':"text/markdown; charset=utf-8",
    #'Content-Type': 'application/json',
}

doc_id = "5479b59237ac11f0ac074e79a2571c31"
doc_id = "b1d2fb6c379e11f08c294e79a2571c31"
doc_id = "574d50223acb11f09b1c66fbdfc83c6b"
list_chunks = f"http://101.52.216.178/v1/document/get_md_html/{doc_id}"
import json
response = requests.get(list_chunks, headers=headers)
print(response)
print(response.content.decode('utf-8-sig'))
response.raise_for_status()  # Check if request was successful

#list_chunks = f"http://101.52.216.178/v1/document/get_layout/{doc_id}"
#import json
#response = requests.get(list_chunks, headers=headers)
#print(response)
#response.raise_for_status()  # Check if request was successful
#
#
#from PyPDF2 import PdfReader
#from io import BytesIO
#
#pdf_file = BytesIO(response.content)
#pdf_reader = PdfReader(pdf_file)
#text_content = []
#
#for page in pdf_reader.pages:
#   text = page.extract_text()
#   if text:  # 跳过空白页
#       text_content.append(text)
#
##6. 打印结果
#if text_content:
#   print("="*50 + "\nPDF 内容：\n" + "="*50)
#   print("\n".join(text_content))
#else:
#   print("警告：未提取到文本内容（可能是扫描件图片PDF）")
#
