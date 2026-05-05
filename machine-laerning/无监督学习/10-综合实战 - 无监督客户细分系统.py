import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

# 设置中文
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 1. 生成客户数据（无标签）
np.random.seed(42)
n_customers = 500

# 客户特征：
# 年龄、年收入、消费频率、客单价、会员时长
customers = pd.DataFrame({
    '年龄': np.random.normal(40, 12, n_customers),
    '年收入': np.random.exponential(50, n_customers) * 1000,
    '消费频率': np.random.gamma(2, 2, n_customers),
    '客单价': np.random.normal(200, 80, n_customers),
    '会员时长': np.random.uniform(1, 60, n_customers)
})

# 添加一些自然形成的客户群
customers.loc[:100, '年收入'] *= 1.5  # 高收入群
customers.loc[100:200, '消费频率'] *= 2  # 高频群
customers.loc[200:300, '客单价'] *= 2  # 高客单价群

print("客户数据概览：")
print(customers.describe())

# 2. 数据预处理
scaler = StandardScaler()
customers_scaled = scaler.fit_transform(customers)

# 3. 确定最优K值
inertias = []
silhouettes = []
K_range = range(2, 11)

for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(customers_scaled)
    inertias.append(kmeans.inertia_)
    silhouettes.append(silhouette_score(customers_scaled, labels))

# 4. 使用PCA进行可视化
pca = PCA(n_components=2)
customers_pca = pca.fit_transform(customers_scaled)

# 5. 选择最佳K（肘部法则 + 轮廓系数）
best_k = K_range[np.argmax(silhouettes)]

# 6. 应用最佳K值
final_kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
customer_segments = final_kmeans.fit_predict(customers_scaled)

# 7. 可视化结果
fig, axes = plt.subplots(2, 3, figsize=(16, 10))

# 肘部法则图
axes[0, 0].plot(K_range, inertias, 'bo-', linewidth=2)
axes[0, 0].axvline(x=best_k, color='red', linestyle='--', label=f'最佳K={best_k}')
axes[0, 0].set_xlabel('K值')
axes[0, 0].set_ylabel('惯性')
axes[0, 0].set_title('肘部法则')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

# 轮廓系数图
axes[0, 1].plot(K_range, silhouettes, 'go-', linewidth=2)
axes[0, 1].axvline(x=best_k, color='red', linestyle='--', label=f'最佳K={best_k}')
axes[0, 1].set_xlabel('K值')
axes[0, 1].set_ylabel('轮廓系数')
axes[0, 1].set_title('轮廓系数（越高越好）')
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3)

# 2D可视化（PCA降维）
scatter = axes[0, 2].scatter(customers_pca[:, 0], customers_pca[:, 1],
                             c=customer_segments, cmap='tab10', s=30, alpha=0.6)
axes[0, 2].set_xlabel('第一主成分')
axes[0, 2].set_ylabel('第二主成分')
axes[0, 2].set_title(f'客户分群可视化（K={best_k}）')
plt.colorbar(scatter, ax=axes[0, 2])

# 8. 分析每个群的特征
segment_analysis = customers.copy()
segment_analysis['Segment'] = customer_segments

# 计算每个群的平均特征
segment_profiles = segment_analysis.groupby('Segment').mean()

# 热力图展示
im = axes[1, 0].imshow(segment_profiles.T, cmap='RdYlBu_r', aspect='auto')
axes[1, 0].set_xticks(range(len(segment_profiles)))
axes[1, 0].set_xticklabels([f'群{i}' for i in range(len(segment_profiles))])
axes[1, 0].set_yticks(range(len(segment_profiles.columns)))
axes[1, 0].set_yticklabels(segment_profiles.columns)
axes[1, 0].set_title('各客户群特征画像')
plt.colorbar(im, ax=axes[1, 0])

# 9. 群大小分布
segment_sizes = segment_analysis['Segment'].value_counts().sort_index()
axes[1, 1].bar(segment_sizes.index, segment_sizes.values, color='steelblue')
axes[1, 1].set_xlabel('客户群')
axes[1, 1].set_ylabel('客户数量')
axes[1, 1].set_title('各群客户数量分布')
for i, v in enumerate(segment_sizes.values):
    axes[1, 1].text(i, v + 5, str(v), ha='center')

# 10. 业务建议
axes[1, 2].axis('off')
axes[1, 2].text(0.1, 0.9, '客户分群业务建议：', fontsize=12, fontweight='bold')

y_pos = 0.75
for segment in range(best_k):
    profile = segment_profiles.loc[segment]
    # 识别群特征
    age = profile['年龄']
    income = profile['年收入']
    freq = profile['消费频率']

    if income > segment_profiles['年收入'].mean():
        strategy = '高价值客户，提供VIP服务'
    elif freq > segment_profiles['消费频率'].mean():
        strategy = '高频客户，推会员积分活动'
    elif age > segment_profiles['年龄'].mean():
        strategy = '年长客户，推健康类产品'
    else:
        strategy = '潜力客户，推新人优惠'

    axes[1, 2].text(0.1, y_pos, f'群{segment}: {strategy}', fontsize=9)
    y_pos -= 0.1

plt.tight_layout()
plt.show()

# 11. 报告输出
print("\n" + "=" * 60)
print("客户细分分析报告")
print("=" * 60)

print(f"\n发现{best_k}个客户群")

print("\n各客户群特征：")
for segment in range(best_k):
    print(f"\n群{segment}（{segment_sizes[segment]}个客户，{segment_sizes[segment] / n_customers * 100:.1f}%）:")
    profile = segment_profiles.loc[segment]
    print(f"  平均年龄: {profile['年龄']:.0f}岁")
    print(f"  平均年收入: ¥{profile['年收入']:,.0f}")
    print(f"  平均消费频率: {profile['消费频率']:.1f}次/月")
    print(f"  平均客单价: ¥{profile['客单价']:.0f}")
    print(f"  平均会员时长: {profile['会员时长']:.0f}个月")

# 12. 更新策略
print("\n推荐营销策略：")
for segment in range(best_k):
    profile = segment_profiles.loc[segment]
    if profile['年收入'] > segment_profiles['年收入'].mean():
        print(f"• 群{segment}: 高端客户，推送新品和VIP服务")
    elif profile['消费频率'] > segment_profiles['消费频率'].mean():
        print(f"• 群{segment}: 活跃客户，推积分活动和社交营销")
    elif profile['会员时长'] > segment_profiles['会员时长'].mean():
        print(f"• 群{segment}: 忠诚客户，推推荐奖励和升级服务")
    else:
        print(f"• 群{segment}: 潜力客户，推首次购买优惠")