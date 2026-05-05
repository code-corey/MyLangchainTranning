import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 生成多组数据
np.random.seed(42)
data = []
for i in range(5):
    # 不同分布的组
    if i == 0:
        group = np.random.normal(50, 10, 200)  # 正常分布
    elif i == 1:
        group = np.random.normal(60, 15, 200)  # 波动大
    elif i == 2:
        group = np.random.exponential(50, 200)  # 右偏分布
    elif i == 3:
        group = np.random.uniform(30, 80, 200)  # 均匀分布
    else:
        group = np.random.normal(45, 8, 200)  # 左偏分布
    data.append(group)

# 创建图形
fig, axes = plt.subplots(1, 3, figsize=(15, 6))

# 子图1：基本箱线图
bp1 = axes[0].boxplot(data,
                      labels=['组A', '组B', '组C', '组D', '组E'],
                      patch_artist=True,  # 填充颜色
                      showmeans=True,      # 显示均值
                      meanline=True,       # 均值用线表示
                      meanprops={'color': 'red', 'linestyle': '--', 'linewidth': 1.5})

# 设置箱体颜色
colors = ['lightblue', 'lightgreen', 'lightpink', 'lightyellow', 'lightgray']
for patch, color in zip(bp1['boxes'], colors):
    patch.set_facecolor(color)

axes[0].set_title('各组分发数据对比', fontsize=12, fontweight='bold')
axes[0].set_ylabel('数值')
axes[0].grid(True, alpha=0.3, axis='y')

# 子图2：水平箱线图
bp2 = axes[1].boxplot(data, vert=False,  # 水平方向
                      labels=['组A', '组B', '组C', '组D', '组E'],
                      patch_artist=True,
                      showmeans=True)
for patch, color in zip(bp2['boxes'], colors):
    patch.set_facecolor(color)

axes[1].set_title('水平箱线图', fontsize=12, fontweight='bold')
axes[1].set_xlabel('数值')
axes[1].grid(True, alpha=0.3, axis='x')

# 子图3：带缺口和离群值的详细箱线图
# 生成包含异常值的数据
data_with_outliers = []
for i in range(3):
    group = np.random.normal(50, 10, 100)
    if i == 0:
        group = np.append(group, [120, 130, -20])  # 添加异常值
    data_with_outliers.append(group)

bp3 = axes[2].boxplot(data_with_outliers,
                      labels=['正常组', '含异常值组', '另一组'],
                      notch=True,           # 缺口（显示置信区间）
                      sym='r+',              # 异常值标记
                      patch_artist=True,
                      showfliers=True,       # 显示异常值
                      whis=1.5)              # IQR倍数（默认1.5）

for patch, color in zip(bp3['boxes'], ['lightblue', 'lightcoral', 'lightgreen']):
    patch.set_facecolor(color)

axes[2].set_title('带异常值的箱线图', fontsize=12, fontweight='bold')
axes[2].set_ylabel('数值')
axes[2].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.show()

# 额外：详细说明箱线图各部分的含义
fig2, ax = plt.subplots(figsize=(10, 6))

# 生成演示数据
demo_data = np.random.normal(50, 10, 100)
bp = ax.boxplot(demo_data, vert=False, patch_artist=True, showmeans=True,
                meanprops={'marker': 'D', 'markerfacecolor': 'red', 'markersize': 10})

box = bp['boxes'][0]
median = bp['medians'][0]
mean = bp['means'][0]
whiskers = bp['whiskers']
caps = bp['caps']
fliers = bp['fliers']

# 添加注释
ax.set_title('箱线图各组成部分说明', fontsize=14, fontweight='bold')
ax.set_xlabel('数值')

# 添加箭头和文字说明
ax.annotate('上边缘\n(最大值)', xy=(demo_data.max(), 1), xytext=(demo_data.max()+5, 1.2),
            arrowprops=dict(arrowstyle='->', color='red', lw=1.5))
ax.annotate('上四分位数(Q3)', xy=(np.percentile(demo_data, 75), 1),
            xytext=(np.percentile(demo_data, 75)+5, 1.3))
ax.annotate('中位数', xy=(np.median(demo_data), 1),
            xytext=(np.median(demo_data)+5, 0.7))
ax.annotate('均值', xy=(demo_data.mean(), 1),
            xytext=(demo_data.mean()+5, 1.1))
ax.annotate('下四分位数(Q1)', xy=(np.percentile(demo_data, 25), 1),
            xytext=(np.percentile(demo_data, 25)-15, 0.7))
ax.annotate('下边缘\n(最小值)', xy=(demo_data.min(), 1),
            xytext=(demo_data.min()-10, 1.2))
ax.annotate('异常值', xy=(bp['fliers'][0].get_data()[0][0], 1),
            xytext=(bp['fliers'][0].get_data()[0][0]-10, 1.4))

ax.grid(True, alpha=0.3, axis='x')

plt.tight_layout()
plt.show()