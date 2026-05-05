import gradio as gr

def greet(name):
    """一个简单的打招呼函数"""
    return f"你好，{name}！欢迎使用 Gradio！"

# 创建界面
demo = gr.Interface(
    fn=greet,           # 要执行的函数
    inputs="text",      # 输入组件类型
    outputs="text",     # 输出组件类型
    title="Gradio 入门示例",
    description="这是一个简单的打招呼应用"
)

# 启动应用
demo.launch()