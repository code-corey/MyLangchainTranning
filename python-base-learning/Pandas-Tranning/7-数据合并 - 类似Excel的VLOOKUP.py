import pandas as pd

# 创建员工信息表
员工表 = pd.DataFrame({
    '员工ID': [101, 102, 103, 104, 105],
    '姓名': ['张三', '李四', '王五', '赵六', '小明'],
    '部门ID': [1, 2, 1, 3, 2]
})

# 创建部门表
部门表 = pd.DataFrame({
    '部门ID': [1, 2, 3],
    '部门名称': ['销售部', '技术部', '管理部'],
    '地点': ['北京', '上海', '深圳']
})

# 创建工资表
工资表 = pd.DataFrame({
    '员工ID': [101, 102, 103, 104, 106],
    '工资': [8000, 12000, 9500, 15000, 10000],
    '年份': [2024, 2024, 2024, 2024, 2024]
})

print("员工表:")
print(员工表)
print("\n部门表:")
print(部门表)
print("\n工资表:")
print(工资表)

# 合并（类似VLOOKUP）: 员工表 + 部门表
员工信息 = pd.merge(员工表, 部门表, on='部门ID', how='left')
print("\n员工信息（关联部门）:")
print(员工信息)

# 多种合并方式
# left join: 保留左表所有行
左连接 = pd.merge(员工表, 工资表, on='员工ID', how='left')
print("\n左连接（保留所有员工）:")
print(左连接)

# inner join: 只保留两表都有的行
内连接 = pd.merge(员工表, 工资表, on='员工ID', how='inner')
print("\n内连接（只保留有工资的员工）:")
print(内连接)

# outer join: 保留所有行
外连接 = pd.merge(员工表, 工资表, on='员工ID', how='outer')
print("\n外连接（保留所有）:")
print(外连接)

# concat: 纵向拼接
员工表2 = pd.DataFrame({
    '员工ID': [106, 107],
    '姓名': ['小红', '小刚'],
    '部门ID': [2, 1]
})
所有员工 = pd.concat([员工表, 员工表2], ignore_index=True)
print("\n纵向拼接所有员工:")
print(所有员工)