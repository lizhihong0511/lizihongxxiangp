# 考证刷题助手

AI 驱动的考证练习平台，支持考研、公考、教资。

## 功能

- 💬 **AI 问答** — DeepSeek 辅导老师答疑
- ✏️ **智能练习** — 单选/多选/判断/填空，即时反馈
- 📋 **题库浏览** — 按考试→科目→章节浏览题目
- 🤖 **AI 出题** — AI 根据知识点自动生成题目
- 📝 **错题本** — 自动收集错题，标记复习
- 📥 **题库管理** — 上传 Word/PDF 文档，AI 自动提取题目

## 技术栈

| 层面 | 技术 |
|------|------|
| 后端 | Python + FastAPI |
| 前端 | Vue 3 + Vite |
| AI | DeepSeek API |
| 数据库 | SQLite |

## 本地运行

```bash
# 1. 安装后端依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 填入 DEEPSEEK_API_KEY

# 3. 启动后端
uvicorn backend.main:app --port 8000

# 4. 启动前端（新终端）
cd frontend && npm install && npm run dev

# 5. 打开浏览器
# http://localhost:5173
```

## 导入种子数据

```bash
python backend/seed_data.py    # 考研政治 15 题
python backend/seed_more.py    # 考研英语 + 公考 + 教资
```

## 部署

### GitHub Pages（前端）

Push 代码后自动部署，访问 `https://用户名.github.io/仓库名/`

### 后端

部署到 Render.com 或其他支持 FastAPI 的平台：

| 配置 | 值 |
|------|-----|
| Build Command | `pip install -r requirements.txt && cd frontend && npm install && npm run build` |
| Start Command | `uvicorn backend.main:app --host 0.0.0.0 --port $PORT` |

环境变量：`DEEPSEEK_API_KEY`、`ADMIN_IDS`

## 项目结构

```
├── backend/
│   ├── main.py            # FastAPI 入口
│   ├── exam_routes.py     # 考试 API 路由
│   ├── exam_db.py         # 数据库操作
│   ├── exam_qa.py         # AI 问答
│   ├── exam_generate.py   # AI 出题
│   ├── admin_routes.py    # 管理员路由
│   ├── admin_parser.py    # Word/PDF 解析
│   └── tests/             # 测试
├── frontend/
│   └── src/
│       ├── views/         # 6 个页面
│       └── api/           # API 客户端
├── render.yaml            # Render 部署配置
└── Procfile
```

## 管理员权限

在 `.env` 或环境变量中设置 `ADMIN_IDS`，值为你的用户 ID（在「我的」页面底部查看）。
