"""补充更多种子数据：考研英语、公考行测、教资"""
import sqlite3, os, sys

DB_PATH = os.path.join(os.path.dirname(__file__), "exam.db")


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _uuid():
    import uuid
    return str(uuid.uuid4())


def insert_kaoyan_english(conn):
    """考研英语：阅读理解 + 完形填空 + 翻译"""
    print("  inserting 考研英语...")
    eng_id = "s2"  # 已存在
    chapters = [
        ('c6', eng_id, '阅读理解', 'reading', 1),
        ('c7', eng_id, '完形填空', 'cloze', 2),
        ('c8', eng_id, '翻译', 'translation', 3),
    ]
    for c in chapters:
        try:
            conn.execute("INSERT INTO chapters (id,subject_id,name,slug,sort_order) VALUES (?,?,?,?,?)", c)
        except sqlite3.IntegrityError:
            pass

    questions = [
        ('c6', 'single_choice', 'medium',
         'The word "ubiquitous" in the passage most probably means',
         '[{"label":"A","text":"rare"},{"label":"B","text":"everywhere"},{"label":"C","text":"unique"},{"label":"D","text":"visible"}]',
         'B', 'Ubiquitous 意为"无处不在的"，近义词为 everywhere。'),
        ('c6', 'single_choice', 'hard',
         'According to the author, the main cause of climate change is',
         '[{"label":"A","text":"natural cycles"},{"label":"B","text":"human activities"},{"label":"C","text":"solar radiation"},{"label":"D","text":"volcanic eruptions"}]',
         'B', '根据主流科学共识，人类活动是气候变化的主因。'),
        ('c6', 'fill_blank', 'medium',
         'The synonym of "significant" is ____',
         '[]', 'important', 'Significant = important，意为"重要的"。'),
        ('c7', 'single_choice', 'easy',
         'The best title for this passage would be',
         '[{"label":"A","text":"The Future of AI"},{"label":"B","text":"How Technology Changes Our Life"},{"label":"C","text":"The Rise of Remote Work"},{"label":"D","text":"Modern Education Reform"}]',
         'C', '文章主要内容围绕远程办公的兴起。'),
        ('c7', 'multi_choice', 'hard',
         'Which of the following are mentioned as benefits of exercise?',
         '[{"label":"A","text":"Better sleep"},{"label":"B","text":"Improved memory"},{"label":"C","text":"Weight loss"},{"label":"D","text":"Lung capacity"}]',
         'A,B', '文中提到运动改善睡眠和记忆力，未提及减重和肺活量。'),
    ]
    for ch, t, d, text, opt, ans, expl in questions:
        conn.execute(
            "INSERT OR IGNORE INTO questions (id,chapter_id,type,difficulty,question_text,options,correct_answer,explanation,source) VALUES (?,?,?,?,?,?,?,?,'preset')",
            (_uuid(), ch, t, d, text, opt, ans, expl))


def insert_gongkao_xingce(conn):
    """公考行测：言语理解 + 数量关系 + 判断推理"""
    print("  inserting 公考行测...")
    exam_id = "e2"
    try:
        conn.execute("INSERT INTO exam_types (id,name,slug,icon,sort_order) VALUES (?,?,?,?,?)",
                     (exam_id, '公考', 'gongkao', '🏛️', 2))
    except sqlite3.IntegrityError:
        pass

    subj_id = _uuid()
    try:
        conn.execute("INSERT INTO subjects (id,exam_type_id,name,slug,sort_order) VALUES (?,?,?,?,?)",
                     (subj_id, exam_id, '行测', 'xingce', 1))
    except sqlite3.IntegrityError:
        subj_id = [r['id'] for r in conn.execute("SELECT id FROM subjects WHERE exam_type_id=? AND slug=?", (exam_id, 'xingce')).fetchall()]
        subj_id = subj_id[0] if subj_id else _uuid()

    chapters = [
        ('c9', subj_id, '言语理解', 'yanyu', 1),
        ('c10', subj_id, '数量关系', 'shuliang', 2),
        ('c11', subj_id, '判断推理', 'panduan', 3),
    ]
    for c in chapters:
        try:
            conn.execute("INSERT INTO chapters (id,subject_id,name,slug,sort_order) VALUES (?,?,?,?,?)", c)
        except sqlite3.IntegrityError:
            pass

    questions = [
        ('c9', 'single_choice', 'easy',
         '下列词语中，没有错别字的一项是',
         '[{"label":"A","text":"委屈求全"},{"label":"B","text":"委曲求全"},{"label":"C","text":"委屈全求"},{"label":"D","text":"委求曲全"}]',
         'B', '正确写法是"委曲求全"，意为勉强迁就以求保全。'),
        ('c9', 'single_choice', 'medium',
         '"塞翁失马，焉知非福"蕴含的哲学道理是',
         '[{"label":"A","text":"矛盾双方相互转化"},{"label":"B","text":"量变引起质变"},{"label":"C","text":"否定之否定规律"},{"label":"D","text":"现象与本质的辩证关系"}]',
         'A', '塞翁失马体现了祸福相依，即矛盾双方在一定条件下相互转化。'),
        ('c10', 'single_choice', 'hard',
         '甲乙两人从相距 100 公里的两地同时出发相向而行，甲速 6km/h，乙速 4km/h，甲带了一条狗，狗以 10km/h 的速度在两人之间来回奔跑，问两人相遇时狗跑了多少公里？',
         '[{"label":"A","text":"50"},{"label":"B","text":"100"},{"label":"C","text":"80"},{"label":"D","text":"120"}]',
         'B', '相遇时间 = 100/(6+4) = 10 小时，狗跑的距离 = 10×10 = 100 公里。'),
        ('c10', 'single_choice', 'easy',
         '一个长方形的长是宽的 2 倍，周长是 36 米，求面积',
         '[{"label":"A","text":"36"},{"label":"B","text":"54"},{"label":"C","text":"72"},{"label":"D","text":"108"}]',
         'C', '设宽为x，则2(2x+x)=36，x=6，长=12，面积=12×6=72。'),
        ('c11', 'single_choice', 'medium',
         '所有金属都能导电。铜是金属。所以铜能导电。以上推理属于',
         '[{"label":"A","text":"归纳推理"},{"label":"B","text":"演绎推理"},{"label":"C","text":"类比推理"},{"label":"D","text":"因果推理"}]',
         'B', '从一般到特殊的推理是演绎推理，这里用的是三段论。'),
    ]
    for ch, t, d, text, opt, ans, expl in questions:
        conn.execute(
            "INSERT OR IGNORE INTO questions (id,chapter_id,type,difficulty,question_text,options,correct_answer,explanation,source) VALUES (?,?,?,?,?,?,?,?,'preset')",
            (_uuid(), ch, t, d, text, opt, ans, expl))


