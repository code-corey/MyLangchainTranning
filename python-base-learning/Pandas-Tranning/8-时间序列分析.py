import pandas as pd
import numpy as np

# 创建日期范围
dates = pd.date_range('2024-01-01', periods=100, freq='D')
df = pd.DataFrame({
    '日期': dates,
    '销售额': np.random.randint(100, 500, size=100) +
             np.sin(np.arange(100)/10) * 50  # 添加一些波动
})

print("时间序列数据（前10行）:")
print(df.head(10))

# 设置日期为索引
df.set_index('日期', inplace=True)

# 按周汇总
周销售 = df.resample('W').sum()  # W表示周
print("\n按周汇总的销售额:")
print(周销售.head())

# 按月汇总
月销售 = df.resample('ME').mean()
print("\n月平均销售额:")
print(月销售)

# 移动平均（平滑数据）
df['7天移动平均'] = df['销售额'].rolling(window=7).mean()
df['30天移动平均'] = df['销售额'].rolling(window=30).mean()

print("\n添加移动平均后（前15行）:")
print(df.head(15))

# 计算同比增长
df['上月增长率'] = df['销售额'].pct_change(periods=30) * 100
print("\n增长率（前35行中的后10行）:")
print(df['上月增长率'][30:40])

# 时间过滤
print("\n2024年2月的数据:")
二月数据 = df['2024-02-02']
print(二月数据.head())

# 时间偏移
df['昨天销售额'] = df['销售额'].shift(1)
print("\n对比昨天（前5行）:")
print(df[['销售额', '昨天销售额']].head())


"""
解释：
date_range()创建日期序列；
resample()重采样；
rolling()移动窗口；
pct_change()计算增长率；
shift()数据偏移。
"""