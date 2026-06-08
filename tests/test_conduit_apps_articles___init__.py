import pytest
from conduit.apps.articles import compute_reading_time


class TestComputeReadingTime:
    """Tests for the compute_reading_time helper."""

    def test_happy_path_short_body(self):
        """A body with fewer than 200 words should yield 1 minute."""
        body = "word " * 50  # 50 words
        assert compute_reading_time(body) == 1

    def test_edge_case_empty_body(self):
        """Empty or whitespace-only body returns 1 (the minimum)."""
        assert compute_reading_time("") == 1
        assert compute_reading_time("   ") == 1

    def test_edge_case_exact_200_words(self):
        """Exactly 200 words returns 1 minute."""
        body = "word " * 200
        body = body.rstrip()
        assert compute_reading_time(body) == 1

    def test_error_path_none_body(self):
        """Passing None should raise AttributeError because None has no split."""
        with pytest.raises(AttributeError):
            compute_reading_time(None)