import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体（解决中文乱码）
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False    # 用来正常显示负号

# 准备数据
x = [1, 2, 3, 4, 5, 6]  # 月份
y = [20, 22, 25, 28, 30, 32]  # 温度

# 创建图形
plt.figure(figsize=(10, 6))  # 设置图片大小（宽度10英寸，高度6英寸）

# 绘制折线图
plt.plot(x, y,
         marker='o',        # 数据点标记为圆圈
         linewidth=2,       # 线宽
         markersize=8,      # 标记大小
         color='red',       # 线条颜色
         label='温度')       # 图例标签

# 添加标题和标签
plt.title('2024年上半年月平均温度变化', fontsize=16, fontweight='bold')
plt.xlabel('月份', fontsize=12)
plt.ylabel('温度（℃）', fontsize=12)

# 添加网格
plt.grid(True, alpha=0.3, linestyle='--')

# 添加图例
plt.legend()

# 显示数值（在每个点上显示温度值）
for i, (xi, yi) in enumerate(zip(x, y)):
    plt.text(xi, yi + 0.5, f'{yi}℃', ha='center', fontsize=10)

# 设置x轴刻度
plt.xticks(x, ['1月', '2月', '3月', '4月', '5月', '6月'])

# 显示图表
plt.show()