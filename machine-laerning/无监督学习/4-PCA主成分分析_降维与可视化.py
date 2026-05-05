import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.datasets import load_digits, load_iris
from sklearn.preprocessing import StandardScaler

# 设置中文
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 1. 加载高维数据（手写数字数据集，64维）
digits = load_digits()
X = digits.data  # 1797个样本，64个特征
y = digits.target  # 真实标签（但PCA不需要）

print("原始数据形状:", X.shape)

# 2. 标准化数据
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 3. 应用PCA
pca = PCA()
X_pca = pca.fit_transform(X_scaled)

# 4. 分析解释方差
explained_variance_ratio = pca.explained_variance_ratio_
cumulative_variance = np.cumsum(explained_variance_ratio)

# 5. 可视化
fig, axes = plt.subplots(2, 3, figsize=(15, 10))

# 累计方差解释率图
axes[0, 0].plot(range(1, len(cumulative_variance) + 1), cumulative_variance, 'bo-')
axes[0, 0].axhline(y=0.95, color='r', linestyle='--', label='95%方差')
axes[0, 0].set_xlabel('主成分数量')
axes[0, 0].set_ylabel('累计方差解释率')
axes[0, 0].set_title('PCA主成分累计方差')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

# 各主成分方差解释率
axes[0, 1].bar(range(1, 21), explained_variance_ratio[:20])
axes[0, 1].set_xlabel('主成分')
axes[0, 1].set_ylabel('方差解释率')
axes[0, 1].set_title('前20个主成分方差贡献')
axes[0, 1].set_xticks(range(1, 21))

# 2D可视化（前两个主成分）
pca_2d = PCA(n_components=2)
X_pca_2d = pca_2d.fit_transform(X_scaled)

scatter = axes[0, 2].scatter(X_pca_2d[:, 0], X_pca_2d[:, 1],
                             c=digits.target, cmap='tab10', s=20, alpha=0.6)
axes[0, 2].set_xlabel('第一主成分')
axes[0, 2].set_ylabel('第二主成分')
axes[0, 2].set_title('手写数字2D可视化（无监督降维）')
plt.colorbar(scatter, ax=axes[0, 2])

# 3D可视化
from mpl_toolkits.mplot3d import Axes3D

pca_3d = PCA(n_components=3)
X_pca_3d = pca_3d.fit_transform(X_scaled)

ax_3d = fig.add_subplot(2, 3, 4, projection='3d')
scatter_3d = ax_3d.scatter(X_pca_3d[:, 0], X_pca_3d[:, 1], X_pca_3d[:, 2],
                           c=digits.target, cmap='tab10', s=20, alpha=0.6)
ax_3d.set_xlabel('PC1')
ax_3d.set_ylabel('PC2')
ax_3d.set_zlabel('PC3')
ax_3d.set_title('手写数字3D可视化')
plt.colorbar(scatter_3d, ax=ax_3d, shrink=0.5)

# 原始数据 vs 降维后重构
n_components_95 = np.argmax(cumulative_variance >= 0.95) + 1
pca_95 = PCA(n_components=n_components_95)
X_pca_95 = pca_95.fit_transform(X_scaled)
X_reconstructed = pca_95.inverse_transform(X_pca_95)

# 显示原始和重构的图像
axes[1, 0].axis('off')
axes[1, 0].text(0.1, 0.9, f'用{n_components_95}个主成分保留95%方差', fontsize=10, fontweight='bold')

for i in range(4):
    # 原始图像
    axes[1, 1].imshow(X[i].reshape(8, 8), cmap='gray')
    axes[1, 1].set_title(f'原始{i}')
    axes[1, 1].axis('off')

    # 重构图像
    axes[1, 2].imshow(X_reconstructed[i].reshape(8, 8), cmap='gray')
    axes[1, 2].set_title(f'重构{i}')
    axes[1, 2].axis('off')

plt.tight_layout()
plt.show()

print(f"\n保留95%方差需要的主成分数: {n_components_95}")
print(f"数据从64维降到{n_components_95}维，压缩了{(1 - n_components_95 / 64) * 100:.1f}%")