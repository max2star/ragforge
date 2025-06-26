import json
import random
import sys

import random
import textwrap
import sys

import json
import random
import textwrap
import sys

def generate_readable_chinese_text(length):
    """生成指定长度的可读中文文本"""
    # 经典中文文本片段库
    classical_texts = [
        "子曰：学而时习之，不亦说乎？有朋自远方来，不亦乐乎？人不知而不愠，不亦君子乎？",
        "大学之道，在明明德，在亲民，在止于至善。知止而后有定，定而后能静，静而后能安，安而后能虑，虑而后能得。",
        "道可道，非常道；名可名，非常名。无名天地之始，有名万物之母。故常无欲，以观其妙；常有欲，以观其徼。",
        "北冥有鱼，其名为鲲。鲲之大，不知其几千里也；化而为鸟，其名为鹏。鹏之背，不知其几千里也；怒而飞，其翼若垂天之云。",
        "关关雎鸠，在河之洲。窈窕淑女，君子好逑。参差荇菜，左右流之。窈窕淑女，寤寐求之。",
        "天地玄黄，宇宙洪荒。日月盈昃，辰宿列张。寒来暑往，秋收冬藏。闰余成岁，律吕调阳。",
        "古之欲明明德于天下者，先治其国；欲治其国者，先齐其家；欲齐其家者，先修其身；欲修其身者，先正其心；",
        "昔孟母，择邻处。子不学，断机杼。窦燕山，有义方。教五子，名俱扬。养不教，父之过。教不严，师之惰。",
        "人之初，性本善。性相近，习相远。苟不教，性乃迁。教之道，贵以专。",
        "君子曰：学不可以已。青，取之于蓝，而青于蓝；冰，水为之，而寒于水。",
        "夫君子之行，静以修身，俭以养德。非淡泊无以明志，非宁静无以致远。",
        "先天下之忧而忧，后天下之乐而乐。噫！微斯人，吾谁与归？"
    ]
    
    # 常用连接词和过渡句
    transitions = [
        "由此观之，", "故而，", "然而，", "况且，", "因此，", "换言之，", "譬如，", "诚然，", 
        "综上所述，", "反观之，", "再者，", "不可否认，", "值得注意的是，", "另一方面，"
    ]
    
    text = []
    char_count = 0
    
    # 添加标题
    title = "中华文化经典文选\n\n"
    text.append(title)
    char_count += len(title)
    
    # 生成可读文本
    section_count = 0
    while char_count < length:
        # 添加章节标题
        if section_count > 0 and char_count % 2000 == 0:
            section_title = f"\n\n卷{section_count+1}：文化精粹\n\n"
            text.append(section_title)
            char_count += len(section_title)
        
        # 随机选择文本片段
        segment = random.choice(classical_texts)
        
        # 随机添加过渡词
        if random.random() > 0.7 and text and not text[-1].endswith('\n'):
            transition = random.choice(transitions)
            segment = transition + segment
        
        # 添加段落
        text.append(segment)
        char_count += len(segment)
        
        # 添加段落分隔
        if random.random() > 0.3:
            text.append(" ")
            char_count += 1
        
        # 每段后添加换行
        if random.random() > 0.6 and char_count < length - 2:
            text.append("\n\n")
            char_count += 2
        
        section_count += 1
    
    # 添加结束语
    ending = "\n\n—— 摘自中华文化经典著作汇编"
    if char_count + len(ending) <= length:
        text.append(ending)
        char_count += len(ending)
    
    # 确保精确长度
    result = ''.join(text)
    if len(result) > length:
        result = result[:length]
    elif len(result) < length:
        # 补充随机汉字
        supplement = ''.join(random.choice("天地玄黄宇宙洪荒日月盈昃辰宿列张寒来暑往秋收冬藏") 
                             for _ in range(length - len(result)))
        result += supplement
    
    return result

def create_json_with_chinese_content(model_name="DeepSeek-R1-Distill-Llama-70B",filename='deepseek_70b_llm.json',text_length=32768):
    """创建包含中文内容的 JSON 文件"""
    # 生成 32768 字符的中文文本
    chinese_text = generate_readable_chinese_text(text_length)
    
    # 验证长度
    actual_length = len(chinese_text)
    print(f"生成文本长度: {actual_length} 字符")
    
    # 构建 JSON 结构
    if model_name == "DeepSeek-R1-Distill-Llama-70B":
        json_data = {
            "model": str(model_name),
            "messages": [{
             "role": "system",
             "content": "You are a helpful assistant."
            },
            {
             "role": "user",
             "content": "请翻译以下内容为英文："+chinese_text
            }],
            #TODO
            #"max_tokens": 1000,
            "presence_penalty": 1.03,
            "frequency_penalty": 1.0,
            "seed": None,
            "temperature": 0.5,
            "top_p": 0.95,
            "stream":False 
        }
    if model_name == "DeepSeek-R1-Distill-Qwen-32B":
        json_data = {
            "model": str(model_name),
            "messages": [
                {"role": "system", "content": "你是一个翻译"},
                {"role": "user", "content": "请翻译以下内容为英文："+chinese_text}
            ],
            "stream": False,
            #"max_tokens": 1024,
            "presence_penalty": 1.03,
            "frequency_penalty": 1.0,
            "repetition_penalty": 1.0,
            "temperature": 0.5,
            "top_p": 0.95,
            "top_k": 10,
            "seed": None,
            "stop": ["stop1", "stop2"],
            "include_stop_str_in_output": False,
            "skip_special_tokens": True,
            "ignore_eos": False
        }
    # 输出到 JSON 文件（UTF-8 编码）
    with open(filename, "w", encoding="utf-8") as f:
        # 注意：ensure_ascii=False 确保中文字符不被转义
        # indent=2 使输出更可读（可选）
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    print(f"已创建 JSON 文件: {filename}")
    print("文件内容预览（前200字符）:")
    print(chinese_text[:200] + "...")
    
    # 验证 JSON 文件
    try:
        with open(filename, "r", encoding="utf-8") as f:
            loaded_data = json.load(f)
            print("\nJSON 文件验证成功！")
    except Exception as e:
        print(f"JSON 文件验证失败: {e}")

if __name__ == "__main__":
    create_json_with_chinese_content(model_name="DeepSeek-R1-Distill-Llama-70B",filename='deepseek_70b_llm.json',text_length=16380)
    create_json_with_chinese_content(model_name="DeepSeek-R1-Distill-Qwen-32B",filename='deepseek_32b_llm.json',text_length=16380)
