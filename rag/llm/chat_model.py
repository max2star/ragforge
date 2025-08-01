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
import asyncio
import json
import logging
import os
import random
import re
import time
from abc import ABC

import openai
import requests
from dashscope import Generation
from ollama import Client
from openai import OpenAI
from openai.lib.azure import AzureOpenAI
from zhipuai import ZhipuAI

from rag.nlp import is_chinese, is_english
from rag.utils import num_tokens_from_string

# Error message constants
ERROR_PREFIX = "**ERROR**"
ERROR_RATE_LIMIT = "RATE_LIMIT_EXCEEDED"
ERROR_AUTHENTICATION = "AUTH_ERROR"
ERROR_INVALID_REQUEST = "INVALID_REQUEST"
ERROR_SERVER = "SERVER_ERROR"
ERROR_TIMEOUT = "TIMEOUT"
ERROR_CONNECTION = "CONNECTION_ERROR"
ERROR_MODEL = "MODEL_ERROR"
ERROR_CONTENT_FILTER = "CONTENT_FILTERED"
ERROR_QUOTA = "QUOTA_EXCEEDED"
ERROR_MAX_RETRIES = "MAX_RETRIES_EXCEEDED"
ERROR_GENERIC = "GENERIC_ERROR"

LENGTH_NOTIFICATION_CN = "······\n由于大模型的上下文窗口大小限制，回答已经被大模型截断。"
LENGTH_NOTIFICATION_EN = "...\nThe answer is truncated by your chosen LLM due to its limitation on context length."


