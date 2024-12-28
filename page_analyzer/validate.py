import re
from urllib.parse import urlparse

import psycopg2
from flask import flash, get_flashed_messages

from page_analyzer.config import DATABASE_URL

MAX_LENGTH = 255


class MaxLengthError(Exception):
    """Возникает, если URL содержит более MAX_LENGTH символов."""
    pass


class ValidationError(Exception):
    """Возникает, если URL-адрес недействителен."""
    pass


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
        created_at = created_at.strftime("%Y-%m-%d %H:%M:%S")
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
