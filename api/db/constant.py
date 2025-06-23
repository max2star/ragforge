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
general=[
  {
    "id": 1,
    "name": "标题",
    "code": "title",
    "description": "标题",
    "must_exist": True
  },
  {
    "id": 2,
    "name": "系列信息",
    "code": "",
    "description": "系列信息",
    "must_exist": True
  },
  {
    "id": 3,
    "name": "作者",
    "code": "authors",
    "description": "作者",
    "must_exist": True
  },
  {
    "id": 4,
    "name": "其他作者",
    "code": "other_authors",
    "description": "其他作者",
    "must_exist": False
  },
  {
    "id": 5,
    "name": "责任单位",
    "code": "",
    "description": "",
    "must_exist": False
  },
  {
    "id": 6,
    "name": "其他责任单位",
    "code": "",
    "description": "",
    "must_exist": False
  },
  {
    "id": 7,
    "name": "摘要",
    "code": "",
    "description": "",
    "must_exist": True
  },
  {
    "id": 8,
    "name": "关键词",
    "code": "keywords",
    "description": "描述信息内容的关键词",
    "must_exist": True
  },
  {
    "id": 9,
    "name": "分类",
    "code": "",
    "description": "",
    "must_exist": False
  },
  {
    "id": 10,
    "name": "其他分类",
    "code": "",
    "description": "",
    "must_exist": False
  },
  {
    "id": 11,
    "name": "ISBN",
    "code": "ISBN",
    "description": "",
    "must_exist": False
  },
  {
    "id": 12,
    "name": "出版机构",
    "code": "",
    "description": "",
    "must_exist": False
  },
  # {
  #   "id": 13,
  #   "name": "出版时间",
  #   "code": "",
  #   "description": "",
  #   "must_exist": False
  # },
]
journal=[
  {
    "id": 1,
    "name": "唯一标识",
    "code": "identifier",
    "description": "期刊的唯一标识",
    "must_exist": True
  },
  {
    "id": 2,
    "name": "期刊名称",
    "code": "title",
    "description": "期刊名",
    "must_exist": True
  },
  {
    "id": 3,
    "name": "其他题名",
    "code": "alternative",
    "description": "其他期刊名",
    "must_exist": False
  },
  {
    "id": 4,
    "name": "语种",
    "code": "language",
    "description": "正文语种",
    "must_exist": True
  },
  {
    "id": 5,
    "name": "其他语种",
    "code": "language_alternative",
    "description": "其他语种",
    "must_exist": False
  },
  {
    "id": 6,
    "name": "主题",
    "code": "subject",
    "description": "描述信息内容的5～8个关键词",
    "must_exist": False
  },
  {
    "id": 7,
    "name": "出版商",
    "code": "publisher",
    "description": "期刊出版单位",
    "must_exist": True
  },
  # {
  #   "id": 8,
  #   "name": "创刊日期",
  #   "code": "start_date",
  #   "description": "期刊创刊日期",
  #   "must_exist": True
  # },
  # {
  #   "id": 9,
  #   "name": "停刊日期",
  #   "code": "end_date",
  #   "description": "期刊停刊日期",
  #   "must_exist": False
  # },
  {
    "id": 10,
    "name": "简介",
    "code": "introduction",
    "description": "期刊的基本介绍",
    "must_exist": True
  },
  {
    "id": 11,
    "name": "分类",
    "code": "class",
    "description": "数聚平台的技术体系",
    "must_exist": False
  },
  {
    "id": 12,
    "name": "其他分类",
    "code": "class_alternative",
    "description": "其他分类体系",
    "must_exist": False
  },
  {
    "id": 13,
    "name": "责任单位",
    "code": "corporate",
    "description": "期刊的主办单位",
    "must_exist": False 
  },
  {
    "id": 14,
    "name": "ISSN",
    "code": "issn",
    "description": "连续出版物编号",
    "must_exist": False 
  },
  {
    "id": 15,
    "name": "其他代码",
    "code": "journal_code",
    "description": "其他期刊代码，如邮发号、coden等",
    "must_exist": False 
  },
  {
    "id": 16,
    "name": "收录机构",
    "code": "source_agency",
    "description": "收录该信息的机构",
    "must_exist": False 
  }
]
# 图书元数据
Book = [
  # {
  #   "id": 1,
  #   "name": "唯一标识",
  #   "code": "identifier",
  #   "description": "图书唯一标识",
  #   "must_exist": True,
  #   "外键": ""
  # },
  {
    "id": 2,
    "name": "题名",
    "code": "title",
    "description": "图书版权页的图书名称",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 3,
    "name": "其他题名",
    "code": "alternative",
    "description": "其他题名",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 4,
    "name": "系列信息",
    "code": "series_info",
    "description": "系列名称+系列号",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 5,
    "name": "语种",
    "code": "language",
    "description": "正文语种",
    "must_exist": True,
    "外键": "语种代码表 三位代码"
  },
  # {
  #   "id": 6,
  #   "name": "其他语种",
  #   "code": "language_alternative",
  #   "description": "图书其他语种",
  #   "must_exist": False,
  #   "外键": "语种代码表 三位代码"
  # },
  {
    "id": 7,
    "name": "作者",
    "code": "author",
    "description": "作者名",
    "must_exist": False,
    "外键": "作者表 identify"
  },
  {
    "id": 8,
    "name": "其他作者",
    "code": "author_alternative",
    "description": "其他作者名",
    "must_exist": False,
    "外键": "作者表 identify"
  },
  {
    "id": 9,
    "name": "责任单位",
    "code": "corporate",
    "description": "团体作者名",
    "must_exist": False,
    "外键": "机构表 identify"
  },
  {
    "id": 10,
    "name": "其他责任单位",
    "code": "corporate_alternative",
    "description": "其他团体作者名",
    "must_exist": False,
    "外键": "机构表 identify"
  },
  # {
  #   "id": 11,
  #   "name": "发布日期",
  #   "code": "issue_date",
  #   "description": "图书出版日期",
  #   "must_exist": False,
  #   "外键": ""
  # },
  {
    "id": 12,
    "name": "主题",
    "code": "subject",
    "description": "描述信息内容的5~8个关键词",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 13,
    "name": "摘要",
    "code": "abstract",
    "description": "描述图书内容的信息",
    "must_exist": False,
    "外键": ""
  },
  # {
  #   "id": 14,
  #   "name": "分类",
  #   "code": "class",
  #   "description": "数聚平台技术分类",
  #   "must_exist": False,
  #   "外键": ""
  # },
  # {
  #   "id": 15,
  #   "name": "其他分类",
  #   "code": "class_alternative",
  #   "description": "其他分类方法",
  #   "must_exist": False,
  #   "外键": ""
  # },
  # {
  #   "id": 16,
  #   "name": "doi",
  #   "code": "doi",
  #   "description": "数字对象唯一标识符",
  #   "must_exist": False,
  #   "外键": ""
  # },
  {
    "id": 17,
    "name": "ISBN",
    "code": "isbn",
    "description": "10位或13位国际统一书号",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 18,
    "name": "ISSN",
    "code": "issn",
    "description": "连续出版物编号",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 19,
    "name": "版次",
    "code": "version_number",
    "description": "图书出版的版次说明",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 20,
    "name": "出版者",
    "code": "publisher",
    "description": "出版机构",
    "must_exist": False,
    "外键": "机构表 identify"
  },
  {
    "id": 21,
    "name": "收录机构",
    "code": "source_agency",
    "description": "收录该信息的机构",
    "must_exist": False,
    "外键": "机构表 identify"
  },
  # {
  #   "id": 22,
  #   "name": "文献类型",
  #   "code": "literature_type",
  #   "description": "本条知识的文献类型",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 23,
  #   "name": "知识所有者",
  #   "code": "belong_to",
  #   "description": "本条知识的所有者",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 24,
  #   "name": "所属部所",
  #   "code": "of_department",
  #   "description": "知识所有者所属部所",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 25,
  #   "name": "附件",
  #   "code": "enclosure",
  #   "description": "本条知识的原文,/[path]/[filename]",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 26,
  #   "name": "密级",
  #   "code": "confidential",
  #   "description": "选择公开/内部/秘密/机密",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 27,
  #   "name": "知悉范围",
  #   "code": "scope_of_information",
  #   "description": "选择知悉范围,完全共享/选择知悉范围",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 28,
  #   "name": "知识提交者",
  #   "code": "submiter",
  #   "description": "本条知识的提交者",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 29,
  #   "name": "提交日期",
  #   "code": "submit_date",
  #   "description": "本条知识的提交时间",
  #   "must_exist": True,
  #   "外键": ""
  # }
]

