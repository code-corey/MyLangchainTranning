import pandas as pd
import numpy as np

# 1. 生成模拟数据
np.random.seed(42)
"""
# 没有seed = 每次都是新的一副随机牌
# 有seed = 把牌按照固定顺序摆好，每次发的牌都一样
"""

n_rows = 5000

df = pd.DataFrame({
    '订单ID': range(10001, 10001 + n_rows),
    '日期': pd.date_range('2024-01-01', periods=n_rows, freq='h'),
    '区域': np.random.choice(['北区', '南区', '东区', '西区'], n_rows, p=[0.3, 0.3, 0.2, 0.2]),
    '产品类别': np.random.choice(['电子产品', '服装', '食品', '家居'], n_rows),
    '产品名称': np.random.choice(['手机', '电脑', 'T恤', '牛仔裤', '零食', '饮料', '沙发', '床'], n_rows),
    '销售额': np.random.uniform(50, 5000, n_rows),
    '数量': np.random.randint(1, 10, n_rows),
    '客户ID': np.random.randint(1000, 2000, n_rows)
})

"""
np.random.choice(a, size=None, replace=True, p=None)

a	抽取的池子（列表、数组或整数）
size	抽取多少个
replace	是否放回（能否重复抽到同一个）
p	每个元素的概率权重
"""



# 添加一些缺失值
df.loc[np.random.choice(n_rows, 100), '销售额'] = np.nan
df.loc[np.random.choice(n_rows, 50), '客户ID'] = np.nan

print("="*60)
print("销售数据分析报告")
print("="*60)

# 2. 数据清洗
print("\n1. 数据概览:")
print(f"总订单数: {len(df):,}")
print(f"数据时间范围: {df['日期'].min()} 至 {df['日期'].max()}")
print(f"缺失值情况:\n{df.isnull().sum()}")

# 清洗：删除销售额缺失的行
df_clean = df.dropna(subset=['销售额'])
# 填充客户ID缺失值
df_clean['客户ID'] = df_clean['客户ID'].fillna(0).astype(int)

print(f"\n清洗后订单数: {len(df_clean):,}")

# 3. 基础统计
print("\n2. 销售统计:")
print(f"总销售额: ¥{df_clean['销售额'].sum():,.2f}")
print(f"平均订单金额: ¥{df_clean['销售额'].mean():,.2f}")
print(f"最高单笔订单: ¥{df_clean['销售额'].max():,.2f}")
print(f"总销售数量: {df_clean['数量'].sum():,}")

# 4. 按区域分析
区域销售 = df_clean.groupby('区域').agg({
    '销售额': ['sum', 'mean', 'count'],
    '数量': 'sum'
}).round(2)
区域销售.columns = ['总销售额', '平均销售额', '订单数', '总销量']
区域销售 = 区域销售.sort_values('总销售额', ascending=False)
print("\n3. 各区域销售分析:")
print(区域销售)

# 5. 按产品类别分析
产品类别销售 = df_clean.groupby('产品类别')['销售额'].agg(['sum', 'mean', 'count'])
产品类别销售 = 产品类别销售.sort_values('sum', ascending=False)
print("\n4. 各产品类别销售排行:")
print(产品类别销售)

# 6. 时间趋势分析
df_clean['月份'] = df_clean['日期'].dt.month
df_clean['星期'] = df_clean['日期'].dt.dayofweek
df_clean['小时'] = df_clean['日期'].dt.hour

月度销售 = df_clean.groupby('月份')['销售额'].sum()
print("\n5. 月度销售趋势:")
print(月度销售)

# 7. 客户分析
客户消费 = df_clean.groupby('客户ID')['销售额'].agg(['sum', 'count', 'mean'])
客户消费.columns = ['总消费', '购买次数', '平均消费']
# 分析高价值客户（消费前10）
top_customers = 客户消费.nlargest(10, '总消费')
print("\n6. TOP10 高价值客户:")
print(top_customers)

# 8. 创建透视表
透视表 = pd.pivot_table(df_clean,
                        values='销售额',
                        index='区域',
                        columns='产品类别',
                        aggfunc='sum',
                        fill_value=0)
print("\n7. 区域×产品类别销售矩阵:")
print(透视表)

# 9. RFM分析（客户价值模型）
# 计算最近购买时间、购买频率、消费金额
rfm = df_clean.groupby('客户ID').agg({
    '日期': lambda x: (df_clean['日期'].max() - x.max()).days,  # 最近
    '订单ID': 'count',  # 频率
    '销售额': 'sum'  # 金额
})
rfm.columns = ['Recency', 'Frequency', 'Monetary']

# 打分
rfm['R_score'] = pd.qcut(rfm['Recency'], 4, labels=['4', '3', '2', '1'])
rfm['F_score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 4, labels=['1', '2', '3', '4'])
rfm['M_score'] = pd.qcut(rfm['Monetary'], 4, labels=['1', '2', '3', '4'])
rfm['RFM_score'] = rfm['R_score'].astype(str) + rfm['F_score'].astype(str) + rfm['M_score'].astype(str)

print("\n8. RFM客户分层（前10行）:")
print(rfm.head(10))

# 10. 保存分析结果
区域销售.to_csv('区域销售分析.csv')
客户消费.to_csv('客户消费分析.csv')
print("\n9. 分析结果已保存到CSV文件")

print("\n" + "="*60)
print("分析报告完成！")
print("="*60)