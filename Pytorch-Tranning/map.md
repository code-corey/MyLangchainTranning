# PyTorch 系统学习清单

## 第一阶段：基础入门（1-2周）

### 1. PyTorch 基础概念
- [ ] Tensor 的创建和基本操作
  - `torch.tensor()`, `torch.zeros()`, `torch.ones()`, `torch.randn()`
  - Tensor 的属性：`shape`, `dtype`, `device`
  - Tensor 与 NumPy 的转换：`numpy()`, `from_numpy()`
- [ ] 数据类型和精度
  - `float32`, `float64`, `int64`, `bool`
  - 精度设置和转换：`.to(dtype=torch.float32)`
- [ ] 设备管理
  - CPU vs GPU：`.to(device)`, `cuda()`
  - 多GPU基础：`torch.cuda.device_count()`

### 2. Tensor 操作
- [ ] 索引和切片（类似NumPy）
- [ ] 形状操作：`reshape()`, `view()`, `squeeze()`, `unsqueeze()`, `permute()`
- [ ] 数学运算
  - 逐元素运算：`+`, `-`, `*`, `/`, `**`
  - 矩阵运算：`torch.mm()`, `torch.matmul()`, `@`
  - 广播机制
- [ ] 聚合操作：`sum()`, `mean()`, `max()`, `min()`, `argmax()`

### 3. 自动微分机制
- [ ] `requires_grad` 参数理解
- [ ] 计算图概念
- [ ] 反向传播：`.backward()`
- [ ] 梯度访问：`.grad`
- [ ] 梯度清零：`.zero_grad()`
- [ ] 禁用梯度计算：`with torch.no_grad()`

---

## 第二阶段：神经网络基础（2-3周）

### 4. `torch.nn` 模块
- [ ] `nn.Module` 基类
  - 自定义网络结构
  - `__init__` 和 `forward` 方法
- [ ] 常用层（Layers）
  - 线性层：`nn.Linear`
  - 卷积层：`nn.Conv1d/2d/3d`
  - 池化层：`nn.MaxPool2d`, `nn.AvgPool2d`
  - 归一化层：`nn.BatchNorm1d/2d`, `nn.LayerNorm`
  - 激活函数：`nn.ReLU`, `nn.Sigmoid`, `nn.Tanh`, `nn.GELU`
  - Dropout：`nn.Dropout`
  - Embedding：`nn.Embedding`

### 5. 损失函数
- [ ] 回归任务：`MSELoss`, `L1Loss`
- [ ] 分类任务：`CrossEntropyLoss`, `BCELoss`, `BCEWithLogitsLoss`
- [ ] 其他：`NLLLoss`, `KLDivLoss`

### 6. 优化器
- [ ] 基础优化器：SGD, Adam, AdamW, RMSprop
- [ ] 学习率调度
  - `StepLR`, `MultiStepLR`
  - `ReduceLROnPlateau`
  - `CosineAnnealingLR`
- [ ] 参数组管理

### 7. 数据加载
- [ ] Dataset 类
  - 自定义 Dataset
  - 内置数据集：`torchvision.datasets`
- [ ] DataLoader
  - `batch_size`, `shuffle`, `num_workers`
  - `collate_fn` 自定义批处理
- [ ] 数据转换：`torchvision.transforms`

---

## 第三阶段：训练流程（2周）

### 8. 完整训练循环
- [ ] 训练模式 vs 评估模式：`model.train()`, `model.eval()`
- [ ] 典型训练流程
  ```python
  for epoch in range(num_epochs):
      for batch in dataloader:
          # 前向传播
          outputs = model(inputs)
          loss = criterion(outputs, labels)
          # 反向传播
          optimizer.zero_grad()
          loss.backward()
          optimizer.step()
  ```
- [ ] 验证和测试流程
- [ ] 模型保存与加载
  - `torch.save(model.state_dict(), 'model.pth')`
  - `model.load_state_dict(torch.load('model.pth'))`

