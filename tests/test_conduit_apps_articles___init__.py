import pytest
from conduit.apps.articles import compute_reading_time

class TestComputeReadingTime:
    """Tests for the compute_reading_time utility."""

    # Happy path tests
    def test_happy_path_normal_body(self):
        # Normal article length ~400 words => 2 minutes
        body = "word " * 400
        assert compute_reading_time(body) == 2

    def test_happy_path_exact_boundary(self):
        # Exactly 200 words => 1 minute
        body = "word " * 200
        assert compute_reading_time(body) == 1

    def test_ceiling_round_up(self):
        # 201 words => ceil(201/200)=2, min 1 => 2
        body = "word " * 201
        assert compute_reading_time(body) == 2

    # Edge case tests
    def test_edge_empty_body_returns_min_one(self):
        assert compute_reading_time("") == 1

    def test_error_non_string_input(self):
        # Passing something without split should raise AttributeError
        with pytest.raises(AttributeError):
            compute_reading_time(None)