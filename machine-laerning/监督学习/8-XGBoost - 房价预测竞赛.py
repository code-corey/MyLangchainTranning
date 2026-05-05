import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score
import xgboost as xgb

# 设置中文
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 1. 生成复杂房价数据
np.random.seed(42)
n_houses = 3000

# 特征
X = np.zeros((n_houses, 12))
X[:, 0] = np.random.uniform(50, 300, n_houses)  # 面积
X[:, 1] = np.random.randint(1, 6, n_houses)     # 卧室数
X[:, 2] = np.random.randint(1, 4, n_houses)     # 卫生间数
X[:, 3] = np.random.randint(0, 50, n_houses)    # 房龄
X[:, 4] = np.random.uniform(0, 2, n_houses)     # 距离地铁站(km)
X[:, 5] = np.random.randint(0, 2, n_houses)     # 学区房
X[:, 6] = np.random.uniform(100, 500, n_houses) # 物业费
X[:, 7] = np.random.randint(1, 10, n_houses)    # 楼层
X[:, 8] = np.random.uniform(50, 300, n_houses)  # 周边配套评分
X[:, 9] = np.random.choice([0, 1], n_houses)    # 有无电梯
X[:, 10] = np.random.choice([0, 1], n_houses)   # 有无车位
X[:, 11] = np.random.uniform(0, 5, n_houses)    # 装修评分

# 真实房价公式（非线性）
y = (X[:, 0] * 1.2 +
     X[:, 1] * 20 +
     X[:, 2] * 15 -
     X[:, 3] * 0.5 +
     X[:, 4] * -30 +
     X[:, 5] * 50 +
     X[:, 8] * 1.5 +
     X[:, 9] * 30 +
     X[:, 10] * 25 +
     X[:, 11] * 10 +
     np.random.normal(0, 15, n_houses))  # 噪声

# 添加非线性项
y += (X[:, 0] * X[:, 1]) * 0.1
y += (X[:, 2] ** 2) * 2

print("="*60)
print("监督学习 - XGBoost房价预测")
print("="*60)
print(f"房屋数量: {n_houses}")
print(f"特征数量: {X.shape[1]}")
print(f"房价范围: {y.min():.0f} - {y.max():.0f} 万元")

# 2. 划分数据
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 3. 训练XGBoost
model = xgb.XGBRegressor(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)
model.fit(X_train, y_train)

# 4. 预测
y_pred_train = model.predict(X_train)
y_pred_test = model.predict(X_test)

# 5. 评估
train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
train_r2 = r2_score(y_train, y_pred_train)
test_r2 = r2_score(y_test, y_pred_test)

print(f"\n模型性能:")
print(f"  训练集 RMSE: {train_rmse:.2f} 万元")
print(f"  测试集 RMSE: {test_rmse:.2f} 万元")
print(f"  训练集 R²: {train_r2:.3f}")
print(f"  测试集 R²: {test_r2:.3f}")

# 6. 特征重要性
feature_names = [
    '面积', '卧室数', '卫生间数', '房龄', '距地铁',
    '学区房', '物业费', '楼层', '配套评分', '电梯', '车位', '装修'
]

importance = model.feature_importances_

# 7. 可视化
fig, axes = plt.subplots(2, 3, figsize=(15, 10))

# 特征重要性
indices = np.argsort(importance)[::-1]
axes[0, 0].barh(range(12), importance[indices])
axes[0, 0].set_yticks(range(12))
axes[0, 0].set_yticklabels(np.array(feature_names)[indices])
axes[0, 0].set_xlabel('重要性')
axes[0, 0].set_title('XGBoost特征重要性')

# 预测vs真实
axes[0, 1].scatter(y_test, y_pred_test, alpha=0.5)
axes[0, 1].plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()],
                'r--', linewidth=2, label='完美预测')
axes[0, 1].set_xlabel('真实房价')
axes[0, 1].set_ylabel('预测房价')
axes[0, 1].set_title('预测值 vs 真实值')
axes[0, 1].legend()

# 残差分析
residuals = y_test - y_pred_test
axes[0, 2].scatter(y_pred_test, residuals, alpha=0.5)
axes[0, 2].axhline(y=0, color='red', linestyle='--')
axes[0, 2].set_xlabel('预测房价')
axes[0, 2].set_ylabel('残差')
axes[0, 2].set_title('残差分布')

# 训练过程中性能变化
results = model.evals_result()
if hasattr(model, 'evals_result'):
    epochs = len(results['validation_0']['rmse'])
    axes[1, 0].plot(range(epochs), results['validation_0']['rmse'], 'b-', label='训练')
    axes[1, 0].set_xlabel('迭代次数')
    axes[1, 0].set_ylabel('RMSE')
    axes[1, 0].set_title('学习曲线')
    axes[1, 0].legend()

# 误差分布
axes[1, 1].hist(residuals, bins=30, edgecolor='black', alpha=0.7)
axes[1, 1].set_xlabel('预测误差')
axes[1, 1].set_ylabel('频数')
axes[1, 1].set_title('预测误差分布')
axes[1, 1].axvline(x=0, color='red', linestyle='--')

# 交叉验证
cv_scores = cross_val_score(model, X_train, y_train, cv=5,
                            scoring='r2', n_jobs=-1)
axes[1, 2].bar(range(1, 6), cv_scores)
axes[1, 2].axhline(y=cv_scores.mean(), color='red', linestyle='--',
                   label=f'平均: {cv_scores.mean():.3f}')
axes[1, 2].set_xlabel('折')
axes[1, 2].set_ylabel('R²')
axes[1, 2].set_title('5折交叉验证')
axes[1, 2].legend()

plt.tight_layout()
plt.show()

# 8. 新房价预测
print("\n新房价预测:")
new_house = np.array([[
    120,  # 面积
    3,    # 卧室
    2,    # 卫生间
    5,    # 房龄
    1.5,  # 距地铁
    1,    # 学区房
    200,  # 物业费
    5,    # 楼层
    250,  # 配套评分
    1,    # 电梯
    1,    # 车位
    4     # 装修评分
]])

price = model.predict(new_house)[0]
print(f"房屋特征:")
for name, val in zip(feature_names, new_house[0]):
    print(f"  {name}: {val}")
print(f"\n预测房价: {price:.1f} 万元")