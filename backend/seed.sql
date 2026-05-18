-- 考研政治 种子数据
-- 在 Supabase SQL Editor 中执行

-- 考试类型
INSERT INTO exam_types (name, slug, icon, sort_order) VALUES
  ('考研', 'kaoyan', '🎓', 1),
  ('公考', 'gongkao', '🏛️', 2),
  ('教资', 'jiaozi', '📖', 3);

-- 考研 - 政治 科目
INSERT INTO subjects (exam_type_id, name, slug, sort_order)
  SELECT id, '政治', 'politics', 1 FROM exam_types WHERE slug = 'kaoyan';

INSERT INTO subjects (exam_type_id, name, slug, sort_order)
  SELECT id, '英语', 'english', 2 FROM exam_types WHERE slug = 'kaoyan';

-- 政治 - 章节
WITH politics AS (SELECT id FROM subjects WHERE slug = 'politics')
INSERT INTO chapters (subject_id, name, slug, sort_order) VALUES
  ((SELECT id FROM politics), '马克思主义哲学', 'marx-philosophy', 1),
  ((SELECT id FROM politics), '政治经济学', 'political-economy', 2),
  ((SELECT id FROM politics), '科学社会主义', 'scientific-socialism', 3),
  ((SELECT id FROM politics), '毛泽东思想', 'mao-thought', 4),
  ((SELECT id FROM politics), '中国特色社会主义', 'socialism-chinese', 5);

-- 政治 - 预设题目 (15道)
WITH philosophy AS (SELECT id FROM chapters WHERE slug = 'marx-philosophy'),
     economy AS (SELECT id FROM chapters WHERE slug = 'political-economy'),
     chinese_socialism AS (SELECT id FROM chapters WHERE slug = 'socialism-chinese')
INSERT INTO questions (chapter_id, type, difficulty, question_text, options, correct_answer, explanation, source) VALUES

-- 马哲 (5题)
((SELECT id FROM philosophy), 'single_choice', 'easy',
 '马克思主义哲学认为，世界的统一性在于它的',
 '[{"label":"A","text":"多样性"},{"label":"B","text":"物质性"},{"label":"C","text":"运动性"},{"label":"D","text":"矛盾性"}]',
 'B', '辩证唯物主义认为世界是物质的，世界的真正统一性在于它的物质性。这是马克思主义哲学的基本立场。', 'preset'),

((SELECT id FROM philosophy), 'single_choice', 'medium',
 '矛盾的普遍性和特殊性的关系是',
 '[{"label":"A","text":"整体和部分的关系"},{"label":"B","text":"共性和个性的关系"},{"label":"C","text":"内容和形式的关系"},{"label":"D","text":"原因和结果的关系"}]',
 'B', '矛盾的普遍性即共性，矛盾的特殊性即个性。普遍性寓于特殊性之中，并通过特殊性表现出来。', 'preset'),

((SELECT id FROM philosophy), 'true_false', 'easy',
 '实践是检验真理的唯一标准',
 '[]',
 'True', '实践是检验真理的唯一标准，这是马克思主义认识论的基本观点。真理是对客观事物及其规律的正确反映，其检验标准只能是社会实践。', 'preset'),

((SELECT id FROM philosophy), 'single_choice', 'medium',
 '辩证否定观的实质是',
 '[{"label":"A","text":"全盘否定"},{"label":"B","text":"全盘肯定"},{"label":"C","text":"扬弃"},{"label":"D","text":"抛弃"}]',
 'C', '辩证否定观的实质是"扬弃"，即既克服又保留，既批判又继承。它不是简单的否定一切，而是事物发展和联系的环节。', 'preset'),

((SELECT id FROM philosophy), 'fill_blank', 'easy',
 '马克思主义哲学的两大基本派别是唯物主义和____',
 '[]',
 '唯心主义', '哲学的基本问题是思维和存在的关系问题。根据对这个问题的不同回答，哲学分为唯物主义和唯心主义两大基本派别。', 'preset'),

-- 政治经济学 (5题)
((SELECT id FROM economy), 'single_choice', 'medium',
 '商品的二因素是指',
 '[{"label":"A","text":"使用价值和交换价值"},{"label":"B","text":"使用价值和价值"},{"label":"C","text":"价值和交换价值"},{"label":"D","text":"价值和价格"}]',
 'B', '商品是使用价值和价值的统一体。使用价值是商品的自然属性，价值是商品的社会属性。', 'preset'),