class Base(ABC):
    def __init__(self, key, model_name, base_url):
        timeout = int(os.environ.get("LM_TIMEOUT_SECONDS", 600))
        self.client = OpenAI(api_key=key, base_url=base_url, timeout=timeout)
        self.model_name = model_name
        # Configure retry parameters
        self.max_retries = int(os.environ.get("LLM_MAX_RETRIES", 5))
        self.base_delay = float(os.environ.get("LLM_BASE_DELAY", 2.0))
        self.is_tools = False

    def _get_delay(self, attempt):
        """Calculate retry delay time"""
        return self.base_delay * (2**attempt) + random.uniform(0, 0.5)

    def _classify_error(self, error):
        """Classify error based on error message content"""
        error_str = str(error).lower()

        if "rate limit" in error_str or "429" in error_str or "tpm limit" in error_str or "too many requests" in error_str or "requests per minute" in error_str:
            return ERROR_RATE_LIMIT
        elif "auth" in error_str or "key" in error_str or "apikey" in error_str or "401" in error_str or "forbidden" in error_str or "permission" in error_str:
            return ERROR_AUTHENTICATION
        elif "invalid" in error_str or "bad request" in error_str or "400" in error_str or "format" in error_str or "malformed" in error_str or "parameter" in error_str:
            return ERROR_INVALID_REQUEST
        elif "server" in error_str or "502" in error_str or "503" in error_str or "504" in error_str or "500" in error_str or "unavailable" in error_str:
            return ERROR_SERVER
        elif "timeout" in error_str or "timed out" in error_str:
            return ERROR_TIMEOUT
        elif "connect" in error_str or "network" in error_str or "unreachable" in error_str or "dns" in error_str:
            return ERROR_CONNECTION
        elif "quota" in error_str or "capacity" in error_str or "credit" in error_str or "billing" in error_str or "limit" in error_str and "rate" not in error_str:
            return ERROR_QUOTA
        elif "filter" in error_str or "content" in error_str or "policy" in error_str or "blocked" in error_str or "safety" in error_str or "inappropriate" in error_str:
            return ERROR_CONTENT_FILTER
        elif "model" in error_str or "not found" in error_str or "does not exist" in error_str or "not available" in error_str:
            return ERROR_MODEL
        else:
            return ERROR_GENERIC

    def bind_tools(self, toolcall_session, tools):
        if not (toolcall_session and tools):
            return
        self.is_tools = True
        self.toolcall_session = toolcall_session
        self.tools = tools

    def chat_with_tools(self, system: str, history: list, gen_conf: dict):
        if "max_tokens" in gen_conf:
            del gen_conf["max_tokens"]

        tools = self.tools

        if system:
            history.insert(0, {"role": "system", "content": system})

        ans = ""
        tk_count = 0
        # Implement exponential backoff retry strategy
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(model=self.model_name, messages=history, tools=tools, **gen_conf)

                assistant_output = response.choices[0].message
                if not ans and "tool_calls" not in assistant_output and "reasoning_content" in assistant_output:
                    ans += "<think>" + ans + "</think>"
                ans += response.choices[0].message.content

                if not response.choices[0].message.tool_calls:
                    tk_count += self.total_token_count(response)
                    if response.choices[0].finish_reason == "length":
                        if is_chinese([ans]):
                            ans += LENGTH_NOTIFICATION_CN
                        else:
                            ans += LENGTH_NOTIFICATION_EN
                    return ans, tk_count

                tk_count += self.total_token_count(response)
                history.append(assistant_output)

                for tool_call in response.choices[0].message.tool_calls:
                    name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)

                    tool_response = self.toolcall_session.tool_call(name, args)
                    # if tool_response.choices[0].finish_reason == "length":
                    #     if is_chinese(ans):
                    #         ans += LENGTH_NOTIFICATION_CN
                    #     else:
                    #         ans += LENGTH_NOTIFICATION_EN
                    #     return ans, tk_count + self.total_token_count(tool_response)
                    history.append({"role": "tool", "tool_call_id": tool_call.id, "content": str(tool_response)})

                final_response = self.client.chat.completions.create(model=self.model_name, messages=history, tools=tools, **gen_conf)
                assistant_output = final_response.choices[0].message
                if "tool_calls" not in assistant_output and "reasoning_content" in assistant_output:
                    ans += "<think>" + ans + "</think>"
                ans += final_response.choices[0].message.content
                if final_response.choices[0].finish_reason == "length":
                    tk_count += self.total_token_count(response)
                    if is_chinese([ans]):
                        ans += LENGTH_NOTIFICATION_CN
                    else:
                        ans += LENGTH_NOTIFICATION_EN
                    return ans, tk_count
                return ans, tk_count

            except Exception as e:
                logging.exception("OpenAI cat_with_tools")
                # Classify the error
                error_code = self._classify_error(e)

                # Check if it's a rate limit error or server error and not the last attempt
                should_retry = (error_code == ERROR_RATE_LIMIT or error_code == ERROR_SERVER) and attempt < self.max_retries - 1

                if should_retry:
                    delay = self._get_delay(attempt)
                    logging.warning(f"Error: {error_code}. Retrying in {delay:.2f} seconds... (Attempt {attempt + 1}/{self.max_retries})")
                    time.sleep(delay)
                else:
                    # For non-rate limit errors or the last attempt, return an error message
                    logging.error(f"Error: {error_code}. Attempt {attempt + 1}/{self.max_retries})")
                    if attempt == self.max_retries - 1:
                        error_code = ERROR_MAX_RETRIES
                    return f"{ERROR_PREFIX}: {error_code} - {str(e)}", 0

    def chat(self, system, history, gen_conf):
        if system:
            history.insert(0, {"role": "system", "content": system})
        if "max_tokens" in gen_conf:
            del gen_conf["max_tokens"]

        # Implement exponential backoff retry strategy
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(model=self.model_name, messages=history, **gen_conf)

                if any([not response.choices, not response.choices[0].message, not response.choices[0].message.content]):
                    return "", 0
                ans = response.choices[0].message.content.strip()
                if response.choices[0].finish_reason == "length":
                    if is_chinese(ans):
                        ans += LENGTH_NOTIFICATION_CN
                    else:
                        ans += LENGTH_NOTIFICATION_EN
                return ans, self.total_token_count(response)
            except Exception as e:
                logging.exception("chat_model.Base.chat got exception")
                import traceback
                traceback.print_exc()
                logging.error("Exception {} ,excetion info is {}".format(e, traceback.format_exc()))
                # Classify the error
                error_code = self._classify_error(e)

                # Check if it's a rate limit error or server error and not the last attempt
                should_retry = (error_code == ERROR_RATE_LIMIT or error_code == ERROR_SERVER) and attempt < self.max_retries - 1

                if should_retry:
                    delay = self._get_delay(attempt)
                    logging.warning(f"Error: {error_code}. Retrying in {delay:.2f} seconds... (Attempt {attempt + 1}/{self.max_retries})")
                    time.sleep(delay)
                else:
                    logging.error(f"Error: {error_code}. Attempt {attempt + 1}/{self.max_retries})")
                    # For non-rate limit errors or the last attempt, return an error message
                    if attempt == self.max_retries - 1:
                        error_code = ERROR_MAX_RETRIES
                    return f"{ERROR_PREFIX}: {error_code} - {str(e)}", 0

    def _wrap_toolcall_message(self, stream):
        final_tool_calls = {}

        for chunk in stream:
            for tool_call in chunk.choices[0].delta.tool_calls or []:
                index = tool_call.index

                if index not in final_tool_calls:
                    final_tool_calls[index] = tool_call

                final_tool_calls[index].function.arguments += tool_call.function.arguments

        return final_tool_calls

    def chat_streamly_with_tools(self, system: str, history: list, gen_conf: dict):
        if "max_tokens" in gen_conf:
            del gen_conf["max_tokens"]

        tools = self.tools

        if system:
            history.insert(0, {"role": "system", "content": system})

        ans = ""
        total_tokens = 0
        reasoning_start = False
        finish_completion = False
        final_tool_calls = {}
        try:
            response = self.client.chat.completions.create(model=self.model_name, messages=history, stream=True, tools=tools, **gen_conf)
            while not finish_completion:
                for resp in response:
                    if resp.choices[0].delta.tool_calls:
                        for tool_call in resp.choices[0].delta.tool_calls or []:
                            index = tool_call.index

                            if index not in final_tool_calls:
                                final_tool_calls[index] = tool_call

                            final_tool_calls[index].function.arguments += tool_call.function.arguments
                        if resp.choices[0].finish_reason != "stop":
                            continue
                    else:
                        if not resp.choices:
                            continue
                        if not resp.choices[0].delta.content:
                            resp.choices[0].delta.content = ""
                        if hasattr(resp.choices[0].delta, "reasoning_content") and resp.choices[0].delta.reasoning_content:
                            ans = ""
                            if not reasoning_start:
                                reasoning_start = True
                                ans = "<think>"
                            ans += resp.choices[0].delta.reasoning_content + "</think>"
                        else:
                            reasoning_start = False
                            ans = resp.choices[0].delta.content

                        tol = self.total_token_count(resp)
                        if not tol:
                            total_tokens += num_tokens_from_string(resp.choices[0].delta.content)
                        else:
                            total_tokens += tol

                        finish_reason = resp.choices[0].finish_reason
                        if finish_reason == "tool_calls" and final_tool_calls:
                            for tool_call in final_tool_calls.values():
                                name = tool_call.function.name
                                try:
                                    if name == "get_current_weather":
                                        args = json.loads('{"location":"Shanghai"}')
                                    else:
                                        args = json.loads(tool_call.function.arguments)
                                except Exception:
                                    continue
                                # args = json.loads(tool_call.function.arguments)
                                tool_response = self.toolcall_session.tool_call(name, args)
                                history.append(
                                    {
                                        "role": "assistant",
                                        "refusal": "",
                                        "content": "",
                                        "audio": "",
                                        "function_call": "",
                                        "tool_calls": [
                                            {
                                                "index": tool_call.index,
                                                "id": tool_call.id,
                                                "function": tool_call.function,
                                                "type": "function",
                                            },
                                        ],
                                    }
                                )
                                # if tool_response.choices[0].finish_reason == "length":
                                #     if is_chinese(ans):
                                #         ans += LENGTH_NOTIFICATION_CN
                                #     else:
                                #         ans += LENGTH_NOTIFICATION_EN
                                #     return ans, total_tokens + self.total_token_count(tool_response)
                                history.append({"role": "tool", "tool_call_id": tool_call.id, "content": str(tool_response)})
                            final_tool_calls = {}
                            response = self.client.chat.completions.create(model=self.model_name, messages=history, stream=True, tools=tools, **gen_conf)
                            continue
                        if finish_reason == "length":
                            if is_chinese(ans):
                                ans += LENGTH_NOTIFICATION_CN
                            else:
                                ans += LENGTH_NOTIFICATION_EN
                            return ans, total_tokens + self.total_token_count(resp)
                        if finish_reason == "stop":
                            finish_completion = True
                            yield ans
                            break
                        yield ans
                        continue

        except openai.APIError as e:
            yield ans + "\n**ERROR**: " + str(e)

        yield total_tokens

    def chat_streamly(self, system, history, gen_conf):
        if system:
            history.insert(0, {"role": "system", "content": system})
        if "max_tokens" in gen_conf:
            del gen_conf["max_tokens"]
        ans = ""
        total_tokens = 0
        reasoning_start = False
        try:
            response = self.client.chat.completions.create(model=self.model_name, messages=history, stream=True, **gen_conf)
            for resp in response:
                if not resp.choices:
                    continue
                if not resp.choices[0].delta.content:
                    resp.choices[0].delta.content = ""
                if hasattr(resp.choices[0].delta, "reasoning_content") and resp.choices[0].delta.reasoning_content:
                    ans = ""
                    if not reasoning_start:
                        reasoning_start = True
                        ans = "<think>"
                    ans += resp.choices[0].delta.reasoning_content + "</think>"
                else:
                    reasoning_start = False
                    ans = resp.choices[0].delta.content

                tol = self.total_token_count(resp)
                if not tol:
                    total_tokens += num_tokens_from_string(resp.choices[0].delta.content)
                else:
                    total_tokens += tol

                if resp.choices[0].finish_reason == "length":
                    if is_chinese(ans):
                        ans += LENGTH_NOTIFICATION_CN
                    else:
                        ans += LENGTH_NOTIFICATION_EN
                yield ans

        except openai.APIError as e:
            yield ans + "\n**ERROR**: " + str(e)

        yield total_tokens

    def total_token_count(self, resp):
        try:
            return resp.usage.total_tokens
        except Exception:
            pass
        try:
            return resp["usage"]["total_tokens"]
        except Exception:
            pass
        return 0

    def _calculate_dynamic_ctx(self, history):
        """Calculate dynamic context window size"""

        def count_tokens(text):
            """Calculate token count for text"""
            # Simple calculation: 1 token per ASCII character
            # 2 tokens for non-ASCII characters (Chinese, Japanese, Korean, etc.)
            total = 0
            for char in text:
                if ord(char) < 128:  # ASCII characters
                    total += 1
                else:  # Non-ASCII characters (Chinese, Japanese, Korean, etc.)
                    total += 2
            return total

        # Calculate total tokens for all messages
        total_tokens = 0
        for message in history:
            content = message.get("content", "")
            # Calculate content tokens
            content_tokens = count_tokens(content)
            # Add role marker token overhead
            role_tokens = 4
            total_tokens += content_tokens + role_tokens

        # Apply 1.2x buffer ratio
        total_tokens_with_buffer = int(total_tokens * 1.2)

        if total_tokens_with_buffer <= 8192:
            ctx_size = 8192
        else:
            ctx_multiplier = (total_tokens_with_buffer // 8192) + 1
            ctx_size = ctx_multiplier * 8192

        return ctx_size


class GptTurbo(Base):
    def __init__(self, key, model_name="gpt-3.5-turbo", base_url="https://api.openai.com/v1"):
        if not base_url:
            base_url = "https://api.openai.com/v1"
        super().__init__(key, model_name, base_url)


class MoonshotChat(Base):
    def __init__(self, key, model_name="moonshot-v1-8k", base_url="https://api.moonshot.cn/v1"):
        if not base_url:
            base_url = "https://api.moonshot.cn/v1"
        super().__init__(key, model_name, base_url)


class XinferenceChat(Base):
    def __init__(self, key=None, model_name="", base_url=""):
        if not base_url:
            raise ValueError("Local llm url cannot be None")
        if base_url.split("/")[-1] != "v1":
            base_url = os.path.join(base_url, "v1")
        super().__init__(key, model_name, base_url)


class HuggingFaceChat(Base):
    def __init__(self, key=None, model_name="", base_url=""):
        if not base_url:
            raise ValueError("Local llm url cannot be None")
        if base_url.split("/")[-1] != "v1":
            base_url = os.path.join(base_url, "v1")
        super().__init__(key, model_name.split("___")[0], base_url)


class ModelScopeChat(Base):
    def __init__(self, key=None, model_name="", base_url=""):
        if not base_url:
            raise ValueError("Local llm url cannot be None")
        base_url = base_url.rstrip("/")
        if base_url.split("/")[-1] != "v1":
            base_url = os.path.join(base_url, "v1")
        super().__init__(key, model_name.split("___")[0], base_url)


class DeepSeekChat(Base):
    def __init__(self, key, model_name="deepseek-chat", base_url="https://api.deepseek.com/v1"):
        if not base_url:
            base_url = "https://api.deepseek.com/v1"
        super().__init__(key, model_name, base_url)


class AzureChat(Base):
    def __init__(self, key, model_name, **kwargs):
        api_key = json.loads(key).get("api_key", "")
        api_version = json.loads(key).get("api_version", "2024-02-01")
        super().__init__(key, model_name, kwargs["base_url"])
        self.client = AzureOpenAI(api_key=api_key, azure_endpoint=kwargs["base_url"], api_version=api_version)
        self.model_name = model_name


class BaiChuanChat(Base):
    def __init__(self, key, model_name="Baichuan3-Turbo", base_url="https://api.baichuan-ai.com/v1"):
        if not base_url:
            base_url = "https://api.baichuan-ai.com/v1"
        super().__init__(key, model_name, base_url)

    @staticmethod
    def _format_params(params):
        return {
            "temperature": params.get("temperature", 0.3),
            "top_p": params.get("top_p", 0.85),
        }

    def chat(self, system, history, gen_conf):
        if system:
            history.insert(0, {"role": "system", "content": system})
        if "max_tokens" in gen_conf:
            del gen_conf["max_tokens"]
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=history,
                extra_body={"tools": [{"type": "web_search", "web_search": {"enable": True, "search_mode": "performance_first"}}]},
                **self._format_params(gen_conf),
            )
            ans = response.choices[0].message.content.strip()
            if response.choices[0].finish_reason == "length":
                if is_chinese([ans]):
                    ans += LENGTH_NOTIFICATION_CN
                else:
                    ans += LENGTH_NOTIFICATION_EN
            return ans, self.total_token_count(response)
        except openai.APIError as e:
            return "**ERROR**: " + str(e), 0

    def chat_streamly(self, system, history, gen_conf):
        if system:
            history.insert(0, {"role": "system", "content": system})
        if "max_tokens" in gen_conf:
            del gen_conf["max_tokens"]
        ans = ""
        total_tokens = 0
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=history,
                extra_body={"tools": [{"type": "web_search", "web_search": {"enable": True, "search_mode": "performance_first"}}]},
                stream=True,
                **self._format_params(gen_conf),
            )
            for resp in response:
                if not resp.choices:
                    continue
                if not resp.choices[0].delta.content:
                    resp.choices[0].delta.content = ""
                ans = resp.choices[0].delta.content
                tol = self.total_token_count(resp)
                if not tol:
                    total_tokens += num_tokens_from_string(resp.choices[0].delta.content)
                else:
                    total_tokens = tol
                if resp.choices[0].finish_reason == "length":
                    if is_chinese([ans]):
                        ans += LENGTH_NOTIFICATION_CN
                    else:
                        ans += LENGTH_NOTIFICATION_EN
                yield ans

        except Exception as e:
            yield ans + "\n**ERROR**: " + str(e)

        yield total_tokens


