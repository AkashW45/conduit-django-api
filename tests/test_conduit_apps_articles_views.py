import pytest
import math
from unittest import mock

from rest_framework import status
from rest_framework.test import APIRequestFactory

from conduit.apps.articles.views import _add_reading_time, ArticleViewSet
from conduit.apps.articles.serializers import ArticleSerializer


class TestAddReadingTime:
    def test_single_dict_normal_body(self):
        data = {"body": "a " * 300}  # 300 words
        result = _add_reading_time(data)
        assert result["reading_time_minutes"] == 2  # ceil(300/200)=2

    def test_single_dict_empty_body(self):
        data = {"body": ""}
        result = _add_reading_time(data)
        assert result["reading_time_minutes"] == 1  # minimum 1

    def test_single_dict_one_word(self):
        data = {"body": "hello"}
        result = _add_reading_time(data)
        assert result["reading_time_minutes"] == 1

    def test_single_dict_missing_body_key(self):
        data = {"title": "No body"}
        result = _add_reading_time(data)
        assert result["reading_time_minutes"] == 1  # defaults to 1

    def test_list_of_dicts(self):
        items = [
            {"body": "word1 word2 word3"},          # 3 words -> 1 minute
            {"body": "a " * 400},                    # 400 words -> 2 minutes
            {"title": "No content"}                  # no body -> 1 minute
        ]
        result = _add_reading_time(items)
        assert result[0]["reading_time_minutes"] == 1
        assert result[1]["reading_time_minutes"] == 2
        assert result[2]["reading_time_minutes"] == 1


class TestArticleViewSetCreate:
    @mock.patch.object(ArticleViewSet, 'serializer_class', autospec=True)
    def test_create_response_includes_reading_time(self, mock_serializer_class):
        factory = APIRequestFactory()
        request = factory.post(
            '/fake-url/',
            {'article': {'body': 'quick brown fox'}},
            format='json'
        )
        # Mock a user with a profile
        request.user = mock.MagicMock()
        request.user.profile = mock.MagicMock()

        # Setup the mocked serializer
        serializer_instance = mock_serializer_class.return_value
        serializer_instance.is_valid.return_value = True
        serializer_instance.save.return_value = None
        # The serializer.data will be the initial data we passed
        serializer_instance.data = {'body': 'quick brown fox'}

        view = ArticleViewSet()
        response = view.create(request)

        assert response.status_code == status.HTTP_201_CREATED
        # reading time for 3 words -> ceil(3/200)=1
        assert response.data['reading_time_minutes'] == 1
        assert 'body' in response.data