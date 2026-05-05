import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs
from sklearn.preprocessing import StandardScaler

# 设置中文
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 1. 生成无标签的客户数据
np.random.seed(42)
n_samples = 300

# 特征：年消费金额、月均访问次数
data = np.random.randn(n_samples, 2)
# 创建3个不同的客户群
data[:100] = data[:100] * 0.5 + [2, 3]      # 高消费高频率群
data[100:200] = data[100:200] * 0.5 + [1, 1] # 中等群
data[200:] = data[200:] * 0.5 + [4, 0.5]     # 高消费低频群

# 2. 标准化数据（K-Means需要）
scaler = StandardScaler()
data_scaled = scaler.fit_transform(data)

# 3. 使用肘部法则确定最佳K值
inertias = []
K_range = range(1, 11)
for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(data_scaled)
    inertias.append(kmeans.inertia_)

# 4. 绘制肘部图
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# 肘部法则图
axes[0].plot(K_range, inertias, 'bo-')
axes[0].set_xlabel('K值（聚类数）')
axes[0].set_ylabel('惯性（Inertia）')
axes[0].set_title('肘部法则确定最佳K值')
axes[0].axvline(x=3, color='red', linestyle='--', label='最佳K=3')
axes[0].legend()

# 5. 应用K-Means（K=3）
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
labels = kmeans.fit_predict(data_scaled)

# 6. 可视化聚类结果
axes[1].scatter(data[:, 0], data[:, 1], c=labels, cmap='viridis', s=50, alpha=0.6)
axes[1].scatter(kmeans.cluster_centers_[:, 0] * scaler.scale_[0] + scaler.mean_[0],
                kmeans.cluster_centers_[:, 1] * scaler.scale_[1] + scaler.mean_[1],
                c='red', marker='X', s=200, linewidths=3, edgecolors='black')
axes[1].set_xlabel('年消费金额（万元）')
axes[1].set_ylabel('月均访问次数')
axes[1].set_title('客户分群结果')

# 7. 分析每个群的特征
cluster_centers = scaler.inverse_transform(kmeans.cluster_centers_)
axes[2].axis('off')
axes[2].text(0.1, 0.9, '客户群特征分析：', fontsize=12, fontweight='bold')
for i in range(3):
    axes[2].text(0.1, 0.7 - i*0.2,
                 f'群{i+1}: 年消费={cluster_centers[i,0]:.1f}万, 月访问={cluster_centers[i,1]:.1f}次',
                 fontsize=10)

plt.tight_layout()
plt.show()

print("\n客户分群统计：")
for i in range(3):
    print(f"群{i+1}: {np.sum(labels == i)}个客户")