# 调试版本 - 找出具体哪里出错
import traceback
import sys

print("1. 尝试导入库...")
try:
    from sentence_transformers import SentenceTransformer
    print("✅ sentence_transformers 导入成功")
except Exception as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

print("2. 尝试加载模型...")
try:
    # 尝试本地缓存，如果没有会自动下载
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2', device='cpu')
    print("✅ 模型加载成功")
except Exception as e:
    print(f"❌ 模型加载失败: {e}")
    print(f"错误详情: {traceback.format_exc()}")
    sys.exit(1)

print("3. 尝试编码第一条文本...")
try:
    result = model.encode("测试文本")
    print(f"✅ 编码成功，向量维度: {len(result)}")
    print(f"结果类型: {type(result)}")
except Exception as e:
    print(f"❌ 编码失败: {e}")
    print(f"错误详情: {traceback.format_exc()}")