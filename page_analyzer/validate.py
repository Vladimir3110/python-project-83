from urllib.parse import urlparse, urlunparse

import psycopg2
import validators
from flask import flash

from page_analyzer.config import DATABASE_URL


def validate_url(url):
    """Валидация URL."""
    if not validators.url(url) and len(url) <= 255:
        flash('Некорректный URL')
        return False
    return True


# Хранение уже нормализованных URL для проверки дубликатов
existing_urls = set()


# def normalize_url(url):
#    """Нормализация URL, добавление схемы, если она отсутствует."""
#    parsed_url = urlparse(url)

#    if not parsed_url.scheme:
#        url = 'http://' + url
#        parsed_url = urlparse(url)  # Повторный разбор после добавления схемы
#    # Нормализация компонентов URL
#    scheme = parsed_url.scheme.lower()
#    netloc = parsed_url.netloc.lower()
#    path = parsed_url.path.lower().rstrip('/')
#    query = parsed_url.query
#    fragment = parsed_url.fragment
#    # Удаление стандартных портов
#    if scheme == 'http' and netloc.endswith(':80'):
#        netloc = netloc[:-3]  # Удаление ':80'
#    elif scheme == 'https' and netloc.endswith(':443'):
#        netloc = netloc[:-4]  # Удаление ':443'
#    # Восстановление нормализованного URL
#    normalized_url = urlunparse((scheme, netloc, path, '', query, fragment))
#    if normalized_url.endswith('/') and normalized_url != 'http://':
#        normalized_url = normalized_url[:-1]

#    # Проверка на существование URL
#    if normalized_url.startswith('https://'):
#        normalized_url = normalized_url.replace('https://', 'http://', 1)
#    # Проверка на существование URL
#    if normalized_url in existing_urls:
#        return "Страница уже существует"
#    # Добавление нормализованного URL в набор
#    existing_urls.add(normalized_url)
#    return normalized_url
# ================================
def get_existing_url_id(url):
    """Получение ID существующего URL из базы данных."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        with conn.cursor() as cursor:
            cursor.execute('SELECT id FROM urls WHERE name = %s', (url,))
            existing_url = cursor.fetchone()
            return existing_url[0] if existing_url else None
    finally:
        if 'conn' in locals():
            conn.close()


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
    if normalized_url.endswith('/') and normalized_url != 'http://':
        normalized_url = normalized_url[:-1]
    # Проверка на существование URL в базе данных
    existing_url_id = get_existing_url_id(normalized_url)
    if existing_url_id:
        return existing_url_id  # Возвращаем ID существующего URL
    # Добавление нормализованного URL в набор
    existing_urls.add(normalized_url)
    return normalized_url
