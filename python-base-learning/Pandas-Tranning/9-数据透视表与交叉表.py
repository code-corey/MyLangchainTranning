import pandas as pd
import numpy as np

# 创建销售数据
np.random.seed(42)
数据量 = 1000
df = pd.DataFrame({
    '日期': pd.date_range('2024-01-01', periods=数据量, freq='D'),
    '区域': np.random.choice(['北区', '南区', '东区', '西区'], 数据量),
    '产品': np.random.choice(['手机', '电脑', '平板', '耳机'], 数据量),
    '销售额': np.random.randint(1000, 10000, 数据量),
    '数量': np.random.randint(1, 20, 数据量),
    '客户等级': np.random.choice(['A', 'B', 'C'], 数据量)
})

print("原始数据前5行:")
print(df.head())

# 添加月份列
df['月份'] = df['日期'].dt.month

# 透视表：区域 × 产品的销售额总和
透视表1 = pd.pivot_table(df,
                         values='销售额',
                         index='区域',
                         columns='产品',
                         aggfunc='sum')
print("\n透视表：按区域和产品的销售额总和:")
print(透视表1)

# 多值透视表
透视表2 = pd.pivot_table(df,
                         values=['销售额', '数量'],
                         index='区域',
                         columns='产品',
                         aggfunc=['sum', 'mean'])
print("\n透视表：多个值和多个聚合函数:")
print(透视表2)

# 交叉表：频率统计
交叉表 = pd.crosstab(df['区域'], df['客户等级'], margins=True)
print("\n交叉表：各区域客户等级分布:")
print(交叉表)

# 带权重的交叉表
加权交叉表 = pd.crosstab(df['区域'], df['产品'],
                        values=df['销售额'],
                        aggfunc='sum',
                        normalize='index')
print("\n加权交叉表：各区域产品销售占比:")
print(加权交叉表)

# 多层索引透视表
多层透视表 = pd.pivot_table(df,
                           values='销售额',
                           index=['区域', '客户等级'],
                           columns='月份',
                           aggfunc='mean',
                           fill_value=0)
print("\n多层透视表：")
print(多层透视表)


"""
解释：
pivot_table()创建数据透视表；
crosstab()计算频率表；
index定义行；
columns定义列；
values定义值；
aggfunc定义聚合函数。
"""