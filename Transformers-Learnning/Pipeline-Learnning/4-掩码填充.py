from transformers import pipeline
unmasker = pipeline("fill-mask")


# 填空题大师。模型会根据上下文预测 [MASK] 处概率最大的单词。
result = unmasker("I love Paris in the <mask> time of the year.")
for item in result:
    print(item['token_str'], item['score'])
# 输出: 'spring' (高分), 'best', 'most' ...