import numpy as np
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules

# 注意：需要安装 mlxtend: pip install mlxtend

# 1. 模拟交易数据（无标签）
np.random.seed(42)
n_transactions = 1000

# 商品列表
products = ['牛奶', '面包', '鸡蛋', '黄油', '咖啡', '茶', '果汁', '麦片']

# 生成购物篮数据
transactions = []
for _ in range(n_transactions):
    # 随机决定购买哪些商品
    basket = np.random.choice(products, size=np.random.randint(1, 6), replace=False)
    transactions.append(basket)

print(f"总交易数: {len(transactions)}")
print(f"商品种类: {len(products)}")

# 2. 转换为One-Hot编码
# 创建商品-交易矩阵
unique_products = sorted(products)
basket_df = pd.DataFrame(columns=unique_products)

for i, basket in enumerate(transactions):
    row = pd.Series([1 if p in basket else 0 for p in unique_products],
                    index=unique_products)
    basket_df.loc[i] = row

print(f"\n交易矩阵形状: {basket_df.shape}")
print("前5行预览:")
print(basket_df.head())

# 3. 使用Apriori算法发现频繁项集
print("\n挖掘频繁项集...")
frequent_itemsets = apriori(basket_df, min_support=0.05, use_colnames=True)
print(f"发现{len(frequent_itemsets)}个频繁项集")

print("\n频繁项集示例（支持度>0.1）:")
print(frequent_itemsets[frequent_itemsets['support'] > 0.1].head(10))

# 4. 生成关联规则
rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1.0)
print(f"\n发现{len(rules)}条关联规则")

# 5. 分析结果
print("\n强关联规则（提升度>1.5）:")
strong_rules = rules[rules['lift'] > 1.5].sort_values('lift', ascending=False)
for _, rule in strong_rules.head(10).iterrows():
    antecedents = ', '.join(list(rule['antecedents']))
    consequents = ', '.join(list(rule['consequents']))
    print(f"如果买了 {antecedents} -> 也会买 {consequents}")
    print(f"  支持度: {rule['support']:.3f}, 置信度: {rule['confidence']:.3f}, 提升度: {rule['lift']:.3f}")
    print()

# 6. 可视化关联规则
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# 支持度 vs 置信度散点图
scatter = axes[0].scatter(rules['support'], rules['confidence'],
                          c=rules['lift'], cmap='viridis', s=50, alpha=0.6)
axes[0].set_xlabel('支持度')
axes[0].set_ylabel('置信度')
axes[0].set_title('关联规则质量评估')
plt.colorbar(scatter, ax=axes[0], label='提升度')

# 提升度最高的规则
top_rules = rules.nlargest(10, 'lift')
axes[1].barh(range(len(top_rules)), top_rules['lift'].values)
axes[1].set_yticks(range(len(top_rules)))
rule_names = [f"{', '.join(list(r['antecedents']))} -> {', '.join(list(r['consequents']))}"
              for _, r in top_rules.iterrows()]
axes[1].set_yticklabels([name[:30] + '...' if len(name) > 30 else name for name in rule_names])
axes[1].set_xlabel('提升度（Lift）')
axes[1].set_title('TOP10关联规则')

plt.tight_layout()
plt.show()

# 7. 实际应用建议
print("\n购物篮分析建议：")
print("="*50)

# 找出最常作为前提的商品
antecedent_counts = pd.Series()
for rule in strong_rules.iterrows():
    for item in rule[1]['antecedents']:
        antecedent_counts[item] = antecedent_counts.get(item, 0) + 1

print("\n最常见的触发商品（常被一起买）:")
for item, count in antecedent_counts.nlargest(5).items():
    print(f"  {item}: 出现在{count}条规则中")

# 推荐组合
print("\n推荐商品组合策略：")
if len(strong_rules) > 0:
    top_rule = strong_rules.iloc[0]
    antecedents = ', '.join(list(top_rule['antecedents']))
    consequents = ', '.join(list(top_rule['consequents']))
    print(f"  购买{antecedents}的顾客，推荐{consequents}")