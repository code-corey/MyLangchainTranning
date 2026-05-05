import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, roc_auc_score
import pandas as pd

# 设置中文
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 1. 生成银行客户数据
np.random.seed(42)
n_customers = 2000

# 特征
data = {
    '年龄': np.random.randint(18, 70, n_customers),
    '收入': np.random.exponential(50, n_customers) * 1000,
    '信用分': np.random.randint(300, 850, n_customers),
    '账户年限': np.random.uniform(1, 20, n_customers),
    '月交易次数': np.random.poisson(10, n_customers),
    '负债率': np.random.uniform(0, 0.8, n_customers),
    '客服投诉': np.random.poisson(1, n_customers)
}

X = pd.DataFrame(data)

# 标签：是否流失（监督信号）
# 流失客户特征：信用分低、投诉多、负债率高、账户年限短
y = ((X['信用分'] < 550) |
     (X['客服投诉'] > 2) |
     (X['负债率'] > 0.6) |
     (X['账户年限'] < 2)).astype(int)
# 添加随机性
y = y | (np.random.random(n_customers) < 0.1)
y = y.astype(int)

print("="*60)
print("监督学习 - 随机森林客户流失预测")
print("="*60)
print(f"客户总数: {n_customers}")
print(f"流失客户: {sum(y)} ({sum(y)/n_customers*100:.1f}%)")
print(f"特征数量: {X.shape[1]}")

# 2. 划分数据
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 3. 训练随机森林
rf = RandomForestClassifier(n_estimators=100, max_depth=10,
                            random_state=42, n_jobs=-1)
rf.fit(X_train, y_train)

# 4. 交叉验证
cv_scores = cross_val_score(rf, X_train, y_train, cv=5)
print(f"\n交叉验证准确率: {cv_scores.mean():.3f} (+/- {cv_scores.std()*2:.3f})")

# 5. 测试集评估
y_pred = rf.predict(X_test)
y_pred_proba = rf.predict_proba(X_test)[:, 1]

accuracy = accuracy_score(y_test, y_pred)
auc = roc_auc_score(y_test, y_pred_proba)

print(f"\n测试集表现:")
print(f"  准确率: {accuracy:.3f}")
print(f"  AUC: {auc:.3f}")

# 6. 可视化
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 特征重要性
importances = rf.feature_importances_
feature_names = X.columns
indices = np.argsort(importances)[::-1]

axes[0, 0].barh(range(len(importances)), importances[indices])
axes[0, 0].set_yticks(range(len(importances)))
axes[0, 0].set_yticklabels(feature_names[indices])
axes[0, 0].set_xlabel('重要性')
axes[0, 0].set_title('随机森林特征重要性')

# 预测概率分布
churn_proba = y_pred_proba[y_test == 1]
retain_proba = y_pred_proba[y_test == 0]

axes[0, 1].hist(retain_proba, bins=30, alpha=0.7, label='留存客户', color='green')
axes[0, 1].hist(churn_proba, bins=30, alpha=0.7, label='流失客户', color='red')
axes[0, 1].set_xlabel('预测流失概率')
axes[0, 1].set_ylabel('频数')
axes[0, 1].set_title('预测概率分布')
axes[0, 1].legend()

# 树的数量影响
n_estimators_range = [10, 50, 100, 200, 300]
scores = []
for n in n_estimators_range:
    rf_temp = RandomForestClassifier(n_estimators=n, max_depth=10,
                                      random_state=42, n_jobs=-1)
    rf_temp.fit(X_train, y_train)
    scores.append(accuracy_score(y_test, rf_temp.predict(X_test)))

axes[1, 0].plot(n_estimators_range, scores, 'bo-', linewidth=2)
axes[1, 0].set_xlabel('决策树数量')
axes[1, 0].set_ylabel('准确率')
axes[1, 0].set_title('集成学习效果：更多树提升性能')
axes[1, 0].grid(True, alpha=0.3)

# 高风险客户识别
proba_threshold = 0.7
high_risk = X_test[y_pred_proba > proba_threshold]
risk_probas = y_pred_proba[y_pred_proba > proba_threshold]

axes[1, 1].bar(range(len(high_risk)), risk_probas, color='red', alpha=0.6)
axes[1, 1].axhline(y=proba_threshold, color='black', linestyle='--',
                   label=f'风险阈值 ({proba_threshold})')
axes[1, 1].set_xlabel('高风险客户')
axes[1, 1].set_ylabel('流失概率')
axes[1, 1].set_title(f'识别高风险客户（共{len(high_risk)}个）')
axes[1, 1].legend()

plt.tight_layout()
plt.show()

# 7. 风险客户分析
print(f"\n高风险客户分析（流失概率>{proba_threshold}）:")
risk_df = X_test[y_pred_proba > proba_threshold].copy()
risk_df['流失概率'] = risk_probas

if len(risk_df) > 0:
    print(f"发现{len(risk_df)}个高风险客户")
    print("\n高风险客户特征:")
    for col in risk_df.columns[:-1]:
        avg_val = risk_df[col].mean()
        overall_avg = X_test[col].mean()
        print(f"  {col}: {avg_val:.2f} (整体平均: {overall_avg:.2f})")