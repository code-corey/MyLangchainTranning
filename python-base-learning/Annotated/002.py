from typing import Annotated, get_type_hints

class User:
    age: Annotated[int, "必须大于0"]
    name: str

# 读取类型信息
hints = get_type_hints(User, include_extras=True)

for field, info in hints.items():
    # 检查是否有 Annotated
    if hasattr(info, '__metadata__'):
        print(f"{field}: 类型={info.__origin__}, 标签={info.__metadata__}")
    else:
        print(f"{field}: 类型={info}")

# 输出：
# age: 类型=<class 'int'>, 标签=('必须大于0',)
# name: 类型=<class 'str'>

"""
核心：程序可以读取 Annotated 的标签并做特殊处理
"""