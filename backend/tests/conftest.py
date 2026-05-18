import pytest


@pytest.fixture
def mock_user_id():
    return "test-user-123"


@pytest.fixture
def sample_question():
    return {
        "id": "q-001",
        "type": "single_choice",
        "difficulty": "medium",
        "question_text": "矛盾的普遍性和特殊性的关系是？",
        "options": [
            {"label": "A", "text": "整体和部分的关系"},
            {"label": "B", "text": "共性和个性的关系"},
            {"label": "C", "text": "内容和形式的关系"},
        ],
        "correct_answer": "B",
        "explanation": "普遍性是共性，特殊性是个性。",
        "source": "preset",
    }


@pytest.fixture
def sample_exam_types():
    return [
        {"id": "e1", "name": "考研", "slug": "kaoyan", "icon": "🎓", "sort_order": 1},
        {"id": "e2", "name": "公考", "slug": "gongkao", "icon": "🏛️", "sort_order": 2},
    ]
