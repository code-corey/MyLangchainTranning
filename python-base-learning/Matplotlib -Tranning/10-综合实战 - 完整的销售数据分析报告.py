import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.gridspec import GridSpec

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False    # 用来正常显示负号

# 生成销售数据
np.random.seed(42)
dates = pd.date_range('2024-01-01', '2024-12-31', freq='D')
n = len(dates)

df = pd.DataFrame({
    '日期': dates,
    '销售额': np.random.normal(5000, 1000, n).cumsum() / 100 + 100,
    '订单量': np.random.poisson(50, n) + 20,
    '客户数': np.random.randint(30, 80, n),
    '区域': np.random.choice(['北区', '南区', '东区', '西区'], n, p=[0.3, 0.35, 0.2, 0.15]),
    '产品类别': np.random.choice(['电子产品', '服装', '食品', '家居'], n, p=[0.4, 0.25, 0.2, 0.15])
})

# 添加月份和季度
df['月份'] = df['日期'].dt.month
df['季度'] = df['日期'].dt.quarter

# 创建报告
fig = plt.figure(figsize=(16, 12))
gs = GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)

# ========== 1. 标题 ==========
fig.suptitle('2024年度销售数据分析报告', fontsize=20, fontweight='bold', y=0.98)

# ========== 2. KPI卡片（使用text） ==========
kpi_positions = [(0.05, 0.92), (0.35, 0.92), (0.65, 0.92)]
kpi_data = [
    ('总销售额', f'¥{df["销售额"].sum():,.0f}', '+15.2%'),
    ('总订单量', f'{df["订单量"].sum():,}', '+8.7%'),
    ('平均客单价', f'¥{df["销售额"].sum()/df["订单量"].sum():.2f}', '+5.3%')
]

for (x, y), (title, value, trend) in zip(kpi_positions, kpi_data):
    ax_kpi = fig.add_axes([x, y, 0.25, 0.05])
    ax_kpi.axis('off')
    trend_color = 'green' if '+' in trend else 'red'
    ax_kpi.text(0.1, 0.6, title, fontsize=10, color='gray')
    ax_kpi.text(0.1, 0.2, value, fontsize=16, fontweight='bold')
    ax_kpi.text(0.7, 0.6, trend, fontsize=10, color=trend_color, fontweight='bold')

# ========== 3. 销售额趋势图（占据左上大区域） ==========
ax1 = fig.add_subplot(gs[0, 0:2])
# 按周汇总
weekly_sales = df.resample('W', on='日期')['销售额'].sum()
ax1.plot(weekly_sales.index, weekly_sales.values, 'b-', linewidth=2, label='周销售额')
# 添加移动平均
ma_4 = weekly_sales.rolling(4).mean()
ax1.plot(ma_4.index, ma_4.values, 'r--', linewidth=2, label='4周移动平均')
ax1.fill_between(weekly_sales.index, weekly_sales.values, alpha=0.3)
ax1.set_title('销售额趋势分析', fontsize=12, fontweight='bold')
ax1.set_xlabel('日期')
ax1.set_ylabel('销售额（元）')
ax1.legend()
ax1.grid(True, alpha=0.3)

# ========== 4. 月度对比柱状图 ==========
ax2 = fig.add_subplot(gs[0, 2])
monthly_sales = df.groupby('月份')['销售额'].sum()
bars = ax2.bar(range(1, 13), monthly_sales.values, color='steelblue', edgecolor='black')
ax2.set_title('月度销售额对比', fontsize=12, fontweight='bold')
ax2.set_xlabel('月份')
ax2.set_ylabel('销售额（元）')
ax2.set_xticks(range(1, 13))
# 在柱子上显示数值
for bar, value in zip(bars, monthly_sales.values):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 2000,
             f'{value/10000:.1f}w', ha='center', va='bottom', fontsize=8)

# ========== 5. 区域销售占比饼图 ==========
ax3 = fig.add_subplot(gs[1, 0])
region_sales = df.groupby('区域')['销售额'].sum()
colors_region = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
wedges, texts, autotexts = ax3.pie(region_sales.values, labels=region_sales.index,
                                    colors=colors_region, autopct='%1.1f%%',
                                    startangle=90, shadow=True)
ax3.set_title('各区域销售额占比', fontsize=12, fontweight='bold')

