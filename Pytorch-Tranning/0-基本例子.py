import torch

print(torch.cuda.is_available())

x = torch.rand(5, 3)
print(x)


# 这是一个 2x3 的张量
t = torch.tensor([[1, 2, 3],
                  [4, 5, 6]])

print(f"形状: {t.shape}")    # torch.Size([2, 3])
print(f"维度: {t.ndim}")     # 2
print(f"数据类型: {t.dtype}") # torch.int64

# 张量可以自动求导（深度学习训练的基础）
x = torch.tensor([2.0], requires_grad=True)
y = x ** 2
y.backward()  # 自动计算 dy/dx
print(x.grad) # tensor([4.])，导数 2x = 4