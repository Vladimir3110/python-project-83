from datetime import datetime

import psycopg2
from flask import flash, redirect, url_for

from page_analyzer.parser import check_seo


def handle_check_url(cursor, conn, id):
    """Обработчик проверки URL."""
    formatted_check_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        # Пытаемся подключиться к базе данных
        cursor = conn.cursor()
        print('Установлено соединение с базой данных')

        # Получаем URL из базы данных
        cursor.execute('SELECT name FROM urls WHERE id = %s', (id,))
        url = cursor.fetchone()
        if not url:
            flash('URL не найден', 'error')
            return redirect(url_for('list_urls'))
        # Проверяем SEO-параметры и получаем данные
        seo_data = check_seo(url[0])  # Передаем URL в функцию check_seo
        # Добавляем запись в таблицу url_checks
        cursor.execute(
            'INSERT INTO url_checks (url_id, status_code, title,\
            description, created_at) VALUES (%s, %s, %s, %s, %s)',
            (id, seo_data.get('status_code'), seo_data.get('title'),
             seo_data.get('description'), formatted_check_date)
        )
        conn.commit()
        flash('Страница успешно проверена!', 'success')
    except KeyError:
        # print('DATABASE_URL не найден в конфигурации приложения')
        flash('Ошибка конфигурации базы данных', 'error')
    except psycopg2.OperationalError as e:
        print(f'Невозможно установить соединение с базой данных: {e}')
        flash('Ошибка подключения к базе данных', 'error')
    except Exception as e:
        flash(f'Ошибка при добавлении проверки: {e}', 'error')
    finally:
        if 'conn' in locals():
            conn.close()
    return redirect(url_for('show_url', id=id))
