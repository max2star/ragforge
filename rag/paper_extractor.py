#
#  Copyright 2025 The RobuSoft Authors. All Rights Reserved.
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
import logging
import re
import numpy as np
import trio
import json
from rag.utils import truncate
from rag.paper_prompts import paper_extraction_prompt
from graphrag.utils import (
    get_llm_cache,
    get_embed_cache,
    set_embed_cache,
    set_llm_cache,
    chat_limiter,
)
from api.db import constant

# 使用方法：
# 以传递的参数、大模型构建本实例，执行调用
# 传递的最重要的参数是 prompt 
class PaperExtractor:
    def __init__(
        self, llm_model, prompt, key):
        self._llm_model = llm_model
        self._prompt = prompt
        self._key= key

    async def _chat(self, system, history, gen_conf):
        response = await trio.to_thread.run_sync(
            lambda: self._llm_model.chat(system, history, gen_conf)
        )
        logging.info(f"response begin ==>\n{response}")
        if "</think>" in response:
            response = re.sub(r"^.*?</think>", "", response, flags=re.DOTALL)
        if "```json" in response:
            response = re.sub(r"```json|```", "", response, flags=re.DOTALL).strip()
        logging.info(f"response clean ==>\n{response}")
        if response.find("**ERROR**") >= 0:
            logging.error(f"request system is {system},history is {history}")
            raise Exception(response)
        #set_llm_cache(self._llm_model.llm_name, system, response, history, gen_conf)
        return response


    async def __call__(self, content, key_to_parse, metadata_type="default",callback=None):
        results = {}
        #该异步函数执行对内容的要素抽取
        async def extract(content):
            nonlocal results
            nonlocal key_to_parse
            result = None
            logging.info(f"PaperExtractor extract for {key_to_parse}")
            if not key_to_parse:
                key_to_parse = constant.keyvalues_mapping.get(metadata_type)
            # 过滤字段
            keys_to_use_list = []
            for i in key_to_parse:
                if i["name"] not in constant.exclude_fields:
                    keys_to_use_list.append(i['name'])

            keys_to_use = "、".join(keys_to_use_list)
            logging.info(f"PaperExtractor extract for {keys_to_use}")
            prompt_use =  paper_extraction_prompt(content,keys_to_use)
            async with chat_limiter:
                result = await self._chat(
                    "You're a helpful assistant.",
                    [
                        {
                            "role": "user",
                            "content": prompt_use,
                        },
                        {
                            "role": "system",
                            "content": prompt_use,
                        }

                    ],
                    {"temperature": 0.3,'response_format':{'type': 'json_object'}},
                )
            logging.info(f"PaperExtractor Result : {result}")
            try:
                keyvalues = json.loads(result)
                logging.info(f"dict {keyvalues}")
            except Exception as e:
                logging.error(f"PaperExtractor Failed for {e}")
                keyvalues = {}
            for key_, value_ in keyvalues.items():
                key__ = key_.replace(" ", "")
                if key__ in keys_to_use_list:
                    results[key__]=value_
                    #results[key_+'@@@AI']=value_
            return results
        async with trio.open_nursery() as nursery:
               async with chat_limiter:
                    nursery.start_soon(extract, content)

        if callback:
            callback(
                msg="要素抽取完成"
            )
        return results 
