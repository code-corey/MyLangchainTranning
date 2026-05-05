from sentence_transformers import SentenceTransformer, losses
from datasets import load_dataset

# 1. 加载官方STS-Benchmark数据集（有标签的句子对）
train_dataset = load_dataset("sentence-transformers/stsb", split="train")
print(f"训练样本数: {len(train_dataset)}")
print(train_dataset[0])  # {'sentence1': '...', 'sentence2': '...', 'score': 3.8}

# 2. 数据集格式转换
def convert_to_input_examples(dataset):
    from sentence_transformers import InputExample
    examples = []
    for item in dataset:
        # score范围0-5，需要归一化到0-1
        normalized_score = item['score'] / 5.0
        examples.append(InputExample(
            texts=[item['sentence1'], item['sentence2']],
            label=normalized_score
        ))
    return examples

train_examples = convert_to_input_examples(train_dataset)

# 3. 训练
model = SentenceTransformer('all-MiniLM-L6-v2')
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)
train_loss = losses.CosineSimilarityLoss(model)

model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=3,
    warmup_steps=500,
    output_path='./stsb_finetuned'
)