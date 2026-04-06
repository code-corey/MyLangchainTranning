import os

from langchain_chroma import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory, RunnableLambda
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.documents import Document

os.environ["LANGCHAIN_TRACING_V2"] = "true"

ARK_BASE_URL = os.environ.get("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


# 定义模型
model = ChatOpenAI(
    model=os.environ["ModelID"],
    base_url=os.environ["BaseUrl"]
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

## 准备好向量文档

Documents = [
    Document(
        page_content="大熊猫是中国特有物种，以竹子为主食，被誉为‘活化石’和‘中国国宝’。",
        metadata={"name": "大熊猫", "category": "哺乳动物", "habitat": "中国四川、陕西等山区", "diet": "竹子"}
    ),
    Document(
        page_content="非洲象是陆地上最大的动物，拥有长鼻和巨大的耳朵，主要生活在非洲草原和森林。",
        metadata={"name": "非洲象", "category": "哺乳动物", "habitat": "非洲草原与森林", "diet": "草、树叶、果实"}
    ),
    Document(
        page_content="猎豹是速度最快的陆地动物，最高时速可达120公里，主要分布在非洲和伊朗。",
        metadata={"name": "猎豹", "category": "哺乳动物", "habitat": "非洲草原", "diet": "羚羊等中小型动物"}
    ),
    Document(
        page_content="帝企鹅是体型最大的企鹅，生活在南极冰盖，能在极寒环境中繁殖后代。",
        metadata={"name": "帝企鹅", "category": "鸟类", "habitat": "南极", "diet": "鱼类、磷虾"}
    ),
    Document(
        page_content="蓝鲸是地球上体型最大的动物，体重可达200吨，以磷虾为食，遍布全球海洋。",
        metadata={"name": "蓝鲸", "category": "海洋哺乳动物", "habitat": "全球海洋", "diet": "磷虾"}
    ),
    Document(
        page_content="红眼树蛙生活在热带雨林，拥有鲜艳的红色眼睛和绿色的身体，善于攀爬。",
        metadata={"name": "红眼树蛙", "category": "两栖动物", "habitat": "中美洲雨林", "diet": "昆虫"}
    ),
    Document(
        page_content="袋鼠是澳大利亚的标志性动物，后腿强壮，善于跳跃，雌性有育儿袋。",
        metadata={"name": "袋鼠", "category": "有袋类", "habitat": "澳大利亚", "diet": "草、树叶"}
    ),
    Document(
        page_content="金刚鹦鹉是色彩最艳丽的鹦鹉之一，寿命长，智商高，主要生活在南美洲雨林。",
        metadata={"name": "金刚鹦鹉", "category": "鸟类", "habitat": "南美洲雨林", "diet": "坚果、种子、果实"}
    ),
    Document(
        page_content="北极熊是北极地区的顶级捕食者，以海豹为主食，依赖海冰生存。",
        metadata={"name": "北极熊", "category": "哺乳动物", "habitat": "北极圈", "diet": "海豹、鱼类"}
    ),
    Document(
        page_content="变色龙以能改变体色闻名，舌头长度可超过身体，主要分布在马达加斯加。",
        metadata={"name": "变色龙", "category": "爬行动物", "habitat": "马达加斯加及非洲", "diet": "昆虫"}
    )
]

## 实例化一个向量库,以向量文档为依托，openAI的
embeddings = OpenAIEmbeddings(
    model="embedding-3",
    base_url=os.environ["BaseUrl"]
)
vector_store = Chroma.from_documents(Documents, embedding=embeddings)

## 对文档进行相似度查询，分数越低，相似度越高
# print(vector_store.similarity_search_with_score("狗熊"))

## 构建一个检索器,选取相似度最高的1个
##
retriever = RunnableLambda(vector_store.similarity_search).bind(k=1)

print(retriever.batch(['咖啡猫', '老鼠']))
