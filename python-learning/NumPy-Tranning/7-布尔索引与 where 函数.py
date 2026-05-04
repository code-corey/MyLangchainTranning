import numpy as np

# 生成 10 个随机年龄 (18~60)
ages = np.random.randint(18, 61, size=10)
print("年龄数组:", ages)

# 布尔索引: 选出 30 岁以上的
adult_mask = ages > 30
print("大于30的年龄:", ages[adult_mask])

# 用 where 替换: 将大于30的标记为 'Senior', 否则 'Junior'
labels = np.where(ages > 30, "Senior", "Junior")
print("对应标签:", labels)

# 结合多个条件 (30到50之间)
middle = ages[(ages > 30) & (ages < 50)]
print("30到50之间的年龄:", middle)


"""
目的：通过条件快速筛选、替换数组元素

解释：布尔索引可以传入一个与数组形状相同的布尔数组，返回满足 True 位置的元素。
np.where(condition, x, y) 类似三目运算符，满足条件的位置取 x，否则取 y。
多条件需用 &（且）或 |（或）连接，要加括号。
"""