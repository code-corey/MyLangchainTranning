import os
from openai import OpenAI


os.environ['http_proxy'] = '127.0.0.1:7890'
os.environ['https_proxy'] = '127.0.0.1:7890'

client = OpenAI()
models = client.models.list()
print(models)
'''
Model(id='dall-e-3', created=1698785189, object='model', owned_by='system')

'''

model_list = [model.id for model in models.data]
print(model_list)

# 根据模型名字，直接获得模型的信息
model_info = client.models.retrieve('gpt-4o')
print(model_info)

'''
1、created: 这是模型创建的时间戳，单位为 Unix 时间戳（自1970年1月1日（00:00:00 GMT）以后的秒数）。
2、id: 这是模型的唯一标识符。
3、object: 这个字段表示的是当前对象的类型。
4、owned_by: 这个字段表示的是模型的所有者。
'''