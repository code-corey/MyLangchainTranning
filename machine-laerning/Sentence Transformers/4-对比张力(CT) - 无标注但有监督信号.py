from sentence_transformers import SentenceTransformer, losses

# 注意：CT只需要纯句子列表，但通过构造正负对产生监督信号
sentences = [
    "机器学习是AI的分支",
    "深度学习需要大量数据",
    "自然语言处理处理文本",
    "计算机视觉处理图像",
]

model = SentenceTransformer('all-MiniLM-L6-v2')

# 特殊数据加载器：自动构造(相同句子, 不同句子)对
train_dataloader = losses.ContrastiveTensionDataLoader(
    sentences,
    batch_size=4,
    pos_neg_ratio=1  # 1个正例对应1个负例
)

train_loss = losses.ContrastiveTensionLoss(model)

model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=3,
    output_path='./ct_model'
)