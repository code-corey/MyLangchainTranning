from transformers import pipeline

qa = pipeline("document-question-answering")

context = "The Moon is Earth's only natural satellite. It orbits at an average distance of 384,400 km."
question = "What is the distance from Earth to the Moon?"

result = qa(question=question, context=context,image="H:\\11.png")
print(result)
# 输出: 384,400 km