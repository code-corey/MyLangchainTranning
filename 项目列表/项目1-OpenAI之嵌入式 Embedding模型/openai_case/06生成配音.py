import os
from openai import OpenAI


os.environ['http_proxy'] = '127.0.0.1:7890'
os.environ['https_proxy'] = '127.0.0.1:7890'

client = OpenAI()

# with client.audio.speech.with_streaming_response.create(
#     model='tts-1',
#     voice='onyx',
#     input='二营长！你他娘的意大利炮呢？给我拉来！'
# ) as resp:
#     resp.stream_to_file('./audio/test2.mp3')

with client.audio.speech.with_streaming_response.create(
    model='tts-1',
    voice='nova',
    response_format='wav',
    speed=1.5,
    input='新华社北京6月12日电 近日，中共中央总书记、国家主席、中央军委主席习近平给中国科学院院士、清华大学教授姚期智回信，向他致以诚挚问候并提出殷切希望。习近平在回信中说，你回国任教二十年来，将爱国之情化为报国之行，在清华大学潜心耕耘、默默奉献，教书育人、科研创新都取得了丰硕成果，向你表示诚挚问候。'
) as resp:
    resp.stream_to_file('./audio/test3.wav')