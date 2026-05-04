from langgraph.graph import StateGraph, MessagesState, START, END

def mock_llm(state: MessagesState):
    return {"messages": [{"role": "ai", "content": "hello world"}]}

graph = StateGraph(MessagesState)
graph.add_node(mock_llm)
graph.add_edge(START, "mock_llm")
graph.add_edge("mock_llm", END)
graph = graph.compile()

a= graph.invoke({"messages": [{"role": "user", "content": "hi!"}]})
print(a)

"""
{'messages': 
[
HumanMessage(content='hi!', additional_kwargs={}, response_metadata={}, id='d4a6b545-e6ce-49b3-b869-4d3b4c8155f4'), 
AIMessage(content='hello world', additional_kwargs={}, response_metadata={}, id='13cb0aae-d8f3-4797-bbed-695a28ed7515', 
tool_calls=[], invalid_tool_calls=[])]}

"""