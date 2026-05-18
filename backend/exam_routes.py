from fastapi import APIRouter, HTTPException, Query
from backend import exam_db
from backend import exam_qa
from backend import exam_generate

router = APIRouter(prefix="/api/exam")


# ── 考试类型 / 科目 / 章节 ──

@router.get("/types")
def list_exam_types():
    return _ok(exam_db.get_exam_types())


@router.get("/types/{exam_id}/subjects")
def list_subjects(exam_id: str):
    return _ok(exam_db.get_subjects(exam_id))


@router.get("/subjects/{subject_id}/chapters")
def list_chapters(subject_id: str):
    return _ok(exam_db.get_chapters(subject_id))


# ── 题目 ──

@router.get("/questions")
def list_questions(
    subject_id: str = Query(None),
    chapter_id: str = Query(None),
    difficulty: str = Query(None),
    type: str = Query(None, alias="type"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=50),
):
    result = exam_db.get_questions(
        subject_id=subject_id, chapter_id=chapter_id,
        difficulty=difficulty, qtype=type,
        page=page, size=size,
    )
    return _ok({"items": result["data"], "total": result["count"], "page": page, "size": size})


@router.get("/questions/{question_id}")
def get_question(question_id: str):
    try:
        q = exam_db.get_question_by_id(question_id)
        return _ok(q)
    except Exception:
        raise HTTPException(status_code=404, detail="题目不存在")


# ── 练习 ──

@router.post("/practice/start")
def practice_start(body: dict):
    subject_id = body["subject_id"]
    chapter_id = body.get("chapter_id")
    difficulty = body.get("difficulty")
    count = min(body.get("count", 10), 30)

    result = exam_db.get_questions(
        subject_id=subject_id, chapter_id=chapter_id,
        difficulty=difficulty, size=count,
    )
    questions = result["data"]

    # 隐藏正确答案
    safe = []
    for q in questions:
        safe.append({
            "id": q["id"], "type": q["type"], "difficulty": q["difficulty"],
            "question_text": q["question_text"], "options": q.get("options", []),
        })

    return _ok({"questions": safe, "total": len(safe)})


@router.post("/practice/submit")
def practice_submit(body: dict):
    user_id = body.get("user_id", "anonymous")
    question_id = body["question_id"]
    user_answer = body["user_answer"]
    subject_id = body.get("subject_id")
    chapter_id = body.get("chapter_id")

    try:
        q = exam_db.get_question_by_id(question_id)
    except Exception:
        raise HTTPException(status_code=404, detail="题目不存在")

    is_correct = str(user_answer).strip() == str(q["correct_answer"]).strip()

    # 更新进度
    if subject_id:
        try:
            exam_db.upsert_progress(user_id, subject_id, chapter_id, is_correct)
        except Exception:
            pass

    # 错题入错题本
    if not is_correct:
        try:
            exam_db.upsert_wrong_answer(user_id, question_id, user_answer)
        except Exception:
            pass

    return _ok({
        "is_correct": is_correct,
        "correct_answer": q["correct_answer"],
        "explanation": q.get("explanation", ""),
    })


# ── 进度 ──

@router.get("/progress")
def get_progress(
    user_id: str = Query(..., description="用户ID"),
    subject_id: str = Query(None),
):
    return _ok(exam_db.get_progress(user_id, subject_id))


# ── 错题本 ──

@router.get("/wrong-answers")
def list_wrong_answers(
    user_id: str = Query(..., description="用户ID"),
    is_reviewed: bool = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=50),
):
    result = exam_db.get_wrong_answers(user_id, is_reviewed, page, size)
    return _ok({"items": result["data"], "total": result["count"], "page": page, "size": size})


@router.post("/wrong-answers/{wrong_id}/retry")
def retry_wrong(wrong_id: str, body: dict):
    exam_db.mark_wrong_reviewed(wrong_id)
    return _ok(None, "已标记为已复习")


@router.delete("/wrong-answers/{wrong_id}")
def remove_wrong(wrong_id: str):
    exam_db.delete_wrong_answer(wrong_id)
    return _ok(None, "已删除")


# ── AI 问答 ──

@router.post("/qa/ask")
def qa_ask(body: dict):
    question = body["question"]
    subject_name = body.get("subject_name")
    user_id = body.get("user_id", "anonymous")
    subject_id = body.get("subject_id")

    answer = exam_qa.ask_question(question, subject_name)

    try:
        exam_db.save_qa_session(user_id, question, answer, subject_id)
    except Exception:
        pass

    return _ok({"question": question, "answer": answer})


@router.get("/qa/history")
def qa_history(
    user_id: str = Query(..., description="用户ID"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=50),
):
    return _ok(exam_db.get_qa_history(user_id, page, size))


# ── AI 出题 ──

@router.post("/practice/generate")
def generate_practice(body: dict):
    subject_id = body["subject_id"]
    chapter_id = body.get("chapter_id")
    count = min(body.get("count", 5), 10)

    # 获取科目和章节名称
    subject_name = body.get("subject_name", "")
    chapter_name = body.get("chapter_name", "")
    weak_topics = body.get("weak_topics", [])

    # 获取参考样题
    refs = []
    if chapter_id:
        refs = exam_db.get_preset_questions(chapter_id, limit=3)

    # 如果没有参考题，尝试从科目下获取
    if not refs and subject_id:
        result = exam_db.get_questions(subject_id=subject_id, size=3)
        refs = result["data"]

    questions = exam_generate.generate_questions(
        subject_name=subject_name,
        chapter_name=chapter_name,
        weak_topics=weak_topics,
        reference_questions=refs,
        count=count,
    )

    # 补充 chapter_id, subject_id, source
    for q in questions:
        q.setdefault("chapter_id", chapter_id)
        q.setdefault("source", "ai_generated")
        if "options" in q and not isinstance(q["options"], list):
            q["options"] = []
        if "options" in q and isinstance(q["options"], list):
            q["options"] = q["options"]  # 保持原样

    # 保存到数据库
    try:
        question_ids = exam_db.save_generated_questions(questions)
        return _ok({"questions": questions, "ids": question_ids})
    except Exception:
        return _ok({"questions": questions, "ids": [], "note": "题目未持久化"})


# ── 响应工具 ──

def _ok(data=None, message="ok"):
    return {"code": 0, "data": data, "message": message}
