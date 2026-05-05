import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from sklearn.datasets import load_digits, fetch_openml
from sklearn.preprocessing import StandardScaler

# 设置中文
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 1. 加载数据
print("加载MNIST数据集...")
# 使用较小的子集节省时间
from sklearn.datasets import fetch_openml
X, y = fetch_openml('mnist_784', version=1, return_X_y=True, as_frame=False, parser='pandas')
X = X[:2000]  # 只用2000个样本
y = y[:2000].astype(int)

print(f"数据形状: {X.shape}")
print(f"这是784维的图像数据")

# 2. 标准化
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 3. 先用PCA降到50维（加速t-SNE）
from sklearn.decomposition import PCA
pca = PCA(n_components=50)
X_pca = pca.fit_transform(X_scaled)

# 4. 应用t-SNE
print("运行t-SNE（可能需要几秒钟）...")
tsne = TSNE(n_components=2, random_state=42, perplexity=30)
X_tsne = tsne.fit_transform(X_pca)

# 5. 可视化
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# t-SNE可视化
scatter1 = axes[0].scatter(X_tsne[:, 0], X_tsne[:, 1], c=y, cmap='tab10', s=10, alpha=0.6)
axes[0].set_title('t-SNE可视化（数字聚类效果）', fontsize=12)
axes[0].set_xlabel('t-SNE维度1')
axes[0].set_ylabel('t-SNE维度2')
plt.colorbar(scatter1, ax=axes[0], label='数字类别')

# 对比：PCA可视化
pca_vis = PCA(n_components=2)
X_pca_vis = pca_vis.fit_transform(X_scaled)
scatter2 = axes[1].scatter(X_pca_vis[:, 0], X_pca_vis[:, 1], c=y, cmap='tab10', s=10, alpha=0.6)
axes[1].set_title('PCA可视化（对比）', fontsize=12)
axes[1].set_xlabel('第一主成分')
axes[1].set_ylabel('第二主成分')
plt.colorbar(scatter2, ax=axes[1], label='数字类别')

plt.tight_layout()
plt.show()

# 6. 显示一些典型样本
fig2, axes2 = plt.subplots(2, 5, figsize=(12, 5))
for i, digit in enumerate(range(10)):
    # 找到每个数字的一个代表
    idx = np.where(y == digit)[0][0]
    axes2[i // 5, i % 5].imshow(X[idx].reshape(28, 28), cmap='gray')
    axes2[i // 5, i % 5].set_title(f'数字{digit}')
    axes2[i // 5, i % 5].axis('off')

plt.suptitle('MNIST手写数字样本', fontsize=14)
plt.tight_layout()
plt.show()

print("\n观察：t-SNE能够很好地将不同数字分开")
print("虽然t-SNE是无监督的，但自动发现了数字的内在类别结构")