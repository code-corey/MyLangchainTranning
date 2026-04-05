import os

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "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"

# 创建模型
model = ChatOpenAI(
    model="qwen/qwen3.6-plus:free",
    base_url="https://openrouter.ai/api/v1"
)

# 准备提示
msg=[
    SystemMessage(content="请翻译成英语"),
    HumanMessage(content="你吃了没")
]

result= model.invoke(msg)
# print(result)

# 解析数据，格式化
parser= StrOutputParser()
#print(parser.invoke(result))

# 得到链
chain = model | parser

# 直接使用chain来调用

print(chain.invoke(msg))