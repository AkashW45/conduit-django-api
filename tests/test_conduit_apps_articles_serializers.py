import math
import pytest
from unittest.mock import Mock

from conduit.apps.articles.serializers import _compute_reading_time, ArticleSerializer

# Parametrized happy-path cases
@pytest.mark.parametrize(
    "body, expected",
    [
        ("one", 1),                     # 1 word -> 1 min
        ("word " * 200, 1),             # exactly 200 words -> ceil(200/200)=1
        ("word " * 201, 2),             # 201 words -> ceil(201/200)=2
        ("word " * 400, 2),             # exactly 400 words -> ceil(400/200)=2
        ("w " * 5000, 25),              # 5000 words -> ceil(5000/200)=25
    ],
)
def test_compute_reading_time_happy_path(body, expected):
    assert _compute_reading_time(body) == expected


def test_compute_reading_time_empty_body():
    assert _compute_reading_time("") == 1


def test_compute_reading_time_whitespace_only():
    # Multiple spaces/tabs/newlines produce empty list after split -> 0 words, min 1
    assert _compute_reading_time("    \t\n  ") == 1


def test_article_serializer_has_reading_time_minutes_field():
    serializer = ArticleSerializer()
    assert "readingTimeMinutes" in serializer.fields
    field = serializer.fields["readingTimeMinutes"]
    assert field.method_name == "get_reading_time_minutes"


def test_article_serializer_get_reading_time_minutes():
    article = Mock()
    article.body = "This is a sample body with several words."
    result = ArticleSerializer().get_reading_time_minutes(article)
    assert result == 1