import numpy as np

# 生成两个大数组
x = np.linspace(0, 2*np.pi, 1000)
y = np.sin(x)   # 对每个元素计算正弦 (向量化)

# 向量化加法和条件判断
a = np.array([1, 2, 3, 4])
b = np.array([10, 20, 30, 40])
print("a + b =", a + b)          # 逐元素相加
print("a * b =", a * b)          # 逐元素相乘 (不是矩阵乘)
print("a > 2:", a > 2)           # 返回布尔数组

# 通用函数: 求平方根和指数
print("平方根:", np.sqrt(a))
print("e 的幂:", np.exp(a))


"""
目的：用向量化代替 Python 循环，大幅提升计算速度。

解释：

通用函数对数组的每个元素执行快速运算，
底层用 C 实现，比 Python 循环快 10~100 倍。
运算符 + - * / > 等都被重载为 ufunc。
np.sin、np.sqrt 等也是 ufunc。
"""