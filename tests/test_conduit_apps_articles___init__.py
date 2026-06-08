import pytest
from conduit.apps.articles import _compute_reading_time, compute_reading_time


class TestComputeReadingTimeHappyPath:
    def test_typical_body_returns_correct_minutes(self):
        body = "word " * 400  # 400 words -> 2 minutes
        assert _compute_reading_time(body) == 2


class TestComputeReadingTimeEdgeCases:
    @pytest.mark.parametrize(
        "body, expected",
        [
            ("", 1),                     # empty string -> 1 min
            ("single", 1),               # 1 word -> 1 min
            ("word " * 199, 1),          # 199 words -> 1 min
            ("word " * 200, 1),          # 200 words exactly -> ceil(1) = 1, min 1
            ("word " * 201, 2),          # 201 words -> ceil(1.005) = 2
        ],
    )
    def test_boundary_and_zero_word_cases(self, body, expected):
        assert _compute_reading_time(body) == expected


class TestComputeReadingTimeError:
    def test_none_body_raises_attribute_error(self):
        with pytest.raises(AttributeError):
            _compute_reading_time(None)


class TestComputeReadingTimeAlias:
    def test_alias_returns_same_result_as_private_function(self):
        body = "hello world"
        assert compute_reading_time(body) == _compute_reading_time(body) == 1