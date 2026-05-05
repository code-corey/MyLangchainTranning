import numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
import pandas as pd

# 设置中文
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 1. 生成用户-电影评分数据
np.random.seed(42)
n_users = 500
n_features = 10  # 电影特征维度

# 特征：动作、喜剧、爱情、科幻等维度的偏好
X = np.random.randn(n_users, n_features) * 0.5

# 标签：用户喜欢的电影类型（多分类）
# 0:动作片, 1:喜剧片, 2:爱情片, 3:科幻片
y = np.zeros(n_users, dtype=int)

# 根据特征生成标签
X[:, 0] > 0.2, y = X[:, 0] > 0.2, 0  # 动作
X[:, 1] > 0.2, y = X[:, 1] > 0.2, 1  # 喜剧
X[:, 2] > 0.2, y = X[:, 2] > 0.2, 2  # 爱情
X[:, 3] > 0.2, y = X[:, 3] > 0.2, 3  # 科幻

print("="*60)
print("监督学习 - KNN电影推荐系统")
print("="*60)
print(f"用户数: {n_users}")
print(f"特征数: {n_features} (电影属性维度)")

# 2. 标准化特征
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 3. 划分数据
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42
)

# 4. 选择最佳K值
k_range = range(1, 31)
cv_scores = []

for k in k_range:
    knn = KNeighborsClassifier(n_neighbors=k)
    scores = cross_val_score(knn, X_train, y_train, cv=5)
    cv_scores.append(scores.mean())

best_k = k_range[np.argmax(cv_scores)]
print(f"\n最佳K值: {best_k}")
print(f"最佳交叉验证准确率: {max(cv_scores):.3f}")

# 5. 训练最佳模型
knn_best = KNeighborsClassifier(n_neighbors=best_k)
knn_best.fit(X_train, y_train)

# 6. 测试
y_pred = knn_best.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"测试集准确率: {accuracy:.3f}")

# 7. 可视化
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# K值影响
axes[0, 0].plot(k_range, cv_scores, 'bo-', linewidth=2)
axes[0, 0].axvline(x=best_k, color='red', linestyle='--', label=f'最佳K={best_k}')
axes[0, 0].set_xlabel('K值（邻居数量）')
axes[0, 0].set_ylabel('交叉验证准确率')
axes[0, 0].set_title('K值选择对性能的影响')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

# 决策边界可视化（取前两个特征）
X_2d = X_scaled[:, :2]
knn_2d = KNeighborsClassifier(n_neighbors=best_k)
knn_2d.fit(X_2d, y)

# 绘制决策边界
x_min, x_max = X_2d[:, 0].min() - 0.5, X_2d[:, 0].max() + 0.5
y_min, y_max = X_2d[:, 1].min() - 0.5, X_2d[:, 1].max() + 0.5
xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.05),
                     np.arange(y_min, y_max, 0.05))
Z = knn_2d.predict(np.c_[xx.ravel(), yy.ravel()])
Z = Z.reshape(xx.shape)

axes[0, 1].contourf(xx, yy, Z, alpha=0.4, cmap='Set3')
scatter = axes[0, 1].scatter(X_2d[:, 0], X_2d[:, 1], c=y, cmap='tab10', s=30, alpha=0.6)
axes[0, 1].set_xlabel('偏好维度1')
axes[0, 1].set_ylabel('偏好维度2')
axes[0, 1].set_title('KNN决策边界')
plt.colorbar(scatter, ax=axes[0, 1], ticks=[0, 1, 2, 3], label='电影类型')

# 错误分析
misclassified = X_test[y_pred != y_test]
axes[1, 0].scatter(misclassified[:, 0], misclassified[:, 1],
                   c='red', marker='x', s=100, label='错误分类')
axes[1, 0].scatter(X_test[y_pred == y_test][:, 0], X_test[y_pred == y_test][:, 1],
                   c='green', alpha=0.3, label='正确分类')
axes[1, 0].set_xlabel('特征1')
axes[1, 0].set_ylabel('特征2')
axes[1, 0].set_title('错误分类分析')
axes[1, 0].legend()

# 距离权重影响
distances = knn_best.kneighbors(X_test)[0]
avg_distances = distances.mean(axis=1)
axes[1, 1].hist(avg_distances[y_pred == y_test], bins=20, alpha=0.7,
                label='正确分类', color='green')
axes[1, 1].hist(avg_distances[y_pred != y_test], bins=20, alpha=0.7,
                label='错误分类', color='red')
axes[1, 1].set_xlabel('平均到邻居的距离')
axes[1, 1].set_ylabel('频数')
axes[1, 1].set_title('距离与分类正确性关系')
axes[1, 1].legend()

plt.tight_layout()
plt.show()

# 8. 推荐系统示例
print("\n电影推荐系统:")
print("-"*40)

# 新用户特征
new_user = np.array([[0.5, -0.2, 0.3, 0.1, -0.1, 0.2, 0.4, -0.3, 0.2, 0.1]])
new_user_scaled = scaler.transform(new_user)

# 找到相似用户
distances, indices = knn_best.kneighbors(new_user_scaled, n_neighbors=5)
similar_users = indices[0]
genre_names = ['动作片', '喜剧片', '爱情片', '科幻片']

print(f"新用户偏好向量: {new_user[0][:4]}")
print(f"\n找到{len(similar_users)}个相似用户:")
for i, user_idx in enumerate(similar_users):
    user_genre = genre_names[y[user_idx]]
    print(f"  相似用户{i+1}: 喜欢{user_genre}, 距离={distances[0][i]:.3f}")

# 推荐
predicted_genre = genre_names[knn_best.predict(new_user_scaled)[0]]
print(f"\n推荐电影类型: {predicted_genre}")