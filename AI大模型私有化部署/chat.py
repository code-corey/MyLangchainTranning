# 导入必要的库和模块
import os
from pathlib import Path
from threading import Thread
from typing import Union

import gradio as gr
import torch
# from peft import AutoPeftModelForCausalLM, PeftModelForCausalLM
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    PreTrainedModel,
    PreTrainedTokenizer,
    PreTrainedTokenizerFast,
    StoppingCriteria,
    StoppingCriteriaList,
    TextIteratorStreamer
)

"""
========================================
AutoModelForCausalLM
========================================

作用：自动识别并加载适合因果语言建模的模型
因果语言模型：根据前面的token预测下一个token（自回归生成）
典型模型：GPT、LLaMA、GLM、Qwen 等

# 使用示例
model = AutoModelForCausalLM.from_pretrained("gpt2")
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b")
model = AutoModelForCausalLM.from_pretrained("ZhipuAI/glm-4-9b-chat")

========================================
AutoTokenizer
========================================
作用：自动识别并加载与模型匹配的分词器
分词器功能：将文本转换为模型能理解的 token ID 序列

# 使用示例
tokenizer = AutoTokenizer.from_pretrained("gpt2")
# 文本转token
text = "Hello, how are you?"
tokens = tokenizer(text)  # {'input_ids': [15496, 11, 703, 389, 345, 30], ...}
# token转文本
text = tokenizer.decode([15496, 11, 703, 389, 345, 30])  # 'Hello, how are you?'


========================================
PreTrainedModel
========================================
作用：所有预训练模型的基类
from_pretrained()：加载预训练权重
save_pretrained()：保存模型
to()：移动到设备（CPU/GPU）
eval()/train()：切换模式

========================================
PreTrainedTokenizer
========================================
作用：所有Python实现的分词器基类
特点：纯Python实现，速度较慢但功能完整
encode()：文本 → token IDs
decode()：token IDs → 文本
batch_encode()：批量编码

# 使用纯Python实现的分词器
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased", use_fast=False)
# use_fast=False 使用 PreTrainedTokenizer


========================================
PreTrainedTokenizerFast
========================================
作用：所有Rust实现的分词器基类
点：底层用Rust实现，速度很快（通常快10-20倍）
功能：与 PreTrainedTokenizer 相同，但性能更好



========================================
StoppingCriteria
========================================
作用：在生成文本时判断是否应该停止
自定义停止逻辑：继承这个类实现自己的停止条件

========================================
StoppingCriteriaList
========================================
作用：管理多个停止条件
逻辑：只要列表中任意一个条件满足，就停止生成
# 创建多个停止条件
criteria1 = StopOnTokens(token_id=2)      # 遇到[EOS]停止
criteria2 = StopOnTokens(token_id=13)     # 遇到句号停止
criteria3 = MaxLengthCriteria(max_length=100)  # 达到100token停止

# 组合成列表
stop_criteria = StoppingCriteriaList([criteria1, criteria2, criteria3])

# 生成时使用
outputs = model.generate(input_ids, stopping_criteria=stop_criteria)




========================================
TextIteratorStreamer
========================================
作用：流式生成文本，逐token输出
特点：
实时输出，不用等待完整生成
配合多线程使用
提升用户体验

# 你的代码中的使用
streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

# 在子线程中生成
t = Thread(target=model.generate, kwargs=generate_kwargs)
t.start()

# 主线程实时获取生成的token
for new_token in streamer:
    print(new_token, end='', flush=True)  # 逐字显示
"""

# 定义模型和分词器的类型别名
# ModelType = Union[PreTrainedModel, PeftModelForCausalLM]
ModelType = PreTrainedModel
# TokenizerType = Union[PreTrainedTokenizer, PreTrainedTokenizerFast]
TokenizerType = PreTrainedTokenizer

# 设置模型和分词器的路径，默认从环境变量获取
MODEL_PATH = os.environ.get('MODEL_PATH', '/root/autodl-tmp/models/ZhipuAI/glm-4-9b-chat')
TOKENIZER_PATH = os.environ.get("TOKENIZER_PATH", MODEL_PATH)


def _resolve_path(path: Union[str, Path]) -> Path:
    """
    解析相对路径并返回绝对路径
    :param path: 输入的路径字符串或Path对象
    :return: 绝对路径的Path对象

    expanduser ：展开用户目录符号~
    # 示例
    Path("~/models").expanduser()
    # 结果：Path("/home/username/models")  （假设用户名是username）

    Path("~/.cache").expanduser()
    # 结果：Path("/home/username/.cache")


    .resolve()  解析路径中的.和.. ,将相对路径转换为绝对路径
    # 示例
    Path("./my_model").resolve()
    # 假设当前在 /home/user/projects
    # 结果：Path("/home/user/projects/my_model")

    Path("../models").resolve()
    # 结果：Path("/home/user/models")  （上一级目录的models）

    Path("models/./test/../final").resolve()
    # 结果：Path("/home/user/projects/models/final")  （规范化路径）

    """

    return Path(path).expanduser().resolve()


