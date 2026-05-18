import pytest
from unittest.mock import patch
from httpx import AsyncClient, ASGITransport


@pytest.fixture
def app():
    from backend.main import app
    return app


@pytest.mark.asyncio
async def test_health_endpoint(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_list_exam_types(app):
    mock_data = [{"id": "e1", "name": "考研", "slug": "kaoyan"}]
    with patch("backend.exam_routes.exam_db.get_exam_types", return_value=mock_data):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/exam/types")
            assert resp.status_code == 200
            body = resp.json()
            assert body["code"] == 0
            assert body["data"] == mock_data


@pytest.mark.asyncio
async def test_list_questions(app):
    mock_result = {"data": [], "count": 0}
    with patch("backend.exam_routes.exam_db.get_questions", return_value=mock_result):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/exam/questions", params={"subject_id": "s1"})
            assert resp.status_code == 200
            body = resp.json()
            assert body["code"] == 0
            assert body["data"]["items"] == []


@pytest.mark.asyncio
async def test_practice_submit_correct(app):
    mock_q = {
        "id": "q1", "type": "single_choice",
        "question_text": "test?", "correct_answer": "B",
        "explanation": "test explanation",
    }
    with (
        patch("backend.exam_routes.exam_db.get_question_by_id", return_value=mock_q),
        patch("backend.exam_routes.exam_db.upsert_progress"),
        patch("backend.exam_routes.exam_db.upsert_wrong_answer"),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/api/exam/practice/submit", json={
                "user_id": "u1", "question_id": "q1",
                "user_answer": "B", "subject_id": "s1",
            })
            assert resp.status_code == 200
            body = resp.json()
            assert body["data"]["is_correct"] is True


@pytest.mark.asyncio
async def test_practice_submit_wrong(app):
    mock_q = {
        "id": "q1", "type": "single_choice",
        "question_text": "test?", "correct_answer": "B",
        "explanation": "test explanation",
    }
    with (
        patch("backend.exam_routes.exam_db.get_question_by_id", return_value=mock_q),
        patch("backend.exam_routes.exam_db.upsert_progress"),
        patch("backend.exam_routes.exam_db.upsert_wrong_answer"),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/api/exam/practice/submit", json={
                "user_id": "u1", "question_id": "q1",
                "user_answer": "A", "subject_id": "s1",
            })
            assert resp.status_code == 200
            body = resp.json()
            assert body["data"]["is_correct"] is False


@pytest.mark.asyncio
async def test_qa_ask(app):
    mock_answer = "矛盾的普遍性是共性，特殊性是个性。"
    with (
        patch("backend.exam_routes.exam_qa.ask_question", return_value=mock_answer),
        patch("backend.exam_routes.exam_db.save_qa_session"),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/api/exam/qa/ask", json={
                "question": "什么是矛盾？", "user_id": "u1",
            })
            assert resp.status_code == 200
            body = resp.json()
            assert body["data"]["answer"] == mock_answer


@pytest.mark.asyncio
async def test_generate_questions(app):
    mock_questions = [
        {
            "type": "single_choice", "difficulty": "easy",
            "question_text": "AI 生成的题目？",
            "options": [{"label": "A", "text": "选项A"}],
            "correct_answer": "A", "explanation": "解析",
        }
    ]
    with (
        patch("backend.exam_routes.exam_generate.generate_questions", return_value=mock_questions),
        patch("backend.exam_routes.exam_db.save_generated_questions", return_value=["new-q-1"]),
        patch("backend.exam_routes.exam_db.get_preset_questions", return_value=[]),
        patch("backend.exam_routes.exam_db.get_questions", return_value={"data": [], "count": 0}),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/api/exam/practice/generate", json={
                "subject_id": "s1", "subject_name": "政治",
                "chapter_name": "马哲", "count": 3,
            })
            assert resp.status_code == 200
            body = resp.json()
            assert body["code"] == 0
            assert len(body["data"]["questions"]) == 1