class QWenChat(Base):
    def __init__(self, key, model_name=Generation.Models.qwen_turbo, **kwargs):
        super().__init__(key, model_name, base_url=None)

        import dashscope

        dashscope.api_key = key
        self.model_name = model_name
        if self.is_reasoning_model(self.model_name):
            super().__init__(key, model_name, "https://dashscope.aliyuncs.com/compatible-mode/v1")

    def chat_with_tools(self, system: str, history: list, gen_conf: dict) -> tuple[str, int]:
        if "max_tokens" in gen_conf:
            del gen_conf["max_tokens"]
        # if self.is_reasoning_model(self.model_name):
        #     return super().chat(system, history, gen_conf)

        stream_flag = str(os.environ.get("QWEN_CHAT_BY_STREAM", "true")).lower() == "true"
        if not stream_flag:
            from http import HTTPStatus

            tools = self.tools

            if system:
                history.insert(0, {"role": "system", "content": system})

            response = Generation.call(self.model_name, messages=history, result_format="message", tools=tools, **gen_conf)
            ans = ""
            tk_count = 0
            if response.status_code == HTTPStatus.OK:
                assistant_output = response.output.choices[0].message
                if not ans and "tool_calls" not in assistant_output and "reasoning_content" in assistant_output:
                    ans += "<think>" + ans + "</think>"
                ans += response.output.choices[0].message.content

                if "tool_calls" not in assistant_output:
                    tk_count += self.total_token_count(response)
                    if response.output.choices[0].get("finish_reason", "") == "length":
                        if is_chinese([ans]):
                            ans += LENGTH_NOTIFICATION_CN
                        else:
                            ans += LENGTH_NOTIFICATION_EN
                    return ans, tk_count

                tk_count += self.total_token_count(response)
                history.append(assistant_output)

                while "tool_calls" in assistant_output:
                    tool_info = {"content": "", "role": "tool", "tool_call_id": assistant_output.tool_calls[0]["id"]}
                    tool_name = assistant_output.tool_calls[0]["function"]["name"]
                    if tool_name:
                        arguments = json.loads(assistant_output.tool_calls[0]["function"]["arguments"])
                        tool_info["content"] = self.toolcall_session.tool_call(name=tool_name, arguments=arguments)
                    history.append(tool_info)

                    response = Generation.call(self.model_name, messages=history, result_format="message", tools=self.tools, **gen_conf)
                    if response.output.choices[0].get("finish_reason", "") == "length":
                        tk_count += self.total_token_count(response)
                        if is_chinese([ans]):
                            ans += LENGTH_NOTIFICATION_CN
                        else:
                            ans += LENGTH_NOTIFICATION_EN
                        return ans, tk_count

                    tk_count += self.total_token_count(response)
                    assistant_output = response.output.choices[0].message
                    if assistant_output.content is None:
                        assistant_output.content = ""
                    history.append(response)
                ans += assistant_output["content"]
                return ans, tk_count
            else:
                return "**ERROR**: " + response.message, tk_count
        else:
            result_list = []
            for result in self._chat_streamly_with_tools(system, history, gen_conf, incremental_output=True):
                result_list.append(result)
            error_msg_list = [result for result in result_list if str(result).find("**ERROR**") >= 0]
            if len(error_msg_list) > 0:
                return "**ERROR**: " + "".join(error_msg_list), 0
            else:
                return "".join(result_list[:-1]), result_list[-1]

    def chat(self, system, history, gen_conf):
        if "max_tokens" in gen_conf:
            del gen_conf["max_tokens"]
        if self.is_reasoning_model(self.model_name):
            return super().chat(system, history, gen_conf)

        stream_flag = str(os.environ.get("QWEN_CHAT_BY_STREAM", "true")).lower() == "true"
        if not stream_flag:
            from http import HTTPStatus

            if system:
                history.insert(0, {"role": "system", "content": system})

            response = Generation.call(self.model_name, messages=history, result_format="message", **gen_conf)
            ans = ""
            tk_count = 0
            if response.status_code == HTTPStatus.OK:
                ans += response.output.choices[0]["message"]["content"]
                tk_count += self.total_token_count(response)
                if response.output.choices[0].get("finish_reason", "") == "length":
                    if is_chinese([ans]):
                        ans += LENGTH_NOTIFICATION_CN
                    else:
                        ans += LENGTH_NOTIFICATION_EN
                return ans, tk_count

            return "**ERROR**: " + response.message, tk_count
        else:
            g = self._chat_streamly(system, history, gen_conf, incremental_output=True)
            result_list = list(g)
            error_msg_list = [item for item in result_list if str(item).find("**ERROR**") >= 0]
            if len(error_msg_list) > 0:
                return "**ERROR**: " + "".join(error_msg_list), 0
            else:
                return "".join(result_list[:-1]), result_list[-1]

    def _wrap_toolcall_message(self, old_message, message):
        if not old_message:
            return message
        tool_call_id = message["tool_calls"][0].get("id")
        if tool_call_id:
            old_message.tool_calls[0]["id"] = tool_call_id
        function = message.tool_calls[0]["function"]
        if function:
            if function.get("name"):
                old_message.tool_calls[0]["function"]["name"] = function["name"]
            if function.get("arguments"):
                old_message.tool_calls[0]["function"]["arguments"] += function["arguments"]
        return old_message

    def _chat_streamly_with_tools(self, system: str, history: list, gen_conf: dict, incremental_output=True):
        from http import HTTPStatus

        if system:
            history.insert(0, {"role": "system", "content": system})
        if "max_tokens" in gen_conf:
            del gen_conf["max_tokens"]
        ans = ""
        tk_count = 0
        try:
            response = Generation.call(self.model_name, messages=history, result_format="message", tools=self.tools, stream=True, incremental_output=incremental_output, **gen_conf)
            tool_info = {"content": "", "role": "tool"}
            toolcall_message = None
            tool_name = ""
            tool_arguments = ""
            finish_completion = False
            reasoning_start = False
            while not finish_completion:
                for resp in response:
                    if resp.status_code == HTTPStatus.OK:
                        assistant_output = resp.output.choices[0].message
                        ans = resp.output.choices[0].message.content
                        if not ans and "tool_calls" not in assistant_output and "reasoning_content" in assistant_output:
                            ans = resp.output.choices[0].message.reasoning_content
                            if not reasoning_start:
                                reasoning_start = True
                                ans = "<think>" + ans
                            else:
                                ans = ans + "</think>"

                        if "tool_calls" not in assistant_output:
                            reasoning_start = False
                            tk_count += self.total_token_count(resp)
                            if resp.output.choices[0].get("finish_reason", "") == "length":
                                if is_chinese([ans]):
                                    ans += LENGTH_NOTIFICATION_CN
                                else:
                                    ans += LENGTH_NOTIFICATION_EN
                            finish_reason = resp.output.choices[0]["finish_reason"]
                            if finish_reason == "stop":
                                finish_completion = True
                                yield ans
                                break
                            yield ans
                            continue

                        tk_count += self.total_token_count(resp)
                        toolcall_message = self._wrap_toolcall_message(toolcall_message, assistant_output)
                        if "tool_calls" in assistant_output:
                            tool_call_finish_reason = resp.output.choices[0]["finish_reason"]
                            if tool_call_finish_reason == "tool_calls":
                                try:
                                    tool_arguments = json.loads(toolcall_message.tool_calls[0]["function"]["arguments"])
                                except Exception as e:
                                    logging.exception(msg="_chat_streamly_with_tool tool call error")
                                    yield ans + "\n**ERROR**: " + str(e)
                                    finish_completion = True
                                    break

                                tool_name = toolcall_message.tool_calls[0]["function"]["name"]
                                history.append(toolcall_message)
                                tool_info["content"] = self.toolcall_session.tool_call(name=tool_name, arguments=tool_arguments)
                                history.append(tool_info)
                                tool_info = {"content": "", "role": "tool"}
                                tool_name = ""
                                tool_arguments = ""
                                toolcall_message = None
                                response = Generation.call(self.model_name, messages=history, result_format="message", tools=self.tools, stream=True, incremental_output=incremental_output, **gen_conf)
                    else:
                        yield (
                            ans + "\n**ERROR**: " + resp.output.choices[0].message
                            if not re.search(r" (key|quota)", str(resp.message).lower())
                            else "Out of credit. Please set the API key in **settings > Model providers.**"
                        )
        except Exception as e:
            logging.exception(msg="_chat_streamly_with_tool")
            yield ans + "\n**ERROR**: " + str(e)
        yield tk_count

    def _chat_streamly(self, system, history, gen_conf, incremental_output=True):
        from http import HTTPStatus

        if system:
            history.insert(0, {"role": "system", "content": system})
        if "max_tokens" in gen_conf:
            del gen_conf["max_tokens"]
        ans = ""
        tk_count = 0
        try:
            response = Generation.call(self.model_name, messages=history, result_format="message", stream=True, incremental_output=incremental_output, **gen_conf)
            for resp in response:
                if resp.status_code == HTTPStatus.OK:
                    ans = resp.output.choices[0]["message"]["content"]
                    tk_count = self.total_token_count(resp)
                    if resp.output.choices[0].get("finish_reason", "") == "length":
                        if is_chinese(ans):
                            ans += LENGTH_NOTIFICATION_CN
                        else:
                            ans += LENGTH_NOTIFICATION_EN
                    yield ans
                else:
                    yield (
                        ans + "\n**ERROR**: " + resp.message
                        if not re.search(r" (key|quota)", str(resp.message).lower())
                        else "Out of credit. Please set the API key in **settings > Model providers.**"
                    )
        except Exception as e:
            yield ans + "\n**ERROR**: " + str(e)

        yield tk_count

    def chat_streamly_with_tools(self, system: str, history: list, gen_conf: dict, incremental_output=True):
        if "max_tokens" in gen_conf:
            del gen_conf["max_tokens"]

        for txt in self._chat_streamly_with_tools(system, history, gen_conf, incremental_output=incremental_output):
            yield txt

    def chat_streamly(self, system, history, gen_conf):
        if "max_tokens" in gen_conf:
            del gen_conf["max_tokens"]
        if self.is_reasoning_model(self.model_name):
            return super().chat_streamly(system, history, gen_conf)

        return self._chat_streamly(system, history, gen_conf)

    @staticmethod
    def is_reasoning_model(model_name: str) -> bool:
        return any(
            [
                model_name.lower().find("deepseek") >= 0,
                model_name.lower().find("qwq") >= 0 and model_name.lower() != "qwq-32b-preview",
            ]
        )