# 期刊元数据
Journal = [
  # {
  #   "id": 1,
  #   "name": "唯一标识",
  #   "code": "identifier",
  #   "description": "期刊的唯一标识",
  #   "must_exist": True,
  #   "外键": ""
  # },
  {
    "id": 2,
    "name": "期刊名称",
    "code": "title",
    "description": "期刊名",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 3,
    "name": "其他题名",
    "code": "alternative",
    "description": "其他期刊名",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 4,
    "name": "语种",
    "code": "language",
    "description": "正文语种",
    "must_exist": True,
    "外键": "语种代码表 三位代码"
  },
  # {
  #   "id": 5,
  #   "name": "其他语种",
  #   "code": "language_alternative",
  #   "description": "其他语种",
  #   "must_exist": False,
  #   "外键": "语种代码表 三位代码"
  # },
  {
    "id": 6,
    "name": "主题",
    "code": "subject",
    "description": "描述信息内容的5~8个关键词",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 7,
    "name": "出版商",
    "code": "publisher",
    "description": "期刊出版单位",
    "must_exist": True,
    "外键": "机构表 identify"
  },
  # {
  #   "id": 8,
  #   "name": "创刊日期",
  #   "code": "start_date",
  #   "description": "期刊创刊日期",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 9,
  #   "name": "停刊日期",
  #   "code": "end_date",
  #   "description": "期刊停刊日期",
  #   "must_exist": False,
  #   "外键": ""
  # },
  {
    "id": 10,
    "name": "简介",
    "code": "introduction",
    "description": "期刊的基本介绍",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 11,
    "name": "分类",
    "code": "class",
    "description": "数聚平台的技术体系",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 12,
    "name": "其他分类",
    "code": "class_alternative",
    "description": "其他分类体系",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 13,
    "name": "责任单位",
    "code": "corporate",
    "description": "期刊的主办单位",
    "must_exist": True,
    "外键": "机构表 identify"
  },
  {
    "id": 14,
    "name": "ISSN",
    "code": "issn",
    "description": "连续出版物编号",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 15,
    "name": "其他代码",
    "code": "journal_code",
    "description": "其他期刊代码,如邮发号、coden等",
    "must_exist": False,
    "极键": ""
  },
  {
    "id": 16,
    "name": "收录机构",
    "code": "source_agency",
    "description": "收录该信息的机构",
    "must_exist": False,
    "外键": "机构表 identify"
  }
    ]

# 会议元数据
Conference = [
  # {
  #   "id": 1,
  #   "name": "唯一标识",
  #   "code": "identifier",
  #   "description": "会议的唯一标识",
  #   "must_exist": True,
  #   "外键": ""
  # },
  {
    "id": 2,
    "name": "会议名称",
    "code": "title",
    "description": "会议名",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 3,
    "name": "其他题名",
    "code": "alternative",
    "description": "其他会议名",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 4,
    "name": "会议缩写",
    "code": "acronym",
    "description": "会议缩写名",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 5,
    "name": "主办单位",
    "code": "corporate",
    "description": "会议主办机构",
    "must_exist": True,
    "外键": "机构表 identify"
  },
  {
    "id": 6,
    "name": "协办机构",
    "code": "sponsor",
    "description": "会议资助单位",
    "must_exist": False,
    "外键": "机构表 identify"
  },
  # {
  #   "id": 7,
  #   "name": "会议日期",
  #   "code": "start_end_date",
  #   "description": "会议起止日期,格式示例 20250410-20250415",
  #   "must_exist": True,
  #   "外键": ""
  # },
  {
    "id": 8,
    "name": "会议地点",
    "code": "address",
    "description": "会议地点,示例[中国,北京,丰台],[US,AZ,Tucson]",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 9,
    "name": "会议届次",
    "code": "conference_number",
    "description": "会议届次",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 10,
    "name": "主题",
    "code": "subject",
    "description": "描述信息内容的5~8个关键词",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 11,
    "name": "简介",
    "code": "introduction",
    "description": "会议的基本介绍",
    "must_exist": True,
    "外键": ""
  },
  # {
  #   "id": 12,
  #   "name": "分类",
  #   "code": "class",
  #   "description": "数聚平台的技术体系",
  #   "must_exist": False,
  #   "外键": ""
  # },
  # {
  #   "id": 13,
  #   "name": "其他分类",
  #   "code": "class_alternative",
  #   "description": "其他分类体系",
  #   "must_exist": False,
  #   "外键": ""
  # },
  {
    "id": 14,
    "name": "ISBN",
    "code": "ISBN",
    "description": "图书出版标准书号",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 15,
    "name": "出版者",
    "code": "publisher",
    "description": "出版机构",
    "must_exist": False,
    "外键": "机构表 identify"
  },
  {
    "id": 16,
    "name": "收录机构",
    "code": "source_agency",
    "description": "收录该信息的机构",
    "must_exist": False,
    "外键": "机构表 identify"
  }
]