def insert_jiaozi(conn):
    """教资综合素质：教育法律法规 + 教师职业道德"""
    print("  inserting 教资综合素质...")
    exam_id = "e3"
    try:
        conn.execute("INSERT INTO exam_types (id,name,slug,icon,sort_order) VALUES (?,?,?,?,?)",
                     (exam_id, '教资', 'jiaozi', '📖', 3))
    except sqlite3.IntegrityError:
        pass

    subj_id = _uuid()
    try:
        conn.execute("INSERT INTO subjects (id,exam_type_id,name,slug,sort_order) VALUES (?,?,?,?,?)",
                     (subj_id, exam_id, '综合素质', 'zonghe', 1))
    except sqlite3.IntegrityError:
        subj_id = [r['id'] for r in conn.execute("SELECT id FROM subjects WHERE exam_type_id=? AND slug=?", (exam_id, 'zonghe')).fetchall()]
        subj_id = subj_id[0] if subj_id else _uuid()

    chapters = [
        ('c12', subj_id, '教育法律法规', 'education-law', 1),
        ('c13', subj_id, '教师职业道德', 'teacher-ethics', 2),
    ]
    for c in chapters:
        try:
            conn.execute("INSERT INTO chapters (id,subject_id,name,slug,sort_order) VALUES (?,?,?,?,?)", c)
        except sqlite3.IntegrityError:
            pass

    questions = [
        ('c12', 'single_choice', 'easy',
         '《中华人民共和国教育法》规定，我国的教育方针是',
         '[{"label":"A","text":"教育必须为社会主义现代化建设服务"},{"label":"B","text":"教育必须与生产劳动相结合"},{"label":"C","text":"培养德智体美劳全面发展的社会主义建设者和接班人"},{"label":"D","text":"以上都是"}]',
         'D', '教育法规定教育为社会主义现代化建设服务、与生产劳动相结合，培养德智体美劳全面发展的建设者和接班人。'),
        ('c12', 'single_choice', 'medium',
         '根据《未成年人保护法》，学校应当保障未成年学生的',
         '[{"label":"A","text":"受教育权"},{"label":"B","text":"选举权和被选举权"},{"label":"C","text":"婚姻自由权"},{"label":"D","text":"财产继承权"}]',
         'A', '学校主要保障未成年学生的受教育权，其他权利由相应法律保障。'),
        ('c12', 'true_false', 'easy',
         '教师有权对学生的违纪行为进行罚款',
         '[]',
         'False', '教师没有罚款权。对学生的违纪行为应进行批评教育，不得罚款。'),
        ('c13', 'single_choice', 'easy',
         '"学高为师，身正为范"体现了教师的',
         '[{"label":"A","text":"专业素养"},{"label":"B","text":"道德素养"},{"label":"C","text":"教学能力"},{"label":"D","text":"科研能力"}]',
         'B', '"身正为范"强调教师要以身作则，体现了教师的道德素养。'),
        ('c13', 'single_choice', 'medium',
         '教师职业道德的核心是',
         '[{"label":"A","text":"爱国守法"},{"label":"B","text":"爱岗敬业"},{"label":"C","text":"关爱学生"},{"label":"D","text":"教书育人"}]',
         'C', '关爱学生是教师职业道德的核心和灵魂。'),
    ]
    for ch, t, d, text, opt, ans, expl in questions:
        conn.execute(
            "INSERT OR IGNORE INTO questions (id,chapter_id,type,difficulty,question_text,options,correct_answer,explanation,source) VALUES (?,?,?,?,?,?,?,?,'preset')",
            (_uuid(), ch, t, d, text, opt, ans, expl))


if __name__ == "__main__":
    conn = _get_conn()
    insert_kaoyan_english(conn)
    insert_gongkao_xingce(conn)
    insert_jiaozi(conn)
    conn.commit()
    conn.close()
    print("补充种子数据完成！")

    # 统计
    conn2 = _get_conn()
    types = conn2.execute("SELECT id,name,slug FROM exam_types ORDER BY sort_order").fetchall()
    total_q = 0
    for t in types:
        subs = conn2.execute("SELECT id,name FROM subjects WHERE exam_type_id=?", (t['id'],)).fetchall()
        q_count = 0
        for s in subs:
            cnt = conn2.execute("SELECT COUNT(*) FROM questions WHERE chapter_id IN (SELECT id FROM chapters WHERE subject_id=?)", (s['id'],)).fetchone()[0]
            q_count += cnt
        total_q += q_count
        print(f"  {t['name']}: {len(subs)} 个科目, {q_count} 道题")
    print(f"  总计: {total_q} 道题")
    conn2.close()
