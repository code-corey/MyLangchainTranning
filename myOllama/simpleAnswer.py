from openai import OpenAI

# 配置
client = OpenAI(
    base_url="http://192.168.13.23:8842/v1",
    api_key="ollama"
)

# 简单问答函数
def ask(question):
    response = client.chat.completions.create(
        model="Qwen3.5-27B-Q8_0.gguf",
        messages=[{"role": "user", "content": question}],
        stream=False
    )
    return response.choices[0].message.content

# 使用示例
answer = ask("出师表默写一下")
print(answer)