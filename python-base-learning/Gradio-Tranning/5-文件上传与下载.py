import gradio as gr
import pandas as pd
import io


def process_csv(file):
    """处理上传的CSV文件"""
    # 读取CSV
    df = pd.read_csv(file.name)

    # 展示基本信息
    info = f"总行数: {len(df)}\n总列数: {len(df.columns)}\n列名: {', '.join(df.columns)}"

    # 展示前5行
    preview = df.head().to_string()

    # 简单统计分析
    stats = df.describe().to_string()

    # 输出结果
    output = f"📊 数据概况:\n{info}\n\n📝 数据预览:\n{preview}\n\n📈 统计信息:\n{stats}"

    # 返回处理结果和原始数据（供下载）
    return output, df


# 创建界面
with gr.Blocks() as demo:
    gr.Markdown("# 📁 CSV文件分析工具")

    with gr.Row():
        with gr.Column():
            file_input = gr.File(label="上传CSV文件", file_types=[".csv"])
            submit_btn = gr.Button("开始分析")
        with gr.Column():
            output_text = gr.Textbox(label="分析结果", lines=15)

    submit_btn.click(
        process_csv,
        inputs=file_input,
        outputs=output_text
    )

    gr.Markdown("### 示例数据")
    gr.Examples(
        examples=[["sample_data.csv"]],
        inputs=file_input
    )

demo.launch()