import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 生成随机数据（模拟身高体重）
np.random.seed(42)
n = 200
身高 = np.random.normal(170, 10, n)  # 均值170，标准差10
体重 = 身高 * 0.6 + np.random.normal(0, 5, n)  # 体重与身高相关

# 创建子图（1行2列）
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# 子图1：基本散点图
ax1.scatter(身高, 体重,
           alpha=0.6,      # 透明度（重叠点会更明显）
           c='blue',       # 颜色
           s=50,           # 点的大小
           edgecolors='white',  # 点的边缘颜色
           linewidth=0.5)
ax1.set_title('身高与体重关系散点图', fontsize=14)
ax1.set_xlabel('身高（cm）')
ax1.set_ylabel('体重（kg）')
ax1.grid(True, alpha=0.3)

# 添加趋势线
z = np.polyfit(身高, 体重, 1)  # 拟合一次函数
p = np.poly1d(z)
ax1.plot(身高, p(身高), "r--", linewidth=2, label='趋势线')
ax1.legend()

# 子图2：按颜色分组的散点图
# 生成性别标签
性别 = np.random.choice(['男', '女'], n)
colors = {'男': 'blue', '女': 'red'}

for gender, color in colors.items():
    mask = 性别 == gender
    ax2.scatter(身高[mask], 体重[mask],
               alpha=0.6, c=color, label=gender, s=50)
ax2.set_title('按性别分组的身高体重关系', fontsize=14)
ax2.set_xlabel('身高（cm）')
ax2.set_ylabel('体重（kg）')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()  # 自动调整子图间距
plt.show()