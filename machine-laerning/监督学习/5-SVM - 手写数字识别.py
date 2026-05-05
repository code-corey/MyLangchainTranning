import numpy as np
import matplotlib.pyplot as plt
from sklearn import datasets
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.decomposition import PCA

# 设置中文
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 1. 加载手写数字数据集
digits = datasets.load_digits()
X = digits.data  # 64维特征（8x8图像）
y = digits.target  # 0-9的数字标签

print("=" * 60)
print("监督学习 - SVM手写数字识别")
print("=" * 60)
print(f"图像数量: {len(X)}")
print(f"图像大小: {X.shape[1]} 像素")
print(f"类别数: {len(np.unique(y))}")

# 2. 显示一些样本
fig, axes = plt.subplots(2, 5, figsize=(10, 4))
for i, ax in enumerate(axes.flat):
    ax.imshow(X[i].reshape(8, 8), cmap='gray')
    ax.set_title(f'数字: {y[i]}')
    ax.axis('off')
plt.suptitle('手写数字样本', fontsize=14)
plt.tight_layout()
plt.show()

# 3. 划分数据
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 4. 使用PCA降维加速
pca = PCA(n_components=30)
X_train_pca = pca.fit_transform(X_train)
X_test_pca = pca.transform(X_test)

print(f"\n降维后特征数: {X_train_pca.shape[1]}")

# 5. 训练SVM（使用RBF核）
svm = SVC(kernel='rbf', random_state=42)
svm.fit(X_train_pca, y_train)

# 6. 预测
y_pred = svm.predict(X_test_pca)
accuracy = accuracy_score(y_test, y_pred)
print(f"\n基础SVM准确率: {accuracy:.2%}")

# 7. 超参数调优
print("\n进行网格搜索优化...")
param_grid = {
    'C': [0.1, 1, 10],
    'gamma': [0.001, 0.01, 0.1]
}
grid_search = GridSearchCV(SVC(kernel='rbf'), param_grid, cv=3, n_jobs=-1)
grid_search.fit(X_train_pca, y_train)

print(f"最佳参数: {grid_search.best_params_}")
print(f"最佳交叉验证分数: {grid_search.best_score_:.3f}")

# 8. 使用最佳模型
best_svm = grid_search.best_estimator_
y_pred_best = best_svm.predict(X_test_pca)
best_accuracy = accuracy_score(y_test, y_pred_best)
print(f"优化后准确率: {best_accuracy:.2%}")

# 9. 可视化
fig, axes = plt.subplots(2, 3, figsize=(14, 10))

# 混淆矩阵
cm = confusion_matrix(y_test, y_pred_best)
im = axes[0, 0].imshow(cm, cmap='Blues')
axes[0, 0].set_xticks(range(10))
axes[0, 0].set_yticks(range(10))
axes[0, 0].set_xlabel('预测标签')
axes[0, 0].set_ylabel('真实标签')
axes[0, 0].set_title('混淆矩阵')
plt.colorbar(im, ax=axes[0, 0])

# 显示预测错误的样本
misclassified = np.where(y_pred_best != y_test)[0]
axes[0, 1].axis('off')
axes[0, 1].text(0.1, 0.9, f'预测错误的样本: {len(misclassified)}个',
                fontsize=12, fontweight='bold')

for i, idx in enumerate(misclassified[:9]):
    ax = plt.subplot(2, 3, i + 4)  # 从第4个子图开始
    ax.imshow(X_test[idx].reshape(8, 8), cmap='gray')
    ax.set_title(f'真:{y_test[idx]}, 预:{y_pred_best[idx]}', fontsize=8)
    ax.axis('off')

plt.suptitle('SVM手写数字识别结果')
plt.tight_layout()
plt.show()

# 10. 学习曲线分析
print("\n不同训练集大小的表现:")
train_sizes = [0.1, 0.2, 0.3, 0.5, 0.7, 0.9]
scores = []

for size in train_sizes:
    subset_size = int(len(X_train) * size)
    X_subset = X_train_pca[:subset_size]
    y_subset = y_train[:subset_size]

    svm_sub = SVC(kernel='rbf', C=grid_search.best_params_['C'],
                  gamma=grid_search.best_params_['gamma'], random_state=42)
    svm_sub.fit(X_subset, y_subset)
    score = svm_sub.score(X_test_pca, y_test)
    scores.append(score)
    print(f"训练集比例: {size:.0%}, 准确率: {score:.2%}")