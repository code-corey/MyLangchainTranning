from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F

# 加载模型
model_name = "distilbert-base-uncased-finetuned-sst-2-english"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
model.eval()

# 批处理多个文本
texts = [
    "I love using Hugging Face!",
    "This is terrible!",
    "The movie was okay."
]

# 批量分词（自动 padding 和 truncation）
inputs = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")

print(f"批处理后的形状:")
print(f"input_ids shape: {inputs['input_ids'].shape}")  # [3, 序列长度]
print(f"attention_mask shape: {inputs['attention_mask'].shape}")

# 批量推理
with torch.no_grad():
    outputs = model(**inputs)

# 批量处理输出
probabilities = F.softmax(outputs.logits, dim=-1)
predictions = probabilities.argmax(dim=-1)
scores = probabilities.max(dim=-1).values

# 显示结果
id2label = model.config.id2label
for text, pred_id, score in zip(texts, predictions, scores):
    label = id2label[pred_id.item()]
    print(f"文本: {text}")
    print(f"情感: {label}, 置信度: {score:.4f}\n")

# 输出:
# 文本: I love using Hugging Face!
# 情感: POSITIVE, 置信度: 0.9998
#
# 文本: This is terrible!
# 情感: NEGATIVE, 置信度: 0.9995
#
# 文本: The movie was okay.
# 情感: POSITIVE, 置信度: 0.6321 (边缘情况)