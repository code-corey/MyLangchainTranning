from transformers import pipeline

ner = pipeline("ner", grouped_entities=True)

result = ner("My name is Sylvain and I work at Hugging Face in Brooklyn.")
print(result)
# 输出: [{'entity_group': 'PER', 'word': 'Sylvain'}, {'entity_group': 'ORG', 'word': 'Hugging Face'}, {'entity_group': 'LOC', 'word': 'Brooklyn'}]