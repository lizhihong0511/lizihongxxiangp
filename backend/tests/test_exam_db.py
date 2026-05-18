import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture(autouse=True)
def reset_client():
    import backend.exam_db as db
    db._supabase = None


class TestExamDb:
    @patch("backend.exam_db.create_client")
    def test_get_exam_types(self, mock_create, sample_exam_types):
        mock_client = MagicMock()
        mock_create.return_value = mock_client

        mock_chain = MagicMock()
        mock_chain.execute.return_value.data = sample_exam_types
        mock_client.table.return_value.select.return_value.order.return_value = mock_chain

        from backend.exam_db import get_exam_types
        result = get_exam_types()

        assert result == sample_exam_types
        mock_client.table.assert_called_with("exam_types")

    @patch("backend.exam_db.create_client")
    def test_get_subjects(self, mock_create):
        mock_client = MagicMock()
        mock_create.return_value = mock_client
        subjects = [{"id": "s1", "name": "政治", "exam_type_id": "e1"}]
        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = subjects

        from backend.exam_db import get_subjects
        result = get_subjects("e1")

        assert result == subjects

    @patch("backend.exam_db.create_client")
    def test_upsert_progress_new(self, mock_create):
        mock_client = MagicMock()
        mock_create.return_value = mock_client
        # upsert_progress does 2 queries before insert, both return [] for new user
        mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.is_.return_value.execute.return_value.data = []

        from backend.exam_db import upsert_progress
        upsert_progress("u1", "s1", None, True)

        mock_client.table.return_value.insert.assert_called_once()

    @patch("backend.exam_db.create_client")
    def test_upsert_progress_existing(self, mock_create):
        mock_client = MagicMock()
        mock_create.return_value = mock_client

        # First call returns existing, second call for the simpler query
        mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.is_.return_value.execute.return_value.data = []
        mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [{"id": "p1", "total_answered": 5, "total_correct": 3}]

        from backend.exam_db import upsert_progress
        upsert_progress("u1", "s1", "c1", True)

        mock_client.table.return_value.update.return_value.eq.return_value.execute.assert_called_once()

    @patch("backend.exam_db.create_client")
    def test_get_wrong_answers(self, mock_create):
        mock_client = MagicMock()
        mock_create.return_value = mock_client

        mock_chain = MagicMock()
        mock_chain.execute.return_value.data = []
        mock_chain.execute.return_value.count = 0
        mock_client.table.return_value.select.return_value.eq.return_value.range.return_value.order.return_value = mock_chain

        from backend.exam_db import get_wrong_answers
        result = get_wrong_answers("u1")

        assert result == {"data": [], "count": 0}
