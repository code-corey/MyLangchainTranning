import pandas as pd
import numpy as np

# 创建包含缺失值的数据
df = pd.DataFrame({
    '姓名': ['张三', '李四', '王五', '赵六', '小明'],
    '年龄': [25, np.nan, 28, 35, 22],      # np.nan 表示缺失
    '工资': [8000, 12000, np.nan, 15000, 6000],
    '城市': ['北京', '上海', None, '深圳', '北京']
})

print("原始数据（含缺失值）:")
print(df)

# 检测缺失值
print("\n缺失值检测（True表示缺失）:")
print(df.isnull())

print("\n每列缺失值数量:")
print(df.isnull().sum())

# 删除包含缺失值的行
df_dropped = df.dropna()
print("\n删除缺失值后的数据:")
print(df_dropped)

# 填充缺失值
df_filled = df.fillna({
    '年龄': df['年龄'].mean(),  # 用平均值填充年龄
    '工资': 0,                   # 用0填充工资
    '城市': '未知'               # 用'未知'填充城市
})
print("\n填充缺失值后的数据:")
print(df_filled)

# 向前填充（用上一个值填充）
df_ffill = df.fillna(method='ffill')
print("\n向前填充（用上一个值）:")
print(df_ffill)

# 实际工作中的常用操作
df_clean = df.copy()
# 删除年龄为空的行
df_clean = df_clean.dropna(subset=['年龄'])
# 用中位数填充工资
df_clean['工资'] = df_clean['工资'].fillna(df_clean['工资'].median())
print("\n标准清洗后的数据:")
print(df_clean)

