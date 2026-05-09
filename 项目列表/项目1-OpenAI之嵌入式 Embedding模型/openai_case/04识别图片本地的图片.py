import base64
import os

import requests

os.environ['http_proxy'] = '127.0.0.1:7890'
os.environ['https_proxy'] = '127.0.0.1:7890'


# 采用发送http请求的方式来调用：openai的接口。
def import_image(img_path, prompt='请介绍一下图片的内容', max_tokens=1000):
    """
    把本地的图片数据作为大语言模型的输入，
    本地的图片：必须要转换为Base64的编码
    :param img_path:
    :param prompt:
    :param max_tokens:
    :return:
    """

    # 实现图片的Base64编码
    def encode_image(path):
        with open(path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')

    base64_image = encode_image(img_path)

    # 构建一个请求头
    header = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY")}'  # openai的认证token
    }

    # 构建请求负载
    payload = {
        'model': 'gpt-4-turbo',
        'messages': [
            {
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': prompt},  # 输入为文本数据
                    {'type': 'image_url', 'image_url': {
                        'url': f'data:image/jpeg;base64,{base64_image}'
                    }}
                ]
            }
        ],
        'max_tokens': max_tokens
    }

    # 发送请求，
    resp = requests.post('https://api.openai.com/v1/chat/completions', headers=header, json=payload)

    # 处理和打印响应数据
    if resp.status_code == 200:  # 状态码为200才是成功的
        resp_data = resp.json()
        content = resp_data['choices'][0]['message']['content']
        return content
    else:  # 请求失败
        return f'请求失败，状态码为: {resp.status_code}, 失败的信息：{resp.text}'


print(import_image('./images/gdp_1980_2020.jpg'))
print('='*50)
print(import_image('./images/handwriting_0.jpg'))