# 期刊论文元数据
JournalPaper = [
  # {
  #   "id": 1,
  #   "name": "唯一标识",
  #   "code": "identifier",
  #   "description": "期刊论文的唯一标识",
  #   "must_exist": True,
  #   "外键": ""
  # },
  {
    "id": 2,
    "name": "题名",
    "code": "title",
    "description": "主篇名",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 3,
    "name": "其他题名",
    "code": "alternative",
    "description": "其他语种篇名",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 4,
    "name": "语种",
    "code": "language",
    "description": "正文语种",
    "must_exist": True,
    "外键": "语种代码表 三位代码"
  },
  # {
  #   "id": 5,
  #   "name": "其他语种",
  #   "code": "language_alternative",
  #   "description": "期刊论文其他语种",
  #   "must_exist": False,
  #   "外键": "语种代码表 三位代码"
  # },
  {
    "id": 6,
    "name": "作者",
    "code": "author",
    "description": "作者名",
    "must_exist": True,
    "外键": "作者表 identifier"
  },
  {
    "id": 7,
    "name": "其他作者",
    "code": "author_alternative",
    "description": "其他语种作者名",
    "must_exist": False,
    "外键": "作者表 identifier"
  },
  {
    "id": 8,
    "name": "作者单位",
    "code": "affiliate",
    "description": "作者供职单位名",
    "must_exist": True,
    "外键": "机构表 identify"
  },
  {
    "id": 9,
    "name": "其他作者单位",
    "code": "affiliate_alternative",
    "description": "作者供职单位的其他名",
    "must_exist": False,
    "外键": "机构表 identify"
  },
  # {
  #   "id": 10,
  #   "name": "doi",
  #   "code": "doi",
  #   "description": "数字对象唯一标识符",
  #   "must_exist": False,
  #   "外键": ""
  # },
  {
    "id": 11,
    "name": "主题",
    "code": "subject",
    "description": "描述信息内容的5~8个关键词",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 12,
    "name": "摘要",
    "code": "abstract",
    "description": "描述图书内容的信息",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 13,
    "name": "分类",
    "code": "class",
    "description": "数聚平台的技术体系",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 14,
    "name": "其他分类",
    "code": "class_alternative",
    "description": "其他分类体系",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 15,
    "name": "刊名",
    "code": "journal_name",
    "description": "期刊名称",
    "must_exist": True,
    "外键": "期刊表 identifier"
  },
  {
    "id": 16,
    "name": "责任单位",
    "code": "corporate",
    "description": "期刊的主办单位",
    "must_exist": True,
    "外键": "机构表 identify"
  },
  {
    "id": 17,
    "name": "年",
    "code": "year",
    "description": "期刊出版年",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 18,
    "name": "卷",
    "code": "volume",
    "description": "期刊卷次",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 19,
    "name": "期",
    "code": "issue",
    "description": "期刊期次",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 20,
    "name": "出版者",
    "code": "publisher",
    "description": "出版机构",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 21,
    "name": "ISSN",
    "code": "issn",
    "description": "连续出版物编号",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 22,
    "name": "会议名称",
    "code": "conference",
    "description": "会议名称",
    "must_exist": False,
    "外键": "会议表 identifier"
  },
  {
    "id": 23,
    "name": "发布单位",
    "code": "news_agent",
    "description": "新闻发布信息的单位",
    "must_exist": False,
    "外键": "机构表 identify"
  },
  # {
  #   "id": 24,
  #   "name": "发布日期",
  #   "code": "issue_date",
  #   "description": "新闻发布日期",
  #   "must_exist": False,
  #   "外键": ""
  # },
  {
    "id": 25,
    "name": "收录机构",
    "code": "source_agency",
    "description": "收录该信息的机构",
    "must_exist": False,
    "外键": "机构表 identify"
  },
  # {
  #   "id": 26,
  #   "name": "文献类型",
  #   "code": "literature_type",
  #   "description": "本条知识的文献类型",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 27,
  #   "name": "知识所有者",
  #   "code": "belong_to",
  #   "description": "本条知识的所有者",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 28,
  #   "name": "所属部所",
  #   "code": "of_department",
  #   "description": "知识所有者所属部所",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 29,
  #   "name": "附件",
  #   "code": "enclosure",
  #   "description": "本条知识的原文,/[path]/[filename]",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 30,
  #   "name": "密级",
  #   "code": "confidential",
  #   "description": "公开/内部/秘密/机密",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 31,
  #   "name": "知悉范围",
  #   "code": "scope_of_information",
  #   "description": "完全共享/选择知悉范围",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 32,
  #   "name": "知识提交者",
  #   "code": "submiter",
  #   "description": "本条知识的提交者",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 33,
  #   "name": "提交日期",
  #   "code": "submit_date",
  #   "description": "本条知识的提交日期",
  #   "must_exist": True,
  #   "外键": ""
  # }
]