class ZhipuChat(Base):
    def __init__(self, key, model_name="glm-3-turbo", **kwargs):
        super().__init__(key, model_name, base_url=None)

        self.client = ZhipuAI(api_key=key)
        self.model_name = model_name

    def chat(self, system, history, gen_conf):
        if system:
            history.insert(0, {"role": "system", "content": system})
        if "max_tokens" in gen_conf:
            del gen_conf["max_tokens"]
        try:
            if "presence_penalty" in gen_conf:
                del gen_conf["presence_penalty"]
            if "frequency_penalty" in gen_conf:
                del gen_conf["frequency_penalty"]
            response = self.client.chat.completions.create(model=self.model_name, messages=history, **gen_conf)
            ans = response.choices[0].message.content.strip()
            if response.choices[0].finish_reason == "length":
                if is_chinese(ans):
                    ans += LENGTH_NOTIFICATION_CN
                else:
                    ans += LENGTH_NOTIFICATION_EN
            return ans, self.total_token_count(response)
        except Exception as e:
            return "**ERROR**: " + str(e), 0

    def chat_streamly(self, system, history, gen_conf):
        if system:
            history.insert(0, {"role": "system", "content": system})
        if "max_tokens" in gen_conf:
            del gen_conf["max_tokens"]
        if "presence_penalty" in gen_conf:
            del gen_conf["presence_penalty"]
        if "frequency_penalty" in gen_conf:
            del gen_conf["frequency_penalty"]
        ans = ""
        tk_count = 0
        try:
            response = self.client.chat.completions.create(model=self.model_name, messages=history, stream=True, **gen_conf)
            for resp in response:
                if not resp.choices[0].delta.content:
                    continue
                delta = resp.choices[0].delta.content
                ans = delta
                if resp.choices[0].finish_reason == "length":
                    if is_chinese(ans):
                        ans += LENGTH_NOTIFICATION_CN
                    else:
                        ans += LENGTH_NOTIFICATION_EN
                    tk_count = self.total_token_count(resp)
                if resp.choices[0].finish_reason == "stop":
                    tk_count = self.total_token_count(resp)
                yield ans
        except Exception as e:
            yield ans + "\n**ERROR**: " + str(e)

        yield tk_count


class OllamaChat(Base):
    def __init__(self, key, model_name, **kwargs):
        super().__init__(key, model_name, base_url=None)

        self.client = Client(host=kwargs["base_url"]) if not key or key == "x" else Client(host=kwargs["base_url"], headers={"Authorization": f"Bearer {key}"})
        self.model_name = model_name

    def chat(self, system, history, gen_conf):
        if system:
            history.insert(0, {"role": "system", "content": system})
        if "max_tokens" in gen_conf:
            del gen_conf["max_tokens"]
        try:
            # Calculate context size
            ctx_size = self._calculate_dynamic_ctx(history)

            options = {"num_ctx": ctx_size}
            if "temperature" in gen_conf:
                options["temperature"] = gen_conf["temperature"]
            if "max_tokens" in gen_conf:
                options["num_predict"] = gen_conf["max_tokens"]
            if "top_p" in gen_conf:
                options["top_p"] = gen_conf["top_p"]
            if "presence_penalty" in gen_conf:
                options["presence_penalty"] = gen_conf["presence_penalty"]
            if "frequency_penalty" in gen_conf:
                options["frequency_penalty"] = gen_conf["frequency_penalty"]

            response = self.client.chat(model=self.model_name, messages=history, options=options, keep_alive=10)
            ans = response["message"]["content"].strip()
            token_count = response.get("eval_count", 0) + response.get("prompt_eval_count", 0)
            return ans, token_count
        except Exception as e:
            return "**ERROR**: " + str(e), 0

    def chat_streamly(self, system, history, gen_conf):
        if system:
            history.insert(0, {"role": "system", "content": system})
        if "max_tokens" in gen_conf:
            del gen_conf["max_tokens"]
        try:
            # Calculate context size
            ctx_size = self._calculate_dynamic_ctx(history)
            options = {"num_ctx": ctx_size}
            if "temperature" in gen_conf:
                options["temperature"] = gen_conf["temperature"]
            if "max_tokens" in gen_conf:
                options["num_predict"] = gen_conf["max_tokens"]
            if "top_p" in gen_conf:
                options["top_p"] = gen_conf["top_p"]
            if "presence_penalty" in gen_conf:
                options["presence_penalty"] = gen_conf["presence_penalty"]
            if "frequency_penalty" in gen_conf:
                options["frequency_penalty"] = gen_conf["frequency_penalty"]

            ans = ""
            try:
                response = self.client.chat(model=self.model_name, messages=history, stream=True, options=options, keep_alive=10)
                for resp in response:
                    if resp["done"]:
                        token_count = resp.get("prompt_eval_count", 0) + resp.get("eval_count", 0)
                        yield token_count
                    ans = resp["message"]["content"]
                    yield ans
            except Exception as e:
                yield ans + "\n**ERROR**: " + str(e)
            yield 0
        except Exception as e:
            yield "**ERROR**: " + str(e)
            yield 0


