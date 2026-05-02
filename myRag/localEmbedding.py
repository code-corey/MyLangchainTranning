from langchain_huggingface import HuggingFaceEmbeddings

# 定义模型名称（或者指向你本地存放模型的文件夹路径）
model_name = "BAAI/bge-large-zh-v1.5"
model_kwargs = {'device': 'cpu'}  # 如果你有 GPU，可以改为 'cuda'
encode_kwargs = {'normalize_embeddings': True} # 归一化，利于计算余弦相似度

# 初始化 Embedding 对象
embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

# 测试一下
text = "关云长温酒斩华雄"
query_result = embeddings.embed_query(text)

print(f"向量维度: {len(query_result)}")
print(f"向量前五位: {query_result[:5]}")