# 会议论文元数据
ConferencePaper = [
  # {
  #   "id": 1,
  #   "name": "唯一标识",
  #   "code": "identifier",
  #   "description": "会议论文的唯一标识",
  #   "must_exist": True,
  #   "外键": ""
  # },
  {
    "id": 2,
    "name": "题名",
    "code": "title",
    "description": "会议论文名",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 3,
    "name": "其他题名",
    "code": "alternative",
    "description": "会议论文其他题名",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 4,
    "name": "作者",
    "code": "author",
    "description": "会议论文作者",
    "must_exist": True,
    "外键": "作者表 identify"
  },
  {
    "id": 5,
    "name": "其他作者",
    "code": "author_alternative",
    "description": "会议论文其他作者",
    "must_exist": False,
    "外键": "作者表 identify"
  },
  {
    "id": 6,
    "name": "作者单位",
    "code": "affiliate",
    "description": "作者所属的单位",
    "must_exist": True,
    "外键": "机构表 identify"
  },
  {
    "id": 7,
    "name": "其他作者单位",
    "code": "affiliate_alternative",
    "description": "其他作者所属的单位",
    "must_exist": True,
    "外键": "机构表 identify"
  },
  {
    "id": 8,
    "name": "语种",
    "code": "language",
    "description": "期刊论文语种",
    "must_exist": True,
    "外键": "语种代码表 三位代码"
  },
  {
    "id": 9,
    "name": "主题",
    "code": "subject",
    "description": "描述信息内容的5~8个关键词",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 10,
    "name": "摘要",
    "code": "abstract",
    "description": "描述图书内容的信息",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 11,
    "name": "分类",
    "code": "class",
    "description": "数聚平台的技术体系",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 12,
    "name": "其他分类",
    "code": "class_alternative",
    "description": "其他分类体系",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 13,
    "name": "会议名称",
    "code": "conference_name",
    "description": "",
    "must_exist": True,
    "外键": "会议表 identify"
  },
  {
    "id": 14,
    "name": "会议地点",
    "code": "conference_address",
    "description": "会议召开地点",
    "must_exist": True,
    "外键": ""
  },
  # {
  #   "id": 15,
  #   "name": "会议时间",
  #   "code": "conference_period",
  #   "description": "会议的开始时间和结束时间",
  #   "must_exist": True,
  #   "外键": ""
  # },
  {
    "id": 16,
    "name": "责任单位",
    "code": "corporate",
    "description": "会议主办单位",
    "must_exist": True,
    "外键": "机构表 identify"
  },
  {
    "id": 17,
    "name": "其他责任者",
    "code": "contributor",
    "description": "会议协办单位",
    "must_exist": False,
    "外键": "机构表 identify"
  },
  {
    "id": 18,
    "name": "出版者",
    "code": "publisher",
    "description": "会议资料的出版单位",
    "must_exist": True,
    "外键": "机构表 identify"
  },
  {
    "id": 19,
    "name": "ISBN",
    "code": "isbn",
    "description": "连续出版物编号",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 20,
    "name": "收录机构",
    "code": "source_agency",
    "description": "收录该信息的机构",
    "must_exist": False,
    "外键": "机构表 identify"
  },
  # {
  #   "id": 21,
  #   "name": "文献类型",
  #   "code": "literature_type",
  #   "description": "本条知识的文献类型",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 22,
  #   "name": "知识所有者",
  #   "code": "belong_to",
  #   "description": "本条知识的所有者",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 23,
  #   "name": "所属部所",
  #   "code": "of_department",
  #   "description": "知识所有者所属部所",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 24,
  #   "name": "附件",
  #   "code": "enclosure",
  #   "description": "本条知识的原文,/[path]/[filename]",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 25,
  #   "name": "密级",
  #   "code": "confidential",
  #   "description": "选择密级,公开/内部/秘密/机密",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 26,
  #   "name": "知悉范围",
  #   "code": "scope_of_information",
  #   "description": "完全共享/选择知悉范围",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 27,
  #   "name": "知识提交者",
  #   "code": "submiter",
  #   "description": "本条知识的提交者",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 28,
  #   "name": "提交日期",
  #   "code": "submit_date",
  #   "description": "本条知识的提交日期",
  #   "must_exist": True,
  #   "外键": ""
  # }
]

# 报告元数据
Report = [
  # {
  #   "id": 1,
  #   "name": "唯一标识",
  #   "code": "identifier",
  #   "description": "报告的唯一标识",
  #   "must_exist": True,
  #   "外键": ""
  # },
  {
    "id": 2,
    "name": "题名",
    "code": "title",
    "description": "报告题名",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 3,
    "name": "其他题名",
    "code": "alternative",
    "description": "报告其他题名",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 4,
    "name": "语种",
    "code": "language",
    "description": "正文语种",
    "must_exist": True,
    "外键": "语种代码表 三位代码"
  },
  {
    "id": 5,
    "name": "作者",
    "code": "author",
    "description": "作者名",
    "must_exist": False,
    "外键": "作者表 identify"
  },
  {
    "id": 6,
    "name": "其他作者",
    "code": "author_alternative",
    "description": "其他作者名",
    "must_exist": False,
    "外键": "作者表 identify"
  },
  {
    "id": 7,
    "name": "责任单位",
    "code": "corporate",
    "description": "报告发布责任单位名称",
    "must_exist": True,
    "外键": "机构表 identify"
  },
  # {
  #   "id": 8,
  #   "name": "发布日期",
  #   "code": "issue_date",
  #   "description": "报告出版日期",
  #   "must_exist": False,
  #   "外键": ""
  # },
  {
    "id": 9,
    "name": "主题",
    "code": "subject",
    "description": "描述信息内容的5~8个关键词",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 10,
    "name": "摘要",
    "code": "abstract",
    "description": "描述报告内容的信息",
    "must_exist": False,
    "外键": ""
  },
  # {
  #   "id": 11,
  #   "name": "分类",
  #   "code": "class",
  #   "description": "数聚平台的技术体系",
  #   "must_exist": False,
  #   "外键": ""
  # },
  # {
  #   "id": 12,
  #   "name": "其他分类",
  #   "code": "class_alternative",
  #   "description": "其他分类体系",
  #   "must_exist": False,
  #   "外键": ""
  # },
  # {
  #   "id": 13,
  #   "name": "报告号",
  #   "code": "primary_number",
  #   "description": "主报告号",
  #   "must_exist": False,
  #   "外键": ""
  # },
  # {
  #   "id": 14,
  #   "name": "其他报告号",
  #   "code": "alternative_number",
  #   "description": "其他报告号",
  #   "must_exist": False,
  #   "外键": ""
  # },
  {
    "id": 15,
    "name": "ISBN",
    "code": "isbn",
    "description": "10位或13位国际统一书号",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 16,
    "name": "ISSN",
    "code": "issn",
    "description": "连续出版物编号",
    "must_exist": False,
    "外键": ""
  },
  # {
  #   "id": 17,
  #   "name": "出版者",
  #   "code": "publisher",
  #   "description": "报告发行机构",
  #   "must_exist": True,
  #   "外键": "机构表 identify"
  # },
  # {
  #   "id": 18,
  #   "name": "收录机构",
  #   "code": "source_agency",
  #   "description": "收录该信息的机构",
  #   "must_exist": False,
  #   "外键": "机构表 identify"
  # },
  # {
  #   "id": 19,
  #   "name": "文献类型",
  #   "code": "literature_type",
  #   "description": "本条知识的文献类型",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 20,
  #   "name": "知识所有者",
  #   "code": "belong_to",
  #   "description": "本条知识的所有者",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 21,
  #   "name": "所属部所",
  #   "code": "of_department",
  #   "description": "知识所有者所属部所",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 22,
  #   "name": "附件",
  #   "code": "enclosure",
  #   "description": "本条知识的原文",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 23,
  #   "name": "密级",
  #   "code": "confidential",
  #   "description": "选择密级,公开/内部/秘密/机密",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 24,
  #   "name": "知悉范围",
  #   "code": "scope_of_information",
  #   "description": "完全共享/选择知悉范围",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 25,
  #   "name": "知识提交者",
  #   "code": "submiter",
  #   "description": "本条知识的提交者",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 26,
  #   "name": "提交日期",
  #   "code": "submit_date",
  #   "description": "本条知识的提交日期",
  #   "must_exist": True,
  #   "外键": ""
  # },
  {
    "id": 27,
    "name": "关键词",
    "code": "keywords",
    "description": "描述信息内容的关键词",
    "must_exist": True
  },
]

