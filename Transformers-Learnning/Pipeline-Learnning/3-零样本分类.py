from transformers import pipeline
classifier = pipeline("zero-shot-classification")

sequence = "这家餐厅的服务太差了"
candidate_labels = ["food", "service", "price", "atmosphere"]
result = classifier(sequence, candidate_labels)

print(result['labels'][0])  # 输出: 'service'

# 1. 客服工单自动分类
ticket = "我的订单被多扣了50块钱"
categories = ["billing", "technical", "return", "shipping"]
# 结果：'billing'
print(classifier(ticket, categories)['labels'][0])

# 2. 新闻主题分类
headline = "OpenAI发布GPT-5，性能超越人类"
categories = ["technology", "politics", "sports", "entertainment"]
# 结果：'technology'
print(classifier(headline, categories)['labels'][0])

# 3. 邮件智能路由
email = "关于项目进度的周报，请查收"
categories = ["urgent", "weekly report", "meeting request", "junk"]
# 结果：'weekly report'
print(email(headline, categories)['labels'][0])