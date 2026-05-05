from typing import Annotated, TypedDict

# 自定义合并函数
def max_value(old: int, new: int) -> int:
    """保留最大值"""
    return max(old, new) if old is not None else new

# 自定义累加函数
def sum_values(old: int, new: int) -> int:
    """累加"""
    return (old or 0) + (new or 0)

class State(TypedDict):
    max_score: Annotated[int, max_value]
    total_score: Annotated[int, sum_values]
    name: str  # 普通字段，覆盖

"""
"max_score 这个字段，更新时请调用 max_value 函数来处理"

"total_score 这个字段，更新时请调用 sum_values 函数来处理"

"name 这个字段，更新时直接替换就行"
"""


# 模拟 LangGraph
def update_state(old, new):
    result = old.copy()
    for key, new_val in new.items():
        if key == "max_score":
            result[key] = max_value(old.get(key), new_val)
        elif key == "total_score":
            result[key] = sum_values(old.get(key), new_val)
        else:
            result[key] = new_val
    return result

# 测试
state = {"max_score": None, "total_score": 0, "name": "Alice"}

state = update_state(state, {"max_score": 50, "total_score": 50, "name": "Bob"})
print(state)  # {'max_score': 50, 'total_score': 50, 'name': 'Bob'}

state = update_state(state, {"max_score": 30, "total_score": 30, "name": "Charlie"})
print(state)  # {'max_score': 50, 'total_score': 80, 'name': 'Charlie'}
#               ↑ 保留最大值 50  ↑ 累加 50+30=80  ↑ 覆盖