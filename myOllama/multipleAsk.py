from openai import OpenAI

client = OpenAI(
    base_url="http://192.168.13.23:8842/v1",
    api_key="ollama"
)

# 维护对话历史
conversation = [
    {"role": "system", "content": "你是一个古文专家，擅长背诵和解释古文。"}
]

while True:
    user_input = input("你: ")
    if user_input == "exit":
        break

    conversation.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="Qwen3.5-27B-Q8_0.gguf",
        messages=conversation,
        stream=True  # 开启流式输出，体验更好
    )

    print("AI: ", end="")
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            print(content, end="", flush=True)
            full_response += content
    print()

    conversation.append({"role": "assistant", "content": full_response})