import numpy as np
import matplotlib.pyplot as plt
from sklearn.neural_network import MLPClassifier
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler

# 设置中文
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 1. 加载数据
digits = load_digits()
X = digits.data
y = digits.target

print("="*60)
print("监督学习 - 神经网络手写数字识别")
print("="*60)
print(f"样本数: {len(X)}")
print(f"特征数: {X.shape[1]}")
print(f"类别数: {len(np.unique(y))}")

# 2. 标准化
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 3. 划分数据
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42
)

# 4. 训练神经网络
mlp = MLPClassifier(
    hidden_layer_sizes=(100, 50),  # 两层隐藏层
    activation='relu',
    solver='adam',
    max_iter=300,
    random_state=42,
    early_stopping=True,
    validation_fraction=0.1
)

print("\n训练神经网络...")
mlp.fit(X_train, y_train)

# 5. 评估
train_score = mlp.score(X_train, y_train)
test_score = mlp.score(X_test, y_test)

print(f"\n训练集准确率: {train_score:.2%}")
print(f"测试集准确率: {test_score:.2%}")

# 6. 预测
y_pred = mlp.predict(X_test)

print("\n分类报告:")
print(classification_report(y_test, y_pred))

# 7. 可视化
fig, axes = plt.subplots(2, 3, figsize=(14, 10))

# 混淆矩阵
cm = confusion_matrix(y_test, y_pred)
im = axes[0, 0].imshow(cm, cmap='Blues')
axes[0, 0].set_xlabel('预测标签')
axes[0, 0].set_ylabel('真实标签')
axes[0, 0].set_title('混淆矩阵')
plt.colorbar(im, ax=axes[0, 0])

# 显示预测错误的样本
misclassified = np.where(y_pred != y_test)[0]
axes[0, 1].axis('off')
axes[0, 1].text(0.1, 0.9, f'识别错误的数字: {len(misclassified)}个',
                fontsize=12, fontweight='bold')

for i, idx in enumerate(misclassified[:8]):
    ax = plt.subplot(2, 4, i+5)  # 从第5个位置开始
    ax.imshow(X_test[idx].reshape(8, 8), cmap='gray')
    ax.set_title(f'真:{y_test[idx]}, 预:{y_pred[idx]}', fontsize=8)
    ax.axis('off')

plt.suptitle('神经网络识别结果')

# 学习曲线
plt.figure(figsize=(10, 6))
plt.plot(mlp.loss_curve_, 'b-', linewidth=2)
plt.xlabel('迭代次数')
plt.ylabel('损失值')
plt.title('神经网络学习曲线')
plt.grid(True, alpha=0.3)
plt.show()

# 8. 不同隐藏层大小的影响
hidden_layer_sizes = [(50,), (100,), (50, 25), (100, 50)]
accuracies = []

for hidden in hidden_layer_sizes:
    mlp_temp = MLPClassifier(hidden_layer_sizes=hidden, max_iter=300,
                             random_state=42, early_stopping=True)
    mlp_temp.fit(X_train, y_train)
    accuracies.append(mlp_temp.score(X_test, y_test))

# 可视化对比
fig2, ax = plt.subplots(figsize=(10, 6))
layer_names = ['50', '100', '50-25', '100-50']
ax.bar(layer_names, accuracies, color='steelblue')
ax.set_xlabel('网络结构')
ax.set_ylabel('测试准确率')
ax.set_title('不同神经网络结构性能对比')
ax.set_ylim(0.9, 1.0)
for i, acc in enumerate(accuracies):
    ax.text(i, acc + 0.002, f'{acc:.3f}', ha='center')
plt.show()

print(f"\n最佳网络结构: {hidden_layer_sizes[np.argmax(accuracies)]}")
print(f"最佳准确率: {max(accuracies):.3f}")