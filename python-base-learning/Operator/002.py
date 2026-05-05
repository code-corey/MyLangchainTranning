from typing import Annotated, TypedDict
import operator

class State(TypedDict):
    messages: Annotated[list, operator.add]

# 假设当前状态
state = {"messages": ["用户: 你好"]}

# 节点返回更新
update = {"messages": ["AI: 你好！"]}

# LangGraph 内部实际执行：
state["messages"] = operator.add(state["messages"], update["messages"])

print(state["messages"])

# 等价于：
state["messages"] = ["用户: 你好"] + ["AI: 你好！"]
# 结果：
state["messages"] = ["用户: 你好", "AI: 你好！"]