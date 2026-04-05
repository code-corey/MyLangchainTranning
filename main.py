import os

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGCHAIN_API_KEY"] = ""

# 创建模型
model = ChatOpenAI(
    model=os.environ["ModelID"],
    base_url="https://ark.cn-beijing.volces.com/api/v3"
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


## 定义好模版
promptTemplate = ChatPromptTemplate.from_messages(
    [
        ('system','把内容翻译成{language}'),
        ('user','{text}')
    ]
)

# 得到链
chain = promptTemplate | model | parser

# 直接使用chain来调用


## print(chain.invoke(msg))

print(chain.invoke({
    'language': 'English',
    'text': '今天天气好'
}))