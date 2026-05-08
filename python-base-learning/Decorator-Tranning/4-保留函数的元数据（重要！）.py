# demo4_preserve_metadata.py

"""
理解：装饰器会覆盖原函数的信息，需要用 wraps 修复
"""

from functools import wraps

def bad_decorator(func):
    """不保留元数据的装饰器"""
    def wrapper(*args, **kwargs):
        """这是 wrapper 的文档"""
        return func(*args, **kwargs)
    return wrapper

def good_decorator(func):
    """保留元数据的装饰器"""
    @wraps(func)  # 关键！复制原函数的元数据到 wrapper
    def wrapper(*args, **kwargs):
        """这是 wrapper 的文档"""
        return func(*args, **kwargs)
    return wrapper

@bad_decorator
def calculate(x, y):
    """计算 x 和 y 的和"""
    return x + y

@good_decorator
def calculate_good(x, y):
    """计算 x 和 y 的和"""
    return x + y

print("❌ 不保留元数据:")
print(f"  函数名: {calculate.__name__}")  # 输出: wrapper (不对！)
print(f"  文档: {calculate.__doc__}")    # 输出: 这是 wrapper 的文档 (不对！)

print("\n✅ 保留元数据:")
print(f"  函数名: {calculate_good.__name__}")  # 输出: calculate_good
print(f"  文档: {calculate_good.__doc__}")    # 输出: 计算 x 和 y 的和