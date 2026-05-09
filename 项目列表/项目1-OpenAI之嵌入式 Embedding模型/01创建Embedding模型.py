import pandas as pd
import os
from openai import OpenAI
import tiktoken

os.environ['http_proxy'] = '127.0.0.1:7890'
os.environ['https_proxy'] = '127.0.0.1:7890'

# 需要安装依赖库
# pip install tiktoken openai pandas matplotlib plotly scikit-learn numpy

'''
该数据集包含截至2012年10月用户在亚马逊上留下的共计568,454条美食评论，
我们将使用该数据集的一个子集，
其中包括最近1,000条评论。这些评论都是用英语撰写的，
'''

# 1、首先读取数据，然后预处理

df = pd.read_csv('datas/fine_food_reviews_1k.csv', index_col=0)

df = df[['Time', 'ProductId', 'UserId', 'Score', 'Summary', 'Text']]

# 删除cvs中缺失的数据，NaN，NaT的数据
df = df.dropna()

# 把'Summary', 'Text' 两个字段合并
df['combined'] = "Title:" + df.Summary.str.strip() + "; Content:" + df.Text.str.strip()

# print(df.head(2))

# 2、生成Embedding之后的向量空间，并且保存
# 建议使用官方推荐的第二代嵌入模型：text-embedding-ada-002
embedding_model = "text-embedding-ada-002"

# 对文本进行处理的分词器
tokenizer_name = 'cl100k_base'
max_tokens = 8191
top_n = 1000
df = df.sort_values('Time')
df.drop("Time", axis=1, inplace=True)

# 创建一个分词器
tokenizer = tiktoken.get_encoding(encoding_name=tokenizer_name)

# 控制输入数据的token数量
# 计算token数量

df['count_token'] = df.combined.apply(lambda x: len(tokenizer.encode(x)))

# token的数量不能超过官方的阈值: 超过了就不要。
df = df[df.count_token <= max_tokens].tail(top_n)

print(len(df))

# 初始化openai的客户端
client = OpenAI()


def embedding_text(text, model='text-embedding-ada-002'):
    """
    通过OpenAI的Embedding模型处理文本数据
    :param text: 需要处理的文本数据
    :param model:
    :return:
    """
    resp = client.embeddings.create(input=text, model=model)
    return resp.data[0].embedding


df['embedding'] = df.combined.apply(embedding_text)  # 使用embedding模型处理text

df.to_csv('datas/embedding_output_1k.csv')

print(df['embedding'][0])