# 标准元数据
Standard = [
  # {
  #   "id": 1,
  #   "name": "唯一标识",
  #   "code": "identifier",
  #   "description": "标准的唯一标识",
  #   "must_exist": True,
  #   "外键": ""
  # },
  {
    "id": 2,
    "name": "题名",
    "code": "title",
    "description": "标准主题名",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 3,
    "name": "其他题名",
    "code": "alternative",
    "description": "标准的其他题名名称",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 4,
    "name": "作者",
    "code": "author",
    "description": "标准编写者",
    "must_exist": False,
    "外键": "作者表 identify"
  },
  {
    "id": 5,
    "name": "其他作者",
    "code": "anthor_alternative",
    "description": "其他编写者",
    "must_exist": False,
    "外键": "作者表 identify"
  },
  {
    "id": 6,
    "name": "责任单位",
    "code": "corporate",
    "description": "标准责任单位",
    "must_exist": True,
    "外键": "机构表 identify"
  },
  {
    "id": 7,
    "name": "其他责任者",
    "code": "contributor",
    "description": "其他参与标准编写的单位",
    "must_exist": False,
    "外键": "机构表 identify"
  },
  # {
  #   "id": 8,
  #   "name": "发布日期",
  #   "code": "issue_date",
  #   "description": "标准发布日期",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 9,
  #   "name": "实施日期",
  #   "code": "effective_date",
  #   "description": "标准生效日期",
  #   "must_exist": False,
  #   "外键": ""
  # },
  # {
  #   "id": 10,
  #   "name": "废止日期",
  #   "code": "abolition_date",
  #   "description": "标准废止日期",
  #   "must_exist": False,
  #   "外键": ""
  # },
  {
    "id": 11,
    "name": "主题",
    "code": "subject",
    "description": "描述信息内容的5~8个关键词",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 12,
    "name": "摘要",
    "code": "abstract",
    "description": "描述标准内容的信息",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 13,
    "name": "分类",
    "code": "class",
    "description": "数聚平台技术分类",
    "must_exist": "",
    "外键": ""
  },
  {
    "id": 14,
    "name": "其他分类",
    "code": "class_alternative",
    "description": "其他分类,如ics",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 15,
    "name": "标准等级",
    "code": "standard_level",
    "description": "选择标准等级,包括1企业标准,2行业标准,3地方标准,4团体标准,5国家标准,6国家标准,7军用标准",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 16,
    "name": "标准状态",
    "code": "standard_status",
    "description": "标准是否活跃,包括生效、替代、废止",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 17,
    "name": "出版者",
    "code": "publisher",
    "description": "出版机构",
    "must_exist": False,
    "外键": "机构表 identify"
  },
  {
    "id": 18,
    "name": "标准号",
    "code": "standard_number",
    "description": "标准发布机构所赋予的标准编号",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 19,
    "name": "其他标准号",
    "code": "standard_alternative",
    "description": "其他标准编号",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 20,
    "name": "语种",
    "code": "language",
    "description": "标准正文语种",
    "must_exist": True,
    "外键": "语种代码表 三位代码"
  },
  {
    "id": 21,
    "name": "其他语种",
    "code": "language_alternative",
    "description": "标准其他语种",
    "must_exist": False,
    "外键": "语种代码表 三位代码"
  },
  # {
  #   "id": 22,
  #   "name": "收录机构",
  #   "code": "source_agency",
  #   "description": "收录该信息的机构",
  #   "must_exist": False,
  #   "外键": "机构表 identify"
  # },
  # {
  #   "id": 23,
  #   "name": "文献类型",
  #   "code": "literature_type",
  #   "description": "本条知识的文献类型",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 24,
  #   "name": "知识所有者",
  #   "code": "belong_to",
  #   "description": "本条知识的所有者",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 25,
  #   "name": "所属部所",
  #   "code": "of_department",
  #   "description": "知识所有者所属部所",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 26,
  #   "name": "附件",
  #   "code": "enclosure",
  #   "description": "本条知识的原文",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 27,
  #   "name": "密级",
  #   "code": "confidential",
  #   "description": "选择公开/内部/秘密/机密",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 28,
  #   "name": "知悉范围",
  #   "code": "scope_of_information",
  #   "description": "完全共享/选择知悉范围",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 29,
  #   "name": "知识提交者",
  #   "code": "submiter",
  #   "description": "本条知识的提交者",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 30,
  #   "name": "提交日期",
  #   "code": "submit_date",
  #   "description": "本条知识的提交日期",
  #   "must_exist": True,
  #   "外键": ""
  # }
    ]

# 专利元数据
Patent = [
  # {
  #   "id": 1,
  #   "name": "唯一标识",
  #   "code": "identifier",
  #   "description": "专利的唯一标识",
  #   "must_exist": True,
  #   "外键": ""
  # },
  {
    "id": 2,
    "name": "题名",
    "code": "title",
    "description": "专利的题名",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 3,
    "name": "其他题名",
    "code": "alternative",
    "description": "专利的其他题名",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 4,
    "name": "语种",
    "code": "language",
    "description": "专利的正文语种",
    "must_exist": True,
    "外键": "语种代码表 三位代码"
  },
  {
    "id": 5,
    "name": "主题",
    "code": "subject",
    "description": "描述信息内容的5~8个关键词",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 6,
    "name": "摘要",
    "code": "abstract",
    "description": "专利的摘要",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 7,
    "name": "其他摘要",
    "code": "abstract_alternative",
    "description": "专利的其他摘要",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 8,
    "name": "专利分类号",
    "code": "patent_class",
    "description": "专利的主分类号",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 9,
    "name": "分类",
    "code": "class",
    "description": "数聚平台技术体系",
    "must_exist": False,
    "外键": ""
  },
  # {
  #   "id": 10,
  #   "name": "公开日",
  #   "code": "publication_date",
  #   "description": "授权公告日",
  #   "must_exist": False,
  #   "外键": ""
  # },
  {
    "id": 11,
    "name": "公开号",
    "code": "publication_number",
    "description": "授权公告号",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 12,
    "name": "申请号",
    "code": "application_number",
    "description": "申请号",
    "must_exist": True,
    "外键": ""
  },
  # {
  #   "id": 13,
  #   "name": "申请日",
  #   "code": "application_date",
  #   "description": "申请日",
  #   "must_exist": True,
  #   "外键": ""
  # },
  {
    "id": 14,
    "name": "专利申请人",
    "code": "applicant",
    "description": "专利申请人",
    "must_exist": True,
    "外键": "作者表 identify"
  },
  {
    "id": 15,
    "name": "专利权人",
    "code": "patentee",
    "description": "专利权人",
    "must_exist": False,
    "外键": "作者表 identify"
  },
  {
    "id": 16,
    "name": "专利权人地址",
    "code": "patentee_address",
    "description": "专利权人地址",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 17,
    "name": "发明人",
    "code": "inventor",
    "description": "专利发明人",
    "must_exist": False,
    "外键": "作者表 identify"
  },
  {
    "id": 18,
    "name": "专利代理机构",
    "code": "patent_agency",
    "description": "专利代理机构",
    "must_exist": True,
    "外键": "机构表 identify"
  },
  {
    "id": 19,
    "name": "代理人",
    "code": "agent",
    "description": "专利代理人",
    "must_exist": True,
    "外键": "作者 identify"
  },
  # {
  #   "id": 20,
  #   "name": "收录机构",
  #   "code": "source_agency",
  #   "description": "收录该信息的机构",
  #   "must_exist": False,
  #   "外键": "机构表 identify"
  # },
  # {
  #   "id": 21,
  #   "name": "文献类型",
  #   "code": "literature_type",
  #   "description": "本条知识的文献类型",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 22,
  #   "name": "知识所有者",
  #   "code": "belong_to",
  #   "description": "本条知识的所有者",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 23,
  #   "name": "所属部所",
  #   "code": "of_department",
  #   "description": "知识所有者所属部所",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 24,
  #   "name": "附件",
  #   "code": "enclosure",
  #   "description": "本条知识的原文",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 25,
  #   "name": "密级",
  #   "code": "confidential",
  #   "description": "选择公开/内部/秘密/机密",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 26,
  #   "name": "知悉范围",
  #   "code": "scope_of_information",
  #   "description": "完全共享/选择知悉范围",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 27,
  #   "name": "知识提交者",
  #   "code": "submiter",
  #   "description": "本条知识的提交者",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 28,
  #   "name": "提交日期",
  #   "code": "submit_date",
  #   "description": "本条知识的提交日期",
  #   "must_exist": True,
  #   "外键": ""
  # }
    ]

