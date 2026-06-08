import pytest
from conduit.apps.articles.serializers import ArticleSerializer

class MockArticle:
    def __init__(self, body):
        self.body = body

def test_reading_time_minutes_200_words_returns_1():
    serializer = ArticleSerializer()
    article = MockArticle(body="word " * 200)
    result = serializer.get_reading_time_minutes(article)
    assert result == 1

def test_reading_time_minutes_201_words_returns_2():
    serializer = ArticleSerializer()
    article = MockArticle(body="word " * 201)
    result = serializer.get_reading_time_minutes(article)
    assert result == 2

def test_reading_time_minutes_single_word_returns_1():
    serializer = ArticleSerializer()
    article = MockArticle(body="hello")
    result = serializer.get_reading_time_minutes(article)
    assert result == 1

def test_reading_time_minutes_empty_body_returns_1():
    serializer = ArticleSerializer()
    article = MockArticle(body="")
    result = serializer.get_reading_time_minutes(article)
    assert result == 1

def test_reading_time_minutes_whitespace_body_returns_1():
    serializer = ArticleSerializer()
    article = MockArticle(body="   \n  ")
    result = serializer.get_reading_time_minutes(article)
    assert result == 1

def test_reading_time_minutes_none_body_raises_attribute_error():
    serializer = ArticleSerializer()
    article = MockArticle(body=None)
    with pytest.raises(AttributeError):
        serializer.get_reading_time_minutes(article)