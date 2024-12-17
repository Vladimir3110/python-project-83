import re
from urllib.parse import urlparse  # urlunparse

import psycopg2

# import validators
from flask import flash, get_flashed_messages

from page_analyzer.config import DATABASE_URL

MAX_LENGTH = 255


class MaxLengthError(Exception):
    """Возникает, если URL содержит более MAX_LENGTH символов."""
    pass


class ValidationError(Exception):
    """Возникает, если URL-адрес недействителен."""
    pass

# def validate_url(url):
#    """Валидация URL."""
#    if not validators.url(url) and len(url) <= 255:
#        flash('Некорректный URL')
#        return False
#    return True


# Хранение уже нормализованных URL для проверки дубликатов
# existing_urls = set()


def get_url_parts(url):
    parse_url = urlparse(url)
    scheme, netloc = parse_url.scheme, parse_url.netloc
    return scheme, netloc


def normalize_url(url):
    scheme, netloc = get_url_parts(url)
    return f'{scheme}://{netloc}'


def validate_url(url):
    scheme, netloc = get_url_parts(url)
    valid_netloc = re.match(r"[a-zA-Z0-9-]+\.[a-zA-Z]+", netloc)

    try:
        if scheme not in {'http', 'https'} or not valid_netloc:
            raise ValidationError
        if len(url) > MAX_LENGTH:
            raise MaxLengthError

    except ValidationError:
        flash('Некорректный URL', 'danger')
        if not url:
            flash('URL обязателен', 'danger')

    except MaxLengthError:
        flash(f'URL превышает {MAX_LENGTH} символов', 'danger')

    return get_flashed_messages(with_categories=True)


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


def check_existing_url(normalized_url):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM urls WHERE name = %s",
                           (normalized_url,))
            result = cursor.fetchone()
            return result[0] if result else None
    except Exception as e:
        print(f'Ошибка при проверке существования URL: {e}')
        return None
    finally:
        if 'conn' in locals():
            conn.close()


def add_url_to_db(database_url, normalized_url, created_at):
    """
    Добавляет нормализованный URL в базу данных.    """
    try:
        # Подключение к базе данных
        conn = psycopg2.connect(database_url)
        with conn.cursor() as cursor:
            # Проверка на существование URL перед добавлением
            cursor.execute("SELECT id FROM urls WHERE name = %s",
                           (normalized_url,))
            existing_url = cursor.fetchone()
            if existing_url:
                return False, existing_url[0]

            # Добавление нового URL в базу данных
            cursor.execute(
                "INSERT INTO urls (name, created_at) VALUES (%s, %s) \
                RETURNING id",
                (normalized_url, created_at)
            )
            new_url_id = cursor.fetchone()[0]  # Получаем ID нового URL
            conn.commit()
            return True, new_url_id

    except Exception as e:
        print(f'Ошибка при добавлении URL в базу данных: {e}')
        return False, None
    finally:
        if 'conn' in locals():
            conn.close()


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
#    # Проверка на существование URL в базе данных
#    existing_url_id = get_existing_url_id(normalized_url)
#    if existing_url_id:
#        return existing_url_id  # Возвращаем ID существующего URL
#    # Добавление нормализованного URL в набор
#    existing_urls.add(normalized_url)
#    return normalized_url
