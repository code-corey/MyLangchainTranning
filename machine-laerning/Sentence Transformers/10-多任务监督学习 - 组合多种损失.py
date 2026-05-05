from sentence_transformers import SentenceTransformer, losses
from datasets import Dataset

model = SentenceTransformer('all-MiniLM-L6-v2')

# 任务1：STS相似度回归数据集
sts_dataset = Dataset.from_dict({
    "sentence1": ["今天天气好", "苹果好吃"],
    "sentence2": ["今日晴朗", "香蕉很甜"],
    "label": [0.9, 0.1],
})

# 任务2：三元组数据集
triplet_dataset = Dataset.from_dict({
    "anchor": ["Python", "苹果"],
    "positive": ["编程语言", "iPhone"],
    "negative": ["天气", "香蕉"],
})

# 使用DatasetDict组合多个数据集
from datasets import DatasetDict
multi_dataset = DatasetDict({
    "sts": sts_dataset,
    "triplet": triplet_dataset,
})

# 为不同数据集使用不同损失函数
losses_dict = {
    "sts": losses.CoSENTLoss(model),
    "triplet": losses.TripletLoss(model),
}

from sentence_transformers import SentenceTransformerTrainer
from sentence_transformers.training_args import SentenceTransformerTrainingArguments

args = SentenceTransformerTrainingArguments(
    output_dir="./multitask",
    num_train_epochs=3,
)

trainer = SentenceTransformerTrainer(
    model=model,
    args=args,
    train_dataset=multi_dataset,
    loss=losses_dict,
)
trainer.train()