import gradio as gr
import numpy as np
from PIL import Image


class ImageProcessor:
    """维护处理的状态"""

    def __init__(self):
        self.current_image = None
        self.history = []

    def load_image(self, image):
        self.current_image = image
        self.history.append({"action": "加载", "step": len(self.history) + 1})
        return self.get_status(), image

    def apply_filter(self, filter_type):
        if self.current_image is None:
            return "请先加载图片", None

        img_array = np.array(self.current_image)

        if filter_type == "灰度":
            result = np.mean(img_array, axis=2)
            result = np.stack([result] * 3, axis=2)
        elif filter_type == "边缘检测":
            # 简化的边缘检测
            result = img_array - np.roll(img_array, 1, axis=0)
            result = result - np.roll(result, 1, axis=1)
        else:  # 原图
            result = img_array

        result = np.clip(result, 0, 255).astype(np.uint8)
        self.current_image = Image.fromarray(result)
        self.history.append({"action": f"应用{filter_type}", "step": len(self.history) + 1})

        return self.get_status(), self.current_image

    def reset(self):
        self.current_image = None
        self.history = []
        return "状态已重置", None

    def get_status(self):
        if self.current_image is None:
            return "状态: 无图片"
        return f"状态: 已加载图片\n历史步骤: {len(self.history)}"


processor = ImageProcessor()

with gr.Blocks() as demo:
    gr.Markdown("# 🔄 图片处理工作流")

    status = gr.Textbox(label="状态", lines=3)

    with gr.Row():
        with gr.Column():
            image_input = gr.Image(type="pil", label="输入图片")
            load_btn = gr.Button("1. 加载图片")
        with gr.Column():
            output_image = gr.Image(label="当前图片")

    with gr.Row():
        filter_choices = gr.Radio(["原图", "灰度", "边缘检测"], label="2. 选择滤镜")
        apply_btn = gr.Button("应用滤镜")

    reset_btn = gr.Button("重置所有")

    load_btn.click(processor.load_image, inputs=image_input, outputs=[status, output_image])
    apply_btn.click(processor.apply_filter, inputs=filter_choices, outputs=[status, output_image])
    reset_btn.click(processor.reset, outputs=[status, output_image])

demo.launch()