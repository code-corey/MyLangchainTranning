import base64
import os
from openai import OpenAI


os.environ['http_proxy'] = '127.0.0.1:7890'
os.environ['https_proxy'] = '127.0.0.1:7890'

client = OpenAI()

# resp = client.images.generate(
#     model='dall-e-3',
#     prompt='一只可爱的哈士奇犬',
#     size='1024x1024',
#     quality='standard',
#     n=1
# )

# resp = client.images.generate(
#     model='dall-e-3',
#     prompt='一只可爱的哈士奇犬，在海滩上奔跑。',
#     size='1024x1024',
#     quality='hd',
#     n=1,
#     style='natural',
#     response_format='b64_json'
# )

resp = client.images.generate(
    model='dall-e-3',
    prompt='一个美女在海边散步',
    size='1024x1024',
    quality='hd',
    n=1,
    style='vivid',
    response_format='b64_json'
)

# print(resp)
b64_img = resp.data[0].b64_json

with open('./images/output01.jpg', 'wb') as f:
    f.write(base64.b64decode(b64_img))
