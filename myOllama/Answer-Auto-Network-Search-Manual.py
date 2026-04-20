from openai import OpenAI
from ddgs import DDGS  # 注意：导入方式变了
import json

# 配置
client = OpenAI(
    base_url="http://192.168.13.23:8842/v1",
    api_key="ollama"
)
MODEL_NAME = "Qwen3.5-27B-Q8_0.gguf"


# ========== 搜索功能 ==========
def web_search(query, max_results=3):
    """执行网络搜索"""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        return results
    except Exception as e:
        print(f"⚠️ 搜索出错: {e}")
        return []


def format_search_results(results):
    """格式化搜索结果"""
    if not results:
        return ""

    formatted = "\n【网络搜索结果】\n"
    for i, r in enumerate(results, 1):
        formatted += f"\n[{i}] {r['title']}\n"
        formatted += f"来源: {r['href']}\n"
        formatted += f"摘要: {r['body'][:500]}\n"
    return formatted


# ========== 智能问答函数（自动联网） ==========
def ask(question, auto_search=True):
    """
    智能问答函数

    Args:
        question: 用户问题
        auto_search: 是否自动判断并执行联网搜索

    Returns:
        回答内容
    """

    # 第一步：判断是否需要搜索
    need_search = False
    search_results = None

    if auto_search:
        need_search = check_if_need_search(question)

        if need_search:
            print(f"🔍 检测到需要实时信息，正在搜索: {question}")
            search_results = web_search(question)

            if search_results:
                print(f"📄 找到 {len(search_results)} 条相关信息")
            else:
                print("⚠️ 未找到搜索结果，将直接回答")

    # 第二步：构建最终提示词
    if search_results:
        # 有搜索结果：基于搜索结果回答
        context = format_search_results(search_results)
        final_prompt = f"""{context}

【用户问题】
{question}

【回答要求】
1. 请基于上述搜索结果回答问题
2. 如果搜索结果不足以完整回答，可以结合你的知识补充
3. 引用搜索结果时请标注来源编号，如[1]
4. 回答要准确、清晰、有条理

请回答："""
    else:
        # 无搜索结果：直接回答
        final_prompt = question

    # 第三步：调用模型
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": final_prompt}],
        stream=False,
        temperature=0.7
    )

    answer = response.choices[0].message.content

    # 如果有搜索结果，附上来源
    if search_results:
        answer += "\n\n---\n📚 信息来源：\n"
        for i, r in enumerate(search_results[:3], 1):
            answer += f"{i}. {r['title']}\n   {r['href']}\n"

    return answer


def check_if_need_search(question):
    """判断问题是否需要联网搜索"""

    # 需要实时/最新信息的关键词
    realtime_keywords = [
        "今天", "昨日", "昨天", "最新", "实时", "现在", "当前",
        "新闻", "热点", "天气", "股价", "股票", "汇率", "油价",
        "2026", "2025", "本月", "本周", "最近", "刚刚",
        "热搜", "头条", "报道", "发布", "宣布", "上线"
    ]

    # 不需要搜索的知识性问题
    knowledge_keywords = [
        "什么是", "解释", "定义", "原理", "历史", "介绍",
        "如何", "怎样", "为什么", "出师表", "唐诗", "宋词"
    ]

    question_lower = question.lower()

    # 优先判断实时性需求
    for keyword in realtime_keywords:
        if keyword in question_lower:
            return True

    # 知识性问题可以不搜索（模型已有知识）
    for keyword in knowledge_keywords:
        if keyword in question_lower:
            # 但如果同时包含时间词，还是需要搜索
            if not any(tk in question_lower for tk in ["今天", "最新", "最近"]):
                return False

    # 默认：超过30字的问题倾向于搜索
    if len(question) > 30:
        return True

    return False


# ========== 带搜索控制的问答 ==========
def ask_force_search(question):
    """强制使用联网搜索"""
    return ask(question, auto_search=True)


def ask_no_search(question):
    """强制不使用联网搜索"""
    return ask(question, auto_search=False)


# ========== 使用示例 ==========
if __name__ == "__main__":
    print("=" * 60)
    print("🤖 智能问答系统（自动联网）")
    print("=" * 60)

    # # 示例1：需要实时信息（会自动搜索）
    # print("\n【示例1】需要实时信息")
    # print("-" * 40)
    # question1 = "今天有什么重要的科技新闻？"
    # print(f"👤 问: {question1}")
    # answer1 = ask(question1)
    # print(f"🤖 答:\n{answer1}")
    #
    # print("\n" + "=" * 60)
    #
    # # 示例2：知识性问题（不会搜索）
    # print("\n【示例2】知识性问题")
    # print("-" * 40)
    # question2 = "出师表默写一下"
    # print(f"👤 问: {question2}")
    # answer2 = ask(question2)
    # print(f"🤖 答:\n{answer2}")
    #
    # print("\n" + "=" * 60)

    # 示例3：交互模式
    print("\n【交互模式】输入问题，系统自动判断是否需要搜索")
    print("提示：输入 'exit' 退出\n")

    while True:
        user_input = input("👤 你: ").strip()
        if user_input.lower() in ['exit', 'quit']:
            print("👋 再见！")
            break
        if not user_input:
            continue

        print("🤖 思考中...")
        answer = ask(user_input)
        print(f"🤖 答:\n{answer}\n")