import os
from openai import OpenAI


os.environ['http_proxy'] = '127.0.0.1:7890'
os.environ['https_proxy'] = '127.0.0.1:7890'

client = OpenAI()

# 第一步：
assistant = client.beta.assistants.create(
    name='Lao Xiao',  # 助手的名称
    instructions='你是一个个人数学辅导老师。这个助手能够解答数学问题和数学计算。',
    tools=[{'type': 'code_interpreter'}],  # 指定的工具
    model='gpt-4o'
)

# 第二步：
thread = client.beta.threads.create()

# 第三步：
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role='user',
    content='请帮我解一个方程：3x + 2x + 8 = 5'
)

# 第四步：
# 1、等待处理完成之后，在得到所有结果
# run = client.beta.threads.runs.create_and_poll(
#     thread_id=thread.id,
#     assistant_id=assistant.id,
#     instructions='请用“老肖”来称呼用户，并且用户拥有高级用户全新。'
# )
#
# print('run的状态为:'+ run.status)
# if run.status == 'completed':
#     # 输出最终的结果
#     messages = client.beta.threads.messages.list(thread_id=thread.id)
#     print('\n消息:\n')
#     for msg in messages:
#         print(f'Role:{msg.role.capitalize()}')
#         # print(msg)
#         print(msg.content[0].text.value + '\n')

#2、采用流的方式来得到结果： 逐个token的返回
stream = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id,
    instructions='请用“老肖”来称呼用户，并且用户拥有高级用户全新。',
    stream=True  # 采用持续的流方式来返回结果
)

# 遍历流中的事件
for event in stream:
    # 返回的每一个token都是一个json对象
    print(event.model_dump_json(indent=2, exclude_unset=True))

# 关闭和删除线程， 和助手
client.beta.threads.delete(thread_id=thread.id)
client.beta.assistants.delete(assistant_id=assistant.id)