### 9. 训练技巧
- [ ] 梯度裁剪：`torch.nn.utils.clip_grad_norm_`
- [ ] 混合精度训练：`torch.cuda.amp`
- [ ] 提前停止（Early Stopping）
- [ ] 检查点（Checkpoint）保存
- [ ] TensorBoard 可视化
- [ ] 进度条库：`tqdm`

---

## 第四阶段：高级主题（3-4周）

### 10. 模型部署与优化
- [ ] TorchScript
  - `torch.jit.trace`
  - `torch.jit.script`
- [ ] ONNX 导出：`torch.onnx.export`
- [ ] 模型量化
  - 动态量化
  - 静态量化
  - QAT（Quantization-Aware Training）
- [ ] 模型剪枝：`torch.nn.utils.prune`

### 11. 分布式训练
- [ ] 数据并行：`nn.DataParallel`
- [ ] 分布式数据并行：`DistributedDataParallel`
- [ ] 混合精度分布式训练

### 12. 自定义扩展
- [ ] 自定义 autograd 函数：`torch.autograd.Function`
- [ ] 自定义 C++/CUDA 扩展
- [ ] 使用 `torch.utils.cpp_extension`

### 13. 特定领域工具
- [ ] torchvision（计算机视觉）
  - 预训练模型：`resnet50`, `vgg16` 等
  - 图像变换和增强
- [ ] torchtext（自然语言处理）
  - 文本数据处理
  - 词向量
- [ ] torchaudio（音频处理）
- [ ] torchmetrics（评估指标）

---

## 第五阶段：实战项目（4-6周）

### 14. 经典模型实现
- [ ] **MLP**：MNIST 手写数字识别
- [ ] **CNN**：CIFAR-10 图像分类
- [ ] **RNN/LSTM**：文本情感分析
- [ ] **Transformer**：机器翻译或文本生成
- [ ] **ResNet**：图像分类（从零实现残差块）
- [ ] **GAN**：生成手写数字
- [ ] **Autoencoder**：图像重建

### 15. 完整项目实践
- [ ] 图像分类系统
  - 数据增强
  - 迁移学习（微调预训练模型）
  - 模型集成
- [ ] 目标检测（YOLO/Faster R-CNN）
- [ ] 语义分割（UNet）
- [ ] 文本生成（类似你代码中的 LLM 推理）
- [ ] 推荐系统（协同过滤 + MLP）

---

## 第六阶段：性能优化（2周）

### 16. 性能调优
- [ ] 内存管理
  - 避免内存泄漏
  - 梯度检查点：`torch.utils.checkpoint`
- [ ] 速度优化
  - 数据加载优化（prefetch, pin_memory）
  - 算子融合
  - 编译优化：`torch.compile`（PyTorch 2.0+）
- [ ] Profiling 工具
  - `torch.profiler`
  - 性能瓶颈分析

---

## 推荐学习资源

### 官方文档
- [PyTorch Tutorials](https://pytorch.org/tutorials/)
- [PyTorch Documentation](https://pytorch.org/docs/stable/)

### 实践项目网站
- Kaggle（PyTorch 竞赛）
- Papers with Code

### 书籍
- 《Deep Learning with PyTorch》
- 《Programming PyTorch for Deep Learning》

### 视频课程
- 李沐《动手学深度学习》（PyTorch版）
- Andrej Karpathy 的神经网络教程

---

## 学习建议

1. **循序渐进**：不要跳阶段，确保基础扎实
2. **边学边练**：每学一个概念就写代码验证
3. **项目驱动**：学完每个阶段做一个小项目
4. **阅读源码**：看 PyTorch 官方示例和模型库源码
5. **调试技巧**：学会使用 `pdb` 和打印中间结果调试
6. **性能意识**：从一开始就注意代码效率

---

## 针对你的代码，建议优先学习

基于你提供的 GLM-4 对话系统代码，建议重点关注：

1. **Tensor 操作和设备管理**（阶段1）
2. **自动微分基础**（阶段1）
3. **模型加载与保存**（阶段3）
4. **DataLoader 和批处理**（阶段3）
5. **多线程推理**（阶段4）
6. **模型部署（TorchScript/ONNX）**（阶段4）

这样可以快速理解现有代码并能够修改和优化它。