import pandas as pd

# 创建一个示例CSV文件（实际使用中会读取真实文件）
data = {
    '产品': ['苹果', '香蕉', '橙子', '葡萄', '西瓜'],
    '销量': [100, 150, 80, 120, 60],
    '单价': [5, 3, 4, 8, 2],
    '区域': ['北区', '南区', '东区', '西区', '北区']
}
df = pd.DataFrame(data)

# 保存为CSV（演示用）
df.to_csv('products.csv', index=False)

# 读取CSV文件
df_read = pd.read_csv('products.csv')
print("读取的CSV文件:")
print(df_read)

# 查看数据的基本信息
print("\n数据基本信息:")
print(df_read.info())

print("\n数据统计描述（数值列）:")
print(df_read.describe())

print("\n前3行数据:")
print(df_read.head(3))

print("\n后2行数据:")
print(df_read.tail(2))