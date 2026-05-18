-- 考证刷题助手 — Supabase 数据库迁移
-- 在 Supabase SQL Editor 中执行此文件

-- 1. 考试类型
CREATE TABLE IF NOT EXISTS exam_types (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  icon TEXT DEFAULT '📚',
  sort_order INT2 DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- 2. 科目
CREATE TABLE IF NOT EXISTS subjects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  exam_type_id UUID NOT NULL REFERENCES exam_types(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  slug TEXT NOT NULL,
  sort_order INT2 DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(exam_type_id, slug)
);

-- 3. 章节（可嵌套）
CREATE TABLE IF NOT EXISTS chapters (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  subject_id UUID NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  slug TEXT NOT NULL,
  parent_id UUID REFERENCES chapters(id) ON DELETE SET NULL,
  sort_order INT2 DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(subject_id, slug)
);

-- 4. 题目
CREATE TABLE IF NOT EXISTS questions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  chapter_id UUID REFERENCES chapters(id) ON DELETE SET NULL,
  type TEXT NOT NULL CHECK (type IN ('single_choice', 'multi_choice', 'true_false', 'fill_blank')),
  difficulty TEXT NOT NULL CHECK (difficulty IN ('easy', 'medium', 'hard')),
  question_text TEXT NOT NULL,
  options JSONB DEFAULT '[]',
  correct_answer TEXT NOT NULL,
  explanation TEXT,
  source TEXT DEFAULT 'preset' CHECK (source IN ('preset', 'ai_generated')),
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_questions_chapter ON questions(chapter_id, difficulty, type);
CREATE INDEX IF NOT EXISTS idx_questions_source ON questions(source);

-- 5. 用户进度
CREATE TABLE IF NOT EXISTS user_progress (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT NOT NULL,
  subject_id UUID NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
  chapter_id UUID REFERENCES chapters(id) ON DELETE CASCADE,
  total_answered INT4 DEFAULT 0,
  total_correct INT4 DEFAULT 0,
  last_practiced_at TIMESTAMPTZ DEFAULT now(),
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(user_id, subject_id, chapter_id)
);

CREATE INDEX IF NOT EXISTS idx_user_progress_user ON user_progress(user_id, subject_id);

-- 6. 错题本
CREATE TABLE IF NOT EXISTS wrong_answers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT NOT NULL,
  question_id UUID NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
  user_answer TEXT NOT NULL,
  is_reviewed BOOL DEFAULT false,
  wrong_count INT2 DEFAULT 1,
  created_at TIMESTAMPTZ DEFAULT now(),
  reviewed_at TIMESTAMPTZ,
  UNIQUE(user_id, question_id)
);

CREATE INDEX IF NOT EXISTS idx_wrong_answers_user ON wrong_answers(user_id, is_reviewed);

-- 7. AI 问答历史
CREATE TABLE IF NOT EXISTS qa_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT NOT NULL,
  question TEXT NOT NULL,
  answer TEXT NOT NULL,
  subject_id UUID REFERENCES subjects(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_qa_sessions_user ON qa_sessions(user_id, created_at DESC);

-- RLS 策略
ALTER TABLE exam_types ENABLE ROW LEVEL SECURITY;
ALTER TABLE subjects ENABLE ROW LEVEL SECURITY;
ALTER TABLE chapters ENABLE ROW LEVEL SECURITY;
ALTER TABLE questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE wrong_answers ENABLE ROW LEVEL SECURITY;
ALTER TABLE qa_sessions ENABLE ROW LEVEL SECURITY;

-- 公开读取
CREATE POLICY "public_read_exam_types" ON exam_types FOR SELECT USING (true);
CREATE POLICY "public_read_subjects" ON subjects FOR SELECT USING (true);
CREATE POLICY "public_read_chapters" ON chapters FOR SELECT USING (true);
CREATE POLICY "public_read_questions" ON questions FOR SELECT USING (true);

-- 用户数据完全开放（MVP 阶段依赖客户端 UUID 隔离）
CREATE POLICY "all_user_progress" ON user_progress FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "all_wrong_answers" ON wrong_answers FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "all_qa_sessions" ON qa_sessions FOR ALL USING (true) WITH CHECK (true);
