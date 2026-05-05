import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 创建3D图形
fig = plt.figure(figsize=(16, 12))

# ========== 子图1：3D散点图 ==========
ax1 = fig.add_subplot(2, 2, 1, projection='3d')
np.random.seed(42)
n = 200
x = np.random.normal(0, 1, n)
y = np.random.normal(0, 1, n)
z = x**2 + y**2 + np.random.normal(0, 0.1, n)

sc = ax1.scatter(x, y, z, c=z, cmap='viridis', s=20, alpha=0.6)
ax1.set_title('3D散点图', fontsize=12, fontweight='bold')
ax1.set_xlabel('X轴')
ax1.set_ylabel('Y轴')
ax1.set_zlabel('Z轴')
plt.colorbar(sc, ax=ax1, label='Z值')

# ========== 子图2：3D曲面图 ==========
ax2 = fig.add_subplot(2, 2, 2, projection='3d')
x = np.linspace(-3, 3, 100)
y = np.linspace(-3, 3, 100)
X, Y = np.meshgrid(x, y)
Z = np.sin(np.sqrt(X**2 + Y**2)) / (np.sqrt(X**2 + Y**2) + 0.1)

# 绘制曲面
surf = ax2.plot_surface(X, Y, Z, cmap='coolwarm', alpha=0.8,
                        linewidth=0, antialiased=True)
ax2.set_title('3D曲面图（Sinc函数）', fontsize=12, fontweight='bold')
ax2.set_xlabel('X轴')
ax2.set_ylabel('Y轴')
ax2.set_zlabel('Z轴')
plt.colorbar(surf, ax=ax2, label='函数值')

# ========== 子图3：3D线框图 ==========
ax3 = fig.add_subplot(2, 2, 3, projection='3d')
x = np.linspace(-2, 2, 20)
y = np.linspace(-2, 2, 20)
X, Y = np.meshgrid(x, y)
Z = X**2 - Y**2

# 绘制线框
ax3.plot_wireframe(X, Y, Z, color='blue', alpha=0.6, linewidth=0.5)
ax3.set_title('3D线框图（双曲抛物面）', fontsize=12, fontweight='bold')
ax3.set_xlabel('X轴')
ax3.set_ylabel('Y轴')
ax3.set_zlabel('Z轴')

# ========== 子图4：3D条形图 ==========
ax4 = fig.add_subplot(2, 2, 4, projection='3d')
# 创建网格数据
x_pos = np.arange(5)
y_pos = np.arange(5)
X_pos, Y_pos = np.meshgrid(x_pos, y_pos)
X_pos = X_pos.flatten()
Y_pos = Y_pos.flatten()
Z_pos = np.zeros_like(X_pos)
dx = dy = 0.8
dz = np.random.randint(1, 10, len(X_pos))

# 定义颜色
colors = plt.cm.viridis(dz / dz.max())
ax4.bar3d(X_pos, Y_pos, Z_pos, dx, dy, dz, color=colors, alpha=0.8)
ax4.set_title('3D条形图', fontsize=12, fontweight='bold')
ax4.set_xlabel('X类别')
ax4.set_ylabel('Y类别')
ax4.set_zlabel('数值')

plt.suptitle('3D可视化示例', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.show()

# ========== 额外：等高线图（2D但展示3D信息） ==========
fig2, (ax5, ax6) = plt.subplots(1, 2, figsize=(14, 6))

# 生成数据
x = np.linspace(-3, 3, 100)
y = np.linspace(-3, 3, 100)
X, Y = np.meshgrid(x, y)
Z = (1 - X/2 + X**5 + Y**3) * np.exp(-X**2 - Y**2)

# 等高线填充图
contour1 = ax5.contourf(X, Y, Z, levels=20, cmap='RdYlBu_r')
ax5.set_title('填充等高线图', fontsize=12, fontweight='bold')
ax5.set_xlabel('X轴')
ax5.set_ylabel('Y轴')
plt.colorbar(contour1, ax=ax5)

# 带标签的等高线图
contour2 = ax6.contour(X, Y, Z, levels=10, colors='black', linewidths=0.5)
ax6.clabel(contour2, inline=True, fontsize=8)  # 添加数值标签
ax6.contourf(X, Y, Z, levels=10, cmap='viridis', alpha=0.6)
ax6.set_title('带标签的等高线图', fontsize=12, fontweight='bold')
ax6.set_xlabel('X轴')
ax6.set_ylabel('Y轴')
plt.colorbar(contour2, ax=ax6)

plt.tight_layout()
plt.show()

# 额外：旋转3D图形的示例
fig3 = plt.figure(figsize=(10, 8))
ax7 = fig3.add_subplot(111, projection='3d')

# 生成螺旋线数据
t = np.linspace(0, 20, 1000)
x_spiral = np.sin(t)
y_spiral = np.cos(t)
z_spiral = t / 2

ax7.plot(x_spiral, y_spiral, z_spiral, 'r-', linewidth=2)
ax7.scatter(x_spiral[::50], y_spiral[::50], z_spiral[::50], c=z_spiral[::50], cmap='plasma', s=50)
ax7.set_title('3D螺旋线', fontsize=14, fontweight='bold')
ax7.set_xlabel('X')
ax7.set_ylabel('Y')
ax7.set_zlabel('Z')

# 设置视角
ax7.view_init(elev=30, azim=45)  # 仰角30度，方位角45度

plt.show()

print("提示：3D图形可以用鼠标拖拽旋转视角！")