"""Supabase 数据库迁移 + 种子数据导入"""
import os, json
from dotenv import load_dotenv
load_dotenv()

from supabase import create_client

supabase = create_client(
    os.getenv("SUPABASE_URL", ""),
    os.getenv("SUPABASE_KEY", ""),
)

SQL_STATEMENTS = [
    # 1. 考试类型
    """CREATE TABLE IF NOT EXISTS exam_types (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      name TEXT NOT NULL,
      slug TEXT UNIQUE NOT NULL,
      icon TEXT DEFAULT '📚',
      sort_order INT2 DEFAULT 0,
      created_at TIMESTAMPTZ DEFAULT now()
    )""",
    # 2. 科目
    """CREATE TABLE IF NOT EXISTS subjects (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      exam_type_id UUID NOT NULL REFERENCES exam_types(id) ON DELETE CASCADE,
      name TEXT NOT NULL,
      slug TEXT NOT NULL,
      sort_order INT2 DEFAULT 0,
      created_at TIMESTAMPTZ DEFAULT now(),
      UNIQUE(exam_type_id, slug)
    )""",
    # 3. 章节
    """CREATE TABLE IF NOT EXISTS chapters (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      subject_id UUID NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
      name TEXT NOT NULL,
      slug TEXT NOT NULL,
      parent_id UUID REFERENCES chapters(id) ON DELETE SET NULL,
      sort_order INT2 DEFAULT 0,
      created_at TIMESTAMPTZ DEFAULT now(),
      UNIQUE(subject_id, slug)
    )""",
    # 4. 题目
    """CREATE TABLE IF NOT EXISTS questions (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      chapter_id UUID REFERENCES chapters(id) ON DELETE SET NULL,
      type TEXT NOT NULL,
      difficulty TEXT NOT NULL,
      question_text TEXT NOT NULL,
      options JSONB DEFAULT '[]',
      correct_answer TEXT NOT NULL,
      explanation TEXT,
      source TEXT DEFAULT 'preset',
      created_at TIMESTAMPTZ DEFAULT now()
    )""",
    # 5. 用户进度
    """CREATE TABLE IF NOT EXISTS user_progress (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      user_id TEXT NOT NULL,
      subject_id UUID NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
      chapter_id UUID REFERENCES chapters(id) ON DELETE CASCADE,
      total_answered INT4 DEFAULT 0,
      total_correct INT4 DEFAULT 0,
      last_practiced_at TIMESTAMPTZ DEFAULT now(),
      created_at TIMESTAMPTZ DEFAULT now(),
      UNIQUE(user_id, subject_id, chapter_id)
    )""",
    # 6. 错题本
    """CREATE TABLE IF NOT EXISTS wrong_answers (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      user_id TEXT NOT NULL,
      question_id UUID NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
      user_answer TEXT NOT NULL,
      is_reviewed BOOL DEFAULT false,
      wrong_count INT2 DEFAULT 1,
      created_at TIMESTAMPTZ DEFAULT now(),
      reviewed_at TIMESTAMPTZ,
      UNIQUE(user_id, question_id)
    )""",
    # 7. AI 问答历史
    """CREATE TABLE IF NOT EXISTS qa_sessions (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      user_id TEXT NOT NULL,
      question TEXT NOT NULL,
      answer TEXT NOT NULL,
      subject_id UUID REFERENCES subjects(id) ON DELETE SET NULL,
      created_at TIMESTAMPTZ DEFAULT now()
    )""",
]


def exec_sql(query: str) -> bool:
    """通过 Supabase rpc 执行 SQL（需要项目开启 pg_graphql 或对应函数）"""
    try:
        # 尝试通过 raw REST API
        import httpx
        resp = httpx.post(
            f"{os.getenv('SUPABASE_URL')}/rest/v1/rpc/exec_sql",
            headers={
                "apikey": os.getenv("SUPABASE_KEY", ""),
                "Authorization": f"Bearer {os.getenv('SUPABASE_KEY', '')}",
                "Content-Type": "application/json",
            },
            json={"query": query},
        )
        return resp.status_code < 400
    except Exception:
        return False


def try_create_tables():
    """尝试多种方式建表，返回成功数量"""
    created = 0

    # 方法1: 逐条用 httpx 调用 SQL
    for sql in SQL_STATEMENTS:
        if exec_sql(sql):
            print(f"  ✓ {sql.split()[2]}")
            created += 1
        else:
            print(f"  ? {sql.split()[2]} (需要 Supabase SQL Editor)")

    return created


if __name__ == "__main__":
    print("Supabase Migration Tool")
    print(f"  URL: {os.getenv('SUPABASE_URL')}")
    print()

    # 先测试连接
    try:
        test = supabase.table("exam_types").select("count", count="exact").execute()
        print(f"  Connection OK (exam_types count: {test.count})")
        tables_exist = True
    except Exception as e:
        err = str(e)
        if "does not exist" in err or "404" in err or "42P01" in err:
            print("  Tables don't exist yet — creating...")
            tables_exist = False
        else:
            print(f"  Connection error: {err[:100]}")
            tables_exist = False

    if not tables_exist:
        print()
        print("Attempting to create tables via API...")
        created = try_create_tables()

        if created < 7:
            print()
            print("=" * 50)
            print("部分表需要手动创建。请在 Supabase Dashboard:")
            print("  SQL Editor → Paste backend/migration.sql → Run")
            print("=" * 50)
    else:
        print("  All tables exist!")

    # 尝试插入种子数据
    print()
    print("Checking seed data...")
    try:
        count = supabase.table("exam_types").select("count", count="exact").execute().count
        print(f"  exam_types: {count} rows")
        if count == 0:
            print("  No seed data. Please run backend/seed.sql in Supabase SQL Editor.")
        else:
            print("  Seed data exists!")
    except Exception:
        print("  Can't check seed data. Run backend/seed.sql in SQL Editor if needed.")
