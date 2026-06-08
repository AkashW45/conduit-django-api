import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from conduit.apps.articles.models import Article
from conduit.apps.profiles.models import Profile

BASE_URL = '/api'

@pytest.fixture
def user(db):
    user = User.objects.create_user(username='testuser', password='testpass')
    Profile.objects.create(user=user, bio='Test bio')
    return user

@pytest.fixture
def article(db, user):
    article = Article.objects.create(
        title='Test Article',
        description='A test article',
        body='This is a test article body with some words.',
        author=user.profile,
    )
    return article

@pytest.fixture
def client():
    return APIClient()

@pytest.mark.django_db
class TestArticleReadingTime:

    def test_article_list_includes_reading_time(self, client, user, article):
        """Happy path: article list returns reading_time_minutes."""
        client.force_authenticate(user=user)
        response = client.get(f'{BASE_URL}/articles/')
        assert response.status_code == 200
        data = response.json()
        articles = data.get('results', data.get('articles', []))
        for art in articles:
            assert 'reading_time_minutes' in art
            assert art['reading_time_minutes'] >= 1

    def test_article_retrieve_includes_reading_time(self, client, user, article):
        """Happy path: article detail returns reading_time_minutes."""
        client.force_authenticate(user=user)
        response = client.get(f'{BASE_URL}/articles/{article.slug}/')
        assert response.status_code == 200
        data = response.json()
        assert 'reading_time_minutes' in data
        assert data['reading_time_minutes'] == 1

    def test_article_create_returns_reading_time(self, client, user):
        """Happy path: newly created article response includes reading_time_minutes."""
        client.force_authenticate(user=user)
        article_data = {
            'article': {
                'title': 'New Article',
                'description': 'A new article',
                'body': 'Word1 Word2 Word3 ' * 100
            }
        }
        response = client.post(
            f'{BASE_URL}/articles/',
            data=article_data,
            format='json'
        )
        assert response.status_code == 201
        data = response.json()
        assert 'reading_time_minutes' in data
        # 300 words / 200 = 1.5 => ceil=2
        assert data['reading_time_minutes'] == 2

    def test_article_update_returns_reading_time(self, client, user, article):
        """Update endpoint should include reading_time_minutes."""
        client.force_authenticate(user=user)
        update_data = {
            'article': {
                'body': 'Updated body with more words.'
            }
        }
        response = client.patch(
            f'{BASE_URL}/articles/{article.slug}/',
            data=update_data,
            format='json'
        )
        assert response.status_code == 200
        data = response.json()
        assert 'reading_time_minutes' in data
        assert data['reading_time_minutes'] == 1

    def test_article_favorite_returns_reading_time(self, client, user, article):
        """Favorite (post) and unfavorite (delete) responses contain reading_time_minutes."""
        client.force_authenticate(user=user)
        # favorite
        response = client.post(f'{BASE_URL}/articles/{article.slug}/favorite/')
        assert response.status_code == 201
        data = response.json()
        assert 'reading_time_minutes' in data
        # unfavorite
        response = client.delete(f'{BASE_URL}/articles/{article.slug}/favorite/')
        assert response.status_code == 200
        data = response.json()
        assert 'reading_time_minutes' in data

    def test_calculate_reading_time_minimum_one(self, client, user, article):
        """Edge case: body with very few words yields minimum of 1 minute."""
        article.body = "a b c"
        article.save()
        client.force_authenticate(user=user)
        response = client.get(f'{BASE_URL}/articles/{article.slug}/')
        assert response.status_code == 200
        data = response.json()
        assert data['reading_time_minutes'] == 1

    def test_article_not_found_returns_404(self, client, user):
        """Error path: requesting non-existent slug returns 404."""
        client.force_authenticate(user=user)
        response = client.get(f'{BASE_URL}/articles/non-existent-slug/')
        assert response.status_code == 404