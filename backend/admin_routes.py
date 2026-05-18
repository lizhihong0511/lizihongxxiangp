"""管理员路由：文档上传 + 题目导入（需授权）"""
import os, tempfile
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from backend import admin_parser, exam_db

router = APIRouter(prefix="/api/admin")

ALLOWED_EXT = {".docx", ".pdf"}


def _get_admin_ids() -> set:
    raw = os.getenv("ADMIN_IDS", "")
    return set(raw.split(",")) if raw else set()


def _check_admin(user_id: str):
    admins = _get_admin_ids()
    if not admins:
        raise HTTPException(status_code=403, detail="管理员未配置 (ADMIN_IDS)")
    if user_id not in admins:
        raise HTTPException(status_code=403, detail="无权访问")


@router.post("/parse-doc")
async def parse_doc(file: UploadFile = File(...), user_id: str = Form(...)):
    """上传 Word/PDF → AI 提取题目 → 返回预览"""
    _check_admin(user_id)

    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(status_code=400, detail=f"不支持的文件格式: {ext}，仅支持 .docx 和 .pdf")

    # 保存到临时文件
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
    try:
        content = await file.read()
        tmp.write(content)
        tmp.close()

        questions = admin_parser.parse_and_extract(tmp.name)
        return _ok({"questions": questions, "total": len(questions)})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析失败: {str(e)}")
    finally:
        os.unlink(tmp.name)


@router.post("/import-questions")
def import_questions(body: dict):
    """确认导入题目到数据库"""
    user_id = body.get("user_id", "")
    _check_admin(user_id)

    questions = body.get("questions", [])
    if not questions:
        raise HTTPException(status_code=400, detail="题目列表为空")

    # 补充默认字段
    subject_id = body.get("subject_id")
    chapter_id = body.get("chapter_id")

    for q in questions:
        q["chapter_id"] = chapter_id
        q["source"] = "preset"
        # 如果是新章节，不填 chapter_id 也能导入

    ids = exam_db.save_generated_questions(questions)
    return _ok({"imported": len(ids), "ids": ids})


def _ok(data=None, message="ok"):
    return {"code": 0, "data": data, "message": message}
