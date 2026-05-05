import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.metrics import mean_squared_error, r2_score
import xgboost as xgb
import warnings
warnings.filterwarnings('ignore')

# 设置中文
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 1. 生成完整数据集
np.random.seed(42)
n_houses = 5000

# 特征
data = {
    '面积': np.random.uniform(50, 300, n_houses),
    '卧室数': np.random.randint(1, 6, n_houses),
    '卫生间数': np.random.randint(1, 4, n_houses),
    '房龄': np.random.randint(0, 50, n_houses),
    '距离地铁站': np.random.uniform(0, 3, n_houses),
    '学区房': np.random.choice([0, 1], n_houses),
    '楼层': np.random.randint(1, 30, n_houses),
    '总楼层': np.random.randint(5, 35, n_houses),
    '物业费': np.random.uniform(100, 500, n_houses),
    '装修标准': np.random.choice(['简装', '中装', '精装', '豪装'], n_houses),
    '朝向': np.random.choice(['东', '南', '西', '北'], n_houses),
    '区域': np.random.choice(['中心区', '次中心', '郊区'], n_houses)
}

df = pd.DataFrame(data)

# 编码分类变量
le_装修 = LabelEncoder()
le_朝向 = LabelEncoder()
le_区域 = LabelEncoder()

df['装修_编码'] = le_装修.fit_transform(df['装修标准'])
df['朝向_编码'] = le_朝向.fit_transform(df['朝向'])
df['区域_编码'] = le_区域.fit_transform(df['区域'])

# 计算楼层比例
df['楼层比例'] = df['楼层'] / df['总楼层']

# 生成房价标签
df['房价'] = (
    df['面积'] * 1.5 +
    df['卧室数'] * 20 +
    df['卫生间数'] * 15 -
    df['房龄'] * 0.3 -
    df['距离地铁站'] * 30 +
    df['学区房'] * 50 +
    df['楼层比例'] * 50 +
    df['装修_编码'] * 15 +
    df['朝向_编码'] * 5 +
    (df['区域_编码'] == 0) * 80 +
    (df['区域_编码'] == 1) * 40 +
    np.random.normal(0, 15, n_houses)
)

print("="*60)
print("监督学习 - 房价预测完整实战")
print("="*60)
print(f"数据集大小: {len(df)} 行, {len(df.columns)} 列")
print(f"房价范围: {df['房价'].min():.0f} - {df['房价'].max():.0f} 万元")

# 2. 探索性数据分析
fig, axes = plt.subplots(2, 3, figsize=(15, 10))

# 房价分布
axes[0, 0].hist(df['房价'], bins=50, edgecolor='black', alpha=0.7)
axes[0, 0].set_xlabel('房价（万元）')
axes[0, 0].set_ylabel('频数')
axes[0, 0].set_title('房价分布')
axes[0, 0].axvline(df['房价'].mean(), color='red', linestyle='--',
                   label=f'均值: {df["房价"].mean():.0f}')
axes[0, 0].legend()

# 面积vs房价
axes[0, 1].scatter(df['面积'], df['房价'], alpha=0.3, s=10)
axes[0, 1].set_xlabel('面积（平方米）')
axes[0, 1].set_ylabel('房价（万元）')
axes[0, 1].set_title('面积 vs 房价')

# 区域vs房价
df.groupby('区域')['房价'].mean().plot(kind='bar', ax=axes[0, 2])
axes[0, 2].set_xlabel('区域')
axes[0, 2].set_ylabel('平均房价')
axes[0, 2].set_title('不同区域平均房价')

# 装修标准vs房价
df.groupby('装修标准')['房价'].mean().plot(kind='bar', ax=axes[1, 0])
axes[1, 0].set_xlabel('装修标准')
axes[1, 0].set_ylabel('平均房价')
axes[1, 0].set_title('装修标准对房价影响')

# 学区房影响
df.groupby('学区房')['房价'].mean().plot(kind='bar', ax=axes[1, 1])
axes[1, 1].set_xticklabels(['非学区', '学区'])
axes[1, 1].set_xlabel('是否学区房')
axes[1, 1].set_ylabel('平均房价')
axes[1, 1].set_title('学区房对房价影响')

# 相关性热力图
numeric_cols = df.select_dtypes(include=[np.number]).columns
corr_matrix = df[numeric_cols].corr()
im = axes[1, 2].imshow(corr_matrix, cmap='coolwarm', aspect='auto')
axes[1, 2].set_xticks(range(len(numeric_cols)))
axes[1, 2].set_yticks(range(len(numeric_cols)))
axes[1, 2].set_xticklabels(numeric_cols, rotation=45, ha='right', fontsize=8)
axes[1, 2].set_yticklabels(numeric_cols, fontsize=8)
axes[1, 2].set_title('特征相关性')
plt.colorbar(im, ax=axes[1, 2])

plt.tight_layout()
plt.show()

