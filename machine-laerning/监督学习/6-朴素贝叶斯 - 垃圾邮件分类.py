import numpy as np
import matplotlib.pyplot as plt
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import pandas as pd

# 设置中文
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 1. 创建邮件数据集（带标签）
emails = [
    # 垃圾邮件
    ("免费领取大奖！点击链接赢取iPhone", "spam"),
    ("限时优惠，购买即送大礼包", "spam"),
    ("您的账户异常，请立即验证", "spam"),
    ("恭喜中奖！奖金100万", "spam"),
    ("低价出售名牌手表", "spam"),
    ("贷款服务，快速审批", "spam"),
    ("兼职刷单，日入300", "spam"),

    # 正常邮件
    ("明天下午3点开会，请准时参加", "ham"),
    ("项目进度报告请查收", "ham"),
    ("关于产品需求的讨论", "ham"),
    ("本周工作总结和下周计划", "ham"),
    ("团队聚餐通知", "ham"),
    ("客户反馈意见汇总", "ham"),
    ("技术文档已更新", "ham"),
]

# 扩展数据集（复制并加扰动）
np.random.seed(42)
emails_extended = emails.copy()
for _ in range(50):
    for email, label in emails[:7]:  # 复制垃圾邮件
        # 添加随机字符扰动
        noisy_email = email + " " + "".join(np.random.choice(['!', '？', '限', '免'], 1))
        emails_extended.append((noisy_email, label))
    for email, label in emails[7:]:  # 复制正常邮件
        emails_extended.append((email, label))

print("=" * 60)
print("监督学习 - 朴素贝叶斯垃圾邮件分类")
print("=" * 60)
print(f"总邮件数: {len(emails_extended)}")
print(f"垃圾邮件: {sum(1 for _, label in emails_extended if label == 'spam')}封")
print(f"正常邮件: {sum(1 for _, label in emails_extended if label == 'ham')}封")

# 2. 提取特征（文本向量化）
X_text = [email for email, _ in emails_extended]
y = [1 if label == 'spam' else 0 for _, label in emails_extended]

# 将文本转换为词频向量
vectorizer = CountVectorizer(max_features=100, stop_words='english')
X = vectorizer.fit_transform(X_text)

print(f"\n特征维度: {X.shape[1]}个词")

# 3. 划分数据
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# 4. 训练朴素贝叶斯
nb = MultinomialNB(alpha=1.0)  # alpha是拉普拉斯平滑参数
nb.fit(X_train, y_train)

# 5. 预测
y_pred = nb.predict(X_test)
y_pred_proba = nb.predict_proba(X_test)[:, 1]

# 6. 评估
print(f"\n模型准确率: {nb.score(X_test, y_test):.2%}")
print("\n分类报告:")
print(classification_report(y_test, y_pred, target_names=['正常邮件', '垃圾邮件']))

# 7. 可视化
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 混淆矩阵
cm = confusion_matrix(y_test, y_pred)
im = axes[0, 0].imshow(cm, cmap='Blues')
axes[0, 0].set_xticks([0, 1])
axes[0, 0].set_yticks([0, 1])
axes[0, 0].set_xticklabels(['正常', '垃圾'])
axes[0, 0].set_yticklabels(['正常', '垃圾'])
axes[0, 0].set_xlabel('预测标签')
axes[0, 0].set_ylabel('真实标签')
axes[0, 0].set_title('混淆矩阵')
for i in range(2):
    for j in range(2):
        axes[0, 0].text(j, i, cm[i, j], ha='center', va='center')
plt.colorbar(im, ax=axes[0, 0])

# 概率分布
spam_proba = y_pred_proba[y_test == 1]
ham_proba = y_pred_proba[y_test == 0]

axes[0, 1].hist(ham_proba, bins=20, alpha=0.7, label='正常邮件', color='green')
axes[0, 1].hist(spam_proba, bins=20, alpha=0.7, label='垃圾邮件', color='red')
axes[0, 1].set_xlabel('预测为垃圾的概率')
axes[0, 1].set_ylabel('频数')
axes[0, 1].set_title('预测概率分布')
axes[0, 1].legend()

# 最重要的特征（词）
feature_names = vectorizer.get_feature_names_out()
top_features = np.argsort(nb.feature_log_prob_[1] - nb.feature_log_prob_[0])[-10:]

axes[1, 0].barh(range(10), nb.feature_log_prob_[1][top_features] - nb.feature_log_prob_[0][top_features])
axes[1, 0].set_yticks(range(10))
axes[1, 0].set_yticklabels(feature_names[top_features])
axes[1, 0].set_xlabel('垃圾邮件指示性')
axes[1, 0].set_title('最指示垃圾邮件的词')

# 错误分析
misclassified_idx = np.where(y_pred != y_test)[0]
axes[1, 1].axis('off')
axes[1, 1].text(0.1, 0.9, f'错误分类邮件（共{len(misclassified_idx)}封）:',
                fontsize=12, fontweight='bold')

X_test_text = vectorizer.inverse_transform(X_test)
for i, idx in enumerate(misclassified_idx[:5]):
    true_label = "垃圾" if y_test[idx] == 1 else "正常"
    pred_label = "垃圾" if y_pred[idx] == 1 else "正常"
    axes[1, 1].text(0.1, 0.7 - i * 0.1,
                    f'邮件: {X_test_text[idx][:50]}...\n  真实:{true_label}, 预测:{pred_label}',
                    fontsize=8)
    axes[1, 1].axhline(y=0.65 - i * 0.1, color='gray', linewidth=0.5)

plt.tight_layout()
plt.show()

# 8. 实时垃圾邮件检测
print("\n实时邮件检测:")
test_emails = [
    "恭喜你中奖了！点击领取100万奖金",
    "关于下周一项目评审的会议通知",
    "限时抢购：全场商品5折优惠",
    "请查收本周的工作周报"
]

X_test_new = vectorizer.transform(test_emails)
predictions = nb.predict(X_test_new)
probabilities = nb.predict_proba(X_test_new)

for email, pred, prob in zip(test_emails, predictions, probabilities):
    label = "⚠️ 垃圾邮件" if pred == 1 else "✓ 正常邮件"
    confidence = prob[pred]
    print(f"\n{email}")
    print(f"  判断: {label}, 置信度: {confidence:.2%}")