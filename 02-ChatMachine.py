import os

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

os.environ["LANGCHAIN_TRACING_V2"] = "true"

# 定义模型
model = ChatOpenAI(
    model=os.environ["ModelID"],
    base_url="https://ark.cn-beijing.volces.com/api/v3",
)

# 定义模版
## MessagesPlaceholder 这里的占位符是因为我们需要引用历史记录Id，所以在这里，我们使用占用

prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个乐于助人的助手，用{language}尽可能回答问题。"),
        MessagesPlaceholder(variable_name="history"),
        MessagesPlaceholder(variable_name="my-msg"),
    ]
)

# 定义链
chain = prompt_template | model

store: dict[str, ChatMessageHistory] = {}

# 定义一个获取session历史记录的接口
def get_session_history(session_id: str) -> ChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# 使用代用历史消息的方法来作为交流接口
do_message = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="my-msg",
    history_messages_key="history",
)

config = {"configurable": {"session_id": "zhangsan123"}}

# 直接调用 do_message方法，执行 invoke方法
resp = do_message.invoke(
    {
        "my-msg": [HumanMessage(content="我是Corey，今年40岁了")],
        "language": "中文",
    },
    config=config,
)

print(resp.content)



# 直接调用 do_message方法，执行 invoke方法
resp = do_message.invoke(
    {
        "my-msg": [HumanMessage(content="我是谁")],
        "language": "中文",
    },
    config=config,
)

print(resp.content)