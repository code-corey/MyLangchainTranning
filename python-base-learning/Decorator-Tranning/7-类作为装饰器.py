# demo7_class_decorator.py
"""
理解：通过 __call__ 方法让类的实例变成可调用对象
"""

from functools import wraps


class CountCalls:
    """统计函数被调用的次数"""

    def __init__(self, func):
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"📊 {self.func.__name__} 已被调用 {self.count} 次")
        return self.func(*args, **kwargs)


class Cache:
    """缓存函数的结果（简单版）"""

    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args, **kwargs):
        # 将参数转为可哈希的键
        key = str(args) + str(sorted(kwargs.items()))

        if key in self.cache:
            print(f"💾 从缓存返回结果: {self.cache[key]}")
            return self.cache[key]

        result = self.func(*args, **kwargs)
        self.cache[key] = result
        print(f"✨ 首次计算并缓存: {result}")
        return result


# 测试调用计数
@CountCalls
def greet(name):
    return f"Hello, {name}!"


print(greet("Alice"))
print(greet("Bob"))
print(greet("Charlie"))
print(f"总共调用了 {greet.count} 次")

print("\n" + "=" * 40 + "\n")


# 测试缓存
@Cache
def expensive_computation(x, y):
    """模拟耗时计算"""
    import time
    print(f"🔄 正在计算 {x} + {y} ...")
    time.sleep(1)  # 模拟耗时
    return x + y


print(expensive_computation(3, 5))
print(expensive_computation(3, 5))  # 第二次调用从缓存取
print(expensive_computation(4, 6))  # 新参数重新计算