class LocalAIChat(Base):
    def __init__(self, key, model_name, base_url):
        super().__init__(key, model_name, base_url=None)

        if not base_url:
            raise ValueError("Local llm url cannot be None")
        if base_url.split("/")[-1] != "v1":
            base_url = os.path.join(base_url, "v1")
        self.client = OpenAI(api_key="empty", base_url=base_url)
        self.model_name = model_name.split("___")[0]


class LocalLLM(Base):
    class RPCProxy:
        def __init__(self, host, port):
            self.host = host
            self.port = int(port)
            self.__conn()

        def __conn(self):
            from multiprocessing.connection import Client

            self._connection = Client((self.host, self.port), authkey=b"infiniflow-token4kevinhu")

        def __getattr__(self, name):
            import pickle

            def do_rpc(*args, **kwargs):
                for _ in range(3):
                    try:
                        self._connection.send(pickle.dumps((name, args, kwargs)))
                        return pickle.loads(self._connection.recv())
                    except Exception:
                        self.__conn()
                raise Exception("RPC connection lost!")

            return do_rpc

    def __init__(self, key, model_name):
        super().__init__(key, model_name, base_url=None)

        from jina import Client

        self.client = Client(port=12345, protocol="grpc", asyncio=True)

    def _prepare_prompt(self, system, history, gen_conf):
        from rag.svr.jina_server import Prompt

        if system:
            history.insert(0, {"role": "system", "content": system})
        return Prompt(message=history, gen_conf=gen_conf)

    def _stream_response(self, endpoint, prompt):
        from rag.svr.jina_server import Generation

        answer = ""
        try:
            res = self.client.stream_doc(on=endpoint, inputs=prompt, return_type=Generation)
            loop = asyncio.get_event_loop()
            try:
                while True:
                    answer = loop.run_until_complete(res.__anext__()).text
                    yield answer
            except StopAsyncIteration:
                pass
        except Exception as e:
            yield answer + "\n**ERROR**: " + str(e)
        yield num_tokens_from_string(answer)

    def chat(self, system, history, gen_conf):
        if "max_tokens" in gen_conf:
            del gen_conf["max_tokens"]
        prompt = self._prepare_prompt(system, history, gen_conf)
        chat_gen = self._stream_response("/chat", prompt)
        ans = next(chat_gen)
        total_tokens = next(chat_gen)
        return ans, total_tokens

    def chat_streamly(self, system, history, gen_conf):
        if "max_tokens" in gen_conf:
            del gen_conf["max_tokens"]
        prompt = self._prepare_prompt(system, history, gen_conf)
        return self._stream_response("/stream", prompt)


class VolcEngineChat(Base):
    def __init__(self, key, model_name, base_url="https://ark.cn-beijing.volces.com/api/v3"):
        super().__init__(key, model_name, base_url=None)

        """
        Since do not want to modify the original database fields, and the VolcEngine authentication method is quite special,
        Assemble ark_api_key, ep_id into api_key, store it as a dictionary type, and parse it for use
        model_name is for display only
        """
        base_url = base_url if base_url else "https://ark.cn-beijing.volces.com/api/v3"
        ark_api_key = json.loads(key).get("ark_api_key", "")
        model_name = json.loads(key).get("ep_id", "") + json.loads(key).get("endpoint_id", "")
        super().__init__(ark_api_key, model_name, base_url)


class MiniMaxChat(Base):
    def __init__(
        self,
        key,
        model_name,
        base_url="https://api.minimax.chat/v1/text/chatcompletion_v2",
    ):
        super().__init__(key, model_name, base_url=None)

        if not base_url:
            base_url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
        self.base_url = base_url
        self.model_name = model_name
        self.api_key = key

    def chat(self, system, history, gen_conf):
        if system:
            history.insert(0, {"role": "system", "content": system})
        for k in list(gen_conf.keys()):
            if k not in ["temperature", "top_p", "max_tokens"]:
                del gen_conf[k]
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = json.dumps({"model": self.model_name, "messages": history, **gen_conf})
        try:
            response = requests.request("POST", url=self.base_url, headers=headers, data=payload)
            response = response.json()
            ans = response["choices"][0]["message"]["content"].strip()
            if response["choices"][0]["finish_reason"] == "length":
                if is_chinese(ans):
                    ans += LENGTH_NOTIFICATION_CN
                else:
                    ans += LENGTH_NOTIFICATION_EN
            return ans, self.total_token_count(response)
        except Exception as e:
            return "**ERROR**: " + str(e), 0

    def chat_streamly(self, system, history, gen_conf):
        if system:
            history.insert(0, {"role": "system", "content": system})
        for k in list(gen_conf.keys()):
            if k not in ["temperature", "top_p", "max_tokens"]:
                del gen_conf[k]
        ans = ""
        total_tokens = 0
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = json.dumps(
                {
                    "model": self.model_name,
                    "messages": history,
                    "stream": True,
                    **gen_conf,
                }
            )
            response = requests.request(
                "POST",
                url=self.base_url,
                headers=headers,
                data=payload,
            )
            for resp in response.text.split("\n\n")[:-1]:
                resp = json.loads(resp[6:])
                text = ""
                if "choices" in resp and "delta" in resp["choices"][0]:
                    text = resp["choices"][0]["delta"]["content"]
                ans = text
                tol = self.total_token_count(resp)
                if not tol:
                    total_tokens += num_tokens_from_string(text)
                else:
                    total_tokens = tol
                yield ans

        except Exception as e:
            yield ans + "\n**ERROR**: " + str(e)

        yield total_tokens


class MistralChat(Base):
    def __init__(self, key, model_name, base_url=None):
        super().__init__(key, model_name, base_url=None)

        from mistralai.client import MistralClient

        self.client = MistralClient(api_key=key)
        self.model_name = model_name

    def chat(self, system, history, gen_conf):
        if system:
            history.insert(0, {"role": "system", "content": system})
        for k in list(gen_conf.keys()):
            if k not in ["temperature", "top_p", "max_tokens"]:
                del gen_conf[k]
        try:
            response = self.client.chat(model=self.model_name, messages=history, **gen_conf)
            ans = response.choices[0].message.content
            if response.choices[0].finish_reason == "length":
                if is_chinese(ans):
                    ans += LENGTH_NOTIFICATION_CN
                else:
                    ans += LENGTH_NOTIFICATION_EN
            return ans, self.total_token_count(response)
        except openai.APIError as e:
            return "**ERROR**: " + str(e), 0

    def chat_streamly(self, system, history, gen_conf):
        if system:
            history.insert(0, {"role": "system", "content": system})
        for k in list(gen_conf.keys()):
            if k not in ["temperature", "top_p", "max_tokens"]:
                del gen_conf[k]
        ans = ""
        total_tokens = 0
        try:
            response = self.client.chat_stream(model=self.model_name, messages=history, **gen_conf)
            for resp in response:
                if not resp.choices or not resp.choices[0].delta.content:
                    continue
                ans = resp.choices[0].delta.content
                total_tokens += 1
                if resp.choices[0].finish_reason == "length":
                    if is_chinese(ans):
                        ans += LENGTH_NOTIFICATION_CN
                    else:
                        ans += LENGTH_NOTIFICATION_EN
                yield ans

        except openai.APIError as e:
            yield ans + "\n**ERROR**: " + str(e)

        yield total_tokens


