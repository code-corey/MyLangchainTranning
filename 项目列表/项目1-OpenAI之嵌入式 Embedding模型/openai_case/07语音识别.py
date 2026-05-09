import os
from openai import OpenAI


os.environ['http_proxy'] = '127.0.0.1:7890'
os.environ['https_proxy'] = '127.0.0.1:7890'

client = OpenAI()

# 把李云龙的配音变成文字(转录)
audio_file = open('./audio/test1.mp3', 'rb')
#
# transcription = client.audio.transcriptions.create(
#     model='whisper-1',
#     file=audio_file
# )
#
# print(transcription.text)


# 转录 + 翻译（翻译成英文）
# translation = client.audio.translations.create(
#     model='whisper-1',
#     file=audio_file,
#     prompt='Translate into English'
# )
#
# print(translation.text)

# 给郭德纲的相声 转换成英文版
gdg_audio_file = open('./audio/gdg.mp3', 'rb')
english_gdg_audio_file = './audio/gdg_english.mp3'

translation = client.audio.translations.create(
    model='whisper-1',
    file=gdg_audio_file,
)

english_txt = translation.text
print(english_txt)
gdg_audio_file.close()

with client.audio.speech.with_streaming_response.create(
    model='tts-1',
    voice='onyx',
    input=english_txt
) as resp:
    resp.stream_to_file(english_gdg_audio_file)




