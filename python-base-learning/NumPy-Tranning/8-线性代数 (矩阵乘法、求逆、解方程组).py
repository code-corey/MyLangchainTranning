import numpy as np

# 定义两个 2x2 矩阵
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])

# 矩阵乘法 (点积)
C = np.dot(A, B)   # 或 A @ B
print("A @ B =\n", C)

# 求逆矩阵 (必须方阵且非奇异)
A_inv = np.linalg.inv(A)
print("A 的逆:\n", A_inv)

# 验证: A * A_inv 应该接近单位阵
print("A * A_inv =\n", np.dot(A, A_inv))

# 解线性方程组:
# 2x + y = 5
# 3x + 2y = 8
coeff = np.array([[2, 1], [3, 2]])
const = np.array([5, 8])
solution = np.linalg.solve(coeff, const)
print("方程组的解: x =", solution[0], "y =", solution[1])


"""
目的：用 NumPy 进行基础线性代数计算。

解释：np.dot() 或 @ 执行真正的矩阵乘法（不是逐元素乘）。

np.linalg.inv() 计算逆矩阵。

np.linalg.solve() 解线性方程组，比先求逆再相乘更高效且数值稳定
"""