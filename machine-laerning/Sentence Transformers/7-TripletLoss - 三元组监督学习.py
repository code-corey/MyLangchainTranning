from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

# 三元组：(anchor, positive, negative)
# anchor与positive相似，与negative不相似
triplet_examples = [
    InputExample(texts=["Python编程", "Python语法", "Java编程"]),  # 后两个都与第一个比较
    InputExample(texts=["苹果手机", "iPhone", "香蕉水果"]),
    InputExample(texts=["机器学习", "深度学习", "天气预报"]),
]

model = SentenceTransformer('all-MiniLM-L6-v2')
train_dataloader = DataLoader(triplet_examples, shuffle=True, batch_size=4)

train_loss = losses.TripletLoss(model, distance_metric='cosine')

model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=5,
    output_path='./triplet_model'
)