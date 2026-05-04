这段代码展示了如何使用 **LangChain** 框架构建一个能够调用外部工具（Tool Calling）的智能体（Agent）。

简单来说，它配置了一个大模型（Qwen/通义千问），并赋予了它“查询天气”的能力。当用户提问时，模型不再是瞎编，而是会主动调用你定义的函数。

---

### 核心步骤解析

#### 1. 定义工具 (Tools)
```python
def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"
```
* 这里定义了一个简单的 Python 函数。
* **关键点**：函数下方的**文档字符串（Docstring）**非常重要。LangChain 会把这个描述发送给大模型，模型通过阅读描述来决定什么时候该调用这个函数。

#### 2. 初始化大模型 (LLM)
```python
llm = ChatOpenAI(
    model="qwen3-vl-flash-2026-01-22",
    api_key=os.environ.get("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)
```
* 虽然使用的是 `ChatOpenAI` 类，但由于修改了 `base_url`，它实际上是在调用 **阿里云百炼（DashScope）** 提供的模型。
* 这里指定了模型版本，并从环境变量中读取 API Key 进行鉴权。

#### 3. 创建智能体 (Agent)
```python
agent = create_agent(
    model=llm,
    tools=[get_weather],
    system_prompt="You are a helpful assistant",
)
```
* `create_agent` 是一个高级封装，它将 **模型**、**工具集** 和 **系统提示词** 绑定在一起。
* 它告诉模型：“你现在不仅可以聊天，如果你觉得有必要，还可以调用 `get_weather` 这个列表里的工具。”

#### 4. 执行与逻辑流
```python
agent.invoke({"messages": [{"role": "user", "content": "what is the weather in sf"}]})
```
当你运行这段代码时，后台发生了以下对话：
1.  **用户**：“旧金山（SF）天气怎么样？”
2.  **模型判断**：发现自己不知道实时天气，但看到有个 `get_weather` 工具。
3.  **模型动作**：输出一个特殊的指令，要求调用 `get_weather(city="sf")`。
4.  **程序执行**：LangChain 拦截到指令，自动运行 Python 函数，得到结果 `"It's always sunny in sf!"`。
5.  **最终回复**：模型根据工具返回的结果，整理成自然语言回复用户。

---

### 💡 注意事项
1.  **版本匹配**：`create_agent` 并不是 LangChain 核心库中最标准的函数名（通常是 `create_tool_calling_agent` 或使用 `langgraph`）。这段代码看起来像是使用了某些特定简化版封装或较新的实验性 API。
2.  **环境要求**：运行前必须在系统中设置 `DASHSCOPE_API_KEY` 环境变量，否则会报错。
3.  **模型能力**：代码中使用了 `qwen3` 这种 2026 年的模型标识（根据你的代码上下文），这表明你正在使用非常前沿或自定义的 API 节点。

```json
{
  "messages": [
    {
      "type": "HumanMessage",
      "content": "what is the weather in sf",
      "additional_kwargs": {},
      "response_metadata": {},
      "id": "ae7f1d9f-699f-4840-beaa-febcd97b833e"
    },
    {
      "type": "AIMessage",
      "content": "",
      "additional_kwargs": {
        "refusal": null
      },
      "response_metadata": {
        "token_usage": {
          "completion_tokens": 123,
          "prompt_tokens": 280,
          "total_tokens": 403,
          "completion_tokens_details": {
            "accepted_prediction_tokens": null,
            "audio_tokens": null,
            "reasoning_tokens": 92,
            "rejected_prediction_tokens": null,
            "text_tokens": 123
          },
          "prompt_tokens_details": {
            "audio_tokens": null,
            "cached_tokens": null,
            "text_tokens": 280
          }
        },
        "model_provider": "openai",
        "model_name": "qwen3.5-flash",
        "system_fingerprint": null,
        "id": "chatcmpl-bc460c9b-9950-994a-ad18-64a30416ad21",
        "finish_reason": "tool_calls",
        "logprobs": null
      },
      "id": "lc_run--019deaf5-8167-7ea3-9d9d-7da6355bae54-0",
      "tool_calls": [
        {
          "name": "get_weather",
          "args": {
            "city": "San Francisco"
          },
          "id": "call_63f17a38bd5a47debc168dba",
          "type": "tool_call"
        }
      ],
      "invalid_tool_calls": [],
      "usage_metadata": {
        "input_tokens": 280,
        "output_tokens": 123,
        "total_tokens": 403,
        "input_token_details": {},
        "output_token_details": {
          "reasoning": 92
        }
      }
    },
    {
      "type": "ToolMessage",
      "content": "It's always sunny in San Francisco!",
      "name": "get_weather",
      "id": "c7ede768-330b-4f26-b2df-18e47dd15681",
      "tool_call_id": "call_63f17a38bd5a47debc168dba"
    },
    {
      "type": "AIMessage",
      "content": "According to the forecast, it's sunny in San Francisco! ☀️",
      "additional_kwargs": {
        "refusal": null
      },
      "response_metadata": {
         // Token 使用统计
        "token_usage": {
          "completion_tokens": 19, # 输出（AI 的回答）消耗的 token 数
          "prompt_tokens": 332, #输入（用户问题 + 历史 + 工具返回）消耗的 token 数
          "total_tokens": 351, 
          "completion_tokens_details": {
            "accepted_prediction_tokens": null, # 未使用（推测解码相关）
            "audio_tokens": null, # 未使用（语音相关）
            "reasoning_tokens": 0, # 推理 token 数。为 0 表示这次回答没有内部推理过程  说明这次回答是直接生成的，没有像 DeepSeek-R1 那样的"思考链"过
            "rejected_prediction_tokens": null, # 未使用
            "text_tokens": 19 # 实际文本输出的 token 数
          },
          "prompt_tokens_details": {
            "audio_tokens": null,
            "cached_tokens": null, --> 未命中缓存（如果有缓存可以降低成本）
            "text_tokens": 332 --> 所有文本输入（对话历史 + 系统提示 + 工具返回）的 token 数
          }
        },
        "model_provider": "openai",
        "model_name": "qwen3.5-flash",
        "system_fingerprint": null,
        "id": "chatcmpl-ffa5aece-5a79-957f-837a-e9dcc38536e7", # 这次 API 调用的唯一 ID，用于追踪和调试
        "finish_reason": "stop",
        "logprobs": null  # 没有开启 logprobs（否则会返回每个 token 的 log 概率）
      },
      "id": "lc_run--019deaf5-8acb-7611-b502-e73b114f1660-0",
      "tool_calls": [],
      "invalid_tool_calls": [],
      "usage_metadata": {
        "input_tokens": 332,
        "output_tokens": 19,
        "total_tokens": 351,
        "input_token_details": {},
        "output_token_details": {
          "reasoning": 0
        }
      }
    }
  ]
}

```

当前的对话理解
``` 
用户：旧金山天气怎么样？
  ↓
AI：调用 get_weather 工具（用了 92 个推理 token）
  ↓
工具：It's always sunny in San Francisco!
  ↓
AI 最终回答：According to the forecast, it's sunny in San Francisco! ☀️
```