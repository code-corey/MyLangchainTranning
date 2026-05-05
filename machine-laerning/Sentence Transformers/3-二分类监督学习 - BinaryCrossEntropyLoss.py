from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

# 监督数据：0=不相似，1=相似
binary_examples = [
    InputExample(texts=["Python是编程语言", "Python由Guido创建"], label=1),   # 相似
    InputExample(texts=["Python是编程语言", "今天天气真好"], label=0),   # 不相似
    InputExample(texts=["人工智能是未来", "AI将改变世界"], label=1),
    InputExample(texts=["人工智能是未来", "我喜欢吃苹果"], label=0),
] * 50  # 扩展数据量

model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
train_dataloader = DataLoader(binary_examples, shuffle=True, batch_size=8)

# BinaryCrossEntropyLoss适合二分类标签
train_loss = losses.BinaryCrossEntropyLoss(model)

model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=10,
    output_path='./binary_classifier'
)