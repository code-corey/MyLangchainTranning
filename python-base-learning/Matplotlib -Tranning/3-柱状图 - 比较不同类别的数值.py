import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 准备数据
产品 = ['手机', '电脑', '平板', '耳机', '手表', '相机']
销量 = [350, 280, 420, 580, 190, 230]
增长率 = [5.2, 3.8, 8.1, 12.5, -2.3, 4.6]

# 创建图形和子图
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# 子图1：垂直柱状图
bars1 = ax1.bar(产品, 销量,
               color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD'],
               edgecolor='black',
               linewidth=1)
ax1.set_title('2024年各产品销量统计', fontsize=14, fontweight='bold')
ax1.set_xlabel('产品名称')
ax1.set_ylabel('销量（台）')
ax1.set_ylim(0, 700)

# 在柱子上显示数值
for bar, value in zip(bars1, 销量):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 10,
             f'{value}', ha='center', va='bottom', fontsize=10, fontweight='bold')

# 添加网格
ax1.grid(True, alpha=0.3, axis='y')  # 只显示水平网格

# 子图2：水平柱状图（更适合类别名称长的情况）
colors = ['red' if g < 0 else 'green' for g in 增长率]
bars2 = ax2.barh(产品, 增长率, color=colors, edgecolor='black')
ax2.set_title('各产品年度增长率', fontsize=14, fontweight='bold')
ax2.set_xlabel('增长率（%）')
ax2.axvline(x=0, color='black', linewidth=1)  # 添加0刻度线

# 在条形上显示数值
for bar, value in zip(bars2, 增长率):
    width = bar.get_width()
    label_x = width + (0.5 if width > 0 else -2)
    ax2.text(label_x, bar.get_y() + bar.get_height()/2,
             f'{value}%', ha='left' if width > 0 else 'right', va='center')

plt.tight_layout()
plt.show()