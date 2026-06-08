import pytest
from unittest.mock import Mock
from conduit.apps.articles.serializers import _compute_reading_time, ArticleSerializer


def test_compute_reading_time_empty_body():
    assert _compute_reading_time("") == 1


def test_compute_reading_time_single_word():
    assert _compute_reading_time("hello") == 1


def test_compute_reading_time_200_words():
    body = "word " * 200  # exactly 200 words
    assert _compute_reading_time(body) == 1


def test_compute_reading_time_201_words():
    body = "word " * 201
    assert _compute_reading_time(body) == 2


def test_compute_reading_time_401_words():
    body = "a " * 401
    assert _compute_reading_time(body) == 3


def test_serializer_reading_time_field():
    mock_article = Mock()
    mock_article.body = "This is a test body with just 8 words"
    serializer = ArticleSerializer(instance=mock_article)
    assert serializer.get_reading_time_minutes(mock_article) == 1