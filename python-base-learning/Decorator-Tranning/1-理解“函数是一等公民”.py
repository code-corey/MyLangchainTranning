"""
理解：函数也是对象，可以被赋值和传递
"""

def greet():
    """一个简单的问候函数"""
    return "Hello!"

# 1. 函数可以赋值给变量
say_hello = greet
print(say_hello())  # 输出: Hello!

# 2. 函数可以作为参数传递
def call_function(func):
    """接收一个函数并调用它"""
    print("准备调用函数...")
    result = func()
    print("函数调用完成！")
    return result

print(call_function(greet))
# 输出:
# 准备调用函数...
# 函数调用完成！
# Hello!

# 3. 函数可以返回函数
def make_greeting(prefix):
    """根据前缀返回不同的问候函数"""
    def greet_with_prefix(name):
        return f"{prefix} {name}!"
    return greet_with_prefix  # 返回内部函数

hello_func = make_greeting("Hello")
print(hello_func("Alice"))  # 输出: Hello Alice!

goodbye_func = make_greeting("Goodbye")
print(goodbye_func("Bob"))  # 输出: Goodbye Bob!