general=[
  {
    "id": 1,
    "name": "标题",
    "code": "title",
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
    "must_exist": False
  },
  {
    "id": 4,
    "name": "其他作者",
    "code": "other_authors",
    "description": "其他作者",
    "must_exist": True
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
    "must_exist": False
  },
  {
    "id": 8,
    "name": "关键词",
    "code": "keywords",
    "description": "描述信息内容的关键词",
    "must_exist": False
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
  {
    "id": 13,
    "name": "出版时间",
    "code": "",
    "description": "",
    "must_exist": False
  },
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
  {
    "id": 8,
    "name": "创刊日期",
    "code": "start_date",
    "description": "期刊创刊日期",
    "must_exist": True
  },
  {
    "id": 9,
    "name": "停刊日期",
    "code": "end_date",
    "description": "期刊停刊日期",
    "must_exist": False
  },
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

keyvalues_mapping = {
        'default':general,
        'journal':journal,
    }
