import numpy as np

arr = np.arange(6)   # [0 1 2 3 4 5]
print("原始一维:", arr)

# 重塑为 2x3 矩阵
reshaped = arr.reshape(2, 3)
print("重塑为 2x3:\n", reshaped)

# 展平为一维 (返回新数组)
flattened = reshaped.flatten()
print("flatten 展平:", flattened)

# 更高效的 ravel (尽可能返回视图)
raveled = reshaped.ravel()
print("ravel 展平:", raveled)

# 转置 (行列互换)
transposed = reshaped.T
print("转置:\n", transposed)


"""
解释：
reshape() 不改变数据总量，只改变视图（条件允许时）。

flatten() 总是返回新副本；

ravel() 试图返回视图，更高效。

.T 是转置的快捷属性，对二维矩阵很实用

"""