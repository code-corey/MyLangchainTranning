import gradio as gr
import time


# ========== 模拟的 AI 响应函数 ==========
def mock_ai_response(history, prompt, max_length, top_p, temperature):
    """
    模拟 AI 生成回复
    """
    if not history:
        return history

    # 获取用户最后一条消息（兼容多种格式）
    try:
        if isinstance(history[-1], dict):
            user_message = history[-1].get("content", "")
        elif isinstance(history[-1], (list, tuple)):
            user_message = history[-1][0] if len(history[-1]) > 0 else ""
        else:
            user_message = str(history[-1])
    except:
        user_message = ""

    # 模拟思考过程
    for i in range(3):
        time.sleep(0.3)

        mock_response = f"🤖 我收到了你的消息：'{user_message}'\n\n"
        mock_response += f"📝 当前参数设置：\n"
        mock_response += f"- 最大长度: {max_length}\n"
        mock_response += f"- Top P: {top_p}\n"
        mock_response += f"- Temperature: {temperature}\n\n"
        mock_response += f"✨ 这是模拟回复（第{i + 1}秒）..."

        # 更新历史（兼容多种格式）
        try:
            if isinstance(history[-1], dict):
                history[-1]["content"] = mock_response
            elif isinstance(history[-1], list):
                if len(history[-1]) > 1:
                    history[-1][1] = mock_response
                else:
                    history[-1].append(mock_response)
            elif isinstance(history[-1], tuple):
                history[-1] = (history[-1][0], mock_response)
        except:
            pass

        yield history
        time.sleep(0.5)

    # 最终回复
    final_response = f"🤖 完成！\n\n"
    final_response += f"你的问题：{user_message}\n\n"
    final_response += f"💡 提示：这是一个模拟的聊天机器人\n"
    final_response += f"1. 调整右侧参数体验不同效果\n"
    final_response += f"2. 点击「提示词设置」设置系统提示词\n"
    final_response += f"3. 点击「清除聊天记录」重新开始"

    try:
        if isinstance(history[-1], dict):
            history[-1]["content"] = final_response
        elif isinstance(history[-1], list):
            if len(history[-1]) > 1:
                history[-1][1] = final_response
            else:
                history[-1].append(final_response)
        elif isinstance(history[-1], tuple):
            history[-1] = (history[-1][0], final_response)
    except:
        pass

    yield history


# ========== 辅助函数 ==========
def parse_text(text):
    """处理文本中的特殊字符"""
    if not text:
        return text

    html_escape_table = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
    }
    for char, escape in html_escape_table.items():
        text = text.replace(char, escape)
    return text


# ========== Gradio 界面构建 ==========
def build_chat_interface():
    """构建聊天界面（通用兼容版）"""
    # 不使用 theme 参数（移到 launch）
    with gr.Blocks(title="AI 聊天助手") as demo:
        # 标题
        gr.HTML("""
        <h1 align="center" style="font-size: 2em; margin-bottom: 0;">
            🤖 AI 智能聊天助手
        </h1>
        <p align="center" style="color: #666; margin-top: 0;">
            基于 Gradio 构建的对话界面 | 支持参数调节
        </p>
        """)

        # 主布局：两列
        with gr.Row():
            # 左侧：聊天区域
            with gr.Column(scale=3):
                # 移除所有新参数，只保留最基础的
                chatbot = gr.Chatbot(label="对话记录")

                # 输入区域
                with gr.Row():
                    user_input = gr.Textbox(
                        show_label=False,
                        placeholder="💬 在这里输入你的问题...",
                        lines=3,
                        scale=8
                    )
                    submit_btn = gr.Button("📤 发送", variant="primary", scale=1)

            # 右侧：控制面板
            with gr.Column(scale=1):
                # 系统提示词设置
                with gr.Group():
                    gr.Markdown("### ⚙️ 系统设置")
                    prompt_input = gr.Textbox(
                        label="系统提示词",
                        placeholder="设置 AI 的角色和行为...",
                        lines=3,
                        value="你是一个友好的AI助手"
                    )
                    set_prompt_btn = gr.Button("🔧 应用提示词", size="sm")

                # 参数调节
                with gr.Group():
                    gr.Markdown("### 🎛️ 生成参数")
                    max_length = gr.Slider(
                        0, 4096, value=2048, step=1,
                        label="📏 最大长度"
                    )
                    top_p = gr.Slider(
                        0, 1, value=0.9, step=0.01,
                        label="🎯 Top P"
                    )
                    temperature = gr.Slider(
                        0.01, 1.5, value=0.7, step=0.01,
                        label="🌡️ Temperature"
                    )

                # 其他操作
                with gr.Group():
                    gr.Markdown("### 🛠️ 其他操作")
                    clear_btn = gr.Button("🗑️ 清除聊天记录", variant="secondary", size="sm")

        # ========== 事件绑定 ==========

        # 发送消息的处理函数
        def user_question(query, history):
            """用户发送消息时的处理"""
            if not query or not query.strip():
                return "", history

            if history is None:
                history = []

            # 添加用户消息（使用元组格式，最通用）
            history.append((parse_text(query), ""))
            return "", history

        # 设置提示词
        def set_prompt_message(prompt_text, history):
            """设置提示词并显示提示"""
            if history is None:
                history = []
            if prompt_text and prompt_text.strip():
                history.append((f"📌 系统提示已更新为: {prompt_text}", "收到！我已经记住了新的提示词"))
            return history

        # 清除历史
        def clear_history():
            """清除所有聊天记录"""
            return [], ""

        # 绑定事件
        submit_btn.click(
            user_question,
            inputs=[user_input, chatbot],
            outputs=[user_input, chatbot],
            queue=False
        ).then(
            mock_ai_response,
            inputs=[chatbot, prompt_input, max_length, top_p, temperature],
            outputs=chatbot
        )

        # 回车键也触发发送
        user_input.submit(
            user_question,
            inputs=[user_input, chatbot],
            outputs=[user_input, chatbot],
            queue=False
        ).then(
            mock_ai_response,
            inputs=[chatbot, prompt_input, max_length, top_p, temperature],
            outputs=chatbot
        )

        # 设置提示词
        set_prompt_btn.click(
            set_prompt_message,
            inputs=[prompt_input, chatbot],
            outputs=chatbot
        )

        # 清除聊天记录
        clear_btn.click(
            clear_history,
            outputs=[chatbot, user_input]
        )

    return demo


# ========== 启动应用 ==========
if __name__ == "__main__":
    demo = build_chat_interface()

    demo.queue()

    # 主题移到 launch 中
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=True,
        inbrowser=True
    )