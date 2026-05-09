import os
from openai import OpenAI


os.environ['http_proxy'] = '127.0.0.1:7890'
os.environ['https_proxy'] = '127.0.0.1:7890'

client = OpenAI()

# chat completions ,交互式的API调用

# 1、准备一个message，同时这个message还要记录所有的聊天信息
message = [
    {'role': 'system', 'content': '你是一个无所不能的体育专家。'},
    {
        'role': 'user',
        'content': '你好啊！'
    }
]
result = client.chat.completions.create(
    model='gpt-3.5-turbo',
    messages=message
)

# print(result)
out_result = result.choices[0].message
print(out_result.content)

message.append({'role': out_result.role, 'content': out_result.content})

# 第二轮的聊天

new_chat = {
    'role': 'user',
    'content': '1、2024年的奥运会在哪个国家举行。2、告诉我这个国家的首都是什么？'
}

message.append(new_chat)

result = client.chat.completions.create(
    model='gpt-3.5-turbo',
    messages=message
)
out_result = result.choices[0].message
print(out_result.content)

message.append({'role': out_result.role, 'content': out_result.content})

# 开启第三轮对话：
new_chat = {
    'role': 'user',
    'content': '请问这个国家历史上一共获得过多少金牌？'
}

message.append(new_chat)

result = client.chat.completions.create(
    model='gpt-3.5-turbo',
    messages=message
)
out_result = result.choices[0].message
print(out_result.content)

message.append({'role': out_result.role, 'content': out_result.content})


# 开启一个新会话，单独问一个问题
new_chat = [{
    'role': 'user',
    'content': '请问这个国家历史上一共获得过多少金牌？'
}]

result = client.chat.completions.create(
    model='gpt-3.5-turbo',
    messages=new_chat
)
print(result.choices[0].message.content)