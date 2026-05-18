"""种子数据导入脚本"""
import sys, sqlite3, json, os

DB_PATH = os.path.join(os.path.dirname(__file__), "exam.db")


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _uuid():
    import uuid
    return str(uuid.uuid4())


def _init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS exam_types (id TEXT PRIMARY KEY,name TEXT NOT NULL,slug TEXT UNIQUE NOT NULL,icon TEXT DEFAULT '📚',sort_order INTEGER DEFAULT 0,created_at TEXT DEFAULT (datetime('now')));
        CREATE TABLE IF NOT EXISTS subjects (id TEXT PRIMARY KEY,exam_type_id TEXT NOT NULL REFERENCES exam_types(id),name TEXT NOT NULL,slug TEXT NOT NULL,sort_order INTEGER DEFAULT 0,created_at TEXT DEFAULT (datetime('now')),UNIQUE(exam_type_id, slug));
        CREATE TABLE IF NOT EXISTS chapters (id TEXT PRIMARY KEY,subject_id TEXT NOT NULL REFERENCES subjects(id),name TEXT NOT NULL,slug TEXT NOT NULL,parent_id TEXT REFERENCES chapters(id),sort_order INTEGER DEFAULT 0,created_at TEXT DEFAULT (datetime('now')),UNIQUE(subject_id, slug));
        CREATE TABLE IF NOT EXISTS questions (id TEXT PRIMARY KEY,chapter_id TEXT REFERENCES chapters(id),type TEXT NOT NULL,difficulty TEXT NOT NULL,question_text TEXT NOT NULL,options TEXT DEFAULT '[]',correct_answer TEXT NOT NULL,explanation TEXT,source TEXT DEFAULT 'preset',created_at TEXT DEFAULT (datetime('now')));
        CREATE TABLE IF NOT EXISTS user_progress (id TEXT PRIMARY KEY,user_id TEXT NOT NULL,subject_id TEXT NOT NULL REFERENCES subjects(id),chapter_id TEXT REFERENCES chapters(id),total_answered INTEGER DEFAULT 0,total_correct INTEGER DEFAULT 0,last_practiced_at TEXT DEFAULT (datetime('now')),created_at TEXT DEFAULT (datetime('now')),UNIQUE(user_id, subject_id, chapter_id));
        CREATE TABLE IF NOT EXISTS wrong_answers (id TEXT PRIMARY KEY,user_id TEXT NOT NULL,question_id TEXT NOT NULL REFERENCES questions(id),user_answer TEXT NOT NULL,is_reviewed INTEGER DEFAULT 0,wrong_count INTEGER DEFAULT 1,created_at TEXT DEFAULT (datetime('now')),reviewed_at TEXT,UNIQUE(user_id, question_id));
        CREATE TABLE IF NOT EXISTS qa_sessions (id TEXT PRIMARY KEY,user_id TEXT NOT NULL,question TEXT NOT NULL,answer TEXT NOT NULL,subject_id TEXT REFERENCES subjects(id),created_at TEXT DEFAULT (datetime('now')));
    """)
    conn.commit()
    conn.close()


_init_db()
conn = _get_conn()

# 检查是否已有数据
if conn.execute("SELECT COUNT(*) FROM exam_types").fetchone()[0] > 0:
    print("种子数据已存在，跳过")
    conn.close()
    sys.exit(0)

# 考试类型
conn.execute("INSERT INTO exam_types (id,name,slug,icon,sort_order) VALUES ('e1','考研','kaoyan','🎓',1)")
conn.execute("INSERT INTO exam_types (id,name,slug,icon,sort_order) VALUES ('e2','公考','gongkao','🏛️',2)")
conn.execute("INSERT INTO exam_types (id,name,slug,icon,sort_order) VALUES ('e3','教资','jiaozi','📖',3)")

# 考研 - 政治 科目 + 章节
conn.execute("INSERT INTO subjects (id,exam_type_id,name,slug,sort_order) VALUES ('s1','e1','政治','politics',1)")
conn.execute("INSERT INTO subjects (id,exam_type_id,name,slug,sort_order) VALUES ('s2','e1','英语','english',2)")

chapters = [
    ('c1','s1','马克思主义哲学','marx-philosophy',1),
    ('c2','s1','政治经济学','political-economy',2),
    ('c3','s1','科学社会主义','scientific-socialism',3),
    ('c4','s1','毛泽东思想','mao-thought',4),
    ('c5','s1','中国特色社会主义','socialism-chinese',5),
]
conn.executemany("INSERT INTO chapters (id,subject_id,name,slug,sort_order) VALUES (?,?,?,?,?)", chapters)

# 题目
questions = [
    ('c1','single_choice','easy','马克思主义哲学认为，世界的统一性在于它的',
     json.dumps([{"label":"A","text":"多样性"},{"label":"B","text":"物质性"},{"label":"C","text":"运动性"},{"label":"D","text":"矛盾性"}]),'B',
     '辩证唯物主义认为世界是物质的，世界的真正统一性在于它的物质性。'),
    ('c1','single_choice','medium','矛盾的普遍性和特殊性的关系是',
     json.dumps([{"label":"A","text":"整体和部分的关系"},{"label":"B","text":"共性和个性的关系"},{"label":"C","text":"内容和形式的关系"},{"label":"D","text":"原因和结果的关系"}]),'B',
     '矛盾的普遍性即共性，特殊性即个性。普遍性寓于特殊性之中。'),
    ('c1','true_false','easy','实践是检验真理的唯一标准',
     '[]','True','实践是检验真理的唯一标准，这是马克思主义认识论的基本观点。'),
    ('c1','single_choice','medium','辩证否定观的实质是',
     json.dumps([{"label":"A","text":"全盘否定"},{"label":"B","text":"全盘肯定"},{"label":"C","text":"扬弃"},{"label":"D","text":"抛弃"}]),'C',
     '辩证否定观的实质是"扬弃"，即既克服又保留，既批判又继承。'),
    ('c1','fill_blank','easy','马克思主义哲学的两大基本派别是唯物主义和____',
     '[]','唯心主义','哲学分为唯物主义和唯心主义两大基本派别。'),

    ('c2','single_choice','medium','商品的二因素是指',
     json.dumps([{"label":"A","text":"使用价值和交换价值"},{"label":"B","text":"使用价值和价值"},{"label":"C","text":"价值和交换价值"},{"label":"D","text":"价值和价格"}]),'B',
     '商品是使用价值和价值的统一体。'),
    ('c2','single_choice','hard','在资本主义生产中，工人创造的新价值包括',
     json.dumps([{"label":"A","text":"不变资本和可变资本"},{"label":"B","text":"可变资本和剩余价值"},{"label":"C","text":"不变资本和剩余价值"},{"label":"D","text":"固定资本和流动资本"}]),'B',
     '工人劳动创造的新价值 = 可变资本 + 剩余价值。'),
    ('c2','true_false','easy','具体劳动创造商品的价值，抽象劳动创造商品的使用价值',
     '[]','False','正确的是：具体劳动创造使用价值，抽象劳动创造价值。'),
    ('c2','single_choice','easy','货币的本质是',
     json.dumps([{"label":"A","text":"一般等价物"},{"label":"B","text":"商品交换的媒介"},{"label":"C","text":"价值的符号"},{"label":"D","text":"财富的代表"}]),'A',
     '货币的本质是固定充当一般等价物的商品。'),
    ('c2','fill_blank','medium','资本主义生产过程是劳动过程和____过程的统一',
     '[]','价值增殖','资本主义生产具有二重性：劳动过程和价值增殖过程。'),

    ('c5','single_choice','easy','中国特色社会主义最本质的特征是',
     json.dumps([{"label":"A","text":"人民当家作主"},{"label":"B","text":"中国共产党领导"},{"label":"C","text":"全面依法治国"},{"label":"D","text":"社会主义市场经济"}]),'B',
     '中国特色社会主义最本质的特征是中国共产党领导。'),
    ('c5','single_choice','medium','我国社会主要矛盾已经转化为',
     json.dumps([{"label":"A","text":"人民日益增长的物质文化需要同落后的社会生产之间的矛盾"},{"label":"B","text":"人民日益增长的美好生活需要和不平衡不充分的发展之间的矛盾"},{"label":"C","text":"经济高速增长和高质量发展之间的矛盾"},{"label":"D","text":"城市和农村发展不平衡之间的矛盾"}]),'B',
     '我国社会主要矛盾已转化为人民日益增长的美好生活需要和不平衡不充分的发展之间的矛盾。'),
    ('c5','multi_choice','medium','全面深化改革的总目标是',
     json.dumps([{"label":"A","text":"完善和发展中国特色社会主义制度"},{"label":"B","text":"推进国家治理体系和治理能力现代化"},{"label":"C","text":"实现经济高速增长"},{"label":"D","text":"全面建成小康社会"}]),'A,B',
     '总目标是完善和发展中国特色社会主义制度，推进国家治理体系和治理能力现代化。'),
    ('c5','true_false','easy','共同富裕是社会主义的本质要求',
     '[]','True','共同富裕是社会主义的本质要求，是中国式现代化的重要特征。'),
    ('c5','fill_blank','easy','新发展理念包括创新、协调、绿色、开放、____',
     '[]','共享','五大新发展理念：创新、协调、绿色、开放、共享。'),
]

for ch, t, d, text, opt, ans, expl in questions:
    conn.execute(
        "INSERT INTO questions (id,chapter_id,type,difficulty,question_text,options,correct_answer,explanation,source) VALUES (?,?,?,?,?,?,?,?,'preset')",
        (_uuid(), ch, t, d, text, opt, ans, expl)
    )

conn.commit()
conn.close()
print("种子数据导入完成！")
print("  - 3 个考试类型（考研/公考/教资）")
print("  - 2 个科目（政治/英语）")
print("  - 5 个章节")
print("  - 15 道考研政治题目")
