# 自定义的embeddings模型
import os

from langchain_core.embeddings import Embeddings
from openai import OpenAI

# 必须实现两个方法：embed_documents(批量处理) 和 embed_query(单个查询)
class CustomEmbeddings(Embeddings):
    def __init__(self):
        # 创建一个调用远程API的客户端，用来访问某个提供向量服务的服务器
        self.client = OpenAI(
            api_key=os.getenv("API_KEY"),
            base_url=os.getenv("API_BASE")
        )
    def embed_documents(self, texts):
        batch_size = 10
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i: i + batch_size]
            batch = [t for t in batch if t.strip()]
            if not batch:
                continue
            response = self.client.embeddings.create(
                model="text-embedding-v4",# 使用哪个向量模型
                input=batch,# 要转换的文本列表，比如["你好","世界"]
                dimensions=1024# 生成的向量维度（数字个数）即每个文字转成1024个数字
            )
            # 提取结果，API返回的结果，结构类似：
            # [
            #     {embedding: [0.12, -0.45, ...]},  # 第1个文本的向量
            #     {embedding: [0.33, 0.21, ...]},   # 第2个文本的向量
            # ]
            # all_embeddings.extend([...])把新得到的向量列表追加到总结果里
            all_embeddings.extend([data.embedding for data in response.data])
        return all_embeddings

    def embed_query(self, text):
        # 输入：单个查询（如“什么是人工智能？”）
        # 输出：该查询的向量
        return self.embed_documents([text])[0]