from typing import Annotated, TypedDict
import operator

"""
Annotated[list, operator.add] 的含义

这行代码的意思是："这个字段是一个列表，当更新它时，请使用 operator.add 来合并新旧值"

Annotated[list, operator.add]
   ↑         ↑        ↑
   │         │        └─ 第2个参数：元数据（告诉怎么合并）
   │         └────────── 第1个参数：类型
   └──────────────────── 语法标记
"""

# 定义状态类
class State(TypedDict):
    # 有 Annotated 的字段
    history: Annotated[list, operator.add]
    # 没有 Annotated 的字段
    current: str

"""
def update_state(old_state: dict, new_state: dict) -> dict:
#                             ↑            ↑         ↑
#                             │            │         └─ 返回值类型
#                             │            └─────────── 参数2的类型
#                             └──────────────────────── 参数1的类型
"""

# 模拟 LangGraph 的状态更新函数
def update_state(old_state: dict, new_state: dict) -> dict:
    result = old_state.copy()

    for key, new_value in new_state.items():
        # 检查这个字段是否有 Annotated 和 operator.add
        if key == "history":  # 模拟检查到有 operator.add
            # 追加模式
            result[key] = old_state.get(key, []) + new_value
        else:
            # 覆盖模式
            result[key] = new_value

    return result

# 测试
state = {"history": [], "current": "hello"}

# 第一次更新
state = update_state(state, {"history": [1, 2], "current": "world"})
print(state)  # {'history': [1, 2], 'current': 'world'}

# 第二次更新
state = update_state(state, {"history": [3, 4], "current": "!"})
print(state)  # {'history': [1, 2, 3, 4], 'current': '!'}
#               ↑ 追加      ↑ 覆盖
