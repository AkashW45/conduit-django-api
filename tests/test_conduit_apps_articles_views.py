import math
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory, force_authenticate

from conduit.apps.articles.views import (
    _add_reading_time, ArticleViewSet
)
from conduit.apps.articles.models import Article


@pytest.mark.django_db
class TestAddReadingTimeFunction:
    """Unit tests for _add_reading_time helper."""

    def test_single_dict_adds_reading_time(self):
        data = {'body': 'hello world'}  # 2 words
        result = _add_reading_time(data)
        assert result['reading_time_minutes'] == 1
        assert isinstance(result['reading_time_minutes'], int)

    def test_empty_body_returns_1_minute(self):
        data = {'body': ''}
        result = _add_reading_time(data)
        assert result['reading_time_minutes'] == 1

    def test_body_with_many_words_rounds_up(self):
        # 500 words -> 500/200 = 2.5 -> ceil 3
        data = {'body': 'word ' * 500}
        result = _add_reading_time(data)
        assert result['reading_time_minutes'] == 3

    def test_boundary_200_words_is_1_minute(self):
        data = {'body': 'word ' * 200}
        result = _add_reading_time(data)
        assert result['reading_time_minutes'] == 1

    def test_boundary_201_words_is_2_minutes(self):
        data = {'body': 'word ' * 201}
        result = _add_reading_time(data)
        assert result['reading_time_minutes'] == 2

    def test_list_of_dicts_adds_reading_time_to_each(self):
        data = [
            {'body': 'a b c'},  # 3 words -> 1
            {'body': 'a'}       # 1 word -> 1
        ]
        result = _add_reading_time(data)
        assert result[0]['reading_time_minutes'] == 1
        assert result[1]['reading_time_minutes'] == 1

    def test_missing_body_key_defaults_to_empty_string(self):
        data = {}
        result = _add_reading_time(data)
        assert result['reading_time_minutes'] == 1


@pytest.mark.django_db
class TestArticleCreateViewReadingTime:
    """Integration tests for ArticleViewSet.create endpoint."""

    def _create_user(self):
        return User.objects.create_user(
            username='testuser',
            password='secret',
            email='test@test.com'
        )

    def _setup_request(self, user, data):
        factory = APIRequestFactory()
        request = factory.post('/articles/', data, format='json')
        force_authenticate(request, user=user)
        return request

    def test_happy_path_reading_time_present(self):
        user = self._create_user()
        # Article data with a specific body word count
        data = {
            'article': {
                'title': 'Test Article',
                'description': 'desc',
                'body': 'one two three four five',  # 5 words -> 1 minute
            }
        }
        request = self._setup_request(user, data)
        view = ArticleViewSet.as_view({'post': 'create'})
        response = view(request)
        assert response.status_code == 201
        assert 'reading_time_minutes' in response.data
        assert response.data['reading_time_minutes'] == 1

    def test_empty_body_reading_time_is_1(self):
        user = self._create_user()
        data = {
            'article': {
                'title': 'Empty',
                'body': '',
            }
        }
        request = self._setup_request(user, data)
        view = ArticleViewSet.as_view({'post': 'create'})
        response = view(request)
        assert response.status_code == 201
        assert response.data['reading_time_minutes'] == 1

    def test_large_body_reading_time_rounds_up(self):
        user = self._create_user()
        body_words = 'word ' * 500  # 500 words
        data = {
            'article': {
                'title': 'Long',
                'body': body_words,
            }
        }
        request = self._setup_request(user, data)
        view = ArticleViewSet.as_view({'post': 'create'})
        response = view(request)
        assert response.status_code == 201
        assert response.data['reading_time_minutes'] == 3

    def test_invalid_data_does_not_add_reading_time(self):
        user = self._create_user()
        # Missing required fields – serializer should reject
        data = {'article': {}}
        request = self._setup_request(user, data)
        view = ArticleViewSet.as_view({'post': 'create'})
        response = view(request)
        # Expect validation error
        assert response.status_code == 400
        # reading_time_minutes should not be in response (errors are serializer.errors)
        assert 'reading_time_minutes' not in response.data