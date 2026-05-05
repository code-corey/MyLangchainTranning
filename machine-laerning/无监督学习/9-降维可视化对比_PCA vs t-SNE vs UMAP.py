import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.datasets import make_classification

# 尝试导入UMAP（可选）
try:
    import umap
    UMAP_AVAILABLE = True
except ImportError:
    UMAP_AVAILABLE = False
    print("UMAP未安装，将跳过UMAP演示")
    print("安装: pip install umap-learn")

# 1. 生成高维复杂数据
np.random.seed(42)
n_samples = 1000
n_features = 50
n_classes = 5

X, y = make_classification(n_samples=n_samples,
                           n_features=n_features,
                           n_informative=20,
                           n_redundant=10,
                           n_clusters_per_class=2,
                           n_classes=n_classes,
                           random_state=42)

print(f"生成数据形状: {X.shape}")
print(f"真实类别数: {len(np.unique(y))}")

# 2. 应用各种降维方法
print("\n降维中...")

# PCA
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X)

# t-SNE
tsne = TSNE(n_components=2, random_state=42, perplexity=30)
X_tsne = tsne.fit_transform(X)

# UMAP（如果可用）
if UMAP_AVAILABLE:
    umap_reducer = umap.UMAP(n_components=2, random_state=42)
    X_umap = umap_reducer.fit_transform(X)

# 3. 可视化对比
if UMAP_AVAILABLE:
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
else:
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# PCA
scatter1 = axes[0].scatter(X_pca[:, 0], X_pca[:, 1], c=y, cmap='tab10', s=20, alpha=0.6)
axes[0].set_title('PCA降维\n（线性，保持全局结构）', fontsize=12)
axes[0].set_xlabel('PC1')
axes[0].set_ylabel('PC2')
plt.colorbar(scatter1, ax=axes[0])

# t-SNE
scatter2 = axes[1].scatter(X_tsne[:, 0], X_tsne[:, 1], c=y, cmap='tab10', s=20, alpha=0.6)
axes[1].set_title('t-SNE降维\n（非线性，保持局部结构）', fontsize=12)
axes[1].set_xlabel('t-SNE1')
axes[1].set_ylabel('t-SNE2')
plt.colorbar(scatter2, ax=axes[1])

# UMAP
if UMAP_AVAILABLE:
    scatter3 = axes[2].scatter(X_umap[:, 0], X_umap[:, 1], c=y, cmap='tab10', s=20, alpha=0.6)
    axes[2].set_title('UMAP降维\n（非线性，速度更快）', fontsize=12)
    axes[2].set_xlabel('UMAP1')
    axes[2].set_ylabel('UMAP2')
    plt.colorbar(scatter3, ax=axes[2])

plt.tight_layout()
plt.show()

# 4. 定量比较
print("\n降维方法对比：")
print("="*50)

# 计算聚类效果（使用轮廓系数）
from sklearn.metrics import silhouette_score

print(f"\n聚类质量（轮廓系数，越高越好）:")
print(f"PCA:   {silhouette_score(X_pca, y):.3f}")
print(f"t-SNE: {silhouette_score(X_tsne, y):.3f}")
if UMAP_AVAILABLE:
    print(f"UMAP:  {silhouette_score(X_umap, y):.3f}")

print(f"\n方差解释率（PCA）:")
print(f"PC1: {pca.explained_variance_ratio_[0]:.2%}")
print(f"PC2: {pca.explained_variance_ratio_[1]:.2%}")
print(f"累计: {sum(pca.explained_variance_ratio_):.2%}")

# 5. 选择建议
fig2, ax = plt.subplots(figsize=(10, 4))
ax.axis('off')
ax.text(0.1, 0.9, '降维方法选择建议：', fontsize=14, fontweight='bold')
ax.text(0.1, 0.7, '• PCA：数据线性相关，需要可解释性，速度快', fontsize=11)
ax.text(0.1, 0.55, '• t-SNE：可视化复杂结构，但速度慢，不能用于新数据', fontsize=11)
ax.text(0.1, 0.4, '• UMAP：平衡质量和速度，可扩展到大数据集', fontsize=11)
ax.text(0.1, 0.2, '提示：降维后通常用于可视化，不建议直接用于特征工程',
        fontsize=10, color='red')

plt.tight_layout()
plt.show()