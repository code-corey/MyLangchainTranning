from transformers import pipeline

translator = pipeline("text-generation", model="Helsinki-NLP/opus-mt-en-zh")

result = translator("Hugging Face is creating amazing tools for AI practitioners.")
# 注意：返回的 key 也从 'translation_text' 变成了 'generated_text'
print(result[0]['generated_text'])

"""
[
'any-to-any', 
'audio-classification', 
'automatic-speech-recognition', 
'depth-estimation', 
'document-question-answering', 
'feature-extraction', 
'fill-mask', 
'image-classification', 
'image-feature-extraction', 
'image-segmentation', 
'image-text-to-text', 
'keypoint-matching',
 'mask-generation', 
 'ner', 
 'object-detection', 
 'sentiment-analysis', 
 'table-question-answering', 
 'text-classification', 
 'text-generation', 
 'text-to-audio', 
 'text-to-speech',
  'token-classification', 
  'video-classification', 
  'zero-shot-audio-classification', 
  'zero-shot-classification', 
  'zero-shot-image-classification',
   'zero-shot-object-detection']
"""
