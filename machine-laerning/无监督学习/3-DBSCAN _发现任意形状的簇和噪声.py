import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
from sklearn.datasets import make_moons, make_circles

# 设置中文
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 1. 生成复杂形状的数据（无标签）
np.random.seed(42)

# 数据集1：月牙形
moon_data, _ = make_moons(n_samples=200, noise=0.05)

# 数据集2：同心圆
circle_data, _ = make_circles(n_samples=200, factor=0.5, noise=0.05)

# 数据集3：带噪声的数据
noise_data = np.random.randn(200, 2) * 0.3
noise_data = np.vstack([moon_data + [2, 0], noise_data])

# 2. 应用DBSCAN
fig, axes = plt.subplots(2, 3, figsize=(15, 10))

datasets = [moon_data, circle_data, noise_data]
titles = ['月牙形数据', '同心圆数据', '带噪声数据']
eps_values = [0.2, 0.15, 0.2]  # DBSCAN的邻域半径参数

for i, (data, title, eps) in enumerate(zip(datasets, titles, eps_values)):
    # 应用DBSCAN
    dbscan = DBSCAN(eps=eps, min_samples=5)
    labels = dbscan.fit_predict(data)

    # 统计聚类结果
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = list(labels).count(-1)

    # 绘制聚类结果
    unique_labels = set(labels)
    colors = plt.cm.Set3(np.linspace(0, 1, len(unique_labels)))

    for label, color in zip(unique_labels, colors):
        if label == -1:
            # 噪声点为黑色
            color = 'black'
            marker = 'x'
            size = 30
            alpha = 0.5
        else:
            marker = 'o'
            size = 50
            alpha = 0.6

        mask = labels == label
        axes[0, i].scatter(data[mask, 0], data[mask, 1],
                           c=[color], marker=marker, s=size, alpha=alpha)

    axes[0, i].set_title(f'{title}\n发现{n_clusters}个簇，{n_noise}个噪声点', fontsize=10)
    axes[0, i].set_xticks([])
    axes[0, i].set_yticks([])

# 3. 对比K-Means和DBSCAN
from sklearn.cluster import KMeans

# 对月牙形数据应用K-Means
kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
kmeans_labels = kmeans.fit_predict(moon_data)

# 对比可视化
axes[1, 0].scatter(moon_data[:, 0], moon_data[:, 1], c=kmeans_labels, cmap='viridis', s=50, alpha=0.6)
axes[1, 0].set_title('K-Means聚类结果（错误）', fontsize=10)
axes[1, 0].set_xticks([])
axes[1, 0].set_yticks([])

# 对月牙形数据应用DBSCAN
dbscan = DBSCAN(eps=0.2, min_samples=5)
dbscan_labels = dbscan.fit_predict(moon_data)
axes[1, 1].scatter(moon_data[:, 0], moon_data[:, 1], c=dbscan_labels, cmap='viridis', s=50, alpha=0.6)
axes[1, 1].set_title('DBSCAN聚类结果（正确）', fontsize=10)
axes[1, 1].set_xticks([])
axes[1, 1].set_yticks([])

# 参数说明
axes[1, 2].axis('off')
axes[1, 2].text(0.1, 0.9, 'DBSCAN优势：', fontsize=12, fontweight='bold')
axes[1, 2].text(0.1, 0.7, '1. 发现任意形状的簇', fontsize=10)
axes[1, 2].text(0.1, 0.55, '2. 自动识别噪声点', fontsize=10)
axes[1, 2].text(0.1, 0.4, '3. 不需要指定簇数量', fontsize=10)
axes[1, 2].text(0.1, 0.2, '参数：eps=邻域半径', fontsize=10)
axes[1, 2].text(0.1, 0.1, '      min_samples=最小样本数', fontsize=10)

plt.tight_layout()
plt.show()

print("\nDBSCAN vs K-Means 对比：")
print("K-Means只能发现球形簇，DBSCAN能发现任意形状")