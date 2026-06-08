import pytest
from conduit.apps.articles import _compute_reading_time, compute_reading_time


class TestComputeReadingTime:
    @pytest.mark.parametrize("body, expected", [
        ("word", 1),
        ("one two three", 1),
        ("a " * 200, 1),
        ("a " * 201, 2),
        ("a " * 400, 2),
        ("a " * 1000, 5),
    ])
    def test_reading_time_happy_path(self, body, expected):
        assert _compute_reading_time(body) == expected
        assert compute_reading_time(body) == expected

    @pytest.mark.parametrize("body", ["", "   ", "\n\t "])
    def test_reading_time_minimum_one(self, body):
        assert _compute_reading_time(body) == 1
        assert compute_reading_time(body) == 1

    def test_reading_time_none_input(self):
        with pytest.raises(AttributeError):
            _compute_reading_time(None)
        with pytest.raises(AttributeError):
            compute_reading_time(None)

    def test_reading_time_non_string_input(self):
        with pytest.raises(AttributeError):
            _compute_reading_time(123)
        with pytest.raises(AttributeError):
            compute_reading_time(123)

    def test_reading_time_alias_identity(self):
        assert compute_reading_time is _compute_reading_time