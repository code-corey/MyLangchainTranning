from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F


class MySentimentPipeline:
    def __init__(self, model_name="distilbert-base-uncased-finetuned-sst-2-english"):
        print(f"加载模型: {model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.eval()  # 评估模式

    def __call__(self, text):
        # 1. 分词
        inputs = self.tokenizer(text, return_tensors="pt")

        # 2. 推理
        with torch.no_grad():
            outputs = self.model(**inputs)

        # 3. 处理输出
        probabilities = F.softmax(outputs.logits, dim=-1)
        score = probabilities.max().item()
        label_id = probabilities.argmax().item()
        label = self.model.config.id2label[label_id]

        # 4. 返回结果
        return [{"label": label, "score": score}]


# 使用自定义的 pipeline
my_classifier = MySentimentPipeline()
result = my_classifier("I love using Hugging Face!")
print(result)
# 输出: [{'label': 'POSITIVE', 'score': 0.9998}]