class BedrockChat(Base):
    def __init__(self, key, model_name, **kwargs):
        super().__init__(key, model_name, base_url=None)

        import boto3

        self.bedrock_ak = json.loads(key).get("bedrock_ak", "")
        self.bedrock_sk = json.loads(key).get("bedrock_sk", "")
        self.bedrock_region = json.loads(key).get("bedrock_region", "")
        self.model_name = model_name

        if self.bedrock_ak == "" or self.bedrock_sk == "" or self.bedrock_region == "":
            # Try to create a client using the default credentials (AWS_PROFILE, AWS_DEFAULT_REGION, etc.)
            self.client = boto3.client("bedrock-runtime")
        else:
            self.client = boto3.client(service_name="bedrock-runtime", region_name=self.bedrock_region, aws_access_key_id=self.bedrock_ak, aws_secret_access_key=self.bedrock_sk)

    def chat(self, system, history, gen_conf):
        from botocore.exceptions import ClientError

        for k in list(gen_conf.keys()):
            if k not in ["temperature"]:
                del gen_conf[k]
        for item in history:
            if not isinstance(item["content"], list) and not isinstance(item["content"], tuple):
                item["content"] = [{"text": item["content"]}]

        try:
            # Send the message to the model, using a basic inference configuration.
            response = self.client.converse(
                modelId=self.model_name,
                messages=history,
                inferenceConfig=gen_conf,
                system=[{"text": (system if system else "Answer the user's message.")}],
            )

            # Extract and print the response text.
            ans = response["output"]["message"]["content"][0]["text"]
            return ans, num_tokens_from_string(ans)

        except (ClientError, Exception) as e:
            return f"ERROR: Can't invoke '{self.model_name}'. Reason: {e}", 0

    def chat_streamly(self, system, history, gen_conf):
        from botocore.exceptions import ClientError

        for k in list(gen_conf.keys()):
            if k not in ["temperature"]:
                del gen_conf[k]
        for item in history:
            if not isinstance(item["content"], list) and not isinstance(item["content"], tuple):
                item["content"] = [{"text": item["content"]}]

        if self.model_name.split(".")[0] == "ai21":
            try:
                response = self.client.converse(modelId=self.model_name, messages=history, inferenceConfig=gen_conf, system=[{"text": (system if system else "Answer the user's message.")}])
                ans = response["output"]["message"]["content"][0]["text"]
                return ans, num_tokens_from_string(ans)

            except (ClientError, Exception) as e:
                return f"ERROR: Can't invoke '{self.model_name}'. Reason: {e}", 0

        ans = ""
        try:
            # Send the message to the model, using a basic inference configuration.
            streaming_response = self.client.converse_stream(
                modelId=self.model_name, messages=history, inferenceConfig=gen_conf, system=[{"text": (system if system else "Answer the user's message.")}]
            )

            # Extract and print the streamed response text in real-time.
            for resp in streaming_response["stream"]:
                if "contentBlockDelta" in resp:
                    ans = resp["contentBlockDelta"]["delta"]["text"]
                    yield ans

        except (ClientError, Exception) as e:
            yield ans + f"ERROR: Can't invoke '{self.model_name}'. Reason: {e}"

        yield num_tokens_from_string(ans)


class GeminiChat(Base):
    def __init__(self, key, model_name, base_url=None):
        super().__init__(key, model_name, base_url=None)

        from google.generativeai import GenerativeModel, client

        client.configure(api_key=key)
        _client = client.get_default_generative_client()
        self.model_name = "models/" + model_name
        self.model = GenerativeModel(model_name=self.model_name)
        self.model._client = _client

    def chat(self, system, history, gen_conf):
        from google.generativeai.types import content_types

        if system:
            self.model._system_instruction = content_types.to_content(system)
        for k in list(gen_conf.keys()):
            if k not in ["temperature", "top_p", "max_tokens"]:
                del gen_conf[k]
        for item in history:
            if "role" in item and item["role"] == "assistant":
                item["role"] = "model"
            if "role" in item and item["role"] == "system":
                item["role"] = "user"
            if "content" in item:
                item["parts"] = item.pop("content")

        try:
            response = self.model.generate_content(history, generation_config=gen_conf)
            ans = response.text
            return ans, response.usage_metadata.total_token_count
        except Exception as e:
            return "**ERROR**: " + str(e), 0

    def chat_streamly(self, system, history, gen_conf):
        from google.generativeai.types import content_types

        if system:
            self.model._system_instruction = content_types.to_content(system)
        for k in list(gen_conf.keys()):
            if k not in ["temperature", "top_p", "max_tokens"]:
                del gen_conf[k]
        for item in history:
            if "role" in item and item["role"] == "assistant":
                item["role"] = "model"
            if "content" in item:
                item["parts"] = item.pop("content")
        ans = ""
        try:
            response = self.model.generate_content(history, generation_config=gen_conf, stream=True)
            for resp in response:
                ans = resp.text
                yield ans

            yield response._chunks[-1].usage_metadata.total_token_count
        except Exception as e:
            yield ans + "\n**ERROR**: " + str(e)

        yield 0


class GroqChat(Base):
    def __init__(self, key, model_name, base_url=""):
        super().__init__(key, model_name, base_url=None)

        from groq import Groq

        self.client = Groq(api_key=key)
        self.model_name = model_name

    def chat(self, system, history, gen_conf):
        if system:
            history.insert(0, {"role": "system", "content": system})
        for k in list(gen_conf.keys()):
            if k not in ["temperature", "top_p", "max_tokens"]:
                del gen_conf[k]
        ans = ""
        try:
            response = self.client.chat.completions.create(model=self.model_name, messages=history, **gen_conf)
            ans = response.choices[0].message.content
            if response.choices[0].finish_reason == "length":
                if is_chinese(ans):
                    ans += LENGTH_NOTIFICATION_CN
                else:
                    ans += LENGTH_NOTIFICATION_EN
            return ans, self.total_token_count(response)
        except Exception as e:
            return ans + "\n**ERROR**: " + str(e), 0

    def chat_streamly(self, system, history, gen_conf):
        if system:
            history.insert(0, {"role": "system", "content": system})
        for k in list(gen_conf.keys()):
            if k not in ["temperature", "top_p", "max_tokens"]:
                del gen_conf[k]
        ans = ""
        total_tokens = 0
        try:
            response = self.client.chat.completions.create(model=self.model_name, messages=history, stream=True, **gen_conf)
            for resp in response:
                if not resp.choices or not resp.choices[0].delta.content:
                    continue
                ans = resp.choices[0].delta.content
                total_tokens += 1
                if resp.choices[0].finish_reason == "length":
                    if is_chinese(ans):
                        ans += LENGTH_NOTIFICATION_CN
                    else:
                        ans += LENGTH_NOTIFICATION_EN
                yield ans

        except Exception as e:
            yield ans + "\n**ERROR**: " + str(e)

        yield total_tokens


## openrouter
class OpenRouterChat(Base):
    def __init__(self, key, model_name, base_url="https://openrouter.ai/api/v1"):
        if not base_url:
            base_url = "https://openrouter.ai/api/v1"
        super().__init__(key, model_name, base_url)


class StepFunChat(Base):
    def __init__(self, key, model_name, base_url="https://api.stepfun.com/v1"):
        if not base_url:
            base_url = "https://api.stepfun.com/v1"
        super().__init__(key, model_name, base_url)


class NvidiaChat(Base):
    def __init__(self, key, model_name, base_url="https://integrate.api.nvidia.com/v1"):
        if not base_url:
            base_url = "https://integrate.api.nvidia.com/v1"
        super().__init__(key, model_name, base_url)


class LmStudioChat(Base):
    def __init__(self, key, model_name, base_url):
        if not base_url:
            raise ValueError("Local llm url cannot be None")
        if base_url.split("/")[-1] != "v1":
            base_url = os.path.join(base_url, "v1")
        super().__init__(key, model_name, base_url)
        self.client = OpenAI(api_key="lm-studio", base_url=base_url)
        self.model_name = model_name


class OpenAI_APIChat(Base):
    def __init__(self, key, model_name, base_url):
        if not base_url:
            raise ValueError("url cannot be None")
        model_name = model_name.split("___")[0]
        super().__init__(key, model_name, base_url)


class PPIOChat(Base):
    def __init__(self, key, model_name, base_url="https://api.ppinfra.com/v3/openai"):
        if not base_url:
            base_url = "https://api.ppinfra.com/v3/openai"
        super().__init__(key, model_name, base_url)


