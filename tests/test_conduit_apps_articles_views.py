import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from conduit.apps.articles.views import _add_reading_time
from conduit.apps.articles.models import Article
from conduit.apps.profiles.models import Profile

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='testpass')

@pytest.fixture
def user2():
    return User.objects.create_user(username='otheruser', password='testpass')

@pytest.fixture
def profile(user):
    return Profile.objects.get(user=user)

@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client

@pytest.fixture
def article(profile):
    return Article.objects.create(
        title='Test Title',
        slug='test-title',
        body='This is a simple body with a few words.',
        description='Test description',
        author=profile,
    )

class TestAddReadingTime:
    def test_single_article_happy_path(self):
        data = {'body': 'word ' * 200}  # 200 words exactly
        updated = _add_reading_time(data)
        assert updated['reading_time_minutes'] == 1

    def test_single_article_rounds_up_above_200(self):
        data = {'body': 'word ' * 201}  # 201 words
        updated = _add_reading_time(data)
        assert updated['reading_time_minutes'] == 2

    def test_empty_body_minimum_one_minute(self):
        data = {'body': ''}
        updated = _add_reading_time(data)
        assert updated['reading_time_minutes'] == 1

    def test_no_body_key_minimum_one_minute(self):
        data = {'title': 'missing body'}
        updated = _add_reading_time(data)
        assert updated['reading_time_minutes'] == 1

    def test_list_of_articles_adds_reading_time_to_each(self):
        data_list = [
            {'body': 'one two three'},
            {'body': 'word ' * 100},
            {'body': ''}
        ]
        updated = _add_reading_time(data_list)
        assert updated[0]['reading_time_minutes'] == 1  # 3 words -> ceil(3/200)=1
        assert updated[1]['reading_time_minutes'] == 1  # 100 words -> 1
        assert updated[2]['reading_time_minutes'] == 1

class TestArticleCreateView:
    def test_create_returns_reading_time(self, authenticated_client, profile):
        article_data = {
            'title': 'Test',
            'body': 'hello ' * 100,  # 100 words
            'description': 'desc'
        }
        response = authenticated_client.post('/api/articles/', 
                                            {'article': article_data}, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert 'reading_time_minutes' in response.data
        assert response.data['reading_time_minutes'] == 1  # ceil(100/200)=1

    def test_create_long_body_reading_time(self, authenticated_client, profile):
        article_data = {
            'title': 'Long article',
            'body': 'word ' * 500,  # 500 words
            'description': 'desc'
        }
        response = authenticated_client.post('/api/articles/', 
                                            {'article': article_data}, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['reading_time_minutes'] == 3  # ceil(500/200)=3

class TestArticleListView:
    def test_list_includes_reading_time(self, authenticated_client, article):
        response = authenticated_client.get('/api/articles/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1  # paginated
        article_data = response.data['results'][0]
        assert 'reading_time_minutes' in article_data
        assert article_data['reading_time_minutes'] == 1  # article body has 9 words -> 1 minute

    def test_list_multiple_articles(self, authenticated_client, profile):
        Article.objects.create(
            title='Short',
            slug='short',
            body='Hi',
            description='short',
            author=profile
        )
        Article.objects.create(
            title='Long',
            slug='long',
            body='hello ' * 400,
            description='long',
            author=profile
        )
        response = authenticated_client.get('/api/articles/')
        assert response.status_code == 200
        results = response.data['results']
        assert len(results) == 2
        reading_times = [article['reading_time_minutes'] for article in results]
        assert 1 in reading_times  # first article min 1
        assert 2 in reading_times  # ceil(400/200)=2

class TestFavoriteAPIView:
    def test_favorite_post_returns_reading_time(self, authenticated_client, user2, profile):
        # Create an article by another user
        other_profile = Profile.objects.get(user=user2)
        article = Article.objects.create(
            title='Fav',
            slug='fav',
            body='Some body text here',
            description='fav desc',
            author=other_profile
        )
        response = authenticated_client.post(f'/api/articles/{article.slug}/favorite/')
        assert response.status_code == status.HTTP_201_CREATED
        assert 'reading_time_minutes' in response.data
        assert response.data['reading_time_minutes'] == 1  # 4 words -> 1 min

    def test_favorite_delete_returns_reading_time(self, authenticated_client, user2, profile):
        other_profile = Profile.objects.get(user=user2)
        article = Article.objects.create(
            title='Unfav',
            slug='unfav',
            body='Test',
            description='desc',
            author=other_profile
        )
        # First favorite it
        authenticated_client.post(f'/api/articles/{article.slug}/favorite/')
        response = authenticated_client.delete(f'/api/articles/{article.slug}/favorite/')
        assert response.status_code == status.HTTP_200_OK
        assert 'reading_time_minutes' in response.data
        assert response.data['reading_time_minutes'] == 1