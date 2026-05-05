from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

# 监督数据：(查询, 相关文档) 对 - 这是隐式的正例
train_examples = [
    InputExample(texts=["如何学Python", "Python入门教程推荐"]),
    InputExample(texts=["苹果手机价格", "iPhone最新报价"]),
    InputExample(texts=["北京景点推荐", "故宫博物院介绍"]),
]

model = SentenceTransformer('all-MiniLM-L6-v2')
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=4)

# 这个损失函数自动将batch内其他文档作为负例
train_loss = losses.MultipleNegativesRankingLoss(model)

model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=5,
    output_path='./retrieval_model'
)