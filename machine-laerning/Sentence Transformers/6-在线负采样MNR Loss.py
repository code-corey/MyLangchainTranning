from sentence_transformers import SentenceTransformer, losses
from datasets import Dataset

# 准备查询-文档对数据
queries = ["Python教程", "北京天气", "苹果手机"]
documents = ["Python入门指南", "北京今日晴", "iPhone 15价格"]

dataset = Dataset.from_dict({
    "anchor": queries,
    "positive": documents,
})

model = SentenceTransformer('all-MiniLM-L6-v2')

# 这个版本使用batch内负采样，训练信号更强
train_loss = losses.MultipleNegativesRankingLoss(model)

# 使用新版Trainer API
from sentence_transformers.training_args import SentenceTransformerTrainingArguments
from sentence_transformers import SentenceTransformerTrainer

args = SentenceTransformerTrainingArguments(
    output_dir="./mnr_model",
    num_train_epochs=3,
    per_device_train_batch_size=8,
)

trainer = SentenceTransformerTrainer(
    model=model,
    args=args,
    train_dataset=dataset,
    loss=train_loss,
)
trainer.train()