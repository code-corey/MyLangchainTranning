import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# 设置中文
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 1. 生成带标签的数据（监督学习核心：有X和y）
np.random.seed(42)
n_samples = 200

# 特征：房屋面积（平方米）
X = np.random.uniform(50, 200, n_samples).reshape(-1, 1)

# 标签：房价（万元）= 面积 * 1.5 + 噪声
y = X[:, 0] * 1.5 + np.random.normal(0, 20, n_samples)

print("="*60)
print("监督学习 - 线性回归房价预测")
print("="*60)
print(f"特征（X）: 房屋面积 {X.shape}")
print(f"标签（y）: 房价 {y.shape}")
print(f"真实关系: 房价 = 面积 × 1.5 + 随机误差")

# 2. 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"\n训练集: {len(X_train)}个样本")
print(f"测试集: {len(X_test)}个样本")

# 3. 训练监督学习模型
model = LinearRegression()
model.fit(X_train, y_train)

# 4. 预测
y_train_pred = model.predict(X_train)
y_test_pred = model.predict(X_test)

# 5. 评估模型
train_mse = mean_squared_error(y_train, y_train_pred)
test_mse = mean_squared_error(y_test, y_test_pred)
train_r2 = r2_score(y_train, y_train_pred)
test_r2 = r2_score(y_test, y_test_pred)

print(f"\n模型参数:")
print(f"  斜率（系数）: {model.coef_[0]:.3f}")
print(f"  截距: {model.intercept_:.3f}")
print(f"\n训练集表现:")
print(f"  MSE: {train_mse:.2f}")
print(f"  R²: {train_r2:.3f}")
print(f"\n测试集表现:")
print(f"  MSE: {test_mse:.2f}")
print(f"  R²: {test_r2:.3f}")

# 6. 可视化
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 回归线图
axes[0].scatter(X_train, y_train, alpha=0.5, label='训练数据', color='blue')
axes[0].scatter(X_test, y_test, alpha=0.5, label='测试数据', color='green')
axes[0].plot(X, model.predict(X), 'r-', linewidth=2, label='回归线')
axes[0].set_xlabel('房屋面积（平方米）')
axes[0].set_ylabel('房价（万元）')
axes[0].set_title('线性回归房价预测')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# 预测vs真实值
axes[1].scatter(y_test, y_test_pred, alpha=0.5)
axes[1].plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()],
             'r--', linewidth=2, label='完美预测线')
axes[1].set_xlabel('真实房价')
axes[1].set_ylabel('预测房价')
axes[1].set_title('预测值 vs 真实值')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# 7. 预测示例
print("\n新房屋价格预测:")
new_houses = np.array([[80], [120], [150]])
predictions = model.predict(new_houses)
for area, price in zip(new_houses, predictions):
    print(f"面积 {area[0]} 平方米 → 预测价格 {price:.1f} 万元")