# ========== 6. 产品类别销售柱状图 ==========
ax4 = fig.add_subplot(gs[1, 1])
category_sales = df.groupby('产品类别')['销售额'].sum().sort_values(ascending=False)
bars = ax4.bar(category_sales.index, category_sales.values,
               color=['#FF9999', '#66B2FF', '#99FF99', '#FFCC99'])
ax4.set_title('产品类别销售排行', fontsize=12, fontweight='bold')
ax4.set_xlabel('产品类别')
ax4.set_ylabel('销售额（元）')
ax4.tick_params(axis='x', rotation=45)
# 显示数值
for bar, value in zip(bars, category_sales.values):
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height + 5000,
             f'{value/10000:.1f}w', ha='center', va='bottom')

# ========== 7. 订单量与客户数关系散点图（修正版） ==========
ax5 = fig.add_subplot(gs[1, 2])
# 按周聚合
weekly_orders = df.resample('W', on='日期')['订单量'].sum()
weekly_customers = df.resample('W', on='日期')['客户数'].mean()
# 修正：使用 isocalendar().week 替代废弃的 .week
week_numbers = weekly_sales.index.isocalendar().week
scatter = ax5.scatter(weekly_orders, weekly_customers,
                      c=week_numbers, cmap='plasma', s=50, alpha=0.6)
ax5.set_title('订单量 vs 客户数', fontsize=12, fontweight='bold')
ax5.set_xlabel('周订单量')
ax5.set_ylabel('平均客户数')
plt.colorbar(scatter, ax=ax5, label='周数')

# ========== 8. 季度销售分布箱线图 ==========
ax6 = fig.add_subplot(gs[2, 0:2])
quarter_data = [df[df['季度'] == q]['销售额'] for q in range(1, 5)]
bp = ax6.boxplot(quarter_data, labels=['Q1', 'Q2', 'Q3', 'Q4'],
                 patch_artist=True, showmeans=True)
for patch, color in zip(bp['boxes'], ['lightblue', 'lightgreen', 'lightpink', 'lightyellow']):
    patch.set_facecolor(color)
ax6.set_title('各季度销售额分布', fontsize=12, fontweight='bold')
ax6.set_xlabel('季度')
ax6.set_ylabel('销售额（元）')
ax6.grid(True, alpha=0.3, axis='y')

# ========== 9. 区域-产品热力图 ==========
ax7 = fig.add_subplot(gs[2, 2])
heatmap_data = pd.pivot_table(df, values='销售额',
                              index='区域', columns='产品类别', aggfunc='sum')
im = ax7.imshow(heatmap_data.values, cmap='YlOrRd', aspect='auto')
ax7.set_xticks(range(len(heatmap_data.columns)))
ax7.set_yticks(range(len(heatmap_data.index)))
ax7.set_xticklabels(heatmap_data.columns, rotation=45, ha='right')
ax7.set_yticklabels(heatmap_data.index)
ax7.set_title('区域-产品热力图', fontsize=12, fontweight='bold')

# 显示数值
for i in range(len(heatmap_data.index)):
    for j in range(len(heatmap_data.columns)):
        ax7.text(j, i, f'{heatmap_data.values[i, j]/10000:.1f}',
                ha='center', va='center', fontsize=8)

plt.colorbar(im, ax=ax7, label='销售额（万元）')

# 调整整体布局
plt.tight_layout()
plt.show()

# ========== 10. 生成分析报告文本 ==========
print("\n" + "="*60)
print("销售数据分析摘要")
print("="*60)

print(f"\n📊 整体表现:")
print(f"  • 总销售额: ¥{df['销售额'].sum():,.2f}")
print(f"  • 总订单数: {df['订单量'].sum():,}")
print(f"  • 平均客单价: ¥{df['销售额'].sum()/df['订单量'].sum():.2f}")

print(f"\n🏆 最佳表现:")
best_region = region_sales.idxmax()
print(f"  • 最佳区域: {best_region} (¥{region_sales.max():,.2f})")
best_category = category_sales.idxmax()
print(f"  • 最佳产品类别: {best_category} (¥{category_sales.max():,.2f})")
best_month = monthly_sales.idxmax()
print(f"  • 最佳月份: {best_month}月")

print(f"\n📈 增长趋势:")
q1_sales = df[df['季度'] == 1]['销售额'].sum()
q4_sales = df[df['季度'] == 4]['销售额'].sum()
growth = (q4_sales - q1_sales) / q1_sales * 100
print(f"  • 年度增长率: {growth:.1f}%")

print("\n" + "="*60)