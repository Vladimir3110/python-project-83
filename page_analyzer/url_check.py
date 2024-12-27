from datetime import datetime

import psycopg2
from flask import flash, redirect, url_for
from page_analyzer.parser import check_seo


def handle_check_url(conn, id):
    """Обработчик проверки URL."""
    formatted_check_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor = None
    try:
        cursor = conn.cursor()
        # Получаем URL из базы данных
        cursor.execute('SELECT name FROM urls WHERE id = %s', (id,))
        url = cursor.fetchone()
        if not url:
            flash('URL не найден', 'error')
            return redirect(url_for('list_urls'))
        # Проверяем SEO-параметры и получаем данные
        seo_data = check_seo(url[0])
        # Отладочное сообщение
        # print(f"SEO данные для URL {url[0]}: {seo_data}")

        # Проверяем, что данные SEO корректны
        if seo_data is None or seo_data.get('status_code') != 200:
            flash('Ошибка при получении данных SEO', 'error')
            return redirect(url_for('show_url', id=id))
        cursor.execute(
            'INSERT INTO url_checks (url_id, status_code, h1, title, \
            description, \
            created_at) VALUES (%s, %s, %s, %s, %s)',
            (id, seo_data.get('status_code'), seo_data.get('title'),
             seo_data.get('description'), formatted_check_date)
        )
        conn.commit()
        flash('Страница успешно проверена!', 'success')
    except psycopg2.OperationalError as e:
        print(f'Невозможно установить соединение с базой данных: {e}')
        flash('Ошибка подключения к базе данных', 'error')
    except Exception as e:
        flash(f'Ошибка при добавлении проверки: {e}', 'error')
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return redirect(url_for('show_url', id=id))
