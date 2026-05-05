import numpy as np

# 生成一个 3 行 4 列的随机整数 (0~100)
np.random.seed(42)
data = np.random.randint(0, 100, size=(3, 4))
print("原始数据:\n", data)

# 全局统计
print("总和:", np.sum(data))
print("平均值:", np.mean(data))
print("标准差:", np.std(data))

# 按列统计 (axis=0: 跨行)
print("每列的平均值:", np.mean(data, axis=0))

# 按行统计 (axis=1: 跨列)
print("每行的总和:", np.sum(data, axis=1))


"""
解释：axis 参数非常关键 —— 

axis=0 表示沿着行方向操作（即垂直压缩，结果维度减少一行）
axis=1 表示沿着列方向操作。
不指定 axis 则对全部元素聚合

"""