import json
from openai import OpenAI
import os

_client = None

GENERATE_SYSTEM_PROMPT = """你是一个专业的中国考试命题专家。根据以下信息生成练习题。

【要求】
1. 题目必须与章节知识点紧密相关
2. 干扰项要有迷惑性但确定唯一正解
3. 填空题目答案不超过10个字
4. 解析要详细，包含知识点回顾

返回严格JSON（不要带markdown标记）："""


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com",
        )
    return _client


def generate_questions(subject_name: str, chapter_name: str,
                       difficulty: str = None, weak_topics: list = None,
                       reference_questions: list = None,
                       count: int = 5) -> list[dict]:
    client = _get_client()

    if difficulty is None:
        difficulty = "简单:中等:困难 = 3:4:3"

    refs_str = json.dumps(reference_questions or [], ensure_ascii=False, indent=2)
    weak_str = ", ".join(weak_topics) if weak_topics else "无明显弱项"

    user_msg = f"""科目：{subject_name}
章节：{chapter_name}
难度分配：{difficulty}
生成数量：{count}道
弱项知识点：{weak_str}

【参考样题】（模仿其风格和难度）
{refs_str}

请根据以上信息生成{count}道题目，返回JSON数组。"""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": GENERATE_SYSTEM_PROMPT + """
{
  "questions": [
    {
      "type": "single_choice | multi_choice | true_false | fill_blank",
      "difficulty": "easy | medium | hard",
      "question_text": "题目内容",
      "options": [{"label": "A", "text": "..."}],
      "correct_answer": "A | True | 答案文本",
      "explanation": "解析"
    }
  ]
}"""
            },
            {"role": "user", "content": user_msg},
        ],
        response_format={"type": "json_object"},
        temperature=0.5,
        max_tokens=3000,
    )

    content = response.choices[0].message.content
    try:
        result = json.loads(content)
        return result.get("questions", [])
    except json.JSONDecodeError:
        raise ValueError("AI 出题格式异常")
