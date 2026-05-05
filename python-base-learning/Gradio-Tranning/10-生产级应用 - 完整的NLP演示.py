import gradio as gr
import numpy as np
from sentence_transformers import SentenceTransformer

# 加载模型（可以是微调后的模型）
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')


def compute_similarity(sentence1, sentence2):
    """计算两个句子的相似度"""
    if not sentence1 or not sentence2:
        return 0.0, "请输入两个句子"

    embeddings = model.encode([sentence1, sentence2])
    similarity = np.dot(embeddings[0], embeddings[1]) / (
            np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
    )

    # 生成分析报告
    if similarity > 0.8:
        level = "非常相似"
        color = "🟢"
    elif similarity > 0.6:
        level = "相似"
        color = "🟡"
    elif similarity > 0.4:
        level = "中等相关"
        color = "🟠"
    else:
        level = "不相似"
        color = "🔴"

    report = f"""
    {color} 相似度分析结果 {color}

    📊 相似度分数: {similarity:.3f}
    📝 判断: {level}

    建议:
    - 相似度 > 0.8: 两句话意思很接近
    - 0.6-0.8: 有一定关联
    - < 0.6: 意思不同
    """

    return similarity, report


def batch_similarity(sentences):
    """批量计算句子相似度矩阵"""
    embeddings = model.encode(sentences)
    n = len(sentences)
    matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            matrix[i, j] = np.dot(embeddings[i], embeddings[j]) / (
                    np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j])
            )
    return matrix


# 创建完整应用
with gr.Blocks(title="句子相似度分析工具", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🔍 句子相似度分析工具

    基于 Sentence Transformers 的语义相似度计算工具
    """)

    with gr.Tab("单对比较"):
        with gr.Row():
            with gr.Column():
                sent1 = gr.Textbox(label="句子1", placeholder="请输入第一个句子...", lines=3)
                sent2 = gr.Textbox(label="句子2", placeholder="请输入第二个句子...", lines=3)
                compare_btn = gr.Button("计算相似度", variant="primary")
            with gr.Column():
                similarity_score = gr.Number(label="相似度分数", precision=3)
                analysis_result = gr.Markdown(label="分析结果")

    with gr.Tab("批量比较"):
        with gr.Row():
            with gr.Column():
                batch_input = gr.Textbox(
                    label="输入多个句子（每行一个）",
                    placeholder="句子1\n句子2\n句子3",
                    lines=10
                )
                batch_btn = gr.Button("批量分析")
            with gr.Column():
                batch_output = gr.Dataframe(label="相似度矩阵", headers=None)

    with gr.Tab("示例"):
        gr.Markdown("""
        ### 📝 示例句子对

        点击以下示例进行测试：
        """)

        examples = [
            ["今天天气很好", "今天天气不错"],
            ["我喜欢吃苹果", "苹果很好吃"],
            ["机器学习很有趣", "今天下雨了"],
            ["Python是一门编程语言", "Java也是编程语言"],
            ["我要去北京旅游", "北京是中国的首都"]
        ]

        for ex in examples:
            gr.Examples(
                examples=[[ex[0], ex[1]]],
                inputs=[sent1, sent2],
                outputs=[similarity_score, analysis_result],
                fn=compute_similarity,
                cache_examples=False
            )

    # 绑定函数
    compare_btn.click(
        compute_similarity,
        inputs=[sent1, sent2],
        outputs=[similarity_score, analysis_result]
    )

    batch_btn.click(
        batch_similarity,
        inputs=batch_input,
        outputs=batch_output
    )

if __name__ == "__main__":
    # 启动应用
    demo.launch(
        server_name="0.0.0.0",  # 允许外部访问
        server_port=7860,  # 端口号
        share=True,  # 生成公共链接
        debug=False  # 生产模式
    )