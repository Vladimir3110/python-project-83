import psycopg2
from flask import current_app


def get_url_and_checks(url_id):
    """Получает URL и все проверки для данного URL из базы данных."""
    url = None
    checks = []

    try:
        # Пытаемся подключиться к базе данных
        with psycopg2.connect(
            current_app.config['DATABASE_URL'],
            sslmode='require'
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
