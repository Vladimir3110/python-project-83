# from contextlib import closing
from datetime import datetime

# import psycopg2
from flask import flash, redirect, url_for

from page_analyzer.db_operators.url_service import insert_url_check
from page_analyzer.parser import check_seo

# from page_analyzer.validate import normalize_url, validate_url


def handle_check_url(conn, id, normalized_url):
    """Обработчик проверки URL."""
    formatted_check_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        seo_data = check_seo(normalized_url)
        if seo_data is None or seo_data.get('status_code') != 200:
            flash('Произошла ошибка при проверке', 'error')
            return redirect(url_for('show_url', id=id))

        title = seo_data.get('title', 'Нет заголовка')
        description = seo_data.get('description', 'Нет описания')
        h1 = seo_data.get('h1', 'Нет h1')

        insert_url_check(id, seo_data.get('status_code'), title,
                         description, h1, formatted_check_date)
        flash('Страница успешно проверена!', 'success')
    except Exception as e:
        flash(f'Ошибка при добавлении проверки: {e}', 'error')
    return redirect(url_for('show_url', id=id))
