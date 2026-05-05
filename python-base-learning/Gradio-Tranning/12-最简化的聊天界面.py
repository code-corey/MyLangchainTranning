import gradio as gr


def respond(message, history):
    """带历史记录的响应函数"""
    # 生成回复
    bot_message = f"🤖 你说：{message}\n\n这是自动回复！"

    # 更新历史（元组格式）
    history = history or []
    history.append((message, bot_message))

    return "", history


# 创建界面
with gr.Blocks(title="聊天机器人", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 💬 AI 聊天助手

    这是一个简单的聊天机器人演示
    """)

    # 聊天组件（老版本）
    chatbot = gr.Chatbot(label="对话记录", height=400)

    with gr.Row():
        msg = gr.Textbox(
            label="输入消息",
            placeholder="在这里输入你的问题...",
            scale=8,
            lines=2
        )
        send_btn = gr.Button("发送", variant="primary", scale=1)

    with gr.Row():
        clear_btn = gr.Button("清空对话", variant="secondary")
        example_btn = gr.Button("示例问题", variant="secondary")

    # 发送消息
    send_btn.click(respond, [msg, chatbot], [msg, chatbot])
    msg.submit(respond, [msg, chatbot], [msg, chatbot])

    # 清空对话
    clear_btn.click(lambda: [], None, chatbot)

    # 示例问题
    example_btn.click(lambda: "你好，请介绍一下自己", None, msg)

demo.launch(server_name="127.0.0.1", server_port=7860)