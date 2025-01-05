import psycopg2
from flask import current_app, flash

from page_analyzer.config import DATABASE_URL


def get_url_and_checks(url_id):
    """Получает URL и все проверки для данного URL из базы данных."""
    url = None
    checks = []

    try:
        # Пытаемся подключиться к базе данных
        with psycopg2.connect(
            current_app.config['DATABASE_URL'],
            sslmode='prefer'
        ) as conn:
            with conn.cursor() as cursor:
                # Получаем URL
                cursor.execute(
                    'SELECT id, name, created_at FROM urls WHERE id = %s', (
                        url_id,)
                )
                url = cursor.fetchone()
                if not url:
                    return None, None
                # Получаем все проверки для данного URL
                cursor.execute(
                    'SELECT * FROM url_checks WHERE url_id = %s\
                    ORDER BY created_at DESC',
                    (url_id,)
                )
                checks = cursor.fetchall()
    except psycopg2.Error as e:
        print(f'Ошибка при работе с базой данных: {e}')
    return url, checks  # Возвращаем URL и проверки


def get_urls_with_checks():
    """Извлекает URL и их последние проверки из базы данных."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT u.id, u.name, u.created_at, uc.status_code
                FROM urls u
                LEFT JOIN (
                    SELECT url_id, status_code
                    FROM url_checks
                    WHERE id IN (
                        SELECT MAX(id) FROM url_checks GROUP BY url_id
                    )
                ) uc ON u.id = uc.url_id
                ORDER BY u.created_at DESC
            """)
            return cursor.fetchall()
    except Exception as e:
        flash(f'Ошибка при получении URL: {e}', 'error')
        return []
    finally:
        if 'conn' in locals():
            conn.close()


def insert_url_check(url_id, status_code, title, description, h1, created_at):
    """Вставляет данные о проверке URL в базу данных."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        with conn.cursor() as cursor:
            cursor.execute(
                'INSERT INTO url_checks (url_id, status_code, title, \
                description, h1, created_at) VALUES (%s, %s, %s, %s, %s, %s)',
                (url_id, status_code, title, description, h1, created_at)
            )
            conn.commit()
    except Exception as e:
        flash(f'Ошибка при добавлении проверки: {e}', 'error')
    finally:
        if 'conn' in locals():
            conn.close()
