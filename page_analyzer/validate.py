from urllib.parse import urlparse

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


def get_url_by_id(id):
    """Получение URL по его ID из базы данных."""
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT name FROM urls WHERE id = %s', (id,))
            result = cursor.fetchone()
            return result[0] if result else None
    finally:
        conn.close()


def normalize_url(url):
    """Нормализация URL, добавление схемы, если она отсутствует."""
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        url = 'http://' + url
    return url
