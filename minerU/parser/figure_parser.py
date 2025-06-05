#
#  Copyright 2025 The InfiniFlow Authors. All Rights Reserved.
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


from PIL import Image

from rag.paper_prompts import vision_llm_paper_extraction_prompt
from rag.utils import clean_markdown_block
import logging
import io
def vision_llm_chunk(binary, vision_model, prompt=None):
    img = binary
    txt = ""

    try:
        img_binary = io.BytesIO()
        img.save(img_binary, format='JPEG')
        img_binary.seek(0)

        ans = clean_markdown_block(vision_model.describe_with_prompt(img_binary.read(), prompt))

        txt += "\n" + ans

        return txt

    except Exception as e:
        logging.info("发生错误 {}".format(e))
        import traceback
        traceback.print_exc()
    return ""

class VisionFigureParser:
    def __init__(self, vision_model=None, figures_data=None, key_list_to_extract=None, prompt=None):
        self.vision_model = vision_model
        self.figures_data = figures_data
        self.prompt = prompt
        if key_list_to_extract is None:
            key_list_to_extract = []
        self.key_list_to_extract = key_list_to_extract

    def __call__(self, **kwargs):
        texts = {}
        for idx, img_binary in enumerate(self.figures_data):
            figure_num = idx  # 0-based
            txt = vision_llm_chunk(
                binary=img_binary,
                vision_model=self.vision_model,
                prompt=self.prompt if self.prompt else vision_llm_paper_extraction_prompt(
                    self.key_list_to_extract
                )
            )
            if txt:
                texts[idx] = txt
        return texts 
