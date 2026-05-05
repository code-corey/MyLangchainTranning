import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 生成模拟数据
np.random.seed(42)
x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)
y3 = np.sin(x) + np.random.normal(0, 0.1, 100)
y4 = np.exp(x/5)

# 方法1：使用subplots创建网格
fig1, axes = plt.subplots(2, 2, figsize=(12, 8))
axes[0, 0].plot(x, y1, 'r-', label='sin(x)')
axes[0, 0].set_title('正弦函数')
axes[0, 0].legend()
axes[0, 1].plot(x, y2, 'b-', label='cos(x)')
axes[0, 1].set_title('余弦函数')
axes[0, 1].legend()
axes[1, 0].scatter(x, y3, alpha=0.5, s=10)
axes[1, 0].set_title('带噪声的数据')
axes[1, 1].plot(x, y4, 'g-', linewidth=2)
axes[1, 1].set_yscale('log')
axes[1, 1].set_title('指数函数（对数坐标）')
plt.tight_layout()
plt.show()

# 方法2：使用GridSpec创建不规则布局
fig2 = plt.figure(figsize=(14, 10))
gs = GridSpec(3, 3, figure=fig2, hspace=0.3, wspace=0.3)

# 大图（占据左上区域）
ax_main = fig2.add_subplot(gs[0:2, 0:2])
ax_main.plot(x, y1, 'b-', linewidth=2)
ax_main.plot(x, y2, 'r--', linewidth=1.5)
ax_main.set_title('主图：sin和cos曲线', fontsize=12, fontweight='bold')
ax_main.set_xlabel('x')
ax_main.set_ylabel('y')
ax_main.legend(['sin(x)', 'cos(x)'])
ax_main.grid(True, alpha=0.3)

# 右上角小图
ax_topright = fig2.add_subplot(gs[0, 2])
ax_topright.hist(y3, bins=20, color='skyblue', edgecolor='black')
ax_topright.set_title('噪声分布', fontsize=10)

# 中间右边图
ax_midright = fig2.add_subplot(gs[1, 2])
ax_midright.boxplot([y1, y2, y3], labels=['sin', 'cos', '噪声'])
ax_midright.set_title('数据分布对比', fontsize=10)

# 底部大图
ax_bottom = fig2.add_subplot(gs[2, :])
ax_bottom.plot(x, y1 * y2, 'g-', linewidth=2)
ax_bottom.fill_between(x, y1 * y2, alpha=0.3)
ax_bottom.set_title('乘积函数 sin(x)*cos(x)', fontsize=12)
ax_bottom.set_xlabel('x')
ax_bottom.grid(True, alpha=0.3)

plt.suptitle('复杂布局示例 - GridSpec', fontsize=16, fontweight='bold')
plt.show()

# 方法3：使用subplot2grid（类似Excel的合并单元格）
fig3 = plt.figure(figsize=(12, 8))

# 定义布局：3行3列，但合并一些单元格
ax1 = plt.subplot2grid((3, 3), (0, 0), colspan=2)  # 第0行，第0列，占2列
ax2 = plt.subplot2grid((3, 3), (0, 2), rowspan=2)  # 第0行，第2列，占2行
ax3 = plt.subplot2grid((3, 3), (1, 0), colspan=2)  # 第1行，第0列，占2列
ax4 = plt.subplot2grid((3, 3), (2, 0))             # 第2行，第0列
ax5 = plt.subplot2grid((3, 3), (2, 1))             # 第2行，第1列
ax6 = plt.subplot2grid((3, 3), (2, 2))             # 第2行，第2列

# 绘制内容
ax1.plot(x, y1, 'r-')
ax1.set_title('sin(x)')
ax1.grid(True)

ax2.hist(y3, bins=20, orientation='horizontal', color='lightblue')
ax2.set_title('水平直方图')

ax3.plot(x, y2, 'b-')
ax3.set_title('cos(x)')
ax3.grid(True)

ax4.scatter(x[:50], y3[:50], color='green')
ax4.set_title('散点图（部分数据）')

ax5.boxplot([y1, y2])
ax5.set_title('箱线图')

ax6.pie([30, 25, 20, 15, 10], labels=['A', 'B', 'C', 'D', 'E'], autopct='%1.0f%%')
ax6.set_title('饼图')

plt.suptitle('Excel风格的subplot2grid布局', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()

# 方法4：共享坐标轴的子图
fig4, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

ax1.plot(x, y1, 'r-', linewidth=2)
ax1.set_ylabel('sin(x)')
ax1.set_title('三个共享X轴的子图', fontsize=12)
ax1.grid(True)

ax2.plot(x, y2, 'b-', linewidth=2)
ax2.set_ylabel('cos(x)')
ax2.grid(True)

ax3.plot(x, y1 * y2, 'g-', linewidth=2)
ax3.set_xlabel('x')
ax3.set_ylabel('乘积')
ax3.grid(True)

plt.tight_layout()
plt.show()