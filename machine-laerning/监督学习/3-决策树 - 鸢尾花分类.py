import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix
import pandas as pd

# 设置中文
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 1. 加载经典数据集（带标签）
iris = load_iris()
X = iris.data  # 特征：花萼长宽、花瓣长宽
y = iris.target  # 标签：3种鸢尾花

print("="*60)
print("监督学习 - 决策树鸢尾花分类")
print("="*60)
print(f"特征: {iris.feature_names}")
print(f"标签: {iris.target_names}")
print(f"样本数: {len(X)}")

# 创建DataFrame查看数据
df = pd.DataFrame(X, columns=iris.feature_names)
df['species'] = y
print("\n数据预览:")
print(df.head())

# 2. 划分数据
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

# 3. 训练决策树（限制深度避免过拟合）
dt = DecisionTreeClassifier(max_depth=3, random_state=42)
dt.fit(X_train, y_train)

# 4. 预测
y_pred = dt.predict(X_test)

# 5. 评估
accuracy = accuracy_score(y_test, y_pred)
print(f"\n模型准确率: {accuracy:.2%}")

print("\n分类报告:")
from sklearn.metrics import classification_report
print(classification_report(y_test, y_pred, target_names=iris.target_names))

# 6. 可视化
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 决策树结构
plot_tree(dt, feature_names=iris.feature_names,
          class_names=iris.target_names,
          filled=True, rounded=True, ax=axes[0, 0], fontsize=8)
axes[0, 0].set_title('决策树可视化', fontsize=12)

# 特征重要性
importance = dt.feature_importances_
axes[0, 1].barh(iris.feature_names, importance, color='coral')
axes[0, 1].set_xlabel('重要性')
axes[0, 1].set_title('特征重要性')

# 混淆矩阵
cm = confusion_matrix(y_test, y_pred)
im = axes[1, 0].imshow(cm, cmap='Blues')
axes[1, 0].set_xticks(range(3))
axes[1, 0].set_yticks(range(3))
axes[1, 0].set_xticklabels(iris.target_names)
axes[1, 0].set_yticklabels(iris.target_names)
axes[1, 0].set_xlabel('预测标签')
axes[1, 0].set_ylabel('真实标签')
axes[1, 0].set_title('混淆矩阵')

for i in range(3):
    for j in range(3):
        axes[1, 0].text(j, i, cm[i, j], ha='center', va='center')

plt.colorbar(im, ax=axes[1, 0])

# 决策边界（取两个最重要的特征）
important_features = [0, 2]  # 花萼长度和花瓣长度
X_2d = X[:, important_features]
dt_2d = DecisionTreeClassifier(max_depth=3, random_state=42)
dt_2d.fit(X_2d, y)

# 绘制决策边界
x_min, x_max = X_2d[:, 0].min() - 0.5, X_2d[:, 0].max() + 0.5
y_min, y_max = X_2d[:, 1].min() - 0.5, X_2d[:, 1].max() + 0.5
xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.02),
                     np.arange(y_min, y_max, 0.02))
Z = dt_2d.predict(np.c_[xx.ravel(), yy.ravel()])
Z = Z.reshape(xx.shape)

axes[1, 1].contourf(xx, yy, Z, alpha=0.4, cmap='Set3')
scatter = axes[1, 1].scatter(X_2d[:, 0], X_2d[:, 1], c=y, cmap='viridis', edgecolors='black')
axes[1, 1].set_xlabel(iris.feature_names[0])
axes[1, 1].set_ylabel(iris.feature_names[2])
axes[1, 1].set_title('决策边界（基于两个最重要特征）')
plt.colorbar(scatter, ax=axes[1, 1], ticks=[0, 1, 2], label='类别')

plt.tight_layout()
plt.show()

# 7. 预测新样本
print("\n预测新鸢尾花:")
new_flowers = np.array([
    [5.1, 3.5, 1.4, 0.2],  # 类似山鸢尾
    [6.5, 3.0, 5.5, 1.8],  # 类似维吉尼亚鸢尾
    [5.9, 3.0, 4.2, 1.5]   # 类似变色鸢尾
])

predictions = dt.predict(new_flowers)
probas = dt.predict_proba(new_flowers)

for i, flower in enumerate(new_flowers):
    species = iris.target_names[predictions[i]]
    prob = probas[i][predictions[i]]
    print(f"花{i+1}: {flower}")
    print(f"  预测: {species}, 置信度: {prob:.2%}\n")