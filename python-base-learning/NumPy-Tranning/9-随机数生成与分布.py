import numpy as np

# 设置随机种子，保证结果可复现
np.random.seed(42)

# 均匀分布 [0,1) 的 2x3 数组
uniform_arr = np.random.rand(2, 3)
print("均匀分布:\n", uniform_arr)

# 标准正态分布 (均值0，方差1)
normal_arr = np.random.randn(3, 3)
print("\n标准正态分布:\n", normal_arr)

# 指定范围的随机整数 [low, high)
int_arr = np.random.randint(10, 21, size=(2, 4))
print("\n随机整数 10~20:\n", int_arr)

# 二项分布 (10次试验，成功概率0.5，形状2x3)
binomial_arr = np.random.binomial(n=10, p=0.5, size=(2, 3))
print("\n二项分布:\n", binomial_arr)


"""
目的：生成符合不同概率分布的随机数据，用于模拟或初始化

解释：np.random.rand() 输出 [0,1) 均匀分布；

randn() 输出标准正态分布；
randint(low, high, size) 输出整数。
binomial 模拟抛硬币成功次数。
通过 seed(42) 固定随机数序列，便于调试
"""