((SELECT id FROM economy), 'single_choice', 'hard',
 '在资本主义生产中，工人创造的新价值包括',
 '[{"label":"A","text":"不变资本和可变资本"},{"label":"B","text":"可变资本和剩余价值"},{"label":"C","text":"不变资本和剩余价值"},{"label":"D","text":"固定资本和流动资本"}]',
 'B', '工人劳动创造的新价值 = 可变资本（v）+ 剩余价值（m）。不变资本（c）转移的是生产资料的价值，不是工人新创造的。', 'preset'),

((SELECT id FROM economy), 'true_false', 'easy',
 '具体劳动创造商品的价值，抽象劳动创造商品的使用价值',
 '[]',
 'False', '这个说法是错误的。正确的是：具体劳动创造商品的使用价值，抽象劳动创造商品的价值。具体劳动和抽象劳动是同一劳动的两个方面。', 'preset'),

((SELECT id FROM economy), 'single_choice', 'easy',
 '货币的本质是',
 '[{"label":"A","text":"一般等价物"},{"label":"B","text":"商品交换的媒介"},{"label":"C","text":"价值的符号"},{"label":"D","text":"财富的代表"}]',
 'A', '货币的本质是固定充当一般等价物的商品。它体现着商品经济条件下人们之间的社会关系。', 'preset'),

((SELECT id FROM economy), 'fill_blank', 'medium',
 '资本主义生产过程是劳动过程和____过程的统一',
 '[]',
 '价值增殖', '资本主义生产过程具有二重性：一方面是生产使用价值的劳动过程，另一方面是生产剩余价值的价值增殖过程。', 'preset'),

-- 中国特色社会主义 (5题)
((SELECT id FROM chinese_socialism), 'single_choice', 'easy',
 '中国特色社会主义最本质的特征是',
 '[{"label":"A","text":"人民当家作主"},{"label":"B","text":"中国共产党领导"},{"label":"C","text":"全面依法治国"},{"label":"D","text":"社会主义市场经济"}]',
 'B', '中国特色社会主义最本质的特征是中国共产党领导，中国特色社会主义制度的最大优势是中国共产党领导。', 'preset'),

((SELECT id FROM chinese_socialism), 'single_choice', 'medium',
 '我国社会主要矛盾已经转化为',
 '[{"label":"A","text":"人民日益增长的物质文化需要同落后的社会生产之间的矛盾"},{"label":"B","text":"人民日益增长的美好生活需要和不平衡不充分的发展之间的矛盾"},{"label":"C","text":"经济高速增长和高质量发展之间的矛盾"},{"label":"D","text":"城市和农村发展不平衡之间的矛盾"}]',
 'B', '党的十九大报告指出，我国社会主要矛盾已经转化为人民日益增长的美好生活需要和不平衡不充分的发展之间的矛盾。', 'preset'),

((SELECT id FROM chinese_socialism), 'multi_choice', 'medium',
 '全面深化改革的总目标是',
 '[{"label":"A","text":"完善和发展中国特色社会主义制度"},{"label":"B","text":"推进国家治理体系和治理能力现代化"},{"label":"C","text":"实现经济高速增长"},{"label":"D","text":"全面建成小康社会"}]',
 'A,B', '全面深化改革的总目标是完善和发展中国特色社会主义制度，推进国家治理体系和治理能力现代化。这是党的十八届三中全会提出的。', 'preset'),

((SELECT id FROM chinese_socialism), 'true_false', 'easy',
 '共同富裕是社会主义的本质要求',
 '[]',
 'True', '共同富裕是社会主义的本质要求，是中国式现代化的重要特征。要坚持以人民为中心的发展思想，在高质量发展中促进共同富裕。', 'preset'),

((SELECT id FROM chinese_socialism), 'fill_blank', 'easy',
 '新发展理念包括创新、协调、绿色、开放、____',
 '[]',
 '共享', '五大新发展理念：创新、协调、绿色、开放、共享。这是习近平新时代中国特色社会主义思想的重要内容。', 'preset');
