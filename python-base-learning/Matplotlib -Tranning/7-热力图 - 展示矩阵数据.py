import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 生成相关性矩阵数据
np.random.seed(42)
n_vars = 8
# 创建相关矩阵（模拟变量之间的相关性）
corr_matrix = np.random.uniform(-1, 1, (n_vars, n_vars))
# 使矩阵对称
corr_matrix = (corr_matrix + corr_matrix.T) / 2
np.fill_diagonal(corr_matrix, 1)  # 对角线设为1

变量名 = [f'变量{i+1}' for i in range(n_vars)]

# 创建图形
fig, axes = plt.subplots(2, 2, figsize=(14, 12))

# 子图1：基本热力图
im1 = axes[0, 0].imshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1, aspect='auto')
axes[0, 0].set_title('变量相关性热力图', fontsize=12, fontweight='bold')
axes[0, 0].set_xticks(range(n_vars))
axes[0, 0].set_yticks(range(n_vars))
axes[0, 0].set_xticklabels(变量名, rotation=45, ha='right')
axes[0, 0].set_yticklabels(变量名)
plt.colorbar(im1, ax=axes[0, 0], label='相关系数')

# 在热力图上显示数值
for i in range(n_vars):
    for j in range(n_vars):
        text = axes[0, 0].text(j, i, f'{corr_matrix[i, j]:.2f}',
                               ha="center", va="center", color="black" if abs(corr_matrix[i, j]) < 0.5 else "white")

# 子图2：带掩码的热力图（只显示下三角）
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))  # 上三角掩码
corr_masked = np.ma.masked_where(mask, corr_matrix)

im2 = axes[0, 1].imshow(corr_masked, cmap='coolwarm', vmin=-1, vmax=1, aspect='auto')
axes[0, 1].set_title('下三角相关性矩阵', fontsize=12, fontweight='bold')
axes[0, 1].set_xticks(range(n_vars))
axes[0, 1].set_yticks(range(n_vars))
axes[0, 1].set_xticklabels(变量名, rotation=45, ha='right')
axes[0, 1].set_yticklabels(变量名)
plt.colorbar(im2, ax=axes[0, 1], label='相关系数')

# 子图3：时间-日期热力图（模拟工作日各小时的活动量）
days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
hours = [f'{h}:00' for h in range(9, 21)]  # 9点到20点

# 生成模拟数据
activity_data = np.random.poisson(50, (len(days), len(hours)))
# 周末数据降低
activity_data[5:7, :] *= 0.6
# 午高峰和晚高峰
activity_data[:, 3:5] *= 1.5  # 12-13点
activity_data[:, 8:10] *= 1.3  # 17-18点

im3 = axes[1, 0].imshow(activity_data, cmap='YlOrRd', aspect='auto')
axes[1, 0].set_title('一周活动热度图', fontsize=12, fontweight='bold')
axes[1, 0].set_xticks(range(len(hours)))
axes[1, 0].set_yticks(range(len(days)))
axes[1, 0].set_xticklabels(hours, rotation=45, ha='right')
axes[1, 0].set_yticklabels(days)
plt.colorbar(im3, ax=axes[1, 0], label='活动量')

# 子图4：混淆矩阵（分类结果可视化）
# 模拟分类结果
真实标签 = ['猫', '狗', '鸟', '猫', '狗', '鸟', '猫', '狗', '鸟']
预测标签 = ['猫', '狗', '鸟', '猫', '狗', '猫', '鸟', '狗', '鸟']
类别 = ['猫', '狗', '鸟']

# 计算混淆矩阵
conf_matrix = np.zeros((3, 3))
for true, pred in zip(真实标签, 预测标签):
    conf_matrix[类别.index(true), 类别.index(pred)] += 1

im4 = axes[1, 1].imshow(conf_matrix, cmap='Blues', aspect='auto')
axes[1, 1].set_title('分类混淆矩阵', fontsize=12, fontweight='bold')
axes[1, 1].set_xticks(range(len(类别)))
axes[1, 1].set_yticks(range(len(类别)))
axes[1, 1].set_xticklabels(类别)
axes[1, 1].set_yticklabels(类别)
axes[1, 1].set_xlabel('预测标签')
axes[1, 1].set_ylabel('真实标签')
plt.colorbar(im4, ax=axes[1, 1], label='样本数')

# 显示数值
for i in range(len(类别)):
    for j in range(len(类别)):
        axes[1, 1].text(j, i, int(conf_matrix[i, j]),
                       ha="center", va="center", color="white" if conf_matrix[i, j] > conf_matrix.max()/2 else "black")

plt.tight_layout()
plt.show()

# 额外：带聚类的热力图
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import squareform

fig2, ax = plt.subplots(figsize=(10, 8))

# 计算距离和聚类
distance_matrix = 1 - np.abs(corr_matrix)  # 用相关系数转距离
condensed_dist = squareform(distance_matrix)
linkage_matrix = linkage(condensed_dist, method='average')

# 根据聚类结果重新排序
from scipy.cluster.hierarchy import leaves_list
order = leaves_list(linkage_matrix)
corr_ordered = corr_matrix[order][:, order]
变量名_ordered = [变量名[i] for i in order]

# 绘制带聚类结果的热力图
im = ax.imshow(corr_ordered, cmap='coolwarm', vmin=-1, vmax=1, aspect='auto')
ax.set_title('带聚类的相关性热力图', fontsize=14, fontweight='bold')
ax.set_xticks(range(n_vars))
ax.set_yticks(range(n_vars))
ax.set_xticklabels(变量名_ordered, rotation=45, ha='right')
ax.set_yticklabels(变量名_ordered)

# 添加数值
for i in range(n_vars):
    for j in range(n_vars):
        ax.text(j, i, f'{corr_ordered[i, j]:.2f}',
               ha="center", va="center",
               color="black" if abs(corr_ordered[i, j]) < 0.5 else "white",
               fontsize=8)

plt.colorbar(im, ax=ax, label='相关系数')
plt.tight_layout()
plt.show()