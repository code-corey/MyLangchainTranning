from typing import Annotated, TypedDict
import operator

class WithAnnotation(TypedDict):
    # 有 Annotated：追加
    messages: Annotated[list, operator.add]

class WithoutAnnotation(TypedDict):
    # 无 Annotated：覆盖
    messages: list

# 模拟 LangGraph 的 3 步更新
def run_example(state_class, updates):
    state = {"messages": []}
    print(f"状态类: {state_class.__name__}")

    for i, update in enumerate(updates, 1):
        if state_class == WithAnnotation:
            # 追加模式
            state["messages"] = state["messages"] + update
        else:
            # 覆盖模式
            state["messages"] = update
        
        print(f"  步骤{i}后: {state['messages']}")
    print()

# 测试3次更新
updates = [
    ["用户: 你好"],
    ["AI: 你好！需要帮助吗？"],
    ["用户: 天气怎么样？"]
]

run_example(WithAnnotation, updates)
# 输出：
# 步骤1后: ['用户: 你好']
# 步骤2后: ['用户: 你好', 'AI: 你好！需要帮助吗？']
# 步骤3后: ['用户: 你好', 'AI: 你好！需要帮助吗？', '用户: 天气怎么样？']

run_example(WithoutAnnotation, updates)
# 输出：
# 步骤1后: ['用户: 你好']
# 步骤2后: ['AI: 你好！需要帮助吗？']  ← 丢失了步骤1
# 步骤3后: ['用户: 天气怎么样？']      ← 丢失了步骤1、2
