import os
from openai import OpenAI


os.environ['http_proxy'] = '127.0.0.1:7890'
os.environ['https_proxy'] = '127.0.0.1:7890'

client = OpenAI()

# 1、根据提示，生成英文的文本
# result = client.completions.create(
#     model='gpt-3.5-turbo-instruct',
#     prompt='Say Hello World！',
#     max_tokens=20,
#     temperature=0.5,
#     n=1
# )

# 2、根据提示，生成中文的文本
result = client.completions.create(
    model='gpt-3.5-turbo-instruct',
    prompt='讲5个笑话给小朋友听',
    max_tokens=1000,
    temperature=0.5,
    n=2
)

# 3、根据提示，生成代码
result = client.completions.create(
    model='gpt-3.5-turbo-instruct',
    prompt='请用Python写一个快速排序的算法',
    max_tokens=1000
)
# result是一个completions类型
print(result)
print(result.choices[0].text)