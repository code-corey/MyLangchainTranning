import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report, roc_curve, auc

# 设置中文
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 1. 生成带标签的交易数据
np.random.seed(42)
n_samples = 1000

# 特征：交易金额、交易时间（小时）、用户历史评分
X = np.zeros((n_samples, 3))
X[:, 0] = np.random.exponential(100, n_samples)  # 交易金额
X[:, 1] = np.random.uniform(0, 24, n_samples)   # 交易时间
X[:, 2] = np.random.uniform(0, 100, n_samples)  # 用户评分

# 标签：0=正常，1=欺诈（监督信号）
# 欺诈交易的特征：金额大、深夜、评分低
y = ((X[:, 0] > 200) & (X[:, 1] > 22) & (X[:, 2] < 30)).astype(int)
# 添加一些随机欺诈
y[np.random.choice(n_samples, 30)] = 1

print("="*60)
print("监督学习 - 逻辑回归欺诈检测")
print("="*60)
print(f"总交易数: {n_samples}")
print(f"正常交易: {sum(y==0)}")
print(f"欺诈交易: {sum(y==1)} ({sum(y==1)/n_samples*100:.1f}%)")

# 2. 划分数据
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

# 3. 训练逻辑回归模型
model = LogisticRegression(random_state=42)
model.fit(X_train, y_train)

# 4. 预测
y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)[:, 1]

# 5. 评估
print("\n模型评估:")
print(classification_report(y_test, y_pred,
                           target_names=['正常', '欺诈']))

# 混淆矩阵
cm = confusion_matrix(y_test, y_pred)

# 6. 可视化
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# 混淆矩阵
im = axes[0, 0].imshow(cm, cmap='Blues')
axes[0, 0].set_xticks([0, 1])
axes[0, 0].set_yticks([0, 1])
axes[0, 0].set_xticklabels(['正常', '欺诈'])
axes[0, 0].set_yticklabels(['正常', '欺诈'])
axes[0, 0].set_xlabel('预测标签')
axes[0, 0].set_ylabel('真实标签')
axes[0, 0].set_title('混淆矩阵')

# 添加数值
for i in range(2):
    for j in range(2):
        axes[0, 0].text(j, i, cm[i, j], ha='center', va='center', color='white' if cm[i, j] > cm.max()/2 else 'black')

plt.colorbar(im, ax=axes[0, 0])

# ROC曲线
fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
roc_auc = auc(fpr, tpr)

axes[0, 1].plot(fpr, tpr, 'b-', linewidth=2, label=f'ROC曲线 (AUC = {roc_auc:.3f})')
axes[0, 1].plot([0, 1], [0, 1], 'r--', linewidth=1, label='随机猜测')
axes[0, 1].set_xlabel('假正率')
axes[0, 1].set_ylabel('真正率')
axes[0, 1].set_title('ROC曲线')
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3)

# 特征重要性
feature_names = ['交易金额', '交易时间', '用户评分']
importance = np.abs(model.coef_[0])
axes[1, 0].barh(feature_names, importance, color='steelblue')
axes[1, 0].set_xlabel('特征重要性')
axes[1, 0].set_title('逻辑回归特征权重')

# 概率分布
normal_proba = y_pred_proba[y_test == 0]
fraud_proba = y_pred_proba[y_test == 1]

axes[1, 1].hist(normal_proba, bins=20, alpha=0.7, label='正常交易', color='green')
axes[1, 1].hist(fraud_proba, bins=20, alpha=0.7, label='欺诈交易', color='red')
axes[1, 1].set_xlabel('预测为欺诈的概率')
axes[1, 1].set_ylabel('频数')
axes[1, 1].set_title('预测概率分布')
axes[1, 1].legend()

plt.tight_layout()
plt.show()

# 7. 实时检测示例
print("\n实时交易检测:")
new_transactions = np.array([
    [500, 23, 20],   # 大额、深夜、低分 → 高风险
    [50, 14, 85],    # 小额、白天、高分 → 低风险
    [300, 21, 45]    # 中等风险
])

probs = model.predict_proba(new_transactions)[:, 1]
preds = model.predict(new_transactions)

for i, (amount, hour, score) in enumerate(new_transactions):
    status = "⚠️ 欺诈警告！" if preds[i] == 1 else "✓ 正常"
    risk = "高风险" if probs[i] > 0.7 else ("中风险" if probs[i] > 0.3 else "低风险")
    print(f"交易{i+1}: 金额={amount:.0f}, 时间={hour:.0f}h, 评分={score:.0f}")
    print(f"  欺诈概率: {probs[i]:.2%}, {risk}, {status}\n")