from urllib.parse import urlparse

import validators
from flask import flash


def validate_url(url):
    """Валидация URL."""
    if not validators.url(url) and len(url) <= 255:
        flash('Некорректный URL')
        return False
    return True


def normalize_url(url):
    """Нормализация URL, добавление схемы, если она отсутствует."""
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        url = 'http://' + url
    return url
