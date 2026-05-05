import gradio as gr
import numpy as np
from PIL import Image


def process_image(image, intensity, operation):
    """
    处理上传的图片
    image: PIL Image 对象
    intensity: 处理强度 (0-100的滑块)
    operation: 操作类型 (下拉选择)
    """
    # 转换为numpy数组
    img_array = np.array(image)

    if operation == "提亮":
        # 增加亮度
        result = img_array * (1 + intensity / 100)
    elif operation == "变暗":
        # 降低亮度
        result = img_array * (1 - intensity / 100)
    elif operation == "灰度":
        # 灰度处理
        result = np.mean(img_array, axis=2)
        result = np.stack([result] * 3, axis=2)
    else:
        result = img_array

    # 裁剪到0-255范围
    result = np.clip(result, 0, 255).astype(np.uint8)
    return Image.fromarray(result)


# 创建复杂界面
demo = gr.Interface(
    fn=process_image,
    inputs=[
        gr.Image(type="pil", label="上传图片"),
        gr.Slider(0, 100, value=50, label="处理强度"),
        gr.Dropdown(["提亮", "变暗", "灰度"], label="操作类型")
    ],
    outputs=gr.Image(label="处理结果"),
    title="图片处理工具",
    description="上传图片，调整参数，实时预览处理效果"
)

demo.launch()