def load_model_and_tokenizer(
        model_dir: Union[str, Path], trust_remote_code: bool = True
) -> tuple[ModelType, TokenizerType]:
    model_dir = _resolve_path(model_dir)

    # --- 新增修复代码开始 ---
    import transformers
    from transformers import AutoConfig

    # 修复之前的 max_length 问题
    config = AutoConfig.from_pretrained(model_dir, trust_remote_code=trust_remote_code)
    if not hasattr(config, 'max_length') and hasattr(config, 'seq_length'):
        config.max_length = config.seq_length

    # 修复最新的 all_tied_weights_keys 问题
    # 我们将该属性指向类中现有的 _tied_weights_keys
    from transformers.models.auto.modeling_auto import MODEL_FOR_CAUSAL_LM_MAPPING
    model_class = transformers.AutoModelForCausalLM
    if trust_remote_code:
        # 获取远程代码定义的类
        model_class = transformers.AutoModelForCausalLM.from_config(config, trust_remote_code=True).__class__
        # 强制补丁：如果类里没有 all_tied_weights_keys，就给它一个
        if not hasattr(model_class, "all_tied_weights_keys"):
            model_class.all_tied_weights_keys = property(lambda self: getattr(self, "_tied_weights_keys", []))
            """
            lambda self: getattr(self, "_tied_weights_keys", [])
            lambda => 匿名函数
            self => 类似普通函数的参数
            getattr(对象, "属性名", 默认值)
            
            
            # 等价的标准写法
            property(lambda self: getattr(self, "_tied_weights_keys", []))
            == 
            class MyClass:
                @property
                def all_tied_weights_keys(self):
                    return getattr(self, "_tied_weights_keys", [])
            """

    # --- 新增修复代码结束 ---

    model = AutoModelForCausalLM.from_pretrained(
        model_dir,
        config=config,
        trust_remote_code=trust_remote_code,
        device_map='auto',
        torch_dtype=torch.bfloat16  # 顺便修复 dtype 警告，GLM4 推荐 bfloat16
    )

    tokenizer = AutoTokenizer.from_pretrained(
        model_dir, trust_remote_code=trust_remote_code, use_fast=False
    )
    return model, tokenizer

# 加载模型和分词器实例
model, tokenizer = load_model_and_tokenizer(MODEL_PATH, trust_remote_code=True)


# 定义一个类，用于在生成文本时停止生成
class StopOnTokens(StoppingCriteria):
    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        # 获取模型配置中的结束标记ID
        stop_ids = model.config.eos_token_id
        # 遍历结束标记ID
        for stop_id in stop_ids:
            # 如果当前生成的最后一个token是结束标记，则停止生成
            if input_ids[0][-1] == stop_id:
                return True
        # 如果没有遇到结束标记，则继续生成
        return False


# 定义一个函数，用于解析和格式化输出文本
# 这个函数 parse_text 用于将 Markdown 格式的文本转换为 HTML 格式，特别是处理包含代码块的文本。
def parse_text(text):
    # 按行分割文本
    lines = text.split("\n")
    # 过滤掉空行
    lines = [line for line in lines if line != ""]
    count = 0  # 统计输出文本的行数
    # 遍历每一行文本
    for i, line in enumerate(lines):
        # 检查是否包含代码块标记
        if "```" in line:  # 代码块的起始和结束
            count += 1
            items = line.split('`')
            # 如果是代码块开始，添加HTML标签
            if count % 2 == 1:
                # items[-1] ：计算机语音的标记
                lines[i] = f'<pre><code class="language-{items[-1]}">'
            # 如果是代码块结束，添加HTML标签
            else:
                lines[i] = f'<br></code></pre>'
        else:
            # 如果不是第一行，且在代码块中，对特殊字符进行转义
            if i > 0:
                if count % 2 == 1:
                    line = line.replace("`", "\`")
                    line = line.replace("<", "&lt;")
                    line = line.replace(">", "&gt;")
                    line = line.replace(" ", "&nbsp;")
                    line = line.replace("*", "&ast;")
                    line = line.replace("_", "&lowbar;")
                    line = line.replace("-", "&#45;")
                    line = line.replace(".", "&#46;")
                    line = line.replace("!", "&#33;")
                    line = line.replace("(", "&#40;")
                    line = line.replace(")", "&#41;")
                    line = line.replace("$", "&#36;")
                # 添加换行标签
                lines[i] = "<br>" + line
    # 将处理后的文本行合并
    text = "".join(lines)
    # 返回格式化后的文本
    return text


