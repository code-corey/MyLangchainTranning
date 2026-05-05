import gradio as gr
import numpy as np
import librosa
import soundfile as sf
import tempfile


def process_audio(audio_file):
    """处理上传的音频文件"""
    # 读取音频
    y, sr = librosa.load(audio_file, sr=None)

    # 计算音频特征
    duration = len(y) / sr
    rms = np.sqrt(np.mean(y ** 2))

    # 生成简单的音频效果：加速
    y_fast = librosa.effects.time_stretch(y, rate=0.8)

    # 保存处理后的音频
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmpfile:
        sf.write(tmpfile.name, y_fast, sr)
        output_path = tmpfile.name

    # 生成报告
    report = f"""
    📊 音频信息:
    - 采样率: {sr} Hz
    - 时长: {duration:.2f} 秒
    - 均方根能量: {rms:.4f}

    🎵 分析结果:
    - 音量: {'较大' if rms > 0.1 else '适中' if rms > 0.05 else '较小'}
    - 时长: {'长' if duration > 30 else '适中' if duration > 10 else '短'}
    """

    return report, output_path


with gr.Blocks() as demo:
    gr.Markdown("# 🎵 音频分析工具")

    with gr.Row():
        with gr.Column():
            audio_input = gr.Audio(type="filepath", label="上传音频")
            process_btn = gr.Button("分析并处理")
        with gr.Column():
            report_output = gr.Textbox(label="分析报告", lines=8)
            audio_output = gr.Audio(label="处理后的音频")

    process_btn.click(
        process_audio,
        inputs=audio_input,
        outputs=[report_output, audio_output]
    )

demo.launch()