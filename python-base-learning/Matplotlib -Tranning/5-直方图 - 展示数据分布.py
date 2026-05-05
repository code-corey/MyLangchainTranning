import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 生成模拟数据
np.random.seed(42)
# 生成正态分布数据（例如：身高）
身高 = np.random.normal(170, 8, 1000)
# 生成偏态分布数据（例如：收入）
收入 = np.random.exponential(5000, 1000)

# 创建图形
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 子图1：基本直方图
axes[0, 0].hist(身高, bins=30,          # 分组数
                color='skyblue',
                edgecolor='black',
                alpha=0.7)
axes[0, 0].set_title('身高分布直方图', fontsize=12, fontweight='bold')
axes[0, 0].set_xlabel('身高（cm）')
axes[0, 0].set_ylabel('频数')
# 修正：使用 np.mean() 和 np.median()
axes[0, 0].axvline(np.mean(身高), color='red', linestyle='--', linewidth=2,
                   label=f'均值: {np.mean(身高):.1f}')
axes[0, 0].axvline(np.median(身高), color='green', linestyle='--', linewidth=2,
                   label=f'中位数: {np.median(身高):.1f}')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

# 子图2：带密度曲线的直方图
n, bins, patches = axes[0, 1].hist(身高, bins=30, density=True,
                                    color='lightgreen', edgecolor='black', alpha=0.6)
# 添加正态分布拟合曲线
mu, std = np.mean(身高), np.std(身高)
x = np.linspace(身高.min(), 身高.max(), 100)
y = (1/(std * np.sqrt(2*np.pi))) * np.exp(-0.5*((x-mu)/std)**2)
axes[0, 1].plot(x, y, 'r-', linewidth=2, label='正态分布拟合')
axes[0, 1].set_title('带密度曲线的身高分布', fontsize=12, fontweight='bold')
axes[0, 1].set_xlabel('身高（cm）')
axes[0, 1].set_ylabel('概率密度')
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3)

# 子图3：累积直方图
axes[1, 0].hist(身高, bins=30, cumulative=True, density=True,
                color='orange', edgecolor='black', alpha=0.7)
axes[1, 0].set_title('累积分布图', fontsize=12, fontweight='bold')
axes[1, 0].set_xlabel('身高（cm）')
axes[1, 0].set_ylabel('累积概率')
axes[1, 0].grid(True, alpha=0.3)

# 子图4：分组直方图（对比两组数据）
# 生成两组数据
group1 = np.random.normal(165, 6, 500)  # 女性身高
group2 = np.random.normal(175, 7, 500)  # 男性身高

axes[1, 1].hist([group1, group2], bins=30,
                label=['女性', '男性'],
                color=['pink', 'lightblue'],
                alpha=0.7, edgecolor='black')
axes[1, 1].set_title('男女身高分布对比', fontsize=12, fontweight='bold')
axes[1, 1].set_xlabel('身高（cm）')
axes[1, 1].set_ylabel('频数')
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# 额外：双变量直方图（二维直方图）
fig2, ax = plt.subplots(figsize=(10, 8))

# 生成相关数据
x = np.random.normal(0, 1, 5000)
y = x * 0.8 + np.random.normal(0, 0.6, 5000)

# 绘制二维直方图
h = ax.hist2d(x, y, bins=40, cmap='YlOrRd', alpha=0.8)
ax.set_title('二维直方图（密度热力图）', fontsize=14, fontweight='bold')
ax.set_xlabel('X变量')
ax.set_ylabel('Y变量')

# 添加颜色条
plt.colorbar(h[3], ax=ax, label='频数')

plt.show()

# 打印统计信息
print("="*50)
print("数据统计信息")
print("="*50)
print(f"身高数据 - 均值: {np.mean(身高):.2f}cm, 中位数: {np.median(身高):.2f}cm, 标准差: {np.std(身高):.2f}cm")
print(f"收入数据 - 均值: {np.mean(收入):.2f}元, 中位数: {np.median(收入):.2f}元")