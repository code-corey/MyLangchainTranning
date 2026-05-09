from transformers import pipeline

# 模型地址为：C:\Users\chengongyi\.cache\huggingface\hub

generator = pipeline("text-generation", model="gpt2")

result = generator("The future of AI is", max_length=30, num_return_sequences=1)
print(result[0]['generated_text'])
# 输出: The future of AI is ... (AI自动续写的内容)