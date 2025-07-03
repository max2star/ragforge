#
#  Copyright 2024 The InfiniFlow Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
import pdfplumber
import os
from loguru import logger
import re

def _has_color(o):
    #Non-Stroking Color Space（非描边颜色空间），即文本/图形等的填充颜色所使用的颜色空间模型
    if o.get("ncs", "") == "DeviceGray":
        #颜色空间为DeviceGray（灰度空间，其他还有DeviceRGB/DeviceCMYK等），
        #并且描边颜色的第一个分量为纯白色；
        #并且填充颜色的第一个分量为纯白色;
        if o["stroking_color"] and o["stroking_color"][0] == 1 and o["non_stroking_color"] and \
                o["non_stroking_color"][0] == 1:
            #文本是英文
            if re.match(r"[a-zT_\[\]\(\)-]+", o.get("text", "")):
                #说明是隐藏文字，没有颜色，返回False
                return False
    return True

directory = "./原文"
#directory = "./大模型训练原文"
page_from = 0
page_to = 100
for root, dirs, files in os.walk(directory):
    #只打印第一页
    print_number =1 
    for file in files:
        file_path = os.path.join(root, file)
        #logger.info("当前正在处理的文件是 {}".format(file_path))       
        if file !='从三次国际会议看放射卫生工作的前景_陈兴安.pdf' and file!='Y1089380.pdf':
            continue
        print("当前文件 {}".format(file))
        with pdfplumber.open(file_path) as pdf:
            count_number = 0
            zoomin = 3
            count_number = count_number +1
            #page_images = [p.to_image(resolution=72 * zoomin).annotated for i, p in
            #                            enumerate(pdf.pages[0:10])]
            page_images = []
            for page in pdf.pages:
                p = page.to_image(resolution=72 * zoomin).annotated
                print("当前页面 {},Image 大小 {}".format(count_number,p.size))
                page_images.append(p)
                page_chars = [[c for c in page.dedupe_chars().chars if _has_color(c)] for page in pdf.pages[page_from:page_to]]
                print("非隐藏(可见)字符page_chars length is {}".format(len(page_chars)))
                text = page.extract_text()
                count_number = count_number +1
                if count_number ==print_number:
                    print(text)
                    #break
            #count_number_new = 0
            #for p_ in page_images:
            #    count_number_new = count_number_new +1
            #    print("当前页面 {} 内容长度 {}".format(count_number_new,len(p_.size)))

            ##print("特殊字符page_chars is {}".format((page_chars)))
            #for i in page_chars:
            #    for j in i:
            #        print(j) #['text'])
            #    break

         #with pdfplumber.open("D059537.pdf") as pdf:
         #    for page in pdf.pages:
         #        tables = page.extract_tables()
         #        for table in tables:
         #            print("----- 表格开始 -----")
         #            for row in table:
         #                print(row)
         #            print("----- 表格结束 -----")
