from openai import OpenAI

# 初始化客户端（指向你的本地服务）
client = OpenAI(
    base_url="http://192.168.13.23:8842/v1",  # 注意：不要包含 /chat/completions
    api_key="ollama",  # 本地服务不需要真实API key，随便填
)

# 模型名称
MODEL_NAME = "Qwen3.5-27B-Q8_0.gguf"


def ask_qwen(prompt, system_prompt=None, temperature=0.7, max_tokens=2000, stream=False):
    """
    向千问27B模型提问

    Args:
        prompt: 用户问题
        system_prompt: 系统提示词（可选）
        temperature: 温度参数（0-2，越高越有创意）
        max_tokens: 最大生成token数
        stream: 是否流式输出

    Returns:
        如果stream=False，返回完整回答字符串
        如果stream=True，直接打印输出
    """

    # 构造消息列表
    messages = []
    if system_prompt:
        messages.append({
            "role": "system",
            "content": system_prompt
        })

    messages.append({
        "role": "user",
        "content": prompt
    })

    try:
        # 调用API
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream
        )

        if stream:
            # 流式输出，实时打印
            full_response = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    full_response += content
            print()  # 最后换行
            return full_response
        else:
            # 非流式，直接返回
            return response.choices[0].message.content

    except Exception as e:
        return f"❌ 出错了：{str(e)}"


def chat_session():
    """交互式对话系统（支持多轮对话）"""
    print("🤖 千问27B 问答系统已启动")
    print("=" * 60)
    print(f"📡 API地址: http://192.168.13.23:8842")
    print(f"🧠 模型: {MODEL_NAME}")
    print("💡 提示: 输入 'exit' 退出，输入 'clear' 清空历史，输入 'system' 修改系统提示词")
    print("=" * 60)

    # 默认系统提示词
    system_prompt = "你是一个专业的AI助手，回答要准确、详细、有条理。"

    # 保存对话历史
    messages = [
        {"role": "system", "content": system_prompt}
    ]

    while True:
        user_input = input("\n👤 你: ").strip()

        if user_input.lower() == 'exit':
            print("👋 再见！")
            break
        elif user_input.lower() == 'clear':
            # 清空历史，但保留系统提示词
            messages = [{"role": "system", "content": system_prompt}]
            print("✨ 对话历史已清空")
            continue
        elif user_input.lower() == 'system':
            print(f"当前系统提示词: {system_prompt}")
            new_prompt = input("请输入新的系统提示词 (直接回车保持不变): ").strip()
            if new_prompt:
                system_prompt = new_prompt
                messages[0] = {"role": "system", "content": system_prompt}
                print("✅ 系统提示词已更新")
            continue
        elif not user_input:
            continue

        # 添加用户消息
        messages.append({"role": "user", "content": user_input})

        # 调用模型
        print("🤖 AI: ", end="")
        try:
            # 流式输出
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
                stream=True
            )

            full_response = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    full_response += content
            print()  # 换行

            # 保存助手回复到历史
            messages.append({"role": "assistant", "content": full_response})

            # 可选：限制历史长度，避免token过多
            # 保留最近20轮对话（40条消息）+ 系统提示词
            if len(messages) > 41:  # 1个system + 40条消息(20轮对话)
                # 保留系统提示词和最近40条消息
                messages = [messages[0]] + messages[-40:]

        except Exception as e:
            print(f"\n❌ 出错: {e}")
            # 出错时移除刚才添加的用户消息，避免破坏历史
            messages.pop()


def quick_test():
    """快速测试（单次问答）"""
    print("🧪 快速测试模式")
    print("=" * 50)

    # 测试出师表
    question = "出师表默写一下"
    print(f"👤 问题: {question}")
    print("🤖 回答: ", end="")

    answer = ask_qwen(
        prompt=question,
        system_prompt="你是一个精通中国古典文学的专家，背诵古文要准确完整。",
        temperature=0.3,  # 降低温度，让回答更准确
        stream=True
    )

    print("\n" + "=" * 50)

    # 可以继续测试其他问题
    question2 = "请解释一下《出师表》的创作背景"
    print(f"\n👤 问题: {question2}")
    print("🤖 回答: ", end="")

    answer2 = ask_qwen(
        prompt=question2,
        system_prompt="你是一个精通中国古典文学的专家，解释要清晰透彻。",
        temperature=0.5,
        stream=True
    )


def batch_questions():
    """批量问答（非交互式）"""
    questions = [
        "出师表默写一下",
        "《出师表》的作者是谁？",
        "请概括《出师表》的主要内容"
    ]

    print("📚 批量问答模式")
    print("=" * 60)

    for i, q in enumerate(questions, 1):
        print(f"\n【问题{i}】{q}")
        print("【回答】", end="")

        answer = ask_qwen(
            prompt=q,
            system_prompt="回答要简洁准确。",
            temperature=0.3,
            stream=True
        )
        print("-" * 60)


if __name__ == "__main__":
    # 选择运行模式

    # 模式1：交互式对话（推荐日常使用）
    chat_session()

    # 模式2：快速测试（测试单个问题）
    # quick_test()

    # 模式3：批量问答（处理多个预设问题）
    # batch_questions()