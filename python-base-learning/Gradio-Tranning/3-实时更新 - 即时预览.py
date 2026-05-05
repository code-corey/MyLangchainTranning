import gradio as gr


def calculate_bmi(height, weight):
    """计算BMI指数"""
    if height <= 0 or weight <= 0:
        return "请输入有效数值"

    bmi = weight / ((height / 100) ** 2)

    if bmi < 18.5:
        category = "偏瘦"
        color = "🟡"
    elif bmi < 24:
        category = "正常"
        color = "🟢"
    elif bmi < 28:
        category = "偏胖"
        color = "🟠"
    else:
        category = "肥胖"
        color = "🔴"

    return f"{color} BMI: {bmi:.1f} - {category} {color}"


# 使用实时更新
demo = gr.Interface(
    fn=calculate_bmi,
    inputs=[
        gr.Number(label="身高 (cm)", value=170),
        gr.Number(label="体重 (kg)", value=65)
    ],
    outputs=gr.Textbox(label="BMI结果", lines=3),
    title="BMI计算器",
    description="输入身高和体重，实时计算BMI指数",
    live=True  # 实时更新，不需要点击提交按钮
)

demo.launch()