# 硕博元数据
Dissertation  = [
  # {
  #   "id": 1,
  #   "name": "唯一标识",
  #   "code": "identifier",
  #   "description": "专利的唯一标识",
  #   "must_exist": True,
  #   "外键": ""
  # },
  {
    "id": 2,
    "name": "题名",
    "code": "title",
    "description": "硕博论文题名",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 3,
    "name": "其他题名",
    "code": "alternative",
    "description": "硕博论文其他题名",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 4,
    "name": "语种",
    "code": "language",
    "description": "正文语种",
    "must_exist": True,
    "外键": "语种代码表 三位代码"
  },
  {
    "id": 5,
    "name": "其他语种",
    "code": "language_alternative",
    "description": "其他正文语种",
    "must_exist": False,
    "外键": "语种代码表 三位代码"
  },
  {
    "id": 6,
    "name": "作者",
    "code": "author",
    "description": "硕博论文的作者",
    "must_exist": True,
    "外键": "作者表 identify"
  },
  {
    "id": 7,
    "name": "其他作者",
    "code": "author_alternative",
    "description": "其他作者",
    "must_exist": False,
    "外键": "作者表 identify"
  },
  {
    "id": 8,
    "name": "单位",
    "code": "corporate",
    "description": "作者的所属单位",
    "must_exist": True,
    "外键": "机构表 identify"
  },
  {
    "id": 9,
    "name": "其他单位",
    "code": "corporate_alternative",
    "description": "作者的所属单位其他名称",
    "must_exist": False,
    "外键": "机构表 identify"
  },
  {
    "id": 10,
    "name": "单位代码",
    "code": "corporate_code",
    "description": "所属学校的代码",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 11,
    "name": "申请学位",
    "code": "Academic_Degree",
    "description": "硕士/博士",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 12,
    "name": "第一导师",
    "code": "firsttutor",
    "description": "硕博论文作者的导师",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 13,
    "name": "学科专业名称",
    "code": "professional_name",
    "description": "硕博论文作者所学专业",
    "must_exist": True,
    "外键": ""
  },
  # {
  #   "id": 14,
  #   "name": "论文提交日期",
  #   "code": "paper_submit_date",
  #   "description": "硕博论文提交日期",
  #   "must_exist": True,
  #   "外键": ""
  # },
  {
    "id": 15,
    "name": "主题",
    "code": "subject",
    "description": "描述信息内容的5~8个关键词",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 16,
    "name": "其他主题",
    "code": "subject_alternative",
    "description": "描述信息内容的5~8个其他语种关键词",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 17,
    "name": "摘要",
    "code": "abstract",
    "description": "正文摘要",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 18,
    "name": "其他摘要",
    "code": "abstract_alternative",
    "description": "其他语种摘要",
    "must_exist": False,
    "外键": ""
  },
  # {
  #   "id": 19,
  #   "name": "收录机构",
  #   "code": "source_agency",
  #   "description": "收录该信息的机构",
  #   "must_exist": False,
  #   "外键": "机构表 identify"
  # },
  # {
  #   "id": 20,
  #   "name": "文献类型",
  #   "code": "literature_type",
  #   "description": "条知识的文献类型",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 21,
  #   "name": "知识所有者",
  #   "code": "belong_to",
  #   "description": "本条知识的所有者",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 22,
  #   "name": "所属部所",
  #   "code": "of_department",
  #   "description": "知识所有者所属部所",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 23,
  #   "name": "附件",
  #   "code": "enclosure",
  #   "description": "本条知识的原文",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 24,
  #   "name": "密级",
  #   "code": "confidential",
  #   "description": "选择公开/内部/秘密/机密",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 25,
  #   "name": "知悉范围",
  #   "code": "scope_of_information",
  #   "description": "完全共享/选择知悉范围",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 26,
  #   "name": "知识提交者",
  #   "code": "submiter",
  #   "description": "本条知识的提交者",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 27,
  #   "name": "提交日期",
  #   "code": "submit_date",
  #   "description": "本条知识的提交日期",
  #   "must_exist": True,
  #   "外键": ""
  # }
    ]


