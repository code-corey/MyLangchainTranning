import gradio as gr
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


def update_plot(chart_type, point_count, noise_level):
    """根据参数更新图表"""
    np.random.seed(42)

    # 生成数据
    x = np.linspace(0, 10, point_count)
    y = np.sin(x) + np.random.normal(0, noise_level, point_count)

    df = pd.DataFrame({'X': x, 'Y': y})

    # 根据图表类型创建不同图表
    if chart_type == "散点图":
        fig = px.scatter(df, x='X', y='Y', title='散点图',
                         labels={'X': 'X轴', 'Y': 'Y轴'})
    elif chart_type == "折线图":
        fig = px.line(df, x='X', y='Y', title='折线图')
    elif chart_type == "柱状图":
        # 对数据进行分组
        df['Binned'] = pd.cut(df['X'], bins=10).astype(str)
        grouped = df.groupby('Binned')['Y'].mean().reset_index()
        fig = px.bar(grouped, x='Binned', y='Y', title='柱状图')
    else:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=y, mode='markers', name='数据'))
        fig.add_trace(go.Scatter(x=x, y=np.sin(x), mode='lines', name='理论曲线'))
        fig.update_layout(title='数据对比')

    return fig


with gr.Blocks() as demo:
    gr.Markdown("# 📊 交互式数据可视化")

    with gr.Row():
        chart_type = gr.Dropdown(["散点图", "折线图", "柱状图", "对比图"],
                                 label="图表类型", value="散点图")
        point_count = gr.Slider(10, 200, value=50, step=10, label="数据点数量")
        noise_level = gr.Slider(0, 1, value=0.2, step=0.05, label="噪声水平")

    plot_output = gr.Plot(label="可视化结果")

    # 实时更新
    chart_type.change(update_plot, [chart_type, point_count, noise_level], plot_output)
    point_count.change(update_plot, [chart_type, point_count, noise_level], plot_output)
    noise_level.change(update_plot, [chart_type, point_count, noise_level], plot_output)

demo.launch()