import math
from unittest.mock import MagicMock

import pytest

from conduit.apps.articles.serializers import _compute_reading_time, ArticleSerializer


def test_compute_reading_time_exact_200():
    body = "word " * 200  # exactly 200 words
    assert _compute_reading_time(body) == 1


def test_compute_reading_time_above_200():
    body = "word " * 250  # 250 words, ceil(250/200)=ceil(1.25)=2
    assert _compute_reading_time(body) == 2


def test_compute_reading_time_empty_body():
    assert _compute_reading_time("") == 1


def test_compute_reading_time_whitespace_body():
    body = "   \n  \t  "
    assert _compute_reading_time(body) == 1


def test_article_serializer_reading_time_minutes():
    serializer = ArticleSerializer()
    assert "readingTimeMinutes" in serializer.fields

    mock_article = MagicMock()
    mock_article.body = "word " * 350  # 350 words, ceil(350/200)=ceil(1.75)=2
    result = serializer.get_reading_time_minutes(mock_article)
    assert result == 2