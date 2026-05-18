"""考试模块本地数据库 (SQLite) — MVP 阶段免 Supabase 配置
后期可无缝切换为 Supabase/PostgreSQL"""
import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), "exam.db")


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """首次使用自动建表"""
    conn = _get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS exam_types (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            icon TEXT DEFAULT '📚',
            sort_order INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS subjects (
            id TEXT PRIMARY KEY,
            exam_type_id TEXT NOT NULL REFERENCES exam_types(id),
            name TEXT NOT NULL,
            slug TEXT NOT NULL,
            sort_order INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            UNIQUE(exam_type_id, slug)
        );
        CREATE TABLE IF NOT EXISTS chapters (
            id TEXT PRIMARY KEY,
            subject_id TEXT NOT NULL REFERENCES subjects(id),
            name TEXT NOT NULL,
            slug TEXT NOT NULL,
            parent_id TEXT REFERENCES chapters(id),
            sort_order INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            UNIQUE(subject_id, slug)
        );
        CREATE TABLE IF NOT EXISTS questions (
            id TEXT PRIMARY KEY,
            chapter_id TEXT REFERENCES chapters(id),
            type TEXT NOT NULL CHECK (type IN ('single_choice','multi_choice','true_false','fill_blank')),
            difficulty TEXT NOT NULL CHECK (difficulty IN ('easy','medium','hard')),
            question_text TEXT NOT NULL,
            options TEXT DEFAULT '[]',
            correct_answer TEXT NOT NULL,
            explanation TEXT,
            source TEXT DEFAULT 'preset',
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS user_progress (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            subject_id TEXT NOT NULL REFERENCES subjects(id),
            chapter_id TEXT REFERENCES chapters(id),
            total_answered INTEGER DEFAULT 0,
            total_correct INTEGER DEFAULT 0,
            last_practiced_at TEXT DEFAULT (datetime('now')),
            created_at TEXT DEFAULT (datetime('now')),
            UNIQUE(user_id, subject_id, chapter_id)
        );
        CREATE TABLE IF NOT EXISTS wrong_answers (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            question_id TEXT NOT NULL REFERENCES questions(id),
            user_answer TEXT NOT NULL,
            is_reviewed INTEGER DEFAULT 0,
            wrong_count INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now')),
            reviewed_at TEXT,
            UNIQUE(user_id, question_id)
        );
        CREATE TABLE IF NOT EXISTS qa_sessions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            subject_id TEXT REFERENCES subjects(id),
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_q_chapter ON questions(chapter_id, difficulty, type);
        CREATE INDEX IF NOT EXISTS idx_wa_user ON wrong_answers(user_id, is_reviewed);
        CREATE INDEX IF NOT EXISTS idx_qa_user ON qa_sessions(user_id, created_at DESC);
    """)
    conn.commit()
    conn.close()


def _uuid():
    import uuid
    return str(uuid.uuid4())


# ── 考试类型 / 科目 / 章节 ──

def get_exam_types():
    conn = _get_conn()
    rows = conn.execute("SELECT * FROM exam_types ORDER BY sort_order").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_subjects(exam_type_id: str):
    conn = _get_conn()
    rows = conn.execute("SELECT * FROM subjects WHERE exam_type_id=? ORDER BY sort_order", (exam_type_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_chapters(subject_id: str):
    conn = _get_conn()
    rows = conn.execute("SELECT * FROM chapters WHERE subject_id=? AND parent_id IS NULL ORDER BY sort_order", (subject_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── 题目 ──

def get_questions(subject_id: str = None, chapter_id: str = None,
                  difficulty: str = None, qtype: str = None,
                  page: int = 1, size: int = 20):
    conn = _get_conn()
    where = []
    params = []

    if chapter_id:
        where.append("chapter_id=?")
        params.append(chapter_id)
    elif subject_id:
        where.append("chapter_id IN (SELECT id FROM chapters WHERE subject_id=?)")
        params.append(subject_id)

    if difficulty:
        where.append("difficulty=?")
        params.append(difficulty)
    if qtype:
        where.append("type=?")
        params.append(qtype)

    w = " AND ".join(where) if where else "1=1"
    count = conn.execute(f"SELECT COUNT(*) FROM questions WHERE {w}", params).fetchone()[0]
    offset = (page - 1) * size
    rows = conn.execute(
        f"SELECT * FROM questions WHERE {w} ORDER BY created_at DESC LIMIT ? OFFSET ?",
        params + [size, offset]
    ).fetchall()
    conn.close()
    data = [dict(r) for r in rows]
    for d in data:
        if isinstance(d.get("options"), str):
            d["options"] = json.loads(d["options"])
    return {"data": data, "count": count}


def get_question_by_id(question_id: str):
    conn = _get_conn()
    row = conn.execute("SELECT * FROM questions WHERE id=?", (question_id,)).fetchone()
    conn.close()
    if not row:
        raise ValueError("题目不存在")
    d = dict(row)
    if isinstance(d.get("options"), str):
        d["options"] = json.loads(d["options"])
    return d


def save_generated_questions(questions: list[dict]):
    conn = _get_conn()
    ids = []
    for q in questions:
        qid = _uuid()
        opt = json.dumps(q.get("options", []), ensure_ascii=False)
        conn.execute(
            "INSERT INTO questions (id, chapter_id, type, difficulty, question_text, options, correct_answer, explanation, source) VALUES (?,?,?,?,?,?,?,?,?)",
            (qid, q.get("chapter_id"), q.get("type"), q.get("difficulty", "medium"),
             q["question_text"], opt, q["correct_answer"], q.get("explanation", ""), "ai_generated")
        )
        ids.append(qid)
    conn.commit()
    conn.close()
    return ids


def get_preset_questions(chapter_id: str, limit: int = 5):
    conn = _get_conn()
    rows = conn.execute(
        "SELECT type, difficulty, question_text, options, correct_answer, explanation FROM questions WHERE chapter_id=? AND source='preset' LIMIT ?",
        (chapter_id, limit)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── 用户进度 ──

def upsert_progress(user_id: str, subject_id: str, chapter_id: str = None, is_correct: bool = False):
    conn = _get_conn()
    row = conn.execute(
        "SELECT id, total_answered, total_correct FROM user_progress WHERE user_id=? AND subject_id=? AND chapter_id IS ?",
        (user_id, subject_id, chapter_id)
    ).fetchone()
    if row:
        t = row["total_answered"] + 1
        c = row["total_correct"] + (1 if is_correct else 0)
        conn.execute("UPDATE user_progress SET total_answered=?, total_correct=?, last_practiced_at=datetime('now') WHERE id=?", (t, c, row["id"]))
    else:
        conn.execute(
            "INSERT INTO user_progress (id, user_id, subject_id, chapter_id, total_answered, total_correct) VALUES (?,?,?,?,?,?)",
            (_uuid(), user_id, subject_id, chapter_id, 1, 1 if is_correct else 0)
        )
    conn.commit()
    conn.close()


def get_progress(user_id: str, subject_id: str = None):
    conn = _get_conn()
    if subject_id:
        rows = conn.execute("SELECT * FROM user_progress WHERE user_id=? AND subject_id=? ORDER BY last_practiced_at DESC", (user_id, subject_id)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM user_progress WHERE user_id=? ORDER BY last_practiced_at DESC", (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── 错题本 ──

def upsert_wrong_answer(user_id: str, question_id: str, user_answer: str):
    conn = _get_conn()
    row = conn.execute("SELECT id, wrong_count FROM wrong_answers WHERE user_id=? AND question_id=?", (user_id, question_id)).fetchone()
    if row:
        conn.execute("UPDATE wrong_answers SET user_answer=?, is_reviewed=0, wrong_count=wrong_count+1 WHERE id=?", (user_answer, row["id"]))
    else:
        conn.execute("INSERT INTO wrong_answers (id, user_id, question_id, user_answer) VALUES (?,?,?,?)", (_uuid(), user_id, question_id, user_answer))
    conn.commit()
    conn.close()


def get_wrong_answers(user_id: str, is_reviewed: bool = None,
                      page: int = 1, size: int = 20):
    conn = _get_conn()
    params = [user_id]
    w = "user_id=?"
    if is_reviewed is not None:
        w += " AND is_reviewed=?"
        params.append(1 if is_reviewed else 0)
    count = conn.execute(f"SELECT COUNT(*) FROM wrong_answers WHERE {w}", params).fetchone()[0]
    offset = (page - 1) * size
    rows = conn.execute(
        f"SELECT wa.*, q.* FROM wrong_answers wa JOIN questions q ON q.id=wa.question_id WHERE {w} ORDER BY wa.created_at DESC LIMIT ? OFFSET ?",
        params + [size, offset]
    ).fetchall()
    conn.close()
    data = []
    for r in rows:
        d = dict(r)
        d["question"] = {k: d.pop(k) for k in list(d.keys()) if k in ("id","chapter_id","type","difficulty","question_text","options","correct_answer","explanation","source","created_at")}
        if isinstance(d["question"].get("options"), str):
            d["question"]["options"] = json.loads(d["question"]["options"])
        data.append(d)
    return {"data": data, "count": count}


def mark_wrong_reviewed(wrong_id: str):
    conn = _get_conn()
    conn.execute("UPDATE wrong_answers SET is_reviewed=1, reviewed_at=datetime('now') WHERE id=?", (wrong_id,))
    conn.commit()
    conn.close()


def delete_wrong_answer(wrong_id: str):
    conn = _get_conn()
    conn.execute("DELETE FROM wrong_answers WHERE id=?", (wrong_id,))
    conn.commit()
    conn.close()


# ── AI 问答 ──

def save_qa_session(user_id: str, question: str, answer: str, subject_id: str = None):
    conn = _get_conn()
    conn.execute("INSERT INTO qa_sessions (id, user_id, question, answer, subject_id) VALUES (?,?,?,?,?)",
                 (_uuid(), user_id, question, answer, subject_id))
    conn.commit()
    conn.close()


def get_qa_history(user_id: str, page: int = 1, size: int = 20):
    conn = _get_conn()
    offset = (page - 1) * size
    rows = conn.execute("SELECT * FROM qa_sessions WHERE user_id=? ORDER BY created_at DESC LIMIT ? OFFSET ?",
                        (user_id, size, offset)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
