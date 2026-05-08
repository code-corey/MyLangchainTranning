import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision.transforms import v2

# Download training data from open datasets.
training_data = datasets.FashionMNIST(
    root="data",  # 保存位置
    train=True,  # 训练集
    download=True,
    transform=v2.Compose([v2.ToImage(), v2.ToDtype(torch.float32, scale=True)]),
)

"""
# v2.Compose
v2.Compose([...]) 把多个转换操作打包成一个流水线，按顺序依次执行。


# v2.ToImage()
作用：把PIL图像或NumPy数组转换成PyTorch张量(Tensor)

原始数据：PIL Image 对象（例如 <PIL.Image.Image>）
转换后：PyTorch Tensor，形状为 (H, W) 或 (H, W, C)
注意：此时数据类型和数值范围没有变化

# v2.ToDtype(torch.float32, scale=True)
作用：转换数据类型并缩放数值
torch.float32  目标数据类型（32位浮点数）
scale=True  自动缩放到 [0, 1] 范围

归一化	将 0-255 压缩到 0-1，数值更小，模型训练更稳定

比如原始数据
tensor([[  0,  12,  35, ..., 255],
        [ 45,  67,  89, ..., 200],
        ...])  # dtype=torch.uint8 (0-255的整数)

再经过   v2.ToDtype(torch.float32, scale=True)：       

tensor([[0.0000, 0.0471, 0.1373, ..., 1.0000],
        [0.1765, 0.2627, 0.3490, ..., 0.7843],
        ...])  # dtype=torch.float32 (0.0-1.0的浮点数)
        
为什么使用 torch.float32 = 32位浮点数，是PyTorch的默认计算精度

所有模型的权重、梯度、输入输出都主要用这个类型

它牺牲一点存储空间（相比uint8变大4倍），换来能够表示连续的小数，这是深度学习必需的    

为什么神经网络必须用 float32？

# 1. 梯度下降需要小数
权重更新： w = w - 0.001 × 梯度
                 ↑ 学习率是小数的
# 2. 概率值是小数的
softmax输出：[0.1, 0.7, 0.2]  # 都是小数
# 3. 除法会产生小数
归一化： 128 / 255 = 0.50196...  # 不是整数    
"""

# Download test data from open datasets.
test_data = datasets.FashionMNIST(
    root="data",
    train=False,
    download=True,
    transform=v2.Compose([v2.ToImage(), v2.ToDtype(torch.float32, scale=True)]),
)


batch_size = 64

# Create data loaders.
train_dataloader = DataLoader(training_data, batch_size=batch_size)
test_dataloader = DataLoader(test_data, batch_size=batch_size)

for X, y in test_dataloader:
    print(f"Shape of X [N, C, H, W]: {X.shape}")
    print(f"Shape of y: {y.shape} {y.dtype}")
    break



device = torch.accelerator.current_accelerator().type if torch.accelerator.is_available() else "cpu"
print(f"Using {device} device")

# Define model
class NeuralNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        self.flatten = nn.Flatten()
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(28*28, 512),
            nn.ReLU(),
            nn.Linear(512, 512),
            nn.ReLU(),
            nn.Linear(512, 10)
        )

    def forward(self, x):
        x = self.flatten(x)
        logits = self.linear_relu_stack(x)
        return logits

model = NeuralNetwork().to(device)
print(model)