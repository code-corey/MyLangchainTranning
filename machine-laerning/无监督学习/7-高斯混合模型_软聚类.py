import numpy as np
import matplotlib.pyplot as plt
from sklearn.mixture import GaussianMixture
from sklearn.datasets import make_blobs

# 设置中文
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 1. 生成数据（无标签）
np.random.seed(42)
n_samples = 500

# 创建4个重叠的高斯分布
data1 = np.random.randn(150, 2) * 0.8 + [-2, -2]
data2 = np.random.randn(150, 2) * 0.6 + [2, -1]
data3 = np.random.randn(100, 2) * 0.7 + [-1, 2]
data4 = np.random.randn(100, 2) * 0.5 + [2, 2]

X = np.vstack([data1, data2, data3, data4])

# 2. 应用GMM
# 尝试不同的簇数
fig, axes = plt.subplots(2, 3, figsize=(15, 10))

K_values = [2, 3, 4, 5]
for idx, K in enumerate(K_values):
    gmm = GaussianMixture(n_components=K, random_state=42)
    gmm.fit(X)
    labels = gmm.predict(X)
    probs = gmm.predict_proba(X)  # 每个点属于各个簇的概率

    # 硬聚类结果
    axes[0, idx].scatter(X[:, 0], X[:, 1], c=labels, cmap='viridis', s=30, alpha=0.6)
    axes[0, idx].set_title(f'K={K} (硬聚类)')
    axes[0, idx].set_xticks([])
    axes[0, idx].set_yticks([])

    # 软聚类（颜色表示属于某个簇的概率）
    max_prob = probs.max(axis=1)
    axes[1, idx].scatter(X[:, 0], X[:, 1], c=max_prob, cmap='hot', s=30, alpha=0.6)
    axes[1, idx].set_title(f'K={K} (不确定性，颜色越亮越确定)')
    axes[1, idx].set_xticks([])
    axes[1, idx].set_yticks([])

plt.tight_layout()
plt.show()

# 3. 详细分析K=4的情况
gmm = GaussianMixture(n_components=4, random_state=42)
gmm.fit(X)
labels = gmm.predict(X)
probs = gmm.predict_proba(X)

fig2, axes2 = plt.subplots(1, 3, figsize=(15, 5))

# 聚类结果
scatter1 = axes2[0].scatter(X[:, 0], X[:, 1], c=labels, cmap='tab10', s=30, alpha=0.6)
axes2[0].set_title('硬聚类结果（最可能的簇）')
axes2[0].set_xticks([])
axes2[0].set_yticks([])
plt.colorbar(scatter1, ax=axes2[0])

# 不确定性可视化
uncertainty = 1 - probs.max(axis=1)  # 1 - 最大概率 = 不确定性
scatter2 = axes2[1].scatter(X[:, 0], X[:, 1], c=uncertainty, cmap='RdYlBu_r', s=30, alpha=0.6)
axes2[1].set_title('分类不确定性（红色=高不确定性）')
axes2[1].set_xticks([])
axes2[1].set_yticks([])
plt.colorbar(scatter2, ax=axes2[1])

# 显示一些边界点
axes2[2].axis('off')
axes2[2].text(0.1, 0.9, 'GMM vs K-Means对比：', fontsize=12, fontweight='bold')
axes2[2].text(0.1, 0.7, 'GMM（软聚类）:', fontsize=10, fontweight='bold')
axes2[2].text(0.1, 0.55, '• 每个点有隶属概率', fontsize=9)
axes2[2].text(0.1, 0.45, '• 可以处理重叠簇', fontsize=9)
axes2[2].text(0.1, 0.35, '• 发现不同大小形状的簇', fontsize=9)
axes2[2].text(0.1, 0.15, 'K-Means（硬聚类）:', fontsize=10, fontweight='bold')
axes2[2].text(0.1, 0.05, '• 每个点只属于一个簇', fontsize=9)

plt.tight_layout()
plt.show()

# 4. 找出不确定性高的点（边界点）
high_uncertainty_idx = np.where(uncertainty > 0.4)[0]
print(f"\n发现{len(high_uncertainty_idx)}个边界点（分类不确定）")
print("这些点位于簇的边界区域")