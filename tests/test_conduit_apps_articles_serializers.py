import pytest
from unittest.mock import Mock

from conduit.apps.articles.serializers import ArticleSerializer, _compute_reading_time


class TestArticleSerializerReadingTime:
    """Tests for the readingTimeMinutes field and its computation."""

    def test_reading_time_minutes_in_meta_fields(self):
        """Happy path: check that readingTimeMinutes is declared in serializer's Meta.fields."""
        assert 'readingTimeMinutes' in ArticleSerializer.Meta.fields

    def test_get_reading_time_minutes_calls_compute_reading_time(self):
        """Happy path: verify that get_reading_time_minutes delegates to _compute_reading_time."""
        instance = Mock()
        instance.body = "Some article body with multiple words"
        serializer = ArticleSerializer()
        result = serializer.get_reading_time_minutes(instance)
        expected = _compute_reading_time(instance.body)
        assert result == expected

    @pytest.mark.parametrize("body, expected_minutes", [
        ("", 1),                 # empty string -> word_count=1 -> ceil(1/200)=1 -> max(1,1)=1
        ("a", 1),                # 1 word -> 1 min
        ("word " * 200, 1),      # exactly 200 words -> ceil(200/200)=1 -> max(1,1)=1
        ("word " * 201, 2),      # 201 words -> ceil(201/200)=2
        ("word " * 400, 2),      # 400 words -> ceil(400/200)=2
        ("word " * 401, 3),      # 401 words -> ceil(401/200)=3
    ])
    def test_compute_reading_time_edge_cases(self, body, expected_minutes):
        """Edge cases: various body lengths, rounding up, and minimum of 1 minute."""
        # Strip trailing space for accurate word count
        if body.endswith(" "):
            body = body[:-1]
        assert _compute_reading_time(body) == expected_minutes

    def test_get_reading_time_minutes_with_none_body_raises_attribute_error(self):
        """Error path: accessing body=None should raise AttributeError inside _compute_reading_time."""
        instance = Mock()
        instance.body = None
        serializer = ArticleSerializer()
        with pytest.raises(AttributeError):
            serializer.get_reading_time_minutes(instance)