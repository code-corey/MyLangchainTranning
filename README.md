# LangChain学习之旅

## 1-LangChain基本理论
🎯1-01Langchain是什么   
是什么？
作为一个连接和集成不同系统的桥梁。扮演了一种中介的角色。允许使用特定的技术，让AI和其他的系统，应用进行交互。
他允许大语言模型和具体的数据库，PDF，内部系统进行交互（方便做RAG）

🎯2-02Langchain的核心   

核心：
- Models 模型：允许连接大语言模型
- Prompt Templates：提示词模版，可以预定义功能性的提示词模版，然后在真正使用的时候，动态的去传入参数，发送给语言模型
- Chains：把所有的组件全部连接在一起，解决一个特定的任务，构建一个完整的语言模型应用程序。
- Agent：允许语言模型和外部环境进行交互，访问请求API之类的
- Embinddings & VectorStores：向量存储，信息的存储和检索
- Index：帮助从语言模型中提取出相关信息

🎯3-03Langchain的底层原理   

底层原理：
1、用户发起一个问题或者请求，首先从自己的数据库中，进行查询，或者从向量数据库中，进行相似性搜索，得到相关的信息
2、得到的信息，与原始的问题相结合后，由一个处理模型分析，得到了一个答案
3、这个答案可以作为输入，去让下一个Agent去做相关的事情，可以调用API或者和系统交互，这样就完成了任务

应用场景：
1、个人的订票助手，可以帮助查询和订票
2、学习辅助：比如说学习10篇论文，让AI先把所有的文档先看完，然后进行针对性的学习
3、客户数据和科学的分析：链接公司的数据库做分析


🎯4-04Langchain的环境和监控   
pip install langchain-openai
pip install langchain


LangSmith究竟是用来干什么的？
> 用于构建一个生产级LLM平台，从原型到生产的全流程的工具和服务，并且提供了调试，测试，监控，评估等功能 LLM框架构建的链和智能代理的功能。

- 调试和测试：记录langchain构建的大模型应用的中间过程，可以更好的调整提示词，优化模型响应
- 评估应用效果：量化，评估大模型系统的结果，帮助开发者找出潜在的提升点
- 监控应用性能：相当于日志功能，记录的成功，错误的相关情况，提高稳定性和可靠性。
- 数据管理和分析：对于大模型的输入和输出的过程进行存储和分析，帮助理解大模型的中间过程和性能调优
- 团队写作：提示词共享
- 可扩展性和可维护性： 

https://smith.langchain.com/




## 2-LangChain核⼼模块与实战

🎯1-05采用Langtain调用LLM.mp4
完成了最简单的一次调用:

```
import os
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = ""
model = ChatOpenAI(
    model="qwen/qwen3.6-plus:free",
    base_url="https://openrouter.ai/api/v1"
)
msg=[
    SystemMessage(content="请翻译成英语"),
    HumanMessage(content="你吃了没")
]
parser= StrOutputParser()
chain = model | parser
print(chain.invoke(msg))
```

本来还直接的去使用OpenAI，但是充值失败了。于是找到了OpenRouter,直接使用免费的模型进行做为Demo测试。

这里有一个比较关键的信息就是Chain = model | parser ==> chain.invoke(msg)
完成了第一次的入门案例。



## 2026年04月6日 周一 [**第17天**]

🎯2-06Langchain的提示模板.mp4
使用这种方式去定义一个模版，后续在进行调用的时候，就可以直接使用
``` py
promptTemplate = ChatPromptTemplate.from_messages(
    [
        ('system','把内容翻译成{language}'),
        ('user','{text}')
    ]
)
```

直接调用的时候，传入对应的参数就行
``` py
print(chain.invoke({'language': 'English','text': '今天天气好呀'}))
```


🎯3-07部署你的langchain程序.mp4

部署的使用我们需要安装一下 LangServe，这个langserve里面包含了一个FastAPI，用于启动一个Python的web服务器
``` py
pip install langserve[all]
```

我们使用 FastAPI，启动起来
``` py
app= FastAPI(title='我的Langchain服务',version='V1.0',description="使用Langchain翻译任何语句的服务")

add_routes(
    app,
    chain,
    path="/chain"
)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,host="localhost",port=8000)
```

调用的时候，有两种方式，一种是代码，一种是使用Postman

使用代码的方式如下：
``` py

from langserve import RemoteRunnable

if __name__ == "__main__":
    client=RemoteRunnable('http://127.0.0.1:8000/chain')
    print(client.invoke({'language': 'english', 'text': '早上好'}))
```

使用APi调用的方式如下：
```
POST http://127.0.0.1:8000/chain/invoke

{
    "input":{
        "language": "english",
         "text": "早上好"
    }
}
```



- ⭕4-08LangChain构建聊天机器人.mp4
- ⭕5-09流式输出的处理.mp4
- ⭕6-10构建文档和向量空间.mp4
- ⭕7-11检索器和模型结合.mp4
- ⭕8-12Tavily搜索工具.mp4
- ⭕9-13Agent代理的使用.mp4
- ⭕10-14构建RAG对话应用(一).mp4
- ⭕11-15构建RAG问答应用(二).mp4
- ⭕12-16构建RAG问答应用(三).mp4
- ⭕13-17Langchain读取数据库.mp4
- ⭕14-18Langchain和数据库整合.mp4
- ⭕15-19Agent整合数据库.mp4
- ⭕16-20爬取Youtube字幕并构建向量数据库.mp4
- ⭕17-21执行代码并保存向量数据库.mp4
- ⭕18-22加载向量数据库并测试(2).mp4
- ⭕19-23定义数据模型得到检索指令.mp4
- ⭕20-24根据检索条件去执行.mp4
- ⭕21-25提取和输出结构化数据.mp4
- ⭕22-26提取多个对象.mp4

## 3-LangChain实战案例
- ⭕1-27生成一些文本数据   .sz
- ⭕2-28生成结构化的数据(一)   .sz
- ⭕3-29生成结构化的数据(二)   .sz
- ⭕4-30实现文本分类(一)   .sz
- ⭕5-31实现文本分类(二)   .sz
- ⭕6-32文本自动摘要的三种方式   .sz
- ⭕7-33文本自动摘要Stuff方式   .sz
- ⭕8-34文本自动摘要MapReduce(一)   .sz
- ⭕9-35文本自动摘要MapReduce(二)   .sz
- ⭕10-36文本自动摘要Refine方式   .sz

