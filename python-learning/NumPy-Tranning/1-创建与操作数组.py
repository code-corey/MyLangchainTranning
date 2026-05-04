import numpy as np

# 从列表创建一维数组
a = np.array([1, 2, 3, 4, 5])
# 创建全零的 2x3 矩阵
b = np.zeros((2, 3))
# 创建从 0 到 1 的 5 个等间距点
c = np.linspace(0, 1, 5)

print("数组 a:", a)
print("数组 b:\n", b)
print("数组 c:", c)

# 查看形状 (shape)、维度 (ndim)、数据类型 (dtype)
print("a 的形状:", a.shape, "维度:", a.ndim, "类型:", a.dtype)

"""
解释：

NumPy 的核心是 ndarray（N维数组）。

np.array() 从 Python 列表转换；

np.zeros() 生成全 0 矩阵；
np.linspace() 生成等差数列。
.shape 返回各维度大小，
.ndim 返回维度数，
.dtype 指出元素类型。
"""