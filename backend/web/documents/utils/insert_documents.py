import lancedb
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import LanceDB
from langchain_text_splitters import RecursiveCharacterTextSplitter

from web.documents.utils.custom_embeddings import CustomEmbeddings

# 将文本文档转换成向量并存储到数据库
# 把一个data.txt文件里的内容，切分成小段，每段转换成向量（数字列表），然后存到LanceDB数据库中，方便后续做相似度搜索。
def insert_documents():
    # TextLoader默认会把连续的非空行作为一个文档，遇到空行就切分成新文档
    loader=TextLoader('./web/documents/data.txt',encoding='utf-8')
    # documents是一个包含完整文本的列表
    documents=loader.load()
    # 为什么切分：大段文本没法一次处理，需要分成小块
    # chunk_size=500：每块大约500个字符
    # chunk_overlap=50：相邻块有50个字符的重叠（保持上下文连贯）
    text_splitter=RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=50)
    texts=text_splitter.split_documents(documents)
    print(f"已切分成{len(texts)}个片段。")
    # 创建向量化工具
    embeddings=CustomEmbeddings()
    # 连接数据库，LanceDB是一个向量数据库，专门存储和搜索向量，这里在本地创建了一个数据库文件夹
    db=lancedb.connect('./web/documents/lancedb_storage')
    # 生成向量并存入
    # 遍历每个文本片段
    # 调用embeddings.embed_documents()把文字转成向量
    # 把(原文, 向量)存入LanceDB
    # 创建索引方便快速搜索
    vector_db=LanceDB.from_documents(#接收文档列表，自动完成向量化，然后创建并返回一个 LanceDB 向量数据库实例
        documents=texts,
        embedding=embeddings,# 向量转换工具
        connection=db,# 数据库连接
        table_name='my_knowledge_base',#如果已经创建了该数据库，但是table_name不一样，就相当于在该数据库里加表
        mode='overwrite', # 覆盖模式（如果表存在就删了重建）
    )
    print(f'已插入{vector_db._table.count_rows()}行数据')