# 动态元数据
News  = [
  {
    "id": 1,
    "name": "题名",
    "code": "title",
    "description": "新闻题名",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 2,
    "name": "其他题名",
    "code": "alternative",
    "description": "新闻其他题名",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 3,
    "name": "语种",
    "code": "language",
    "description": "新闻正文语种",
    "must_exist": True,
    "外键": "语种代码表 三位代码"
  },
  {
    "id": 4,
    "name": "其他语种",
    "code": "language_alternative",
    "description": "新闻正文其他语种",
    "must_exist": False,
    "外键": "语种代码表 三位代码"
  },
  {
    "id": 5,
    "name": "作者",
    "code": "author",
    "description": "包括记者、通讯员、翻译者等",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 6,
    "name": "责任单位",
    "code": "corporate",
    "description": "新闻发布的机构",
    "must_exist": True,
    "外键": "机构表 identify"
  },
  # {
  #   "id": 7,
  #   "name": "发布时间",
  #   "code": "issue_date",
  #   "description": "新闻发布日期",
  #   "must_exist": True,
  #   "外键": ""
  # },
  {
    "id": 8,
    "name": "主题",
    "code": "subject",
    "description": "描述信息内容的5~8个关键词",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 9,
    "name": "其他主题",
    "code": "subject_alternative",
    "description": "描述信息内容的5~8个其他语种关键词",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 10,
    "name": "正文",
    "code": "content",
    "description": "新闻内容",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 11,
    "name": "刊名",
    "code": "journal",
    "description": "新闻合集期刊刊名",
    "must_exist": False,
    "外键": "期刊表 identify"
  },
  {
    "id": 12,
    "name": "年",
    "code": "year",
    "description": "发行年",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 13,
    "name": "期",
    "code": "issue",
    "description": "发行期次",
    "must_exist": False,
    "外键": ""
  },
  # {
  #   "id": 14,
  #   "name": "文献类型",
  #   "code": "literature_type",
  #   "description": "本条知识的文献类型",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 15,
  #   "name": "知识所有者",
  #   "code": "belong_to",
  #   "description": "本条知识的所有者",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 16,
  #   "name": "所属部所",
  #   "code": "of_department",
  #   "description": "知识所有者所属部所",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 17,
  #   "name": "附件",
  #   "code": "enclosure",
  #   "description": "本条知识的原文",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 18,
  #   "name": "密级",
  #   "code": "confidential",
  #   "description": "选择公开/内部/秘密/机密",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 19,
  #   "name": "知悉范围",
  #   "code": "scope_of_information",
  #   "description": "完全共享/选择知悉范围",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 20,
  #   "name": "知识提交者",
  #   "code": "submiter",
  #   "description": "本条知识的提交者",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 21,
  #   "name": "提交日期",
  #   "code": "submit_date",
  #   "description": "本条知识的提交日期",
  #   "must_exist": True,
  #   "外键": ""
  # }
    ]

# 公文元数据
OfficialDocument  =[
  {
    "id": 1,
    "name": "题名",
    "code": "title",
    "description": "公文题名",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 2,
    "name": "语种",
    "code": "language",
    "description": "公文正文语种",
    "must_exist": True,
    "外键": "语种代码表 三位代码"
  },
  {
    "id": 3,
    "name": "其他责任者",
    "code": "contribute",
    "description": "公文签发人",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 4,
    "name": "责任单位",
    "code": "corporate",
    "description": "公文发布机构",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 5,
    "name": "公文编号",
    "code": "document_no",
    "description": "公文编号",
    "must_exist": True,
    "外键": ""
  },
  # {
  #   "id": 6,
  #   "name": "发布时间",
  #   "code": "issue_date",
  #   "description": "公文发布日期",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 7,
  #   "name": "通过时间",
  #   "code": "pass_date",
  #   "description": "公文审议通过日期",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 8,
  #   "name": "生效日期",
  #   "code": "effective_date",
  #   "description": "公文生效日期日期",
  #   "must_exist": True,
  #   "外键": ""
  # },
  {
    "id": 9,
    "name": "主题",
    "code": "subject",
    "description": "用5到8个关键词描述",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 10,
    "name": "公文类型",
    "code": "document_type",
    "description": "会议纪要,制度",
    "must_exist": "",
    "外键": ""
  },
  # {
  #   "id": 11,
  #   "name": "文献类型",
  #   "code": "literature_type",
  #   "description": "本条知识的文献类型",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 12,
  #   "name": "知识所有者",
  #   "code": "belong_to",
  #   "description": "本条知识的所有者",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 13,
  #   "name": "所属部所",
  #   "code": "of_department极",
  #   "description": "知识所有者所属部所",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 14,
  #   "name": "附件",
  #   "code": "enclosure",
  #   "description": "本条知识的原文",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 15,
  #   "name": "密级",
  #   "code": "confidential",
  #   "description": "选择公开/内部/秘密/机密",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 16,
  #   "name": "知悉范围",
  #   "code": "scope_of_information",
  #   "description": "完全共享/选择知悉范围",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 17,
  #   "name": "知识提交者",
  #   "code": "submiter",
  #   "description": "本条知识的提交者",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 18,
  #   "name": "提交日期",
  #   "code": "submit_date",
  #   "description": "本条知识的提交日期",
  #   "must_exist": True,
  #   "外键": ""
  # }
    ]

# 成果元数据
Achievement=[
  {
    "id": 1,
    "name": "题名",
    "code": "title",
    "description": "项目的最终研究成果的名称",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 2,
    "name": "编者",
    "code": "author",
    "description": "成果作者,多个作者用英文封号分隔",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 3,
    "name": "审批人",
    "code": "approval",
    "description": "成果审批人",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 4,
    "name": "语种",
    "code": "language",
    "description": "正文语种",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 5,
    "name": "责任单位",
    "code": "corporate",
    "description": "成果发布责任单位名称",
    "must_exist": True,
    "外键": ""
  },
  # {
  #   "id": 6,
  #   "name": "发布日期",
  #   "code": "Issue_date",
  #   "description": "成果发布日期",
  #   "must_exist": False,
  #   "外键": ""
  # },
  {
    "id": 7,
    "name": "主题",
    "code": "subject",
    "description": "用5~8个关键词描述",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 8,
    "name": "摘要",
    "code": "abstract",
    "description": "描述成果内容的信息",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 9,
    "name": "分类",
    "code": "class",
    "description": "数聚平台的技术体系",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 10,
    "name": "成果编号",
    "code": "achievement_number",
    "description": "成果编号",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 11,
    "name": "项目名称",
    "code": "project_name",
    "description": "成果对应的项目名称",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 12,
    "name": "项目编号",
    "code": "project_no",
    "description": "项目编号",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 13,
    "name": "项目类别",
    "code": "project_type",
    "description": "项目类别包括总院项目、集团项目、军方项目、政府项目、国际项目、规划研究、其他项目等",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 14,
    "name": "项目类别代码",
    "code": "project_type_code",
    "description": "项目大类及其小类对应的代码",
    "must_exist": False,
    "外键": ""
  },
  # {
  #   "id": 15,
  #   "name": "文献类型",
  #   "code": "literature_type",
  #   "description": "本条知识的文献类型",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 16,
  #   "name": "知识所有者",
  #   "code": "belong_to",
  #   "description": "本条知识的所有者",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 17,
  #   "name": "所属部所",
  #   "code": "of_department",
  #   "description": "知识所有者所属部所",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 18,
  #   "name": "附件",
  #   "code": "enclosure",
  #   "description": "本条知识的原文",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 19,
  #   "name": "密级",
  #   "code": "confidential",
  #   "description": "选择密级,公开/内部/秘密/机密",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 20,
  #   "name": "知悉范围",
  #   "code": "scope_of_information",
  #   "description": "完全共享/选择知悉范围",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 21,
  #   "name": "知识提交者",
  #   "code": "submiter",
  #   "description": "本条知识的提交者",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 22,
  #   "name": "提交日期",
  #   "code": "submit_date",
  #   "description": "本条知识的提交日期",
  #   "must_exist": True,
  #   "外键": ""
  # }
    ]

