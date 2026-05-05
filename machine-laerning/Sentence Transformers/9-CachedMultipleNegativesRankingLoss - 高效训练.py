from sentence_transformers import SentenceTransformer
from datasets import Dataset
from sentence_transformers import SentenceTransformerTrainer
from sentence_transformers.training_args import SentenceTransformerTrainingArguments

# 准备数据集
dataset = Dataset.from_dict({
    "anchor": ["查询1", "查询2", "查询3"],
    "positive": ["文档1", "文档2", "文档3"],
})

model = SentenceTransformer('all-MiniLM-L6-v2')

# 这个loss会缓存embedding，大幅提升训练效率
from sentence_transformers.losses import CachedMultipleNegativesRankingLoss
train_loss = CachedMultipleNegativesRankingLoss(model)

args = SentenceTransformerTrainingArguments(
    output_dir="./cached_mnr",
    num_train_epochs=3,
    per_device_train_batch_size=16,
)

trainer = SentenceTransformerTrainer(
    model=model,
    args=args,
    train_dataset=dataset,
    loss=train_loss,
)
trainer.train()