# 3. 准备特征和标签
feature_cols = ['面积', '卧室数', '卫生间数', '房龄', '距离地铁站',
                '学区房', '楼层比例', '装修_编码', '朝向_编码', '区域_编码']
X = df[feature_cols]
y = df['房价']

# 4. 划分数据
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 5. 标准化
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 6. 多个模型对比
models = {
    '线性回归': LinearRegression(),
    'Ridge回归': Ridge(alpha=1.0),
    'Lasso回归': Lasso(alpha=0.001),
    '随机森林': RandomForestRegressor(n_estimators=100, random_state=42),
    '梯度提升': GradientBoostingRegressor(n_estimators=100, random_state=42),
    'XGBoost': xgb.XGBRegressor(n_estimators=100, random_state=42)
}

results = []
print("\n模型对比:")
print("-"*80)

for name, model in models.items():
    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    results.append({'模型': name, 'RMSE': rmse, 'R²': r2})
    print(f"{name:12} | RMSE: {rmse:.2f} | R²: {r2:.4f}")

# 7. 最优模型调优
best_model = xgb.XGBRegressor(random_state=42)
param_grid = {
    'n_estimators': [100, 200],
    'max_depth': [3, 5, 7],
    'learning_rate': [0.01, 0.1]
}

print("\n最优模型超参数调优...")
grid_search = GridSearchCV(best_model, param_grid, cv=5, scoring='r2', n_jobs=-1)
grid_search.fit(X_train_scaled, y_train)

print(f"最佳参数: {grid_search.best_params_}")
print(f"最佳R²: {grid_search.best_score_:.4f}")

# 8. 最终模型
final_model = grid_search.best_estimator_
final_model.fit(X_train_scaled, y_train)
y_pred_final = final_model.predict(X_test_scaled)
final_rmse = np.sqrt(mean_squared_error(y_test, y_pred_final))
final_r2 = r2_score(y_test, y_pred_final)

print(f"\n最终模型表现:")
print(f"  RMSE: {final_rmse:.2f} 万元")
print(f"  R²: {final_r2:.4f}")

# 9. 结果可视化
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 模型对比
results_df = pd.DataFrame(results)
axes[0, 0].barh(results_df['模型'], results_df['R²'], color='steelblue')
axes[0, 0].set_xlabel('R²')
axes[0, 0].set_title('模型性能对比')
axes[0, 0].axvline(x=final_r2, color='red', linestyle='--', label=f'最优: {final_r2:.3f}')
axes[0, 0].legend()

# 预测vs真实
axes[0, 1].scatter(y_test, y_pred_final, alpha=0.5, s=20)
axes[0, 1].plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()],
                'r--', linewidth=2, label='完美预测')
axes[0, 1].set_xlabel('真实房价')
axes[0, 1].set_ylabel('预测房价')
axes[0, 1].set_title(f'最终模型预测 (R²={final_r2:.3f})')
axes[0, 1].legend()

# 残差分析
residuals = y_test - y_pred_final
axes[1, 0].scatter(y_pred_final, residuals, alpha=0.5, s=20)
axes[1, 0].axhline(y=0, color='red', linestyle='--')
axes[1, 0].set_xlabel('预测房价')
axes[1, 0].set_ylabel('残差')
axes[1, 0].set_title('残差分析')

# 误差分布
axes[1, 1].hist(residuals, bins=30, edgecolor='black', alpha=0.7)
axes[1, 1].set_xlabel('预测误差')
axes[1, 1].set_ylabel('频数')
axes[1, 1].set_title(f'误差分布 (RMSE={final_rmse:.2f})')
axes[1, 1].axvline(x=0, color='red', linestyle='--')
axes[1, 1].axvline(x=residuals.mean(), color='green', linestyle='--',
                   label=f'均值: {residuals.mean():.2f}')
axes[1, 1].legend()

plt.tight_layout()
plt.show()

# 10. 最终报告
print("\n" + "="*60)
print("项目总结")
print("="*60)

print(f"\n1. 数据概况:")
print(f"   - 总样本数: {len(df)}")
print(f"   - 特征数: {len(feature_cols)}")
print(f"   - 房价范围: [{y.min():.0f}, {y.max():.0f}]万元")

print(f"\n2. 模型表现:")
print(f"   - 最优模型: XGBoost")
print(f"   - 最佳参数: {grid_search.best_params_}")
print(f"   - 测试集R²: {final_r2:.4f}")
print(f"   - 测试集RMSE: {final_rmse:.2f}万元")

print(f"\n3. 重要特征:")
importance = final_model.feature_importances_
for name, imp in sorted(zip(feature_cols, importance), key=lambda x: x[1], reverse=True)[:5]:
    print(f"   - {name}: {imp:.3f}")

print(f"\n4. 模型可用性:")
if final_r2 > 0.8:
    print("   ✓ 模型表现优秀，可用于实际预测")
elif final_r2 > 0.6:
    print("   ✓ 模型表现良好，可辅助决策")
else:
    print("   ⚠ 模型需要进一步优化")