# 定义一个函数，用于生成聊天文本
def predict(history, prompt, max_length, top_p, temperature):
    # 创建一个停止条件实例
    stop = StopOnTokens()
    # 初始化消息列表
    messages = []
    # 如果提供了提示词，将其添加到消息列表中
    if prompt:
        messages.append({"role": "system", "content": prompt})
    # 遍历历史消息
    for idx, (user_msg, model_msg) in enumerate(history):  # user_msg是用户的问题，model_msg是大模型的回答
        # 如果提供了提示词，并且是第一条历史消息，则跳过
        if prompt and idx == 0:
            continue
        # 如果是最后一条历史消息，并且模型消息为空，则添加用户消息并结束
        if idx == len(history) - 1 and not model_msg:
            messages.append({"role": "user", "content": user_msg})
            break
        # 如果有用户消息，将其添加到消息列表中
        if user_msg:
            messages.append({"role": "user", "content": user_msg})
        # 如果有模型消息，将其添加到消息列表中
        if model_msg:
            messages.append({"role": "assistant", "content": model_msg})
    # 使用分词器将消息列表转换为模型输入
    # tokenizer：它负责将原始文本转换为模型可以理解的格式。
    model_inputs = (tokenizer.apply_chat_template(messages,
                                                  add_generation_prompt=True,
                                                  tokenize=True,
                                                  return_tensors="pt")  # 这个参数指定了返回的 tensors 类型。"pt" 表示 PyTorch tensors。这意味着输出将会是一个 PyTorch tensor 对象
                    .to(next(model.parameters()).device))
    # 创建一个文本迭代器流
    streamer = TextIteratorStreamer(
        tokenizer,
        timeout=60,  # 超时时间为: 60秒数。流将被终止
        skip_prompt=True,  # 这个参数指示是否跳过生成的初始提示（prompt）。如果设置为 True，则生成的输出将不包含初始提示，只包含模型生成的部分。
        skip_special_tokens=True)  # 跳过特殊 token。特殊 token 包括 [CLS], [SEP], [PAD] 等，这些 token 通常用于模型内部的处理，但在最终输出中没有实际意义。
    # 定义生成文本的参数
    generate_kwargs = {
        "input_ids": model_inputs,
        "streamer": streamer,
        "max_new_tokens": max_length,
        "do_sample": True,
        "top_p": top_p,
        "temperature": temperature,
        "stopping_criteria": StoppingCriteriaList([stop]),
        "repetition_penalty": 1.2,
        "eos_token_id": model.config.eos_token_id,
    }
    # 创建一个线程来生成文本
    t = Thread(target=model.generate, kwargs=generate_kwargs)
    t.start()
    # 遍历生成的文本流
    for new_token in streamer:
        # 如果有新的token，将其添加到历史消息中
        if new_token:
            history[-1][1] += new_token
        # 生成并返回更新后的历史消息
        yield history


# 使用Gradio构建Web界面
with gr.Blocks() as demo:  # gr.Blocks 是 Gradio 的顶级容器，用于创建整个应用的布局。
    # 添加HTML标题
    gr.HTML("""<h1 align="center">马士兵教育私有AI大模型应用</h1>""")
    # 创建一个聊天机器人界面组件
    chatbot = gr.Chatbot()  # 聊天记录的视图组件
    # 创建一个行布局
    with gr.Row():  # 水平布局容器
        # 创建一个列布局
        with gr.Column(scale=3):  # 垂直布局容器
            # 创建一个文本框用于用户输入
            with gr.Column(scale=12):
                user_input = gr.Textbox(show_label=False, placeholder="输入...", lines=10, container=False)
            # 创建一个提交按钮
            with gr.Column(min_width=32, scale=1):
                submitBtn = gr.Button("提交")  # 提交用户问题的 按钮
        # 创建另一个列布局
        with gr.Column(scale=1):
            # 创建一个文本框用于输入提示词
            prompt_input = gr.Textbox(show_label=False, placeholder="提示词", lines=10, container=False)
            # 创建一个按钮用于设置提示词
            pBtn = gr.Button("提示词设置")
        # 创建第三个列布局
        with gr.Column(scale=1):
            # 创建一个按钮用于清除聊天记录
            emptyBtn = gr.Button("清除聊天记录")
            # 创建一个滑块用于设置最大长度
            max_length = gr.Slider(0, 32768, value=8192, step=1.0, label="最大长度", interactive=True)
            # 创建一个滑块用于设置Top P值
            top_p = gr.Slider(0, 1, value=0.8, step=0.01, label="Top P", interactive=True)
            # 创建一个滑块用于设置温度
            temperature = gr.Slider(0.01, 1, value=0.6, step=0.01, label="Temperature", interactive=True)


    # 定义一个函数，用于处理用户输入
    def user_question(query, history):
        return "", history + [[parse_text(query), ""]]


    # 定义一个函数，用于设置提示词
    def set_prompt(prompt_text):
        return [[parse_text(prompt_text), "成功设置提示词"]]


    # 将设置提示词的函数绑定到按钮点击事件
    pBtn.click(set_prompt, inputs=[prompt_input], outputs=chatbot)
    # 将用户输入的函数绑定到提交按钮点击事件
    submitBtn.click(user_question, [user_input, chatbot], [user_input, chatbot], queue=False).then(
        predict, [chatbot, prompt_input, max_length, top_p, temperature], chatbot
    )
    # 将清除聊天记录的函数绑定到按钮点击事件
    emptyBtn.click(lambda: (None, None), None, [chatbot, prompt_input], queue=False)
# 启动Gradio演示
demo.queue()
demo.launch(server_name="127.0.0.1", server_port=6006, inbrowser=True, share=True)
