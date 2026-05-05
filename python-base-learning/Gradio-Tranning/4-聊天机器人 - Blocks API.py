import gradio as gr
import random
import time

# 简单的回复库
responses = {
    "你好": ["你好！很高兴见到你", "嗨！有什么可以帮你的吗？"],
    "天气": ["今天天气不错", "听说要下雨了"],
    "名字": ["我叫ChatBot", "我是Gradio助手"],
    "再见": ["再见！期待下次聊天", "拜拜！"]
}


def respond(message, history):
    """聊天机器人的响应函数"""
    # 模拟打字延迟
    time.sleep(0.5)

    # 匹配关键词
    for key in responses:
        if key in message:
            return random.choice(responses[key])

    return f"你说：'{message}'，我不太理解，换个说法试试？"


# 使用Blocks API创建聊天界面
with gr.Blocks() as demo:
    gr.Markdown("# 🤖 简单聊天机器人")
    gr.Markdown("试试问：你好、天气、名字、再见")

    chatbot = gr.Chatbot()
    msg = gr.Textbox(label="输入消息")
    clear = gr.Button("清空对话")


    def respond_and_update(message, chat_history):
        bot_message = respond(message, chat_history)
        chat_history.append((message, bot_message))
        return "", chat_history


    msg.submit(respond_and_update, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: None, None, chatbot, queue=False)

demo.launch()