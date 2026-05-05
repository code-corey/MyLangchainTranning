import gradio as gr
import numpy as np
from PIL import Image
import random


def analyze_image_and_text(image, text):
    """分析图片和文本的联合输入"""

    # 模拟图片识别
    objects = ["猫", "狗", "车", "房子", "树", "人"]
    detected = random.sample(objects, random.randint(1, 3))

    # 模拟情感分析
    emotions = ["积极", "中性", "消极"]
    sentiment = random.choice(emotions)

    # 生成描述
    description = f"""
    🖼️ 图片分析结果:
    - 检测到的物体: {', '.join(detected)}
    - 图片主题: {random.choice(['自然风景', '城市建筑', '人物肖像', '动物'])}

    💬 文本分析结果:
    - 你的输入: "{text}"
    - 情感倾向: {sentiment}
    - 文本长度: {len(text)} 个字

    🔗 综合判断:
    - 图片和文本{random.choice(['高度相关', '部分相关', '不太相关'])}
    """

    return description


# 创建多模态界面
with gr.Blocks() as demo:
    gr.Markdown("# 🖼️+💬 多模态分析")

    with gr.Row():
        with gr.Column():
            image_input = gr.Image(type="pil", label="上传图片")
            text_input = gr.Textbox(label="请输入相关描述", placeholder="描述你看到的图片...")
            analyze_btn = gr.Button("开始分析")
        with gr.Column():
            output = gr.Textbox(label="分析结果", lines=12)

    analyze_btn.click(
        analyze_image_and_text,
        inputs=[image_input, text_input],
        outputs=output
    )

demo.launch()