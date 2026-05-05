import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 准备数据
市场占有率 = [35, 28, 20, 12, 5]
公司 = ['华为', '苹果', '小米', 'OPPO', '其他']
颜色 = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
# 突出显示华为（分离出来）
explode = (0.1, 0, 0, 0, 0)  # 0.1表示分离10%的半径

# 创建图形
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# 子图1：标准饼图
wedges, texts, autotexts = ax1.pie(市场占有率,
                                    labels=公司,
                                    colors=颜色,
                                    explode=explode,  # 分离效果
                                    autopct='%1.1f%%',  # 显示百分比
                                    startangle=90,      # 起始角度
                                    shadow=True,        # 阴影效果
                                    textprops={'fontsize': 12})

# 美化百分比文字
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')

ax1.set_title('智能手机市场份额', fontsize=14, fontweight='bold')

# 子图2：环形图（更现代）
# 创建数据：内圈是手机品牌，外圈是价格区间
inner_data = [35, 28, 20, 12, 5]
outer_data = [15, 20, 10, 18, 12, 8, 10, 7]
outer_labels = ['旗舰机', '高端机', '中端机', '入门机', '旗舰机', '高端机', '中端机', '入门机']
outer_colors = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99', '#FF6666', '#3399FF', '#66FF66', '#FFB366']

# 绘制内圈
ax2.pie(inner_data, radius=0.7, colors=颜色,
        autopct='%1.1f%%', pctdistance=0.85, startangle=90)

# 绘制外圈
wedges2, texts2 = ax2.pie(outer_data, radius=1.0, colors=outer_colors,
                          labels=outer_labels, labeldistance=1.05,
                          startangle=90, textprops={'fontsize': 9})

ax2.set_title('手机品牌与价格区间分布', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.show()

# 单独展示饼图的最佳实践
fig2, ax3 = plt.subplots(figsize=(8, 8))

# 当数据点太多时，突出主要部分
市场数据 = [35, 28, 20, 8, 5, 4]  # 6个数据
公司名称 = ['华为', '苹果', '小米', 'OPPO', 'vivo', '其他']

# 合并小类别（小于5%的归为"其他"）
threshold = 5
main_data = []
main_labels = []
other_sum = 0

for value, label in zip(市场数据, 公司名称):
    if value >= threshold:
        main_data.append(value)
        main_labels.append(label)
    else:
        other_sum += value

if other_sum > 0:
    main_data.append(other_sum)
    main_labels.append('其他')

colors2 = plt.cm.Set3(range(len(main_data)))  # 使用预定义颜色

ax3.pie(main_data, labels=main_labels, colors=colors2,
        autopct='%1.1f%%', startangle=90, shadow=True)
ax3.set_title('市场份额（合并小类别）', fontsize=14, fontweight='bold')

plt.show()