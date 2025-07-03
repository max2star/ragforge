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
from pypdf import PdfReader as pdf2_read
import logging
        
outlines = []
fnm = "./大模型训练原文/22298.pdf"
fnm = "./原文/D028386.pdf"
outlines_global = []
try:
    pdf = None
    with (pdf2_read(fnm if isinstance(fnm, str)
                    else BytesIO(fnm))) as pdf:
        pdf = pdf
        outlines = pdf.outline
        print("能够获取到的目录结构为 {}".format(pdf.outline))
        def dfs(arr, depth):
            for a in arr:
                if isinstance(a, dict):
                    outlines_global.append((a["/Title"], depth))
                    continue
                dfs(a, depth + 1)

        dfs(outlines, 0)
except Exception as e:
    logging.warning(f"Outlines exception: {e}")

if not outlines:
    logging.warning("Miss outlines")

print("目录结构 {}".format(outlines_global))
