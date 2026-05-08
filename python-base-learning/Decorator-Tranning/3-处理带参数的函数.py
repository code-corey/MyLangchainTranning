# demo3_with_arguments.py
"""
理解：装饰器必须能处理任意参数
"""


def flexible_decorator(func):
    """可以处理带参数的函数"""

    def wrapper(*args, **kwargs):  # *args 接收所有位置参数，**kwargs 接收所有关键字参数
        print(f"📞 调用函数: {func.__name__}")
        print(f"   位置参数: {args}")
        print(f"   关键字参数: {kwargs}")

        result = func(*args, **kwargs)  # 传递参数给原函数

        print(f"   返回值: {result}")
        print("🏁 函数执行完毕")
        return result

    return wrapper


@flexible_decorator
def add(a, b):
    """两数相加"""
    return a + b


@flexible_decorator
def greet(name, greeting="Hello"):
    """问候某人"""
    return f"{greeting}, {name}!"

# 测试
print("结果:", add(3, 5))
print()
print("结果:", greet("Alice", greeting="Hi"))



# 实验1：理解参数收集
def demo_collection(*args, **kwargs):
    print("="*40)
    print("我收集到了：")
    print(f"  args = {args}   (类型: {type(args).__name__})")
    print(f"  kwargs = {kwargs} (类型: {type(kwargs).__name__})")
    print()

# 各种调用方式
demo_collection(1, 2, 3)
demo_collection(name="Alice", age=25)
demo_collection(1, 2, 3, name="Alice", age=25)
demo_collection()  # 什么都不传也可以