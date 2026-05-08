# demo8_multiple_decorators.py
"""
理解：装饰器从下往上应用，从上往下执行

多个装饰器的执行顺序：离函数最近的最先执行。

"""

from functools import wraps

def uppercase(func):
    """将返回值转为大写"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result.upper()
    return wrapper

def bold(func):
    """添加加粗标签"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return f"<b>{result}</b>"
    return wrapper

def italic(func):
    """添加斜体标签"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return f"<i>{result}</i>"
    return wrapper

# 顺序1: 先加粗，再斜体
@bold
@italic
def get_message1():
    return "Hello"

# 顺序2: 先斜体，再加粗
@italic
@bold
def get_message2():
    return "Hello"

# 顺序3: 全部加完再转大写
@uppercase
@bold
@italic
def get_message3():
    return "Hello"

print("顺序1 (bold 包 italic):", get_message1())  # <b><i>Hello</i></b>
print("顺序2 (italic 包 bold):", get_message2())  # <i><b>Hello</b></i>
print("顺序3 (全部再大写):", get_message3())      # <B><I>HELLO</I></B>

print("\n" + "="*40 + "\n")
print("💡 执行流程解释:")
print("装饰器在定义时从下往上应用")
print("执行时从上往下执行")