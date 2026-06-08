from django.apps import AppConfig
import math


def _compute_reading_time(body: str) -> int:
    """
    Estimate reading time in minutes based on 200 words per minute.
    Rounded up, minimum 1 minute.
    """
    word_count = len(body.split())
    minutes = math.ceil(word_count / 200)
    return max(minutes, 1)

# Public alias (backward compatibility)
compute_reading_time = _compute_reading_time


class ArticlesAppConfig(AppConfig):
    name = 'conduit.apps.articles'
    label = 'articles'
    verbose_name = 'Articles'

    def ready(self):
        import conduit.apps.articles.signals

default_app_config = 'conduit.apps.articles.ArticlesAppConfig'
