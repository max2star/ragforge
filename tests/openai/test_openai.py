if __name__ == "__main__":
    import sys
    import numpy as np
    from openai import OpenAI
    client = OpenAI(api_key='gpustack_3c3306069544b759_ea80926d3a80bef2f199944249d6ce89', base_url='http://101.52.216.178:890/v1-openai')
    client = OpenAI( api_key="ollama",base_url='http://10.1.60.39:11434/v1')
    res = client.embeddings.create(input='test',#[truncate('test', 8191)],
        model='bge-m3',encoding_format="float" )
    print(res)
    print("MaXiao encode OpenAIEmbed length {}".format(len(res.data[0].embedding)))
    print("MaXiao encode OpenAIEmbed length {}".format(len(np.array(res.data[0].embedding))))
