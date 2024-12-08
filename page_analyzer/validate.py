from urllib.parse import urlparse

import validators
from flask import flash


def validate_url(url):
    """Валидация URL."""
    if not validators.url(url):
        flash('Некорректный URL. Попробуйте снова.', 'error')
        return False
    return True


def normalize_url(url):
    """Нормализация URL, добавление схемы, если она отсутствует."""
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        url = 'http://' + url
    return url


def check_url_length(url):
    """Проверка длины URL."""
    if len(url) > 255:
        flash(
            'URL слишком длинный. Максимальная длина — 255 символов.', 'error')
        return False
    return True
