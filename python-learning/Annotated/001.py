from typing import Annotated

# 定义变量时添加"标签"
age: Annotated[int, "年龄必须大于0"]
name: Annotated[str, "用户名不能包含特殊字符"]

# 实际使用时，Python 完全忽略标签
age = 25  # ✅ 正常工作，不会检查是否大于0
name = "张三"  # ✅ 正常工作

print(age)  # 25
print(name)  # 张三

"""
结论：Annotated 默认情况下只是"注释"，不影响代码运行。
"""