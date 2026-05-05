
安装pytorch云主机

python -m pip install --upgrade pip

pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

torch>=2.3.0
torchvision>=0.18.0
transformers>=4.42.4
huggingface-hub>=0.24.0
sentencepiece>=0.2.0
jinja2>=3.1.4
pydantic>=2.8.2
timm>=1.0.7
tiktoken>=0.7.0
accelerate>=0.32.1
sentence_transformers>=3.0.1
gradio>=4.38.1 # web demo
openai>=1.35.0 # openai demo
einops>=0.8.0
pillow>=10.4.0
sse-starlette>=2.1.2
bitsandbytes>=0.43.1 # INT4 Loading
vllm>=0.5.2


下载模型
``` python
from modelscope import snapshot_download
model_dir = snapshot_download('ZhipuAI/glm-4-9b-chat', cache_dir='/root/autodl-tmp/models', revision='master')
```

本次课程的大模型
https://www.modelscope.cn/models/ZhipuAI/glm-4-9b-chat

