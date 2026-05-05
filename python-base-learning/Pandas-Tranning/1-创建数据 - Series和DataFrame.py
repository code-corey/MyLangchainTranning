import pandas as pd
import numpy as np

# Series：一维数据（像带标签的列表）
s = pd.Series([1, 3, 5, 7, 9], index=['a', 'b', 'c', 'd', 'e'])
print("Series（一维带标签数组）:")
print(s)
print(f"访问a标签的值: {s['a']}")
print(f"访问前两个: {s[:2]}")

# DataFrame：二维表格（像Excel表格）
df = pd.DataFrame({
    '姓名': ['张三', '李四', '王五', '赵六'],
    '年龄': [25, 30, 28, 35],
    '城市': ['北京', '上海', '广州', '深圳'],
    '工资': [8000, 12000, 10000, 15000]
})
print("\nDataFrame（二维表格）:")
print(df)
print(f"\n表格形状: {df.shape} (行, 列)")
print(f"列名: {df.columns.tolist()}")
print(f"索引: {df.index.tolist()}")