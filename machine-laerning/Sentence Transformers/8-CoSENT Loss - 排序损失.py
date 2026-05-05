from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

# 数据：句子对+相似度标签(0-1)
train_examples = [
    InputExample(texts=["句子A", "句子B1"], label=0.9),
    InputExample(texts=["句子A", "句子B2"], label=0.7),
    InputExample(texts=["句子A", "句子B3"], label=0.3),
]

model = SentenceTransformer('all-MiniLM-L6-v2')
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=4)

# CoSENTLoss是CosineSimilarityLoss的改进版
train_loss = losses.CoSENTLoss(model)

model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=5,
    output_path='./cosent_model'
)