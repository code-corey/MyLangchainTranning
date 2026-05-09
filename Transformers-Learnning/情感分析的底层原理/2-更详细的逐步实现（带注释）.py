from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F

# 第1步：选择模型
# 这是 Hugging Face 上微调好的情感分析模型
model_name = "distilbert-base-uncased-finetuned-sst-2-english"

# 第2步：加载分词器
# 分词器负责：文本 → token IDs
print("加载分词器...")
tokenizer = AutoTokenizer.from_pretrained(model_name)

# 第3步：加载模型
# 模型负责：token IDs → 情感分数
print("加载模型...")
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# 第4步：准备输入文本
text = "I love using Hugging Face!"
print(f"\n输入文本: {text}")

# 第5步：分词（Tokenization）
# 将文本转换成模型可以理解的数字
inputs = tokenizer(text, return_tensors="pt")
print(f"\n分词结果:")
print(f"input_ids: {inputs['input_ids']}")
print(f"attention_mask: {inputs['attention_mask']}")
# input_ids: tensor([[ 101, 1045, 2293, 2478, 17662, 999,  102]])
# 101 = [CLS] (开始标记)
# 1045 = "i"
# 2293 = "love"
# 2478 = "using"
# 17662 = "hugging"
# 999 = "!"
# 102 = [SEP] (结束标记)

# 第6步：模型推理
# 将 token IDs 输入模型，得到 logits（原始分数）
print("\n执行模型推理...")
model.eval()  # 设置为评估模式
with torch.no_grad():  # 不计算梯度（推理时不需要）
    outputs = model(**inputs)

# outputs.logits 是二维张量: [batch_size, num_labels]
print(f"原始输出 logits: {outputs.logits}")
# 例如: tensor([[-0.1234,  0.5678]])

# 第7步：Softmax 归一化
# 将 logits 转换成概率（0-1之间，和为1）
probabilities = F.softmax(outputs.logits, dim=-1)
print(f"Softmax概率: {probabilities}")
# 例如: tensor([[0.3210, 0.6790]])

# 第8步：获取预测结果
predicted_class_id = probabilities.argmax().item()
confidence = probabilities.max().item()

print(f"\n预测类别ID: {predicted_class_id}")
print(f"置信度: {confidence:.4f}")

# 第9步：标签映射
# 不同的模型有不同的标签映射
# 这个模型的配置中有 id2label 映射
id2label = model.config.id2label
# id2label = {0: "NEGATIVE", 1: "POSITIVE"}

predicted_label = id2label[predicted_class_id]

# 第10步：格式化输出（模仿 pipeline 的输出格式）
result = [{"label": predicted_label, "score": confidence}]
print(f"\n最终结果: {result}")
# 输出: [{'label': 'POSITIVE', 'score': 0.9998}]