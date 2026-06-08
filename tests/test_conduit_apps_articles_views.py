import pytest
from math import ceil
from conduit.apps.articles.views import _add_reading_time


class TestAddReadingTime:
    """Tests for the _add_reading_time helper function."""

    def test_single_dict_happy_path(self):
        body = "word " * 500  # 500 words
        data = {"body": body}
        result = _add_reading_time(data)
        expected_minutes = ceil(500 / 200)  # 3
        assert result is data  # should return the same object
        assert result["reading_time_minutes"] == expected_minutes

    def test_list_of_dicts_happy_path(self):
        body1 = "word " * 200   # 200 words -> ceil=1 -> max(1,1)=1
        body2 = "word " * 201   # 201 words -> ceil=2
        data = [
            {"body": body1},
            {"body": body2}
        ]
        result = _add_reading_time(data)
        assert result is data
        assert result[0]["reading_time_minutes"] == 1
        assert result[1]["reading_time_minutes"] == 2

    def test_edge_empty_body(self):
        data = {"body": ""}
        result = _add_reading_time(data)
        assert result["reading_time_minutes"] == 1

    def test_edge_body_exact_200_words(self):
        body = "word " * 200
        data = {"body": body}
        result = _add_reading_time(data)
        # ceil(200/200) = 1, min=1 -> 1
        assert result["reading_time_minutes"] == 1

    def test_edge_body_201_words(self):
        body = "word " * 201
        data = {"body": body}
        result = _add_reading_time(data)
        # ceil(201/200)=2
        assert result["reading_time_minutes"] == 2

    def test_edge_missing_body_key(self):
        data = {"title": "No body"}
        result = _add_reading_time(data)
        # body defaults to '' -> word_count 0 -> max(1,ceil(0))=1
        assert result["reading_time_minutes"] == 1

    def test_error_non_dict_or_list(self):
        with pytest.raises(AttributeError):
            _add_reading_time("not a dict or list")