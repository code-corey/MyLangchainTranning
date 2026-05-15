import os
import base64
from pathlib import Path
from openai import OpenAI


print(os.environ.get("ARK_API_KEY"))



path = Path(r"D:\Github\MyLangchainTranning\Image-Tranning\原始图片.png")
_ext = path.suffix.lower().lstrip(".")
# data:image/<格式>;base64,<编码>，<格式> 为小写 MIME 子类型（如 png、jpeg）
_mime_subtype = {
    "png": "png",
    "jpg": "jpeg",
    "jpeg": "jpeg",
    "gif": "gif",
    "webp": "webp",
    "bmp": "bmp",
    "svg": "svg+xml",
}.get(_ext, "png")
data = path.read_bytes()
_b64_payload = base64.b64encode(data).decode("ascii")
b64 = f"data:image/{_mime_subtype};base64,{_b64_payload}"

# 请确保您已将 API Key 存储在环境变量 ARK_API_KEY 中
# 初始化Ark客户端，从环境变量中读取您的API Key
client = OpenAI(
    # 此为默认路径，您可根据业务所在地域进行配置
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    # 从环境变量中获取您的 API Key。此为默认方式，您可根据需要进行修改
    api_key=os.environ.get("ARK_API_KEY"),
)



imagesResponse = client.images.generate(
    model="doubao-seedream-5-0-260128",
    prompt="扩展这张图片",
    size="2K",
    response_format="url",
    extra_body = {
        "image": b64,
        "watermark": True
    }
)

print(imagesResponse.data[0].url)