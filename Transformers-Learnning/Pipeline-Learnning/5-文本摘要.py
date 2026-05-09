from transformers import pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

text = "Hugging Face was founded in New York... (此处输入长文本)"
result = summarizer(text, max_length=50, min_length=10, do_sample=False)
print(result[0]['summary_text'])
# 输出:文本的核心摘要