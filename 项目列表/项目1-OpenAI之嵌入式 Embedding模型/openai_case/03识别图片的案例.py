import os
from openai import OpenAI


os.environ['http_proxy'] = '127.0.0.1:7890'
os.environ['https_proxy'] = '127.0.0.1:7890'

client = OpenAI()

# 处理在线图片
resp = client.chat.completions.create(
    model='gpt-4-turbo',
    messages=[
        {
            'role': 'user',
            'content': [
                {'type': 'text', 'text': '介绍一下这张图片'},  # 输入为文本数据
                {'type': 'image_url', 'image_url': {
                    'url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg'
                }}
            ]
        }
    ],
    max_tokens=400
)

print(resp.choices[0].message.content)