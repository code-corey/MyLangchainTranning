from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader
from datasets import Dataset

# 1. 准备带标签的监督数据（核心！）
train_examples = [
    InputExample(texts=["今天天气很好", "今天天气不错"], label=0.9),   # 相似度高
    InputExample(texts=["今天天气很好", "我喜欢吃苹果"], label=0.1),   # 不相似
    InputExample(texts=["机器学习很有趣", "深度学习也很棒"], label=0.8), # 相似
    InputExample(texts=["机器学习很有趣", "今天天气真好"], label=0.0),   # 完全不相似
]

# 2. 加载预训练模型
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# 3. 创建DataLoader
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=2)

# 4. 使用CosineSimilarityLoss（需要0-1的相似度标签）
train_loss = losses.CosineSimilarityLoss(model)

# 5. 微调
model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=5,
    warmup_steps=100,
    show_progress_bar=True,
    output_path='./finetuned_sts_model'
)

print("监督学习微调完成！")