class CoHereChat(Base):
    def __init__(self, key, model_name, base_url=""):
        super().__init__(key, model_name, base_url=None)

        from cohere import Client

        self.client = Client(api_key=key)
        self.model_name = model_name

    def chat(self, system, history, gen_conf):
        if system:
            history.insert(0, {"role": "system", "content": system})
        if "max_tokens" in gen_conf:
            del gen_conf["max_tokens"]
        if "top_p" in gen_conf:
            gen_conf["p"] = gen_conf.pop("top_p")
        if "frequency_penalty" in gen_conf and "presence_penalty" in gen_conf:
            gen_conf.pop("presence_penalty")
        for item in history:
            if "role" in item and item["role"] == "user":
                item["role"] = "USER"
            if "role" in item and item["role"] == "assistant":
                item["role"] = "CHATBOT"
            if "content" in item:
                item["message"] = item.pop("content")
        mes = history.pop()["message"]
        ans = ""
        try:
            response = self.client.chat(model=self.model_name, chat_history=history, message=mes, **gen_conf)
            ans = response.text
            if response.finish_reason == "MAX_TOKENS":
                ans += "...\nFor the content length reason, it stopped, continue?" if is_english([ans]) else "······\n由于长度的原因，回答被截断了，要继续吗？"
            return (
                ans,
                response.meta.tokens.input_tokens + response.meta.tokens.output_tokens,
            )
        except Exception as e:
            return ans + "\n**ERROR**: " + str(e), 0

    def chat_streamly(self, system, history, gen_conf):
        if system:
            history.insert(0, {"role": "system", "content": system})
        if "max_tokens" in gen_conf:
            del gen_conf["max_tokens"]
        if "top_p" in gen_conf:
            gen_conf["p"] = gen_conf.pop("top_p")
        if "frequency_penalty" in gen_conf and "presence_penalty" in gen_conf:
            gen_conf.pop("presence_penalty")
        for item in history:
            if "role" in item and item["role"] == "user":
                item["role"] = "USER"
            if "role" in item and item["role"] == "assistant":
                item["role"] = "CHATBOT"
            if "content" in item:
                item["message"] = item.pop("content")
        mes = history.pop()["message"]
        ans = ""
        total_tokens = 0
        try:
            response = self.client.chat_stream(model=self.model_name, chat_history=history, message=mes, **gen_conf)
            for resp in response:
                if resp.event_type == "text-generation":
                    ans = resp.text
                    total_tokens += num_tokens_from_string(resp.text)
                elif resp.event_type == "stream-end":
                    if resp.finish_reason == "MAX_TOKENS":
                        ans += "...\nFor the content length reason, it stopped, continue?" if is_english([ans]) else "······\n由于长度的原因，回答被截断了，要继续吗？"
                yield ans

        except Exception as e:
            yield ans + "\n**ERROR**: " + str(e)

        yield total_tokens


class LeptonAIChat(Base):
    def __init__(self, key, model_name, base_url=None):
        if not base_url:
            base_url = os.path.join("https://" + model_name + ".lepton.run", "api", "v1")
        super().__init__(key, model_name, base_url)


class TogetherAIChat(Base):
    def __init__(self, key, model_name, base_url="https://api.together.xyz/v1"):
        if not base_url:
            base_url = "https://api.together.xyz/v1"
        super().__init__(key, model_name, base_url)


class PerfXCloudChat(Base):
    def __init__(self, key, model_name, base_url="https://cloud.perfxlab.cn/v1"):
        if not base_url:
            base_url = "https://cloud.perfxlab.cn/v1"
        super().__init__(key, model_name, base_url)


class UpstageChat(Base):
    def __init__(self, key, model_name, base_url="https://api.upstage.ai/v1/solar"):
        if not base_url:
            base_url = "https://api.upstage.ai/v1/solar"
        super().__init__(key, model_name, base_url)


class NovitaAIChat(Base):
    def __init__(self, key, model_name, base_url="https://api.novita.ai/v3/openai"):
        if not base_url:
            base_url = "https://api.novita.ai/v3/openai"
        super().__init__(key, model_name, base_url)


class SILICONFLOWChat(Base):
    def __init__(self, key, model_name, base_url="https://api.siliconflow.cn/v1"):
        if not base_url:
            base_url = "https://api.siliconflow.cn/v1"
        super().__init__(key, model_name, base_url)


class YiChat(Base):
    def __init__(self, key, model_name, base_url="https://api.lingyiwanwu.com/v1"):
        if not base_url:
            base_url = "https://api.lingyiwanwu.com/v1"
        super().__init__(key, model_name, base_url)


class ReplicateChat(Base):
    def __init__(self, key, model_name, base_url=None):
        super().__init__(key, model_name, base_url=None)

        from replicate.client import Client

        self.model_name = model_name
        self.client = Client(api_token=key)
        self.system = ""

    def chat(self, system, history, gen_conf):
        if "max_tokens" in gen_conf:
            del gen_conf["max_tokens"]
        if system:
            self.system = system
        prompt = "\n".join([item["role"] + ":" + item["content"] for item in history[-5:]])
        ans = ""
        try:
            response = self.client.run(
                self.model_name,
                input={"system_prompt": self.system, "prompt": prompt, **gen_conf},
            )
            ans = "".join(response)
            return ans, num_tokens_from_string(ans)
        except Exception as e:
            return ans + "\n**ERROR**: " + str(e), 0

    def chat_streamly(self, system, history, gen_conf):
        if "max_tokens" in gen_conf:
            del gen_conf["max_tokens"]
        if system:
            self.system = system
        prompt = "\n".join([item["role"] + ":" + item["content"] for item in history[-5:]])
        ans = ""
        try:
            response = self.client.run(
                self.model_name,
                input={"system_prompt": self.system, "prompt": prompt, **gen_conf},
            )
            for resp in response:
                ans = resp
                yield ans

        except Exception as e:
            yield ans + "\n**ERROR**: " + str(e)

        yield num_tokens_from_string(ans)


class HunyuanChat(Base):
    def __init__(self, key, model_name, base_url=None):
        super().__init__(key, model_name, base_url=None)

        from tencentcloud.common import credential
        from tencentcloud.hunyuan.v20230901 import hunyuan_client

        key = json.loads(key)
        sid = key.get("hunyuan_sid", "")
        sk = key.get("hunyuan_sk", "")
        cred = credential.Credential(sid, sk)
        self.model_name = model_name
        self.client = hunyuan_client.HunyuanClient(cred, "")

    def chat(self, system, history, gen_conf):
        from tencentcloud.common.exception.tencent_cloud_sdk_exception import (
            TencentCloudSDKException,
        )
        from tencentcloud.hunyuan.v20230901 import models

        _gen_conf = {}
        _history = [{k.capitalize(): v for k, v in item.items()} for item in history]
        if system:
            _history.insert(0, {"Role": "system", "Content": system})
        if "max_tokens" in gen_conf:
            del gen_conf["max_tokens"]
        if "temperature" in gen_conf:
            _gen_conf["Temperature"] = gen_conf["temperature"]
        if "top_p" in gen_conf:
            _gen_conf["TopP"] = gen_conf["top_p"]

        req = models.ChatCompletionsRequest()
        params = {"Model": self.model_name, "Messages": _history, **_gen_conf}
        req.from_json_string(json.dumps(params))
        ans = ""
        try:
            response = self.client.ChatCompletions(req)
            ans = response.Choices[0].Message.Content
            return ans, response.Usage.TotalTokens
        except TencentCloudSDKException as e:
            return ans + "\n**ERROR**: " + str(e), 0

    def chat_streamly(self, system, history, gen_conf):
        from tencentcloud.common.exception.tencent_cloud_sdk_exception import (
            TencentCloudSDKException,
        )
        from tencentcloud.hunyuan.v20230901 import models

        _gen_conf = {}
        _history = [{k.capitalize(): v for k, v in item.items()} for item in history]
        if system:
            _history.insert(0, {"Role": "system", "Content": system})
        if "max_tokens" in gen_conf:
            del gen_conf["max_tokens"]
        if "temperature" in gen_conf:
            _gen_conf["Temperature"] = gen_conf["temperature"]
        if "top_p" in gen_conf:
            _gen_conf["TopP"] = gen_conf["top_p"]
        req = models.ChatCompletionsRequest()
        params = {
            "Model": self.model_name,
            "Messages": _history,
            "Stream": True,
            **_gen_conf,
        }
        req.from_json_string(json.dumps(params))
        ans = ""
        total_tokens = 0
        try:
            response = self.client.ChatCompletions(req)
            for resp in response:
                resp = json.loads(resp["data"])
                if not resp["Choices"] or not resp["Choices"][0]["Delta"]["Content"]:
                    continue
                ans = resp["Choices"][0]["Delta"]["Content"]
                total_tokens += 1

                yield ans

        except TencentCloudSDKException as e:
            yield ans + "\n**ERROR**: " + str(e)

        yield total_tokens


class SparkChat(Base):
    def __init__(self, key, model_name, base_url="https://spark-api-open.xf-yun.com/v1"):
        if not base_url:
            base_url = "https://spark-api-open.xf-yun.com/v1"
        model2version = {
            "Spark-Max": "generalv3.5",
            "Spark-Lite": "general",
            "Spark-Pro": "generalv3",
            "Spark-Pro-128K": "pro-128k",
            "Spark-4.0-Ultra": "4.0Ultra",
        }
        version2model = {v: k for k, v in model2version.items()}
        assert model_name in model2version or model_name in version2model, f"The given model name is not supported yet. Support: {list(model2version.keys())}"
        if model_name in model2version:
            model_version = model2version[model_name]
        else:
            model_version = model_name
        super().__init__(key, model_version, base_url)


