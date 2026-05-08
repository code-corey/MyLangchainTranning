import torch
import numpy as np

print("="*50)
print("Demo 1: Tensor 创建方法")
print("="*50)

# 1. 从列表创建
tensor_from_list = torch.tensor([[1, 2, 3], [4, 5, 6]])
print(f"从列表创建:\n{tensor_from_list}\n")

# 2. 全零张量
zeros_tensor = torch.zeros(2, 3)
print(f"全零张量 (2x3):\n{zeros_tensor}\n")

# 3. 全一张量
ones_tensor = torch.ones(2, 3)
print(f"全一张量 (2x3):\n{ones_tensor}\n")

# 4. 随机正态分布
randn_tensor = torch.randn(2, 3)
print(f"随机正态分布 (2x3):\n{randn_tensor}\n")

# 5. 指定范围的均匀分布
rand_tensor = torch.rand(2, 3)  # [0, 1) 均匀分布
print(f"均匀分布 (0-1):\n{rand_tensor}\n")

# 6. 等差序列
arange_tensor = torch.arange(0, 10, 2)  # start, end, step
print(f"等差序列: {arange_tensor}\n")

# 7. 单位矩阵
eye_tensor = torch.eye(3)
print(f"单位矩阵 (3x3):\n{eye_tensor}\n")


"""
1维Tensor：一行数据 [A1, B1, C1, D1]
2维Tensor：整个表格（行+列）
3维Tensor：多个表格叠在一起（像便利贴本）
4维Tensor：多个便利贴本放在一起

"""