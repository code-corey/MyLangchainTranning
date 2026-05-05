import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from sklearn.datasets import make_blobs

# 设置中文
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 1. 生成正常数据和异常数据（无标签）
np.random.seed(42)

# 正常交易数据
n_normal = 500
normal_transactions = np.random.randn(n_normal, 2) * 0.5 + [100, 1000]

# 异常交易数据
n_outliers = 30
outliers = np.random.randn(n_outliers, 2) * 1.5 + [105, 1200]  # 偏离正常范围

# 合并数据（无标签）
X = np.vstack([normal_transactions, outliers])

print(f"总数据量: {len(X)}")
print(f"推测异常比例: {n_outliers / len(X) * 100:.1f}%")

# 2. 应用孤立森林（无监督异常检测）
iso_forest = IsolationForest(contamination=0.1, random_state=42)  # 假设10%异常
predictions = iso_forest.fit_predict(X)  # 1=正常, -1=异常
scores = iso_forest.decision_function(X)  # 异常分数（负值表示异常）

# 3. 可视化
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 原始数据分布
axes[0, 0].scatter(X[:n_normal, 0], X[:n_normal, 1], c='blue', s=30, alpha=0.6, label='正常')
axes[0, 0].scatter(X[n_normal:, 0], X[n_normal:, 1], c='red', s=50, marker='x', label='真实异常')
axes[0, 0].set_xlabel('交易金额（千元）')
axes[0, 0].set_ylabel('交易时间（秒）')
axes[0, 0].set_title('原始数据分布（红点为真实异常）')
axes[0, 0].legend()

# 孤立森林检测结果
normal_detected = X[predictions == 1]
outliers_detected = X[predictions == -1]

axes[0, 1].scatter(normal_detected[:, 0], normal_detected[:, 1],
                   c='green', s=30, alpha=0.6, label='检测为正常')
axes[0, 1].scatter(outliers_detected[:, 0], outliers_detected[:, 1],
                   c='red', s=50, marker='x', label='检测为异常')
axes[0, 1].set_xlabel('交易金额（千元）')
axes[0, 1].set_ylabel('交易时间（秒）')
axes[0, 1].set_title('孤立森林检测结果')
axes[0, 1].legend()

# 异常分数等高线图
xx, yy = np.meshgrid(np.linspace(X[:, 0].min() - 1, X[:, 0].max() + 1, 100),
                     np.linspace(X[:, 1].min() - 1, X[:, 1].max() + 1, 100))
Z = iso_forest.decision_function(np.c_[xx.ravel(), yy.ravel()])
Z = Z.reshape(xx.shape)

contour = axes[1, 0].contourf(xx, yy, Z, levels=50, cmap='RdYlBu_r', alpha=0.7)
axes[1, 0].scatter(X[:, 0], X[:, 1], c=predictions, cmap='RdYlBu', s=20, alpha=0.6)
axes[1, 0].set_xlabel('交易金额（千元）')
axes[1, 0].set_ylabel('交易时间（秒）')
axes[1, 0].set_title('异常分数分布（蓝色区域为正常）')
plt.colorbar(contour, ax=axes[1, 0], label='异常分数')

# 性能统计
true_outliers = set(range(n_normal, len(X)))
detected_outliers = set(np.where(predictions == -1)[0])

TP = len(detected_outliers & true_outliers)  # 正确检测的异常
FP = len(detected_outliers - true_outliers)  # 误报
FN = len(true_outliers - detected_outliers)  # 漏报

axes[1, 1].axis('off')
axes[1, 1].text(0.1, 0.9, '检测性能统计：', fontsize=12, fontweight='bold')
axes[1, 1].text(0.1, 0.75, f'正确检测异常: {TP}/{n_outliers}', fontsize=10)
axes[1, 1].text(0.1, 0.6, f'误报数: {FP}', fontsize=10)
axes[1, 1].text(0.1, 0.45, f'漏报数: {FN}', fontsize=10)
axes[1, 1].text(0.1, 0.25, f'检测率: {TP/n_outliers*100:.1f}%', fontsize=10)

plt.tight_layout()
plt.show()

# 4. 应用场景：信用卡欺诈检测
print("\n应用场景：信用卡实时欺诈检测")
print("="*50)

# 模拟实时交易流
new_transactions = np.array([
    [100.5, 1002],   # 正常交易
    [104.2, 1190],   # 疑似异常
    [99.8, 1005],    # 正常
    [106.1, 1210],   # 异常
    [101.3, 1008]    # 正常
])

predictions_new = iso_forest.predict(new_transactions)

print("\n实时交易检测结果：")
for i, (amount, time) in enumerate(new_transactions):
    status = "⚠️ 异常交易！" if predictions_new[i] == -1 else "✓ 正常交易"
    print(f"交易{i+1}: 金额={amount:.1f}千元, 时间={time:.0f}秒 → {status}")