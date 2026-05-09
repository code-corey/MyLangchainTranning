from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# 1. 加载模型和分词器（pipeline 自动做的）
# 斯坦福情感树库数据集（二分类：正面/负面）
model_name = "distilbert-base-uncased-finetuned-sst-2-english"

## AutoTokenizer 自动加载与模型匹配的分词器 --> 将文本转换成模型能理解的数字（token IDs）
tokenizer = AutoTokenizer.from_pretrained(model_name)

# AutoModelForSequenceClassification --> 自动加载用于序列分类的模型,输入文本，输出分类结果（如正面/负面）
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# 2. 准备输入（pipeline 自动做的）
text = "I love using Hugging Face!"
inputs = tokenizer(text, return_tensors="pt")

# 3. 模型推理（pipeline 自动做的）
with torch.no_grad():
    outputs = model(**inputs)

# 4. 处理输出（pipeline 自动做的）
predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
score = predictions.max().item()
label_id = predictions.argmax().item()

# 5. 映射标签（pipeline 自动做的）
labels = ["NEGATIVE", "POSITIVE"]
result = [{"label": labels[label_id], "score": score}]

print(result)
# 输出: [{'label': 'POSITIVE', 'score': 0.9998}]