import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from scipy.spatial.distance import pdist

# 设置中文
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 1. 生成10只股票的日收益率数据（无标签）
np.random.seed(42)
n_stocks = 10
n_days = 100

# 创建不同的收益率模式
stock_returns = np.zeros((n_stocks, n_days))
# 科技股模式
stock_returns[0:3] = np.random.normal(0.001, 0.02, (3, n_days))
# 金融股模式
stock_returns[3:6] = np.random.normal(0.0005, 0.015, (3, n_days))
# 消费股模式
stock_returns[6:9] = np.random.normal(0.0008, 0.01, (3, n_days))
# 能源股模式
stock_returns[9] = np.random.normal(-0.0002, 0.025, (1, n_days))

stock_names = ['腾讯', '阿里', '百度', '平安', '招行', '中信', 
               '茅台', '伊利', '海尔', '中石油']

# 2. 计算股票之间的相关系数（相似度）
correlation_matrix = np.corrcoef(stock_returns)

# 3. 层次聚类（使用距离矩阵）
# 将相关系数转换为距离（1 - 相关系数）
distance_matrix = 1 - correlation_matrix
# 压缩距离矩阵
condensed_distances = pdist(distance_matrix)
# 进行层次聚类（使用平均链接）
linkage_matrix = linkage(condensed_distances, method='average')

# 4. 绘制树状图
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

# 树状图
dendrogram(linkage_matrix, labels=stock_names, ax=axes[0], 
           orientation='top', leaf_rotation=45)
axes[0].set_title('股票层次聚类树状图', fontsize=12)
axes[0].set_xlabel('股票')
axes[0].set_ylabel('距离')

# 5. 根据距离阈值分类
# 在距离0.3处切割
clusters = fcluster(linkage_matrix, t=0.3, criterion='distance')

# 6. 可视化聚类结果（热力图）
im = axes[1].imshow(distance_matrix, cmap='RdYlBu_r', aspect='auto')
axes[1].set_xticks(range(n_stocks))
axes[1].set_yticks(range(n_stocks))
axes[1].set_xticklabels(stock_names, rotation=45, ha='right')
axes[1].set_yticklabels(stock_names)
axes[1].set_title('股票相关系数距离矩阵', fontsize=12)
plt.colorbar(im, ax=axes[1], label='距离')

# 7. 聚类结果分析
axes[2].axis('off')
axes[2].text(0.1, 0.9, '聚类结果：', fontsize=12, fontweight='bold')
unique_clusters = np.unique(clusters)
y_pos = 0.8
for cluster_id in unique_clusters:
    stocks_in_cluster = [stock_names[i] for i in range(n_stocks) if clusters[i] == cluster_id]
    axes[2].text(0.1, y_pos, f'类别{cluster_id}: {", ".join(stocks_in_cluster)}', fontsize=10)
    y_pos -= 0.1

plt.tight_layout()
plt.show()

print("\n自动发现的股票类别：")
for cluster_id in unique_clusters:
    stocks_in_cluster = [stock_names[i] for i in range(n_stocks) if clusters[i] == cluster_id]
    print(f"类别{cluster_id}: {len(stocks_in_cluster)}只股票")