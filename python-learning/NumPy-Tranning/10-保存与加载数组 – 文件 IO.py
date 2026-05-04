import numpy as np

# 创建一些数据
a = np.arange(20).reshape(4, 5)
b = np.random.randn(10)

print("my_array.npy：",a)

# 保存单个数组为 .npy 文件 (二进制)
np.save('my_array.npy', a)

# 加载
loaded_a = np.load('my_array.npy')
print("加载的数组形状:", loaded_a.shape)
print("前两行:\n", loaded_a[:2])

# 保存多个数组为压缩的 .npz 文件
np.savez('my_data.npz', first=a, second=b)

# 加载 .npz (类字典对象)
data = np.load('my_data.npz')
print("\n文件中包含的键:", list(data.keys()))
print("second 数组的前5个元素:", data['second'][:5])

# 可选: 保存为文本格式 (如 CSV) 用于与其他软件交互
np.savetxt('output.csv', a, delimiter=',', fmt='%d')

"""
目的：将 NumPy 数组持久化保存到硬盘，并重新加载

解释：
.npy 和 .npz 是 NumPy 专有格式，读写极快且无损。

.npy 存一个数组，.npz 可存多个（压缩）。

savetxt 可导出为 CSV 等文本格式，但速度慢且文件大。

加载 .npz 返回类字典对象，通过键名访问数组。
"""