class BaiduYiyanChat(Base):
    def __init__(self, key, model_name, base_url=None):
        super().__init__(key, model_name, base_url=None)

        import qianfan

        key = json.loads(key)
        ak = key.get("yiyan_ak", "")
        sk = key.get("yiyan_sk", "")
        self.client = qianfan.ChatCompletion(ak=ak, sk=sk)
        self.model_name = model_name.lower()
        self.system = ""

    def chat(self, system, history, gen_conf):
        if system:
            self.system = system
        gen_conf["penalty_score"] = ((gen_conf.get("presence_penalty", 0) + gen_conf.get("frequency_penalty", 0)) / 2) + 1
        if "max_tokens" in gen_conf:
            del gen_conf["max_tokens"]
        ans = ""

        try:
            response = self.client.do(model=self.model_name, messages=history, system=self.system, **gen_conf).body
            ans = response["result"]
            return ans, self.total_token_count(response)

        except Exception as e:
            return ans + "\n**ERROR**: " + str(e), 0

    def chat_streamly(self, system, history, gen_conf):
        if system:
            self.system = system
        gen_conf["penalty_score"] = ((gen_conf.get("presence_penalty", 0) + gen_conf.get("frequency_penalty", 0)) / 2) + 1
        if "max_tokens" in gen_conf:
            del gen_conf["max_tokens"]
        ans = ""
        total_tokens = 0

        try:
            response = self.client.do(model=self.model_name, messages=history, system=self.system, stream=True, **gen_conf)
            for resp in response:
                resp = resp.body
                ans = resp["result"]
                total_tokens = self.total_token_count(resp)

                yield ans

        except Exception as e:
            return ans + "\n**ERROR**: " + str(e), 0

        yield total_tokens


class AnthropicChat(Base):
    def __init__(self, key, model_name, base_url=None):
        super().__init__(key, model_name, base_url=None)

        import anthropic

        self.client = anthropic.Anthropic(api_key=key)
        self.model_name = model_name
        self.system = ""

    def chat(self, system, history, gen_conf):
        if system:
            self.system = system
        if "presence_penalty" in gen_conf:
            del gen_conf["presence_penalty"]
        if "frequency_penalty" in gen_conf:
            del gen_conf["frequency_penalty"]
        gen_conf["max_tokens"] = 8192
        if "haiku" in self.model_name or "opus" in self.model_name:
            gen_conf["max_tokens"] = 4096

        ans = ""
        try:
            response = self.client.messages.create(
                model=self.model_name,
                messages=history,
                system=self.system,
                stream=False,
                **gen_conf,
            ).to_dict()
            ans = response["content"][0]["text"]
            if response["stop_reason"] == "max_tokens":
                ans += "...\nFor the content length reason, it stopped, continue?" if is_english([ans]) else "······\n由于长度的原因，回答被截断了，要继续吗？"
            return (
                ans,
                response["usage"]["input_tokens"] + response["usage"]["output_tokens"],
            )
        except Exception as e:
            return ans + "\n**ERROR**: " + str(e), 0

    def chat_streamly(self, system, history, gen_conf):
        if system:
            self.system = system
        if "presence_penalty" in gen_conf:
            del gen_conf["presence_penalty"]
        if "frequency_penalty" in gen_conf:
            del gen_conf["frequency_penalty"]
        gen_conf["max_tokens"] = 8192
        if "haiku" in self.model_name or "opus" in self.model_name:
            gen_conf["max_tokens"] = 4096

        ans = ""
        total_tokens = 0
        reasoning_start = False
        try:
            response = self.client.messages.create(
                model=self.model_name,
                messages=history,
                system=system,
                stream=True,
                **gen_conf,
            )
            for res in response:
                if res.type == "content_block_delta":
                    if res.delta.type == "thinking_delta" and res.delta.thinking:
                        ans = ""
                        if not reasoning_start:
                            reasoning_start = True
                            ans = "<think>"
                        ans += res.delta.thinking + "</think>"
                    else:
                        reasoning_start = False
                        text = res.delta.text
                        ans = text
                        total_tokens += num_tokens_from_string(text)
                    yield ans
        except Exception as e:
            yield ans + "\n**ERROR**: " + str(e)

        yield total_tokens


class GoogleChat(Base):
    def __init__(self, key, model_name, base_url=None):
        super().__init__(key, model_name, base_url=None)

        import base64

        from google.oauth2 import service_account

        key = json.loads(key)
        access_token = json.loads(base64.b64decode(key.get("google_service_account_key", "")))
        project_id = key.get("google_project_id", "")
        region = key.get("google_region", "")

        scopes = ["https://www.googleapis.com/auth/cloud-platform"]
        self.model_name = model_name
        self.system = ""

        if "claude" in self.model_name:
            from anthropic import AnthropicVertex
            from google.auth.transport.requests import Request

            if access_token:
                credits = service_account.Credentials.from_service_account_info(access_token, scopes=scopes)
                request = Request()
                credits.refresh(request)
                token = credits.token
                self.client = AnthropicVertex(region=region, project_id=project_id, access_token=token)
            else:
                self.client = AnthropicVertex(region=region, project_id=project_id)
        else:
            import vertexai.generative_models as glm
            from google.cloud import aiplatform

            if access_token:
                credits = service_account.Credentials.from_service_account_info(access_token)
                aiplatform.init(credentials=credits, project=project_id, location=region)
            else:
                aiplatform.init(project=project_id, location=region)
            self.client = glm.GenerativeModel(model_name=self.model_name)

    def chat(self, system, history, gen_conf):
        if system:
            self.system = system

        if "claude" in self.model_name:
            if "max_tokens" in gen_conf:
                del gen_conf["max_tokens"]
            try:
                response = self.client.messages.create(
                    model=self.model_name,
                    messages=history,
                    system=self.system,
                    stream=False,
                    **gen_conf,
                ).json()
                ans = response["content"][0]["text"]
                if response["stop_reason"] == "max_tokens":
                    ans += "...\nFor the content length reason, it stopped, continue?" if is_english([ans]) else "······\n由于长度的原因，回答被截断了，要继续吗？"
                return (
                    ans,
                    response["usage"]["input_tokens"] + response["usage"]["output_tokens"],
                )
            except Exception as e:
                return "\n**ERROR**: " + str(e), 0
        else:
            self.client._system_instruction = self.system
            if "max_tokens" in gen_conf:
                gen_conf["max_output_tokens"] = gen_conf["max_tokens"]
            for k in list(gen_conf.keys()):
                if k not in ["temperature", "top_p", "max_output_tokens"]:
                    del gen_conf[k]
            for item in history:
                if "role" in item and item["role"] == "assistant":
                    item["role"] = "model"
                if "content" in item:
                    item["parts"] = item.pop("content")
            try:
                response = self.client.generate_content(history, generation_config=gen_conf)
                ans = response.text
                return ans, response.usage_metadata.total_token_count
            except Exception as e:
                return "**ERROR**: " + str(e), 0

    def chat_streamly(self, system, history, gen_conf):
        if system:
            self.system = system

        if "claude" in self.model_name:
            if "max_tokens" in gen_conf:
                del gen_conf["max_tokens"]
            ans = ""
            total_tokens = 0
            try:
                response = self.client.messages.create(
                    model=self.model_name,
                    messages=history,
                    system=self.system,
                    stream=True,
                    **gen_conf,
                )
                for res in response.iter_lines():
                    res = res.decode("utf-8")
                    if "content_block_delta" in res and "data" in res:
                        text = json.loads(res[6:])["delta"]["text"]
                        ans = text
                        total_tokens += num_tokens_from_string(text)
            except Exception as e:
                yield ans + "\n**ERROR**: " + str(e)

            yield total_tokens
        else:
            self.client._system_instruction = self.system
            if "max_tokens" in gen_conf:
                gen_conf["max_output_tokens"] = gen_conf["max_tokens"]
            for k in list(gen_conf.keys()):
                if k not in ["temperature", "top_p", "max_output_tokens"]:
                    del gen_conf[k]
            for item in history:
                if "role" in item and item["role"] == "assistant":
                    item["role"] = "model"
                if "content" in item:
                    item["parts"] = item.pop("content")
            ans = ""
            try:
                response = self.model.generate_content(history, generation_config=gen_conf, stream=True)
                for resp in response:
                    ans = resp.text
                    yield ans

            except Exception as e:
                yield ans + "\n**ERROR**: " + str(e)

            yield response._chunks[-1].usage_metadata.total_token_count


class GPUStackChat(Base):
    def __init__(self, key=None, model_name="", base_url=""):
        if not base_url:
            raise ValueError("Local llm url cannot be None")
        if base_url.split("/")[-1] != "v1":
            base_url = os.path.join(base_url, "v1")
        super().__init__(key, model_name, base_url)
