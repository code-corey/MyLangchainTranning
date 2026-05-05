import torch
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader
from datasets import Dataset


print("测试1: 加载小型模型")
try:
    model_small = SentenceTransformer('paraphrase-MiniLM-L3-v2')
    print("✓ 小型模型加载成功")
except Exception as e:
    print(f"✗ 加载失败: {e}")


device = torch.device('cpu')
print(f"使用设备: {device}")

# 1. 准备带标签的监督数据（核心！）
train_examples = [
    InputExample(texts=["今天天气很好", "今天天气不错"], label=0.9),   # 相似度高
    InputExample(texts=["今天天气很好", "我喜欢吃苹果"], label=0.1),   # 不相似
    InputExample(texts=["机器学习很有趣", "深度学习也很棒"], label=0.8), # 相似
    InputExample(texts=["机器学习很有趣", "今天天气真好"], label=0.0),   # 完全不相似
]

"""
准备训练数据（监督学习的核心）

# 练习题1
句子1 = "今天天气很好"
句子2 = "今天天气不错"
正确答案 = 0.9  # 非常相似

# 练习题2
句子1 = "今天天气很好"
句子2 = "我喜欢吃苹果"
正确答案 = 0.1  # 不相似

# ... 模型从这些"带答案的题"中学习判断标准
"""

# 2. 加载预训练模型(擅长处理"语义相似，多语言，轻量级模型，12层Transformer)
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# 3. 创建DataLoader
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=2)

"""
# batch_size=2 的意思是：
批次1: [练习题1, 练习题2]
批次2: [练习题3, 练习题4]

# 训练时，模型一次看2道题，更新一次参数
"""

# 4. 使用CosineSimilarityLoss（需要0-1的相似度标签）
# 定义损失函数（此时还没有计算任何值！）
train_loss = losses.CosineSimilarityLoss(model)

"""
定义损失函数

损失函数的作用：衡量"模型猜的"和"正确答案"的差距。

# 举例说明
正确答案 = 0.9  # 人标注的
模型猜测 = 0.7  # 模型算出来的

差距 = |0.9 - 0.7| = 0.2  # 损失值

# 训练的目标：让这个差距越来越小

"""

# 5. 微调
model.fit(
    train_objectives=[(train_dataloader, train_loss)], # 数据+损失函数
    epochs=5,  # 把全部数据学5遍
    warmup_steps=100, # 前100步慢慢提高学习率
    show_progress_bar=True,  # 显示进度条
    output_path='./finetuned_sts_model' # 保存微调后的模型
)

print("监督学习微调完成！")