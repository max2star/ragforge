import logging
DEFAULT_KEYS_TO_EXTRACT= {
        #"paper":"标题、系列信息、作者",
        "paper":"标题、系列信息、作者、其他作者、责任单位、其他责任单位、摘要、内容简介、前言、序言、总序、分类、其他分类、DOI、ISBN、ISSN、出版机构、收录机构、出版时间"
}

def paper_extraction_prompt(content, key_to_extract=DEFAULT_KEYS_TO_EXTRACT['paper']):
    prompt_1 = """
Role: You're a text analyzer.
Task: Your task is to extract keyvalue information from the input text content. Don't make it up, get the text directly, pay attention to the restrictions, and don't return only part of the content. Extract the keyvalue information from the text content.
Requirements:
  - The key is in Chinese, and the value is output in the language of the original text.  
  - Don't perform summarization and other operations.
  - Don't get information other than the key. Some keys have no value, so just set the value to an empty character. 
  - Please output the keyvalues in JSON format as the following schema:
    EXAMPLE JSON OUTPUT:
    {
        "标题": "How to improve the performance of OCR",
        "作者": "Jetson",
    }
    """
    prompt_2 = f"""
### Text Content
{content}
### The Key to Extract
{key_to_extract}
"""
    prompt = prompt_1 + prompt_2
    logging.info("prompt is {}".format(prompt))
#prompt = f"""
#角色: 你是大师级的文本分析专家，专业、严谨、精确。
#任务描述: 你的任务是从输入文本内容中提取的keyvalue信息，不要编造，直接获取文本，注意完整性，不要仅返回部分内容。抽取的文本内容中的keyvalue信息，key使用中文，value以原始文本的语言输出，不要进行总结摘要等操作。不要获取key之外的信息，如果某些key没有value，value设置为空字符即可。
#
#### 文本内容 
#{content}
#
#### 要抽取的key
#{key}
#"""
#The output should be a Markdown code snippet formatted in the following schema, including the leading and trailing "```json" and "```":
#```json
#{
#\"Key1\": Value
#\"Key2\": Value
#}
#```".format(content,key)
    return prompt
    #msg = [{"role": "system", "content": prompt}, {"role": "user", "content": "Output: "}]
    #kwd = chat_mdl.chat(prompt, msg, {"temperature": 0.2})
    #kwd = re.sub(r"<think>.*</think>", "", kwd, flags=re.DOTALL)
    #if kwd.find("**ERROR**") >= 0:
    #    return ""
    #return kwd