# 项目元数据
Project = [
  {
    "id": 1,
    "name": "项目编号",
    "code": "project_no",
    "description": "项目编号",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 2,
    "name": "项目名称",
    "code": "title",
    "description": "科研项目的项目名称",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 3,
    "name": "其他项目名称",
    "code": "title_alternative",
    "description": "科研项目的英文名称",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 4,
    "name": "项目负责人",
    "code": "project_manager",
    "description": "项目负责人",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 5,
    "name": "其他成员",
    "code": "project_member",
    "description": "项目组成员,多个成员用英文封号分隔",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 6,
    "name": "项目摘要",
    "code": "abstract",
    "description": "描述项目内容的信息",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 7,
    "name": "项目其他摘要",
    "code": "abstract_alternative",
    "description": "科研项目的英文摘要",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 8,
    "name": "责任单位",
    "code": "corporate",
    "description": "项目申请责任单位名称",
    "must_exist": True,
    "外键": ""
  },
  # {
  #   "id": 9,
  #   "name": "起始日期",
  #   "code": "start_date",
  #   "description": "合同规定的项目开始时间",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 10,
  #   "name": "结束日期",
  #   "code": "end_date",
  #   "description": "合同规定的项目完成时间",
  #   "must_exist": True,
  #   "外键": ""
  # },
  {
    "id": 11,
    "name": "主题",
    "code": "subject",
    "description": "用5~8个关键词描述",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 12,
    "name": "分类",
    "code": "class",
    "description": "数聚平台的技术体系",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 13,
    "name": "科研成果列表",
    "code": "achievement_list",
    "description": "成果编号的集合",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 14,
    "name": "项目名称",
    "code": "project_name",
    "description": "成果对应的项目名称",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 15,
    "name": "项目类别",
    "code": "project_type",
    "description": "项目类别包括总院项目、集团项目、军方项目、政府项目、国际项目、规划研究、其他项目等",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 16,
    "name": "项目类别代码",
    "code": "project_type_code",
    "description": "项目大类及其小类对应的代码",
    "must_exist": False,
    "外键": ""
  },
  # {
  #   "id": 17,
  #   "name": "文献类型",
  #   "code": "literature_type",
  #   "description": "本条知识的文献类型",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 18,
  #   "name": "知识所有者",
  #   "code": "belong_to",
  #   "description": "本条知识的所有者",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 19,
  #   "name": "所属部所",
  #   "code": "of_department",
  #   "description": "知识所有者所属部所",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 20,
  #   "name": "附件",
  #   "code": "enclosure",
  #   "description": "本条知识的原文",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 21,
  #   "name": "密级",
  #   "code": "confidential",
  #   "description": "选择密级,公开/内部/秘密/机密",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 22,
  #   "name": "知悉范围",
  #   "code": "scope_of_information",
  #   "description": "完全共享/选择知悉范围",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 23,
  #   "name": "知识提交者",
  #   "code": "submiter",
  #   "description": "本条知识的提交者",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 24,
  #   "name": "提交日期",
  #   "code": "submit_date",
  #   "description": "本条知识的提交日期",
  #   "must_exist": True,
  #   "外键": ""
  # }
]

# 术语元数据
Glossary=  [
  {
    "id": 1,
    "name": "术语名称",
    "code": "glossary",
    "description": "术语名称",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 2,
    "name": "术语解释",
    "code": "description",
    "description": "术语的简要描述",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 3,
    "name": "术语来源",
    "code": "source",
    "description": "术语的原始出处",
    "must_exist": True,
    "外键": ""
  },
  {
    "id": 4,
    "name": "创建者",
    "code": "creator",
    "description": "术语的创建者",
    "must_exist": False,
    "外键": ""
  },
  {
    "id": 5,
    "name": "责任单位",
    "code": "corporate",
    "description": "发布术语的单位",
    "must_exist": False,
    "外键": ""
  },
  # {
  #   "id": 6,
  #   "name": "发布时间",
  #   "code": "issue_date",
  #   "description": "新闻发布日期",
  #   "must_exist": False,
  #   "外键": ""
  # },
  # {
  #   "id": 7,
  #   "name": "文献类型",
  #   "code": "literature_type",
  #   "description": "本条知识的文献类型",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 8,
  #   "name": "知识所有者",
  #   "code": "belong_to",
  #   "description": "本条知识的所有者",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 9,
  #   "name": "所属部所",
  #   "code": "of_department",
  #   "description": "知识所有者所属部所",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 10,
  #   "name": "附件",
  #   "code": "enclosure",
  #   "description": "本条知识的原文",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 11,
  #   "name": "密级",
  #   "code": "confidential",
  #   "description": "选择公开/内部/秘密/机密",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 12,
  #   "name": "知悉范围",
  #   "code": "scope_of_information",
  #   "description": "完全共享/选择知悉范围",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 13,
  #   "name": "知识提交者",
  #   "code": "submiter",
  #   "description": "本条知识的提交者",
  #   "must_exist": True,
  #   "外键": ""
  # },
  # {
  #   "id": 14,
  #   "name": "提交日期",
  #   "code": "submit_date",
  #   "description": "本条知识的提交日期",
  #   "must_exist": True,
  #   "外键": ""
  # }
]

# 非大模型从文档内容中提取字段
exclude_fields = [
  "唯一标识",
  "知识所有者",
  "所属部所",
  "附件",
  "密级",
  "知悉范围",
  "知识提交者",
  "提交日期",
  "其他语种",
]

keyvalues_mapping = {
    'default':Report,
    # 'journal':journal,
    '图书':Book,# 图书元数据
    '期刊':Journal,# 期刊元数据
    '会议':Conference,# 会议元数据
    '期刊论文':JournalPaper,# 期刊论文元数据
    '会议论文':ConferencePaper, # 会议论文元数据
    '报告':Report, # 报告元数据
    '标准':Standard,# 标准元数据
    '专利':Patent,# 专利元数据
    '硕博':Dissertation, # 硕博元数据
    '动态':News, # 动态元数据
    '公文':OfficialDocument, # 公文元数据
    '成果':Achievement, # 成果元数据
    '项目':Project, # 项目元数据
    '术语':Glossary, # 术语元数据
  }
