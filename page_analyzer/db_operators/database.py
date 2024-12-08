from datetime import datetime

from flask import flash


def add_url_to_db(cursor, url):
    """Добавление URL в базу данных."""
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        cursor.execute(
            'INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id',
            (url, created_at)
        )
        return cursor.fetchone()[0]  # Возвращаем id добавленного URL
    except Exception as e:
        flash(f'Ошибка при добавлении URL: {e}', 'error')
        return None


def add_url_check_to_db(cursor, url_id, status_code):
    """Добавление проверки URL в таблицу url_checks."""
    formatted_check_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        cursor.execute(
            'INSERT INTO url_checks (url_id, status_code, created_at) VALUES (\
            %s, %s, %s)',
            (url_id, status_code, formatted_check_date)
        )
    except Exception as e:
        flash(f'Ошибка при добавлении проверки URL: {e}', 'error')
