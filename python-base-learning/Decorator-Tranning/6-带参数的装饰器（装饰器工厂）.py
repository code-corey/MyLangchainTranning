# demo6_decorator_with_args.py
"""
理解：通过三层嵌套实现参数化的装饰器
"""

from functools import wraps
import time

def repeat(times):
    """
    让函数重复执行指定次数
    用法: @repeat(3)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            results = []
            for i in range(times):
                print(f"第 {i+1}/{times} 次执行")
                result = func(*args, **kwargs)
                results.append(result)
            return results
        return wrapper
    return decorator

def retry(max_attempts=3, delay=1):
    """
    失败时自动重试
    用法: @retry(max_attempts=5, delay=2)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"❌ 第 {attempt} 次尝试失败: {e}")
                    if attempt < max_attempts:
                        print(f"⏳ 等待 {delay} 秒后重试...")
                        time.sleep(delay)
                    else:
                        print(f"💀 重试 {max_attempts} 次后仍然失败")
                        raise
        return wrapper
    return decorator

# 测试 repeat
@repeat(times=3)
def say_hello(name):
    print(f"Hello, {name}!")
    return f"完成对 {name} 的问候"

results = say_hello("Alice")
print(f"返回值列表: {results}")

print("\n" + "="*40 + "\n")

# 测试 retry
@retry(max_attempts=3, delay=0.5)
def unstable_function():
    import random
    if random.random() < 0.7:  # 70% 概率失败
        raise ValueError("随机失败啦！")
    return "成功！"

try:
    result = unstable_function()
    print(f"✅ 最终结果: {result}")
except Exception:
    print("最终失败")