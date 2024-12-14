from urllib.parse import urlparse, urlunparse

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
        parsed_url = urlparse(url)  # Повторный разбор после добавления схемы
    # Нормализация компонентов URL
    scheme = parsed_url.scheme.lower()
    netloc = parsed_url.netloc.lower()
    path = parsed_url.path.lower().rstrip('/')
    query = parsed_url.query
    fragment = parsed_url.fragment
    # Удаление стандартных портов
    if scheme == 'http' and netloc.endswith(':80'):
        netloc = netloc[:-3]  # Удаление ':80'
    elif scheme == 'https' and netloc.endswith(':443'):
        netloc = netloc[:-4]  # Удаление ':443'
    # Восстановление нормализованного URL
    normalized_url = urlunparse((scheme, netloc, path, '', query, fragment))
    return normalized_url
