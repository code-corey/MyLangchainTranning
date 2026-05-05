import operator

# operator.add 等价于：
operator.add(1, 2)    # 3
operator.add([1,2], [3,4])  # [1,2,3,4]
operator.add("hello", " world")  # "hello world"

# 和直接用 + 一样
a= [1,2] + [3,4]  # [1,2,3,4]
print(a)
