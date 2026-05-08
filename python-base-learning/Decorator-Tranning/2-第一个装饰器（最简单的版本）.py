# demo2_simple_decorator.py
"""
理解：装饰器就是一个包装函数
"""

def simple_decorator(func):
    """最简单的装饰器：在函数执行前后打印信息"""
    def wrapper():
        print("🚀 函数执行前...")
        func()
        print("✅ 函数执行后...")
    return wrapper

# 不用装饰器的原始写法
def say_hello():
    print("Hello World!")

# 手动包装
say_hello = simple_decorator(say_hello)
say_hello()
# 输出:
# 🚀 函数执行前...
# Hello World!
# ✅ 函数执行后...

print("\n" + "="*40 + "\n")

# 使用 Python 的装饰器语法 @
@simple_decorator
def say_goodbye():
    print("Goodbye World!")

say_goodbye()
# 输出完全一样:
# 🚀 函数执行前...
# Goodbye World!
# ✅ 函数执行后...