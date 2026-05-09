from transformers import pipeline

# 创建情感分析管道
"""
NLP（自然语言处理）任务 是指让计算机理解、处理和生成人类语言的各种具体问题

pipeline 是 Hugging Face 提供的高级工具，用几行代码就能使用各种预训练模型

pipeline("sentiment-analysis") 创建一个专门用于情感分析的 pipeline 对象
"sentiment-analysis" 告诉 pipeline 加载默认的情感分析模型（通常是 distilbert-base-uncased-finetuned-sst-2-english）
"""
classifier = pipeline("sentiment-analysis")

"""
pipeline 自动完成：分词 → 模型推理 → 后处理
返回一个包含预测结果的列表
"""
result = classifier("I  love using Hugging Face!")

print(result)
# 输出: [{'label': 'POSITIVE', 'score': 0.9998}]



from transformers import pipeline

# 1. 文本生成
generator = pipeline("text-generation", model="gpt2")
print(generator("The future of AI is")[0]['generated_text'])

# 2. 命名实体识别 (NER)
ner_tagger = pipeline("ner", aggregation_strategy="simple")
print(ner_tagger("Elon Musk founded SpaceX in Hawthorne, California."))

# 3. 文本摘要
summarizer = pipeline("summarization")
long_text = "Hugging Face is a company that develops tools for building applications using machine learning. It is most famous for its Transformers library. The library simplifies the process of using and training state-of-the-art models."
print(summarizer(long_text, max_length=20, min_length=5)[0]['summary_text'])

# 4. 问答系统
qa_pipeline = pipeline("question-answering")
context = "Transformers pipelines are easy to use. They support many tasks like translation and summarization."
answer = qa_pipeline(question="What are pipelines easy to use for?", context=context)
print(answer)