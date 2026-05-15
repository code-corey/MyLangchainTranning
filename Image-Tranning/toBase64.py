import base64
from pathlib import Path


def main() -> None:
    # 测试：改成你要编码的物理文件路径
    path = Path(r"D:\Github\MyLangchainTranning\Image-Tranning\原始图片.png")

    data = path.read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    print(b64)


if __name__ == "__main__":
    main()
