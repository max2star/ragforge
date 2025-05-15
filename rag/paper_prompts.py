import logging
DEFAULT_KEYS_TO_EXTRACT= {
        #"paper":"标题、系列信息、作者",
        "paper":"标题、摘要、关键词、系列信息、作者、其他作者、责任单位、其他责任单位、内容简介、前言、序言、总序、分类、其他分类、DOI、ISBN、ISSN、出版机构、收录机构、出版时间"
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

def paper_classification_prompt(content, key_to_extract=DEFAULT_KEYS_TO_EXTRACT['paper']):
    prompt_1 = """
角色: 你是核领域的专家，请帮助对文献资料进行分析。
任务: 你的任务是对输入的文本内容进行分类。请严格按以下步骤判定文本内容的文档类别（仅需输出分类编号和名称）。
第一步：主类特征匹配
根据文本内容选择所有匹配的主类（1-27类可多选），判定优先级如下：

[01] 核物理学

涉及原子核结构/衰变、核反应（裂变/聚变）、中子动力学、射线与物质相互作用等基础理论研究

[02] 放射化学/核化学

包含放射性元素提纯、核反应化学过程（裂变/聚变产物分析）、辐射化学效应等

[03] 核武器

描述核弹类型（氢弹/原子弹）、杀伤因素（冲击波/核辐射）、试验方式（地下核试验）或防扩散技术

[04] 核军控与核材料管控

涉及核裁军条约（NPT/CTBT）、核材料衡算、封隔监视技术或实物保护措施

[05] 核材料生产

包含铀/钍提取、重水生产、氚增殖工艺、锂同位素分离等核材料制备技术

[06] 铀矿地质

关于铀矿床形成机制、地质勘探方法、铀资源评估等地质学研究

[07] 铀矿冶

涉及铀矿石开采、选矿工艺、水冶加工技术或铀矿环境保护

[08] 铀转化

描述铀纯化、金属铀制备、UF6转化或堆后铀处理工艺

[09] 钍循环

包含钍基燃料制备、钍铀混合燃料循环系统设计

[10] 富集铀生产

涉及气体离心法、激光分离法、级联系统设计或铀同位素工厂运营

[11] 燃料组件制造

关于燃料包壳材料（锆合金/MOX燃料）、组件性能测试或制造工艺

[12] 乏燃料处理

包含水法/干法后处理、钚回收工艺或裂变产物管理

[13] 反应堆基础理论

涉及中子输运方程、热工水力分析、临界安全计算等理论建模

[14] 研究试验堆

描述零功率堆、高通量堆等实验堆设计与运行

[15] 生产堆

专门用于钚/氚生产的反应堆系统（石墨堆/重水堆）

[16] 动力堆系统

包含压水堆/快堆/高温气冷堆等能源装置的设计与优化

[17] 核动力装置

涉及核电厂/舰艇动力系统、冷却回路（一/二回路）或蒸汽发生器参数

[18] 受控核聚变

描述托卡马克装置、等离子体约束、聚变堆工程等

[19] 核安全

包含安全分析报告、许可证制度、设计基准事故或纵深防御措施

[20] 核应急

关于辐射事故应急预案、应急响应流程或处置技术

[21] 核安保

涉及核设施反恐措施、核材料追踪或非法贩运预防

[22] 核探测技术

包含半导体探测器、核电子学仪器或辐射剂量测量设备

[23] 辐射防护

描述屏蔽设计标准、放射性流出物监测或生物效应评估

[24] 放射性废物管理

涉及玻璃固化工艺、地质处置库选址或α废物处理

[25] 核设施退役

包含退役去污技术、终态验收标准或反应堆拆除工艺

[26] 同位素应用

关于加速器产同位素、放射源制备或医疗/工业示踪技术

[27] 粒子加速器

涉及回旋加速器设计、束流诊断系统或超导磁体技术

第二步：交叉关联校验
当文本同时涉及时，必须同时选择：

核材料+武器设计 → 必须同时选择[03]和[04]

反应堆运行+废物处理 → 同时选择[16]和[24]

同位素生产+医疗应用 → 同时选择[26]和[22]

请将文本分类编号和名称，按照JSON形式格式化输出：
    EXAMPLE JSON OUTPUT:
    {
        "03": "核材料",
        "22": "医疗应用",
    }

    """
    prompt_2 = f"""
### 文本内容
{content}
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
