import os
from openai import OpenAI

_client = None

QA_SYSTEM_PROMPT = """你是一个中国考证辅导专家。用户会问你关于考试科目的问题。
请用清晰、结构化的方式回答：
- 概念题：给出定义 + 例子 + 记忆技巧
- 题目讲解：解题思路 → 分步解答 → 易错点提醒
回答控制在300字以内，使用Markdown格式（支持加粗、列表）。"""


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com",
        )
    return _client


def ask_question(user_question: str, subject_name: str = None) -> str:
    client = _get_client()
    user_msg = user_question
    if subject_name:
        user_msg = f"当前科目：{subject_name}\n用户问题：{user_question}"

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": QA_SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.5,
        max_tokens=800,
    )
    return response.choices[0].message.content
