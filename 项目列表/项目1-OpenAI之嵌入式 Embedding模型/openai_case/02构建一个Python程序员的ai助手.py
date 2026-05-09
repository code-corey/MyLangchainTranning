import os
from openai import OpenAI


os.environ['http_proxy'] = '127.0.0.1:7890'
os.environ['https_proxy'] = '127.0.0.1:7890'

client = OpenAI()

# 第一步：
assistant = client.beta.assistants.create(
    name='Lao Xiao',  # 助手的名称
    instructions='你是一个Python高级程序员，根据消息生成可运行的Python代码。',
    tools=[{'type': 'code_interpreter'}],  # 指定的工具
    model='gpt-4o'
)

# 第二步：
thread = client.beta.threads.create()

# 第三步：
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role='user',
    content='冒泡排序咋个写法？'
)

# 第四步：
# 1、等待处理完成之后，在得到所有结果
run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id,
    assistant_id=assistant.id,
    instructions='请用“老肖”来称呼用户，并且用户拥有高级用户全新。'
)
if run.status == 'completed':
    # 输出最终的结果
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    print('\n消息:\n')
    for msg in messages:
        print(f'Role:{msg.role.capitalize()}')
        print(msg.content[0].text.value + '\n')


message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role='user',
    content='那红黑树呢？'
)

run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id,
    assistant_id=assistant.id,
    instructions='请用“老肖”来称呼用户，并且用户拥有高级用户全新。'
)

if run.status == 'completed':
    # 输出最终的结果
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    print('\n消息:\n')
    for msg in messages:
        print(f'Role:{msg.role.capitalize()}')
        print(msg.content[0].text.value + '\n')
